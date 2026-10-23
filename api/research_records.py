"""Bounded, read-only exports. Vendored into independent producer deployments.

Adapters supply retained records and explicit dependencies; this module never
fetches sources, changes storage, or substitutes current runtime for saved state.
"""
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import re
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import falcon

SCHEMA = 'swift-saved-research-export-v1'
FILE_LIMIT = 8_000_000
PACKAGE_LIMIT = 64_000_000
PRIVATE = {'Observer', 'owner', 'forecaster', 'forecasterId', 'forecaster_id', 'actor',
           'finalizedBy', 'finalized_by', 'username', 'email', 'password', 'token',
           'access_token', 'api_key', 'client_secret', 'authorization', 'requested_by',
           'created_by', 'createdBy', 'updated_by', 'updatedBy', 'issued_by', 'reviewed_by'}


def readonly_rows(dsn, query, params=(), max_rows=20000):
    """Stream fixed adapter SQL; never use a producer's initializing DB reader."""
    import psycopg
    try:
        with psycopg.connect(dsn, connect_timeout=3) as connection:
            connection.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY')
            connection.execute("SET LOCAL statement_timeout = '3s'")
            with connection.cursor(name='research_saved_rows') as cursor:
                cursor.execute(query, params)
                count = 0
                while rows := cursor.fetchmany(64):
                    for row in rows:
                        count += 1
                        if count > max_rows:
                            raise ValueError('Selected research query exceeds the row limit; no truncated export is returned.')
                        yield row[0]
    except psycopg.Error as exc:
        raise RuntimeError('Saved research database could not be read.') from exc


def sqlite_rows(path, table, query, params=(), max_rows=20000):
    """Read existing SQLite tables without initializing or repairing storage."""
    import sqlite3
    import time
    path = Path(path).resolve()
    if not path.is_file():
        return
    try:
        with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=3) as db:
            db.row_factory = sqlite3.Row
            db.execute('PRAGMA query_only=ON')
            deadline = time.monotonic() + 3
            db.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
            try:
                if not db.execute('SELECT 1 FROM sqlite_master WHERE type=\'table\' AND name=?', (table,)).fetchone():
                    return
                cursor = db.execute(query, params)
                count = 0
                while True:
                    # Limit database work, excluding time the consumer spends
                    # hashing/serializing already fetched rows between yields.
                    deadline = time.monotonic() + 3
                    batch = cursor.fetchmany(64)
                    if not batch:
                        break
                    for row in batch:
                        if count >= max_rows:
                            raise ValueError('Selected research query exceeds the row limit; no truncated export is returned.')
                        count += 1
                        yield dict(row)
            finally:
                db.set_progress_handler(None, 0)
    except sqlite3.Error as exc:
        raise RuntimeError('Saved research database could not be read.') from exc
    finally:
        if 'db' in locals():
            db.close()


def dependencies(item):
    value = item.get('dependencies', [])
    return value() if callable(value) else value


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode('utf-8')


def clean(value):
    if isinstance(value, dict):
        return {key: clean(child) for key, child in value.items() if key not in PRIVATE}
    if isinstance(value, list):
        return [clean(child) for child in value]
    return value


def safe_path(root, name):
    # Reject both Windows and POSIX traversal even when running in Linux Docker.
    if not isinstance(name, str) or '\\' in name or ':' in name:
        raise ValueError('Invalid retained dependency path.')
    parts = PurePosixPath(name)
    if parts.is_absolute() or any(part in ('', '.', '..') for part in name.split('/')):
        raise ValueError('Invalid retained dependency path.')
    target = (root / name).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('Dependency escapes owning storage.')
    return target


def read_json(path, limit=16_000_000):
    with path.open('rb') as handle:
        raw = handle.read(limit + 1)
    if len(raw) > limit:
        raise ValueError('Retained record exceeds the research read limit.')
    result = json.loads(raw)
    if not isinstance(result, dict):
        raise ValueError('Retained record must be an object.')
    return result


def identity(application, family, record):
    return sha256(encoded({'application': application, 'family': family, 'record': clean(record)})).hexdigest()


