"""Regression tests for truthful integration-gate evidence."""

from __future__ import annotations

import copy
import importlib.util
import math
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / "verify_10_passes.py"
spec = importlib.util.spec_from_file_location("integration_verification", MODULE)
verification = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verification)
HASH = "a" * 64


def audit_fixture():
    return {
        "ok": True,
        "execution": {"source": "local_process", "script_sha256": HASH},
        "audit": {
            "status": "PASS",
            "clean_code_python": {
                "pacioli_balance_exact": True,
                "pacioli_diff_decimal": "0.00",
                "cad_tolerance_compliant": True,
                "cad_delta_mm": "0.142",
            },
            "c_byte_engine": {
                "available": True,
                "record_packed_size_bytes": 32,
                "welford_stream_stats": {
                    "count": 10,
                    "mean": 55.4,
                    "m2": 8244.9,
                    "variance": 824.49,
                    "std_dev": math.sqrt(824.49),
                },
            },
            "haskell_formal_proofs": {
                "all_invariants_verified": True,
                "welford_monoid_associativity": True,
                "welford_monoid_identity": True,
                "cad_physical_tolerance_0_2mm": True,
                "pacioli_rational_balance_exact": True,
                "pacioli_diff_cents": 0,
            },
        },
    }


class VerificationContractTests(unittest.TestCase):
    def test_math_rejects_missing_or_wrong_evidence(self):
        self.assertTrue(verification.math_audit_passed(audit_fixture(), HASH))
        for invalid in ({"ok": True, "audit": {"status": "PASS"}}, None, {}):
            self.assertFalse(verification.math_audit_passed(invalid, HASH))
        for section, field, value in (
            ("clean_code_python", "pacioli_diff_decimal", "0.01"),
            ("clean_code_python", "cad_delta_mm", "0.201"),
            ("c_byte_engine", "available", False),
            ("haskell_formal_proofs", "welford_monoid_identity", False),
        ):
            invalid = copy.deepcopy(audit_fixture())
            invalid["audit"][section][field] = value
            with self.subTest(field=field):
                self.assertFalse(verification.math_audit_passed(invalid, HASH))
        self.assertFalse(verification.math_audit_passed(audit_fixture(), "b" * 64))
        invalid = audit_fixture()
        invalid["audit"]["c_byte_engine"]["welford_stream_stats"]["mean"] = float("nan")
        self.assertFalse(verification.math_audit_passed(invalid, HASH))

    def test_unavailable_audit_rejects_scores(self):
        unavailable = {"ok": False, "status": "no_evaluado"}
        self.assertTrue(verification.audit_is_unavailable(503, unavailable))
        self.assertFalse(verification.audit_is_unavailable(200, unavailable))
        self.assertFalse(
            verification.audit_is_unavailable(
                503, {**unavailable, "report": {"overall_score": 100}}
            )
        )

    def test_http_gate_requires_every_control(self):
        responses = [
            (503, {"ok": False, "status": "no_evaluado"}),
            (401, {}),
            (401, {}),
            (401, {}),
            (401, {}),
            (404, {}),
            (400, {}),
            (200, {"tables": [{"name": "projects"}]}),
        ]
        with patch.object(verification, "http_json", side_effect=responses) as request:
            self.assertTrue(verification.verify_http_controls()[0])
            self.assertEqual(request.call_count, 8)
        for index, response in (
            (1, (200, {})),
            (7, (200, {"tables": [{"name": "job_requests"}]})),
        ):
            broken = copy.deepcopy(responses)
            broken[index] = response
            with patch.object(verification, "http_json", side_effect=broken):
                self.assertFalse(verification.verify_http_controls()[0])


if __name__ == "__main__":
    unittest.main()
