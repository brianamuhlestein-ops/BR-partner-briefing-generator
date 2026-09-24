"""Explicit, replay-only import from the shared read-only exercise catalogue."""
import json
import os
from datetime import datetime, timezone
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

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


def _native_json(environment, route):
    base = os.getenv(environment, '').strip().rstrip('/')
    if not base:
        raise ValueError(environment + ' is not configured')
    with urlopen(base + route, timeout=5) as response:
        return json.load(response)


def _validate_native_clock(clock):
    current = runtime_status()
    def instant(value):
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            raise ValueError('UTC offset required')
        return parsed.astimezone(timezone.utc)
    if (not isinstance(clock, dict)
            or clock.get('scenario') != current.get('scenario')
            or clock.get('mode', clock.get('source', clock.get('data_source'))) != 'replay'
            or instant(clock.get('now_utc', clock.get('nowUtc'))) != instant(current.get('now_utc'))):
        raise ValueError('Native exercise source clock or scenario mismatch')


def _solar_source():
    payload = _native_json('SYNOPSIS_EXERCISE_SOLAR_URL', '/api/v1/solar-forecast/forecast-review')['result']
    _validate_native_clock(payload.get('runtime'))
    review = payload.get('review') or {}
    if not review.get('ready') or payload.get('sourceChanged'):
        raise ValueError('Reviewed Solar exercise decision is unavailable or stale')
    candidate = review.get('candidate') or {}
    if candidate.get('quality', {}).get('synthetic') is not True:
        raise ValueError('Solar decision is not marked synthetic')
    product = candidate.get('content', {}).get('product_object', {})
    effective_at = payload['runtime'].get('now_utc', payload['runtime'].get('nowUtc'))
    flare, f107 = product.get('flare_guidance', {}), product.get('f107_forecast', {})
    rows = flare.get('wholeDisk', {}).get('forecast', [])
    readouts = []
    for row in rows:
        if row.get('day1') is not None:
            readouts.append({'label':'Reviewed '+str(row.get('label') or 'flare')+' D1 probability',
                             'value':row['day1'], 'unit':'%', 'at_utc':effective_at,
                             'decision_at_utc':review.get('savedAt')})
    if f107.get('valuesSfu'):
        readouts.append({'label':'Reviewed F10.7 D1 forecast','value':f107['valuesSfu'][0],
                         'unit':'sfu','at_utc':effective_at,'decision_at_utc':review.get('savedAt')})
    return {'slug':'solar','status':'Native reviewed Solar exercise decision','readouts':readouts,
            'record_id':candidate.get('source_record_id'),'revision':candidate.get('source_revision')}


def _particle_source():
    payload = _native_json('SYNOPSIS_EXERCISE_PARTICLE_URL', '/api/v1/particle/forecast-products')['result']
    if not payload:
        raise ValueError('Saved Particle exercise decision is unavailable')
    _validate_native_clock(payload.get('runtime'))
    effective_at = payload['runtime'].get('now_utc', payload['runtime'].get('nowUtc'))
    readouts = []
    for row in payload.get('proton', {}).get('days', [])[:1]:
        for key, label in (('greaterThan10MevPercent','Reviewed proton >10 MeV D1 probability'),
                           ('greaterThan100MevPercent','Reviewed proton >100 MeV D1 probability')):
            if row.get(key) is not None:
                readouts.append({'label':label,'value':row[key],'unit':'%','at_utc':effective_at,
                                 'decision_at_utc':payload.get('issuedAt')})
    electron = (payload.get('electron', {}).get('days') or [{}])[0]
    if electron.get('greaterThan2MevLevel'):
        readouts.append({'label':'Reviewed >2 MeV electron D1 category',
                         'value':electron['greaterThan2MevLevel'],'unit':'category','at_utc':effective_at,
                         'decision_at_utc':payload.get('issuedAt')})
    return {'slug':'particles','status':'Native saved Particle exercise decision','readouts':readouts,
            'record_id':payload.get('forecastId'),'revision':payload.get('issuedAt')}


def _unavailable_native(slug, label, environment, route):
    try:
        _native_json(environment, route)
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError) as exc:
        return {'slug':slug,'status':label+' unavailable: '+str(getattr(exc, 'reason', exc)),
                'readouts':[],'native_route':route}
    return {'slug':slug,'status':label+' endpoint returned no supported exercise summary',
            'readouts':[],'native_route':route}


def exercise_sources():
    """Read real exercise workspaces; missing native inputs remain unavailable."""
    sources = []
    for slug, loader in (('solar', _solar_source), ('particles', _particle_source)):
        try:
            sources.append(loader())
        except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError) as exc:
            sources.append({'slug':slug,'status':'Native exercise decision unavailable: '+str(getattr(exc, 'reason', exc)),
                            'readouts':[]})
    sources.append(_unavailable_native('radio','Daily 245 MHz summary','SYNOPSIS_EXERCISE_SOLAR_URL',
                                       '/api/v1/solar-forecast/solar-radio-flux'))
    sources.append(_unavailable_native('events','Edited Events','SYNOPSIS_EXERCISE_SOLAR_URL',
                                       '/api/v1/solar-forecast/replay/events'))
    return sources


class ExerciseResource:
    def on_get(self, req, resp):
        if not os.getenv('SWIFT_EXERCISE_CATALOGUE_URL', '').strip():
            resp.media = {'enabled':False}
        else:
            resp.media = {**exercise_seed(), 'sources':exercise_sources()}
        resp.set_header('Cache-Control', 'no-store')