def build(application, item):
    record = clean(item['record'])
    record_bytes = encoded(record)
    if len(record_bytes) > 2_000_000:
        raise ValueError('Saved record exceeds the inspection limit.')
    capture = identity(application, item['family'], record)
    files = {'record.json': record_bytes}
    assets = [dict(role='record', path='record.json', description=item['description'], availability='available',
                   media_type='application/json', bytes=len(record_bytes), sha256=sha256(record_bytes).hexdigest())]
    required = dependencies(item)
    if len(required) > 128:
        raise ValueError('Too many dependencies for one selected case.')
    for dependency in required:
        name = dependency['path']
        if not re.fullmatch(r'files/[A-Za-z0-9_./-]+', name) or '..' in name.split('/') or name in files:
            raise ValueError('Invalid or duplicate portable dependency name.')
        role = sha256(name.encode()).hexdigest()
        entry = dict(role=role, path=name, description=dependency['description'], availability='unavailable',
                     media_type=dependency.get('media_type', 'application/json'), bytes=None, sha256=None)
        try:
            if 'raw' in dependency:
                raw = dependency['raw']
                if not isinstance(raw, bytes):
                    raise ValueError('A retained binary dependency must be bytes.')
                expected = dependency.get('expected_sha256')
                if expected and sha256(raw).hexdigest() != expected:
                    raise ValueError('Dependency differs from its saved checksum.')
            elif 'data' in dependency:
                raw = encoded(clean(dependency['data']))
            elif 'root' in dependency:
                target = safe_path(dependency['root'], dependency['relative'])
                with target.open('rb') as handle:
                    raw = handle.read(FILE_LIMIT + 1)
                if len(raw) > FILE_LIMIT:
                    raise ValueError('Dependency exceeds the per-file limit.')
                expected = dependency.get('expected_sha256')
                if expected and sha256(raw).hexdigest() != expected:
                    raise ValueError('Dependency differs from its saved checksum.')
                if entry['media_type'] == 'application/json':
                    raw = encoded(clean(json.loads(raw)))
            else:
                raise FileNotFoundError()
            if len(raw) > FILE_LIMIT:
                raise ValueError('Dependency exceeds the per-file limit.')
            files[name] = raw
            entry.update(availability='available', bytes=len(raw), sha256=sha256(raw).hexdigest())
        except FileNotFoundError:
            entry['problem'] = dependency.get('problem', 'This dependency was not retained or is no longer present.')
        assets.append(entry)
    if sum(map(len, files.values())) > PACKAGE_LIMIT // 2:
        raise ValueError('Selected dependencies exceed the bounded case limit.')
    manifest = dict(schema=SCHEMA, application=application, capture_id=capture, family=item['family'],
                    capture_type='saved research record', title=item['title'], stored_at_utc=item.get('stored_at_utc'),
                    runtime=record.get('runtime') or item.get('runtime') or {'mode': 'not recorded'},
                    record=record, record_sha256=sha256(record_bytes).hexdigest(), assets=assets,
                    scope=item['description'], limitations=item.get('limitations', []) + [
                        'Internal research evidence; saved decisions are not independent validation or a new issued product.',
                        'Structured operator identifiers and credentials are omitted; scientific values and free text are preserved.',
                        'Export checksums describe retained bytes now, not proof of historical ingest integrity. Missing runtime is not inferred from the current clock.',
                    ])
    return manifest, files


