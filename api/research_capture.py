"""Retained briefing/Synopsis decisions and their explicitly linked evidence."""
from hashlib import sha256
import json
import os
from pathlib import Path

from api import research_records as exports

APPLICATION = 'briefing-synopsis'
FAMILIES = ('email-documents', 'bundles', 'drafts', 'workspaces', 'reviews', 'receipts')
ROOT = Path(__file__).resolve().parents[1]


def database():
    return Path(os.getenv('DATABASE_PATH', ROOT/'email_briefing.db'))


def data_root():
    path = Path(os.getenv('SUMMARY_BUILDER_DATA_ROOT', ROOT/'runtime-data/synopsis'))
    return path if path.is_absolute() else ROOT/path


def validate_bundle(bundle):
    import rfc8785
    original = sha256(rfc8785.dumps({key: bundle[key] for key in ('fact_ledger', 'sources')})).hexdigest()
    if original != bundle['integrity']['sha256']:
        raise ValueError('Saved Synopsis bundle differs from its original source/fact checksum.')


def bundle_dependencies(bundle):
    # The retained bundle stores selected source identifiers, not full contexts.
    return [dict(path=f'files/source-context-{index+1:04d}.json',
                 description='Original '+source.get('application_slug', 'producer')+' context '+str(source.get('context_id'))+'.',
                 problem='Only the source identifier, canonical digest and extracted facts were saved in this bundle. The original full context was not frozen here; no current producer context is substituted.')
            for index, source in enumerate(bundle.get('sources', [])) if source.get('context_id')]


def linked_dependencies(record):
    result = []
    bundle_ref = record.get('source_bundle') or {}
    bundle_id = record.get('source_bundle_id') or bundle_ref.get('bundle_id')
    draft_id = record.get('source_draft_id')
    if draft_id:
        path = exports.safe_path(data_root()/'drafts', draft_id+'.json')
        if path.is_file():
            draft = exports.read_json(path)
            if (draft.get('source_bundle') or {}).get('bundle_id') != bundle_id:
                raise ValueError('Saved draft and Synopsis bundle references differ.')
            result.append(dict(path='files/source-draft.json', data=draft, description='Exact saved deterministic draft named by this Synopsis.'))
        else:
            result.append(dict(path='files/source-draft.json', description='Named original Synopsis draft.'))
    if bundle_id:
        path = exports.safe_path(data_root()/'source-bundles', bundle_id+'.json')
        if path.is_file():
            bundle = exports.read_json(path)
            validate_bundle(bundle)
            refs = [ref.get('sha256') for ref in record.get('evidence_refs', []) if ref.get('kind')=='synopsis_source_bundle' and ref.get('record_id')==bundle_id]
            if bundle_ref.get('integrity_sha256'):
                refs.append(bundle_ref['integrity_sha256'])
            if any(ref != bundle['integrity']['sha256'] for ref in refs):
                raise ValueError('Saved Synopsis references a different source bundle revision.')
            result.append(dict(path='files/source-bundle.json', data=bundle, description='Exact referenced source bundle: selected source metadata, extracted facts, consistency checks and original digest.'))
            result.extend(bundle_dependencies(bundle))
        else:
            result.append(dict(path='files/source-bundle.json', description='Original named source bundle; no current evidence recollection.'))
    if record.get('product_text'):
        raw = record['product_text'].encode('utf-8')
        result.append(dict(path='files/synopsis.txt', raw=raw, media_type='text/plain', expected_sha256=record.get('sha256'),
                           description='Exact saved reviewed Synopsis text; not a new product rendering or transmission.'))
    return result


def descriptor(family, record, title, description, stamp=None, dependencies=None):
    return dict(family=family, record=record, title=title, description=description,
                stored_at_utc=stamp, runtime=record.get('runtime') or (record.get('payload') or {}).get('runtime'), dependencies=dependencies or [], limitations=[
                    'Current email/workspace version counters do not establish an intermediate edit history. Immutable bundles, deterministic drafts, reviewed Synopsis and delivery receipts remain separate.',
                    'Client-rendered briefing PDF/PNG and arbitrary linked images were not automatically archived. Selected source references and extracted facts do not establish complete upstream contexts or imagery.',
                    'No source collection, current replay clock, draft generation, review, product delivery or recipient notification runs during research retrieval.',
                ])


def records(family):
    if family in ('bundles', 'drafts'):
        folder, pattern = ('source-bundles', 'ssb-*.json') if family=='bundles' else ('drafts', 'swd-*.json')
        for path in sorted((data_root()/folder).glob(pattern), reverse=True):
            record = exports.read_json(exports.safe_path(data_root()/folder, path.name))
            if family=='bundles':
                validate_bundle(record)
            yield descriptor(family, record, ('Source bundle - ' if family=='bundles' else 'Deterministic draft - ')+path.stem,
                             'Retained Synopsis '+family+': original facts/source selection, generation/validation state and runtime where saved.',
                             record.get('created_at_utc'), lambda record=record: bundle_dependencies(record) if family=='bundles' else linked_dependencies(record))
        return
    table, order = {
        'email-documents': ('email_briefing_documents', 'updated_at DESC, briefing_kind'),
        'workspaces': ('synopsis_workspaces_v2', 'scope'),
        'reviews': ('synopsis_reviews', 'version DESC, id'),
        'receipts': ('synopsis_receipts', 'review_id'),
    }[family]
    for row in exports.sqlite_rows(database(), table, f'SELECT * FROM {table} ORDER BY {order}'):
        if family=='email-documents':
            record = {**row, 'document': json.loads(row['document_json'])}
            del record['document_json']
        else:
            record = {**row, 'payload': json.loads(row['payload'])}
        payload = record.get('payload') or record
        dependencies = lambda payload=payload: linked_dependencies(payload)
        if family=='receipts':
            def dependencies(row=row):
                matches = list(exports.sqlite_rows(database(), 'synopsis_reviews', 'SELECT payload FROM synopsis_reviews WHERE id=?', (row['review_id'],)))
                if not matches:
                    return [dict(path='files/review.json', description='Original reviewed Synopsis named by this receipt.')]
                review = json.loads(matches[0]['payload'])
                return [dict(path='files/review.json', data=review, description='Exact saved reviewed Synopsis named by this delivery receipt.')]+linked_dependencies(review)
        yield descriptor(family, record, family.replace('-', ' ').title()+' - '+str(row.get('briefing_kind') or row.get('id') or row.get('review_id') or row.get('scope')),
                         'Retained '+family+' with its original version, text, review/delivery state and explicitly named dependencies.',
                         row.get('updated_at') or payload.get('reviewed_at_utc') or payload.get('saved_at_utc'), dependencies)
