"""Mode-separated Synopsis drafts, immutable reviews, and product candidates."""
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError

import falcon
from api.config import open_database
from api.runtime import runtime_status

ROOT = '/api/v1/space-weather-summary'


def context():
    runtime = runtime_status()
    if runtime['status'] != 'ok':
        raise falcon.HTTPServiceUnavailable(description='A valid application clock is required.')
    mode = runtime['data_source']
    scenario = runtime.get('scenario')
    if mode == 'replay' and not scenario:
        raise falcon.HTTPServiceUnavailable(description='Replay requires a scenario identity.')
    key = json.dumps([mode, scenario if mode == 'replay' else None], separators=(',', ':'))
    return key, runtime


def stamp(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            raise ValueError()
        return parsed.astimezone(timezone.utc)
    except (ValueError, TypeError):
        raise falcon.HTTPBadRequest(description='Reporting times must include a UTC offset.')


def expected(req, body, key):
    if not isinstance(body, dict) or body.get('runtime_key') != key:
        raise falcon.HTTPConflict(description='Application mode changed. Reload the Synopsis workspace.')
    try:
        return int((req.get_header('If-Match') or '').strip('"'))
    except ValueError:
        raise falcon.HTTPPreconditionRequired(description='Supply the workspace version in If-Match.')


def initialize():
    with open_database() as db:
        db.execute('CREATE TABLE IF NOT EXISTS synopsis_workspaces_v2 (scope TEXT PRIMARY KEY, version INTEGER NOT NULL, payload TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS synopsis_reviews (id TEXT PRIMARY KEY, scope TEXT NOT NULL, version INTEGER NOT NULL, payload TEXT NOT NULL, UNIQUE(scope,version))')
        db.execute('CREATE TABLE IF NOT EXISTS synopsis_receipts (review_id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        db.commit()


def source_evidence(payload, runtime):
    from api.synopsis.config import load_settings
    from api.synopsis.persistence import BundleStore, DraftStore
    bundle_id, draft_id = payload.get('source_bundle_id'), payload.get('source_draft_id')
    exercise_refs = []
    if payload.get('exercise_seed_id'):
        from api.synopsis.exercise import exercise_seed
        seed = exercise_seed()
        if payload['exercise_seed_id'] != seed['record']['id']:
            raise falcon.HTTPBadRequest(description='Unknown exercise seed.')
        exercise_refs = [{'kind':'synthetic_exercise_seed','record_id':seed['record']['id'],
                          'scenario':seed['scenario']['id'],'sha256':seed['record']['sha256']}]
    if not bundle_id:
        if draft_id:
            raise falcon.HTTPBadRequest(description='A source draft requires its evidence bundle.')
        return exercise_refs
    settings = load_settings()
    try:
        bundle = BundleStore(settings.bundle_root).read(bundle_id)
        if draft_id:
            draft = DraftStore(settings.draft_root).read(draft_id)
            if draft['source_bundle']['bundle_id'] != bundle_id:
                raise ValueError('Draft and evidence bundle do not match.')
    except (LookupError, ValueError, TypeError) as exc:
        raise falcon.HTTPBadRequest(description='The selected evidence reference is unavailable or mismatched.') from exc
    clock = bundle['runtime']
    if clock['mode'] != runtime['data_source'] or (clock['mode']=='replay' and clock.get('scenario') != runtime.get('scenario')):
        raise falcon.HTTPConflict(description='Evidence belongs to a different runtime or scenario.')
    if stamp(bundle['cutoff_at_utc']) > stamp(payload['reporting_end_utc']):
        raise falcon.HTTPConflict(description='Evidence extends beyond the reporting cutoff. Recollect evidence for this window.')
    return exercise_refs + [{'kind':'synopsis_source_bundle', 'record_id':bundle_id, 'sha256':bundle['integrity']['sha256']}]


def latest_review(db, key, now):
    rows = db.execute('SELECT payload FROM synopsis_reviews WHERE scope=? ORDER BY version DESC', (key,))
    for row in rows:
        item = json.loads(row['payload'])
        if stamp(item['reporting_end_utc']) <= stamp(now):
            return item
    return None


class WorkspaceResource:
    def __init__(self):
        initialize()

    def on_get(self, req, resp):
        key, runtime = context()
        with open_database() as db:
            row = db.execute('SELECT version,payload FROM synopsis_workspaces_v2 WHERE scope=?', (key,)).fetchone()
            reviewed = latest_review(db, key, runtime['now_utc'])
        item = json.loads(row['payload']) if row else None
        if item and stamp(item['reporting_end_utc']) > stamp(runtime['now_utc']):
            item = None
        now = stamp(runtime['now_utc'])
        resp.media = {'version':row['version'] if row else 0, 'item':item, 'reviewed':reviewed, 'runtime_key':key, 'runtime':runtime,
                      'defaults':{'reporting_start_utc':(now-timedelta(hours=24)).isoformat(), 'reporting_end_utc':now.isoformat()}}
        resp.set_header('Cache-Control', 'no-store')

    def on_put(self, req, resp):
        key, runtime = context()
        data = req.media
        version = expected(req, data, key)
        if not isinstance(data.get('text'), str) or not data['text'].strip() or len(data['text']) > 100000:
            raise falcon.HTTPBadRequest(description='A nonempty synopsis of at most 100,000 characters is required.')
        start, end = stamp(data.get('reporting_start_utc')), stamp(data.get('reporting_end_utc'))
        if end <= start or end > stamp(runtime['now_utc']):
            raise falcon.HTTPBadRequest(description='Reporting start must precede the cutoff, which cannot be after the application clock.')
        payload = {k:data.get(k) for k in ('text','source_bundle_id','source_draft_id','exercise_seed_id')}
        payload.update(reporting_start_utc=start.isoformat(), reporting_end_utc=end.isoformat(), runtime=runtime, saved_at_utc=datetime.now(timezone.utc).isoformat())
        payload['evidence_refs'] = source_evidence(payload, runtime)
        with open_database() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT version FROM synopsis_workspaces_v2 WHERE scope=?', (key,)).fetchone()
            current = row['version'] if row else 0
            if current != version:
                raise falcon.HTTPConflict(description='Another forecaster saved this Synopsis. Reload before saving.')
            db.execute('INSERT INTO synopsis_workspaces_v2 VALUES (?,?,?) ON CONFLICT(scope) DO UPDATE SET version=excluded.version,payload=excluded.payload', (key,version+1,json.dumps(payload)))
            db.commit()
        resp.media = {'version':version+1,'item':payload}


class ReviewResource:
    def on_get(self, req, resp):
        key, runtime = context()
        with open_database() as db:
            item = latest_review(db,key,runtime['now_utc'])
        resp.media = {'item':item,'runtime_key':key,'runtime':runtime}
        resp.set_header('Cache-Control','no-store')

    def on_post(self, req, resp):
        key, runtime = context()
        version = expected(req, req.media, key)
        with open_database() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT version,payload FROM synopsis_workspaces_v2 WHERE scope=?',(key,)).fetchone()
            if not row or row['version'] != version:
                raise falcon.HTTPConflict(description='Save and review the current workspace version first.')
            payload = json.loads(row['payload'])
            if stamp(payload['reporting_end_utc']) > stamp(runtime['now_utc']):
                raise falcon.HTTPConflict(description='The saved Synopsis is ahead of the current replay clock.')
            source_evidence(payload,runtime)
            review_id = 'synopsis-' + hashlib.sha256(key.encode()).hexdigest()[:12] + '-' + str(version)
            existing = db.execute('SELECT payload FROM synopsis_reviews WHERE id=?',(review_id,)).fetchone()
            if existing:
                item = json.loads(existing['payload'])
            else:
                product_text = f"SPACE WEATHER SYNOPSIS\nReporting period: {payload['reporting_start_utc']} to {payload['reporting_end_utc']}\n\n{payload['text'].strip()}\n"
                item = {**payload,'review_id':review_id,'version':version,'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),'product_text':product_text,'sha256':hashlib.sha256(product_text.encode()).hexdigest()}
                db.execute('INSERT INTO synopsis_reviews VALUES (?,?,?,?)',(review_id,key,version,json.dumps(item)))
            db.commit()
        resp.media = {'item':item}


class DeliveryResource:
    def on_post(self, req, resp):
        key, runtime = context()
        version = expected(req, req.media, key)
        exercise = runtime['data_source'] == 'replay'
        base = os.getenv('SYNOPSIS_EXERCISE_LAUNCHER_URL' if exercise else 'SYNOPSIS_PRODUCT_LAUNCHER_URL','').rstrip('/')
        if exercise:
            if not base or not os.getenv('SWIFT_EXERCISE_CATALOGUE_URL','').strip():
                raise falcon.HTTPConflict(description='Replay delivery requires a configured isolated exercise queue.')
            try:
                with urlopen(base+'/health', timeout=5) as response:
                    target = json.load(response)['runtime']
                if target['mode'] != 'exercise' or target['scenario'] != runtime['scenario'] or stamp(target['now_utc']) != stamp(runtime['now_utc']):
                    raise ValueError('Exercise target mismatch')
            except (URLError, TimeoutError, ValueError, KeyError, TypeError) as exc:
                raise falcon.HTTPServiceUnavailable(description='Exercise Launcher identity or clock does not match.') from exc
        with open_database() as db:
            item = latest_review(db,key,runtime['now_utc'])
            current = db.execute('SELECT version FROM synopsis_workspaces_v2 WHERE scope=?',(key,)).fetchone()
            if not item or item['version'] != version or not current or current['version'] != version:
                raise falcon.HTTPConflict(description='Review the latest saved Synopsis before sending it.')
            prior = db.execute('SELECT payload FROM synopsis_receipts WHERE review_id=?',(item['review_id'],)).fetchone()
        age = stamp(runtime['now_utc']) - stamp(item['reporting_end_utc'])
        max_age = float(os.getenv('SYNOPSIS_MAX_DELIVERY_AGE_HOURS','24'))
        if age.total_seconds() > max_age*3600:
            raise falcon.HTTPConflict(description='The reporting cutoff is stale for operational delivery. Review a current assessment.')
        if prior:
            resp.media = {'receipt':json.loads(prior['payload'])}
            return
        candidate = {'schema':'swift_product_candidate_v1','idempotency_key':item['review_id'],
                     'source_application':'swift_partner_briefing_generator','source_record_id':item['review_id'],'source_revision':str(version),
                     'product_key':'space_weather_synopsis','product_name':'Space Weather Synopsis','product_type':'Synopsis','domain':'Space Weather',
                     'created_at_utc':item['reviewed_at_utc'],
                     'content':{'official_text':item['product_text'],'synopsis':item,'runtime':runtime},
                     'evidence_refs':item['evidence_refs']+[{'kind':'reviewed_synopsis','record_id':item['review_id'],'sha256':item['sha256']}],
                     'quality':{'status':'source_reviewed','runtime_mode':'replay' if exercise else 'operational','synthetic':exercise,'crosswalk_status':'working_product_definition'}}
        if not base:
            raise falcon.HTTPServiceUnavailable(description='Product Launcher connection is not configured.')
        try:
            request = Request(base+'/api/v1/product-launcher/candidates', data=json.dumps(candidate).encode(),headers={'Content-Type':'application/json'})
            with urlopen(request,timeout=10) as response:
                result = json.load(response)
            record = result['candidate']
            receipt = {'candidate_id':record['candidate_id'],'candidate_revision':record['current_revision'],'review_id':item['review_id'],'status':'ready_for_review'}
        except (URLError, TimeoutError, ValueError, KeyError) as exc:
            raise falcon.HTTPServiceUnavailable(description='Product Launcher did not confirm receipt. The reviewed Synopsis is retained; retry safely.') from exc
        with open_database() as db:
            db.execute('INSERT OR REPLACE INTO synopsis_receipts VALUES (?,?)',(item['review_id'],json.dumps(receipt)))
            db.commit()
        resp.media = {'receipt':receipt}