def package(manifest, files):
    members = dict(files, **{'manifest.json': encoded(manifest)})
    data = json.dumps(manifest, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    members['viewer.html'] = Path(__file__).with_name('research_record_viewer.html').read_bytes().replace(b'__CAPTURE_JSON__', data.encode())
    members['verify.py'] = Path(__file__).with_name('research_record_verify.py').read_bytes()
    members['SHA256SUMS'] = ''.join(f'{sha256(raw).hexdigest()}  {name}\n' for name, raw in members.items()).encode('ascii')
    if sum(map(len, members.values())) > PACKAGE_LIMIT:
        raise ValueError('Case exceeds the portable export limit.')
    result = BytesIO()
    with ZipFile(result, 'w') as archive:
        for name, raw in members.items():
            archive.writestr(ZipInfo(name, (1980, 1, 1, 0, 0, 0)), raw, compress_type=ZIP_DEFLATED)
    return result.getvalue()


def collection(application, records, family, offset=0, limit=25):
    rows = []
    for index, item in enumerate(records(family)):
        if index >= offset + limit + 1:
            break
        if index < offset:
            continue
        rows.append(dict(id=identity(application, family, item['record']), instrument=item['title'],
                         action=item.get('action', ''), runtime=(item.get('runtime') or item['record'].get('runtime') or {}).get('mode', 'not recorded'),
                         saved_at_utc=item.get('stored_at_utc')))
    return dict(items=rows[:limit], offset=offset, limit=limit, has_more=len(rows)>limit)


def retrieve(application, records, family, capture_id, format_='json', role=None):
    if not re.fullmatch('[a-f0-9]{64}', capture_id):
        raise falcon.HTTPBadRequest(title='A saved research content identifier is required')
    if format_ not in ('json', 'zip', 'asset'):
        raise falcon.HTTPBadRequest(title='Supported formats are json, zip and asset')
    item = next((item for item in records(family) if identity(application, family, item['record']) == capture_id), None)
    if item is None:
        raise falcon.HTTPNotFound(title='Saved research record not found; refresh if the source changed')
    if format_ == 'asset':
        selected = [] if role == 'record' else [entry for entry in dependencies(item) if sha256(entry['path'].encode()).hexdigest() == role]
        if role != 'record' and not selected:
            raise falcon.HTTPNotFound(title='This dependency is not declared by the saved record')
        item = dict(item, dependencies=selected)
    manifest, files = build(application, item)
    if format_ == 'json':
        return encoded(manifest), 'application/json', None
    if format_ == 'zip':
        return package(manifest, files), 'application/zip', f'{family}-{capture_id}.zip'
    entry = next((entry for entry in manifest['assets'] if entry['role'] == role), None)
    if not entry or entry['availability'] != 'available':
        raise falcon.HTTPNotFound(title='This saved dependency is unavailable')
    return files[entry['path']], entry['media_type'], entry['path'].rsplit('/', 1)[-1]


class CollectionResource:
    def __init__(self, application, families, records):
        self.application, self.families, self.records = application, families, records

    def family(self, req):
        family = req.get_param('family')
        if family not in self.families:
            raise falcon.HTTPBadRequest(title='Choose a supported saved evidence family')
        return family

    def on_get(self, req, resp):
        family = self.family(req)
        offset = req.get_param_as_int('offset', min_value=0, max_value=100000) or 0
        limit = req.get_param_as_int('limit', min_value=1, max_value=50) or 25
        try:
            resp.media = collection(self.application, self.records, family, offset, limit)
            resp.set_header('Cache-Control', 'private, no-store')
        except (OSError, RuntimeError) as exc:
            raise falcon.HTTPServiceUnavailable(title='Saved research storage is unavailable') from exc
        except (ValueError, KeyError, TypeError) as exc:
            raise falcon.HTTPConflict(title='Saved evidence could not be read safely') from exc


class ExportResource(CollectionResource):
    def on_get(self, req, resp, capture_id):
        family = self.family(req)
        format_ = req.get_param('format') or 'json'
        try:
            resp.data, resp.content_type, filename = retrieve(self.application, self.records, family, capture_id, format_, req.get_param('role'))
            resp.set_header('Cache-Control', 'private, no-store')
            resp.set_header('X-Content-Type-Options', 'nosniff')
            if filename:
                resp.set_header('Content-Disposition', 'attachment; filename="' + filename + '"')
            if resp.data:
                resp.set_header('ETag', '"' + sha256(resp.data).hexdigest() + '"')
        except (OSError, RuntimeError) as exc:
            raise falcon.HTTPServiceUnavailable(title='Saved research storage is unavailable') from exc
        except (ValueError, KeyError, TypeError) as exc:
            raise falcon.HTTPConflict(title='Saved dependencies are invalid, changed, or exceed the selected-case limit') from exc
