import io
import json
import os
import unittest
from unittest.mock import patch

import falcon
from api.runtime import runtime_status
from api.synopsis.exercise import exercise_seed, exercise_sources


class ExerciseImportTests(unittest.TestCase):
    def test_source_readouts_preserve_quantities_and_isolate_missing_records(self):
        observations = [{'id':key,'label':key,'value':value,'unit':unit,'observed_at_utc':'2024-05-11T03:00:00Z'}
                        for key,value,unit in [('xray','X2.1','GOES class'),('f107',228,'sfu'),('proton',35,'pfu'),('fluence',1200000,'cm^-2 sr^-1'),('electron',85000000,'cm^-2 sr^-1'),('radio245',420,'sfu')]]
        with patch('api.synopsis.exercise.exercise_record',side_effect=[{'item':{'observations':observations}},falcon.HTTPServiceUnavailable()]):
            sources={s['slug']:s for s in exercise_sources()}
        self.assertEqual(len(sources['solar']['readouts']),2)
        self.assertEqual([r['unit'] for r in sources['particles']['readouts']],['pfu','cm^-2 sr^-1','cm^-2 sr^-1'])
        self.assertEqual(sources['radio']['readouts'][0]['value'],420)
        self.assertEqual(sources['events']['readouts'],[])
        self.assertIn('unavailable',sources['events']['status'])

    def test_operational_mode_cannot_load_exercise_seed(self):
        with patch.dict(os.environ, {'SWIFT_EXERCISE_CATALOGUE_URL':'http://catalogue.test'}), patch('api.synopsis.exercise.runtime_status', return_value={'status':'ok','data_source':'operational'}), patch('api.synopsis.exercise.urlopen') as fetch:
            with self.assertRaises(falcon.HTTPConflict):
                exercise_seed()
            fetch.assert_not_called()

    def test_seed_requires_matching_scenario_clock_and_provenance(self):
        runtime = {'status':'ok','data_source':'replay','scenario':'synthetic-storm-v1','now_utc':'2024-05-11T03:00:00Z'}
        payload = {'scenario':{'id':runtime['scenario'],'now_utc':runtime['now_utc'],'data_kind':'synthetic'},
                   'item':{'runtime':{'mode':'replay','scenario':runtime['scenario']},'data_kind':'synthetic','text':'Test'},
                   'record':{'id':'synopsis-seed','sha256':'fixture-digest','data_kind':'synthetic'}}
        with patch.dict(os.environ, {'SWIFT_EXERCISE_CATALOGUE_URL':'http://catalogue.test'}), patch('api.synopsis.exercise.runtime_status',return_value=runtime):
            with patch('api.synopsis.exercise.urlopen',return_value=io.BytesIO(json.dumps(payload).encode())):
                self.assertEqual(exercise_seed()['item']['text'],'Test')
            payload['scenario']['now_utc']='2024-05-12T03:00:00Z'
            with patch('api.synopsis.exercise.urlopen',return_value=io.BytesIO(json.dumps(payload).encode())):
                with self.assertRaises(falcon.HTTPServiceUnavailable):
                    exercise_seed()

    def test_misconfigured_operational_exercise_clock_fails_closed(self):
        with patch.dict(os.environ, {'SWIFT_EXERCISE_CATALOGUE_URL':'http://catalogue.test', 'PARTNER_BRIEFING_API_DATA_SOURCE':'operational'}):
            status=runtime_status()
            self.assertEqual(status['status'],'configuration_error')
            self.assertEqual(status['data_kind'],'synthetic')


if __name__ == '__main__':
    unittest.main()
