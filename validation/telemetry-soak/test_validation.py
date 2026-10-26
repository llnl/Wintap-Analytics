import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('validate_round', Path(__file__).with_name('validate-round.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AcceptanceStatusTests(unittest.TestCase):
    def report(self):
        return dict(errors=[], missing_families=[], qualification=[dict(passed=True)], results=[dict(
            harness='passed', state='yellow', skips=[], cases=[dict(violations=[], missing=[], skips=[], warnings=[], observation='observed')])])

    def test_scoped_observations_do_not_require_green_canary(self):
        self.assertEqual(module.exit_status(self.report()), 0)

    def test_missing_and_skipped_are_incomplete_contradiction_stays_failure(self):
        for field in ('missing', 'skips', 'warnings'):
            report = self.report()
            report['results'][0]['cases'][0][field] = ['unknown']
            self.assertEqual(module.exit_status(report), 2)
            report['results'][0]['cases'][0]['violations'] = ['wrong port']
            self.assertEqual(module.exit_status(report), 1)

    def test_failed_receipt_or_hash_check_is_never_acceptance(self):
        report = self.report()
        report['qualification'][0]['passed'] = False
        self.assertEqual(module.exit_status(report), 2)
        report['qualification'][0]['contradiction'] = True
        self.assertEqual(module.exit_status(report), 1)
