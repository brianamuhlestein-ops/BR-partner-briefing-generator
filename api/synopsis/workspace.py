"""Reviewed synopsis workspace. Saving is not product issuance."""
import json
from datetime import datetime, timezone

import falcon

from api.config import open_database


class WorkspaceResource:
    def __init__(self):
        with open_database() as db:
            db.execute('CREATE TABLE IF NOT EXISTS synopsis_workspace (id INTEGER PRIMARY KEY, version INTEGER NOT NULL, payload TEXT NOT NULL)')
            db.commit()

    def on_get(self, req, resp):
        with open_database() as db:
            row = db.execute('SELECT version, payload FROM synopsis_workspace WHERE id=1').fetchone()
        resp.media = {'version': row['version'] if row else 0, 'item': json.loads(row['payload']) if row else None}
        resp.set_header('ETag', str(resp.media['version']))

    def on_put(self, req, resp):
        try:
            expected = int((req.get_header('If-Match') or '').strip('"'))
        except ValueError:
            raise falcon.HTTPPreconditionRequired(description='Supply the workspace version in If-Match.')
        data = req.media
        if not isinstance(data, dict) or not isinstance(data.get('text'), str) or len(data['text']) > 100000:
            raise falcon.HTTPBadRequest(description='A synopsis text of at most 100,000 characters is required.')
        payload = {key: data.get(key) for key in ('text', 'source_draft_id', 'source_bundle_id')}
        payload['saved_at_utc'] = datetime.now(timezone.utc).isoformat()
        with open_database() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT version FROM synopsis_workspace WHERE id=1').fetchone()
            version = row['version'] if row else 0
            if version != expected:
                raise falcon.HTTPConflict(description='Another forecaster saved this workspace. Reload before saving.')
            db.execute('INSERT INTO synopsis_workspace (id, version, payload) VALUES (1, ?, ?) ON CONFLICT(id) DO UPDATE SET version=excluded.version, payload=excluded.payload', (version + 1, json.dumps(payload)))
            db.commit()
        resp.media = {'version': version + 1, 'item': payload}
        resp.set_header('ETag', str(version + 1))
