"""Explicit, replay-only import from the shared read-only exercise catalogue."""
import json
import os
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import URLError

import falcon
from api.runtime import runtime_status


def exercise_record(record_id):
    runtime = runtime_status()
    base = os.getenv('SWIFT_EXERCISE_CATALOGUE_URL', '').strip().rstrip('/')
    if not base or runtime.get('data_source') != 'replay' or runtime.get('status') != 'ok':
        raise falcon.HTTPConflict(description='Catalogue examples are available only in the configured exercise instance.')
    scenario = runtime.get('scenario')
    try:
        with urlopen(base + '/api/v1/exercises/' + quote(scenario or '', safe='') + '/records/' + quote(record_id, safe=''), timeout=5) as response:
            payload = json.load(response)
        item, metadata = payload['item'], payload['scenario']
        if (metadata['data_kind'] != 'synthetic' or metadata['id'] != scenario
                or metadata['now_utc'] != runtime['now_utc'] or item['runtime']['scenario'] != scenario
                or item['runtime']['mode'] != 'replay' or payload['record']['data_kind'] != 'synthetic'):
            raise ValueError('Exercise clock or identity mismatch')
        return {'enabled':True, 'item':item, 'record':payload['record'], 'scenario':metadata}
    except (URLError, TimeoutError, ValueError, KeyError, TypeError) as exc:
        raise falcon.HTTPServiceUnavailable(description='The exercise catalogue is unavailable or does not match this replay clock.') from exc


def exercise_seed():
    return exercise_record('synopsis-seed')


def exercise_sources():
    """Display catalogue observations without claiming native producer adapters exist."""
    sources = []
    try:
        observations = exercise_record('science-observations')['item']['observations']
        for slug, ids in [('solar', ('xray', 'f107')), ('particles', ('proton', 'fluence', 'electron')), ('radio', ('radio245',))]:
            sources.append({'slug':slug, 'status':'Synthetic catalogue example',
                'readouts':[{'label':o['label'], 'value':o['value'], 'unit':o['unit'], 'at_utc':o['observed_at_utc']}
                            for o in observations if o['id'] in ids]})
    except falcon.HTTPError:
        sources.extend({'slug':slug, 'status':'Catalogue observations unavailable', 'readouts':[]} for slug in ('solar','particles','radio'))
    try:
        events = exercise_record('linked-events')['item']['records']
        sources.append({'slug':'events', 'status':'Synthetic event example · native exchange pending',
            'readouts':[{'label':f"Region {e['region']}", 'value':e['flare_class'], 'unit':'flare', 'at_utc':e['peak_utc']}
                        for e in events if e.get('flare_class')]})
    except falcon.HTTPError:
        sources.append({'slug':'events', 'status':'Catalogue events unavailable', 'readouts':[]})
    return sources


class ExerciseResource:
    def on_get(self, req, resp):
        if not os.getenv('SWIFT_EXERCISE_CATALOGUE_URL', '').strip():
            resp.media = {'enabled':False}
        else:
            resp.media = {**exercise_seed(), 'sources':exercise_sources()}
        resp.set_header('Cache-Control', 'no-store')
