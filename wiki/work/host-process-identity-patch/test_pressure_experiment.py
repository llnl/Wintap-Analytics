import unittest
from pressure_experiment import failed_gates


class PressureGateTests(unittest.TestCase):
    def result(self):
        return dict(historical_db_size_mtime_unchanged=True,hosts=[dict(host='axon-target',
            installed_controls_unchanged=True,rounds=[dict(name='trace-off',gates={'identity':True}),
                dict(name='trace-on',gates={'identity':True},trace={'gates':{'complete':True}})])])

    def test_complete_controls_pass(self):
        self.assertEqual(failed_gates(self.result()),[])

    def test_missing_observer_or_changed_database_blocks_escalation(self):
        result=self.result()
        del result['hosts'][0]['rounds'][1]['trace']
        self.assertEqual(failed_gates(result)[0]['stage'],'missing-trace')
        result=self.result(); result['historical_db_size_mtime_unchanged']=False
        self.assertEqual(failed_gates(result)[0]['stage'],'historical-database')

    def test_any_failed_raw_or_observer_gate_is_preserved(self):
        for category in ('raw','trace'):
            result=self.result(); row=result['hosts'][0]['rounds'][1]
            gates=row['gates'] if category=='raw' else row['trace']['gates']
            gates['example']=False
            self.assertTrue(any(f.get('stage')==category for f in failed_gates(result)))
