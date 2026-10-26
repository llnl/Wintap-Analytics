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

    def test_older_or_partial_tcp_receipt_cannot_claim_new_tuple_contract(self):
        run = dict(runId='fixture', host=dict(hostname='fixture'), selectors=[])
        sensor = dict(enabled=True, tier='core', objectSha256='a' * 64)
        receipt = dict(captureRunId='startup', sensors=dict(Network=sensor, FileOps=sensor))
        for version, attached, passed in ((None, True, False), (0, True, False), (1, False, False), (1, True, True)):
            context = dict(status='temporal', capture_run_id='startup', sensors=dict(Network=dict(features=dict(
                tcpTupleContractVersion=version, tcpTupleLifecycleHooksAttached=attached))))
            report = dict(results=[dict(test='canary-cross-domain', run_id='fixture', runtime=context)])
            checks = module.qualification(None, [run], report, [('fixture', receipt)], dict(Network='a' * 64, FileOps='a' * 64))
            check = next(c for c in checks if c['check'].endswith('TCP tuple lifecycle contract'))
            self.assertEqual(check['passed'], passed)
