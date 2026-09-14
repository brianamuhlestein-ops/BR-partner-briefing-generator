import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from falcon import testing
from api.run_api import create_app


class SynopsisIntegrationTests(unittest.TestCase):
    def test_workspace_survives_app_recreation_and_rejects_stale_saves(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {
                'DATABASE_PATH': str(Path(directory) / 'briefing.db'),
                'GENERATED_DIR': str(Path(directory) / 'generated'),
                'SUMMARY_BUILDER_DATA_ROOT': str(Path(directory) / 'synopsis'),
            }):
                client = testing.TestClient(create_app())
                root = '/api/v1/space-weather-summary'
                self.assertEqual(client.simulate_get(root + '/health').status_code, 200)
                self.assertEqual(client.simulate_get('/api/v1/partner-briefing/now').status_code, 200)
                self.assertEqual(client.simulate_get(root + '/source-bundles').status_code, 200)
                self.assertEqual(client.simulate_get(root + '/workspace').json['version'], 0)
                self.assertEqual(client.simulate_put(root + '/workspace', json={'text': 'Review'}).status_code, 428)
                saved = client.simulate_put(root + '/workspace', headers={'If-Match': '0'}, json={'text': 'Reviewed synopsis'})
                self.assertEqual(saved.status_code, 200)
                client = testing.TestClient(create_app())
                self.assertEqual(client.simulate_get(root + '/workspace').json['item']['text'], 'Reviewed synopsis')
                stale = client.simulate_put(root + '/workspace', headers={'If-Match': '0'}, json={'text': 'Stale text'})
                self.assertEqual(stale.status_code, 409)
                self.assertEqual(client.simulate_get(root + '/workspace').json['item']['text'], 'Reviewed synopsis')


if __name__ == '__main__':
    unittest.main()
