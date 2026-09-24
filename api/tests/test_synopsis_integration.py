import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from falcon import testing
from api.run_api import create_app

ROOT = '/api/v1/space-weather-summary'
CLOCK = {'status':'ok', 'data_source':'operational', 'scenario':None, 'now_utc':'2026-09-23T12:00:00Z'}

class SynopsisIntegrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        folder = Path(temporary.name)
        environment = patch.dict(os.environ, {
            'DATABASE_PATH':str(folder/'briefing.db'),
            'GENERATED_DIR':str(folder/'generated'),
            'SUMMARY_BUILDER_DATA_ROOT':str(folder/'synopsis'),
            'SYNOPSIS_PRODUCT_LAUNCHER_URL':'http://launcher.test',
            'SYNOPSIS_EXERCISE_LAUNCHER_URL':'',
            'SWIFT_EXERCISE_CATALOGUE_URL':'',
        })
        environment.start(); self.addCleanup(environment.stop)
        clock = patch('api.synopsis.workspace.runtime_status', return_value=dict(CLOCK))
        self.clock = clock.start(); self.addCleanup(clock.stop)
        self.client = testing.TestClient(create_app())

    def state(self):
        return self.client.simulate_get(ROOT+'/workspace').json

    def save(self, text='Reviewed assessment', **changes):
        state = self.state()
        payload = dict(runtime_key=state['runtime_key'], text=text, reporting_start_utc='2026-09-22T12:00:00Z', reporting_end_utc='2026-09-23T12:00:00Z')
        payload.update(changes)
        return self.client.simulate_put(ROOT+'/workspace', headers={'If-Match':str(state['version'])}, json=payload)

    def post(self, path, version=None):
        state=self.state()
        return self.client.simulate_post(ROOT+'/'+path, headers={'If-Match':str(state['version'] if version is None else version)}, json={'runtime_key':state['runtime_key']})

    def test_persistence_concurrency_and_immutable_review(self):
        self.assertEqual(self.save().status_code,200)
        first=self.post('reviewed').json['item']
        self.assertEqual(self.post('reviewed').json['item'],first)
        self.client=testing.TestClient(create_app())
        self.assertEqual(self.state()['item']['text'],'Reviewed assessment')
        self.assertEqual(self.save('New draft').status_code,200)
        self.assertEqual(self.state()['reviewed'],first)
        self.assertEqual(self.post('reviewed',1).status_code,409)
        self.assertEqual(self.post('deliver').status_code,409)

    def test_reporting_window_and_mode_conflicts(self):
        self.assertEqual(self.save(reporting_end_utc='2026-09-24T00:00:00Z').status_code,400)
        self.assertEqual(self.save(reporting_start_utc='2026-09-24T00:00:00Z').status_code,400)
        self.assertEqual(self.save(runtime_key='wrong-mode').status_code,409)
        result=self.client.simulate_put(ROOT+'/workspace',json={'runtime_key':self.state()['runtime_key']})
        self.assertEqual(result.status_code,428)

    def test_replay_isolation_and_clock_rewind(self):
        self.save(); self.post('reviewed')
        self.clock.return_value={**CLOCK,'data_source':'replay','scenario':'gannon'}
        self.assertIsNone(self.state()['item'])
        self.assertIsNone(self.state()['reviewed'])
        self.save('Replay assessment'); self.post('reviewed')
        self.assertEqual(self.post('deliver').status_code,409)
        self.clock.return_value={**CLOCK,'data_source':'replay','scenario':'another'}
        self.assertIsNone(self.state()['item'])
        self.clock.return_value={**CLOCK,'data_source':'replay','scenario':'gannon','now_utc':'2026-09-22T12:00:00Z'}
        self.assertIsNone(self.state()['item'])
        self.assertIsNone(self.state()['reviewed'])
        self.clock.return_value=dict(CLOCK)
        self.assertEqual(self.state()['item']['text'],'Reviewed assessment')

    def test_candidate_delivery_is_reviewed_and_idempotent(self):
        self.save(); reviewed=self.post('reviewed').json['item']
        with patch('api.synopsis.workspace.urlopen', return_value=io.BytesIO(json.dumps({'candidate':{'candidate_id':'candidate-1','current_revision':1}}).encode())) as send:
            result=self.post('deliver')
            self.assertEqual(result.status_code,200,result.text)
            again=self.post('deliver')
            self.assertEqual(again.json,result.json)
            self.assertEqual(send.call_count,1)
            request=send.call_args.args[0]
            self.assertTrue(request.full_url.endswith('/candidates'))
            candidate=json.loads(request.data)
            self.assertEqual(candidate['content']['official_text'],reviewed['product_text'])
            self.assertNotIn('valid_end_utc',candidate)
        self.clock.return_value={**CLOCK,'now_utc':'2026-09-25T12:00:00Z'}
        self.assertEqual(self.post('deliver').status_code,409)

    def test_unavailable_clock_and_missing_source(self):
        self.assertEqual(self.save(source_bundle_id='missing').status_code,400)
        self.clock.return_value={**CLOCK,'status':'configuration_error'}
        self.assertEqual(self.client.simulate_get(ROOT+'/workspace').status_code,503)

    def test_exercise_delivery_requires_matching_target_and_retains_provenance(self):
        self.clock.return_value={**CLOCK,'data_source':'replay','scenario':'test-storm'}
        self.save('SYNTHETIC exercise assessment'); self.post('reviewed')
        with patch.dict(os.environ, {'SYNOPSIS_EXERCISE_LAUNCHER_URL':'http://exercise.test',
                                    'SWIFT_EXERCISE_CATALOGUE_URL':'http://catalogue.test'}):
            target={'runtime':{'mode':'exercise','scenario':'test-storm','now_utc':CLOCK['now_utc']}}
            result={'candidate':{'candidate_id':'exercise-1','current_revision':1}}
            with patch('api.synopsis.workspace.urlopen',side_effect=[io.BytesIO(json.dumps(target).encode()),io.BytesIO(json.dumps(result).encode())]) as send:
                response=self.post('deliver')
                self.assertEqual(response.status_code,200,response.text)
                candidate=json.loads(send.call_args.args[0].data)
                self.assertTrue(candidate['quality']['synthetic'])
                self.assertEqual(candidate['quality']['runtime_mode'],'replay')
                self.assertEqual(candidate['content']['synopsis']['runtime']['scenario'],'test-storm')
            for field,value in [('mode','operational'),('scenario','other'),('now_utc','2026-09-24T12:00:00Z')]:
                wrong={'runtime':{**target['runtime'],field:value}}
                with patch('api.synopsis.workspace.urlopen',return_value=io.BytesIO(json.dumps(wrong).encode())) as send:
                    self.assertEqual(self.post('deliver').status_code,503)
                    self.assertEqual(send.call_count,1)

    def test_exercise_review_retains_native_decision_provenance(self):
        self.clock.return_value={**CLOCK,'data_source':'replay','scenario':'test-storm'}
        seed={'record':{'id':'synopsis-seed','sha256':'seed-hash'},
              'scenario':{'id':'test-storm'}}
        sources=[
            {'slug':'solar','readouts':[{'value':42}], 'record_id':'solar-review-4','revision':4},
            {'slug':'particles','readouts':[{'value':18}], 'record_id':'particle-forecast-7','revision':'2026-09-23T11:55:00Z'},
            {'slug':'radio','readouts':[]},
        ]
        with patch('api.synopsis.exercise.exercise_seed', return_value=seed), \
             patch('api.synopsis.exercise.exercise_sources', return_value=sources):
            saved=self.save('Exercise assessment', exercise_seed_id='synopsis-seed')
            self.assertEqual(saved.status_code,200,saved.text)
            reviewed=self.post('reviewed').json['item']
        native=[ref for ref in reviewed['evidence_refs'] if ref['kind']=='native_exercise_decision']
        self.assertEqual([(ref['source'],ref['record_id'],ref['revision']) for ref in native],
                         [('solar','solar-review-4','4'),
                          ('particles','particle-forecast-7','2026-09-23T11:55:00Z')])

if __name__=='__main__': unittest.main()
