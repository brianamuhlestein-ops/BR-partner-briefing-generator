import io
import json
import os
import unittest
from unittest.mock import patch

import falcon
from api.runtime import runtime_status
from api.synopsis.exercise import exercise_seed, exercise_sources


class ExerciseImportTests(unittest.TestCase):
    def test_source_readouts_use_native_reviewed_decisions(self):
        runtime={'status':'ok','data_source':'replay','scenario':'synthetic-storm-v1','now_utc':'2024-05-11T03:00:00Z'}
        solar={'result':{'runtime':{'mode':'replay','scenario':runtime['scenario'],'nowUtc':runtime['now_utc']},
            'sourceChanged':False,'review':{'ready':True,'savedAt':runtime['now_utc'],'candidate':{
                'source_record_id':'solar-review:1','source_revision':'1','quality':{'synthetic':True},
                'content':{'product_object':{'flare_guidance':{'wholeDisk':{'forecast':[
                    {'label':'M Class','day1':70}]}},'f107_forecast':{'valuesSfu':[228]}}}}}}}
        particle={'result':{'forecastId':'particle-1','issuedAt':runtime['now_utc'],
            'runtime':{'mode':'replay','scenario':runtime['scenario'],'now_utc':runtime['now_utc']},
            'proton':{'days':[{'greaterThan10MevPercent':45,'greaterThan100MevPercent':10}]},
            'electron':{'days':[{'greaterThan2MevLevel':'moderate'}]}}}
        radio={'result':{'runtime':{'mode':'replay','scenario':runtime['scenario'],'now_utc':runtime['now_utc']},
            'exerciseSource':{'record_id':'science-observations','sha256':'radio-hash'},
            'observations':[{'time_tag':'2024-05-10T16:02:00Z','details':[{'canonicalFrequency':245}]}],
            'summaries':[{'frequency':245,'maxFlux':420}]}}
        events={'result':{'runtime':{'mode':'replay','scenario':runtime['scenario'],'now_utc':runtime['now_utc']},
            'exerciseSource':{'record_id':'linked-events','sha256':'event-hash'},'bins':[{'id':'flare-1'}]}}
        cme={'status':'ok','item':{'context_id':'exercise-cme-sa-display-r1','generated_at_utc':runtime['now_utc'],
            'runtime':{'mode':'replay','scenario':runtime['scenario'],'effective_at_utc':runtime['now_utc']},
            'lifecycle':{'state':'reviewed','revision':1},
            'cme_analysis':{'assessment':{'nominal_arrival_utc':'2024-05-12T08:59:23Z'}}}}
        with patch('api.synopsis.exercise.runtime_status',return_value=runtime), patch(
                'api.synopsis.exercise._native_json',side_effect=[solar,particle,radio,events,cme]):
            sources={s['slug']:s for s in exercise_sources()}
        self.assertEqual(len(sources['solar']['readouts']),2)
        self.assertEqual([r['unit'] for r in sources['particles']['readouts']],['%','%','category'])
        self.assertEqual(sources['solar']['record_id'],'solar-review:1')
        self.assertEqual(sources['particles']['record_id'],'particle-1')
        self.assertEqual(sources['radio']['readouts'][0]['value'],420)
        self.assertEqual(sources['events']['readouts'][0]['value'],1)
        self.assertEqual(sources['radio']['record_id'],'science-observations')
        self.assertEqual(sources['events']['record_id'],'linked-events')
        self.assertEqual(sources['cme']['record_id'],'exercise-cme-sa-display-r1')

    def test_native_clock_mismatch_does_not_fall_back_to_catalogue_values(self):
        runtime={'status':'ok','data_source':'replay','scenario':'synthetic-storm-v1','now_utc':'2024-05-11T03:00:00Z'}
        wrong={'result':{'runtime':{'mode':'replay','scenario':'other','nowUtc':runtime['now_utc']}}}
        with patch('api.synopsis.exercise.runtime_status',return_value=runtime), patch(
                'api.synopsis.exercise._native_json',side_effect=[wrong,wrong,wrong,wrong,wrong]):
            sources={s['slug']:s for s in exercise_sources()}
        self.assertEqual(sources['solar']['readouts'],[])
        self.assertEqual(sources['particles']['readouts'],[])
        self.assertIn('mismatch',sources['solar']['status'])

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
