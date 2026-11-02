"""Test suite for Chatty COO Executive Command Center and Autonomous Pipeline Daemon.

Verifies:
1. AutonomousPipelineDaemon lifecycle, forced cycles, Little's Law telemetry, and Pacioli compliance.
2. Chatty COO executive directive dispatching across C-Suite directors with SHA-256 digital seals.
3. NetGUI Server REST API endpoints:
   - GET /api/pipeline/daemon/status
   - POST /api/pipeline/daemon/control
   - GET /api/chatty/orders
   - POST /api/chatty/command
   - POST /api/store/submit-profile & GET /api/store/candidates
   - POST /api/store/checkout for PROD-05-CAREER-PLACEMENT with Pacioli balance verification.
"""

from __future__ import annotations

import http.client
import json
import sqlite3
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

import enterprise_hierarchy
import netgui_server
from autonomous_pipeline_daemon import AutonomousPipelineDaemon, DaemonTelemetry


# ---------------------------------------------------------------------------
# 1. AUTONOMOUS PIPELINE DAEMON TESTS
# ---------------------------------------------------------------------------

def test_autonomous_pipeline_daemon_lifecycle():
    """Verify daemon lifecycle: creation, telemetry, force_cycle, pause, and resume."""
    daemon = AutonomousPipelineDaemon(cycle_interval_seconds=3600.0)
    assert not daemon.is_alive()

    # Initial telemetry check
    telemetry = daemon.get_telemetry()
    assert isinstance(telemetry, DaemonTelemetry)
    assert telemetry.cycles_completed == 0
    assert telemetry.current_rho <= 0.80
    assert telemetry.littles_law_compliant is True
    assert telemetry.pacioli_compliant is True

    # Start daemon
    assert daemon.start() is True
    assert daemon.is_alive() is True

    # Test force_cycle
    result = daemon.force_cycle()
    assert result["status"] == "cycle_executed"
    assert result["cycles_completed"] >= 1
    assert result["latency_ms"] >= 0.0

    # Verify telemetry updated
    updated_telem = daemon.get_telemetry()
    assert updated_telem.cycles_completed >= 1
    assert updated_telem.last_cycle_timestamp is not None
    assert updated_telem.last_latency_ms >= 0.0

    # Test pause and resume
    assert daemon.pause() is True
    paused_telem = daemon.get_telemetry()
    assert paused_telem.running is False

    assert daemon.resume() is True
    resumed_telem = daemon.get_telemetry()
    assert resumed_telem.running is True

    # Stop daemon
    assert daemon.stop() is True


def test_autonomous_pipeline_candidate_and_order_scans():
    """Verify daemon scans for unplaced candidates and pending orders execute cleanly."""
    daemon = AutonomousPipelineDaemon(cycle_interval_seconds=3600.0)
    candidates_scanned = daemon.scan_unplaced_candidates()
    assert isinstance(candidates_scanned, int)
    assert candidates_scanned >= 0

    orders_scanned = daemon.scan_pending_orders()
    assert isinstance(orders_scanned, int)
    assert orders_scanned >= 0


# ---------------------------------------------------------------------------
# 2. CHATTY COO EXECUTIVE HIERARCHY & DIRECTIVE DISPATCH TESTS
# ---------------------------------------------------------------------------

def test_chatty_coo_dispatch_presidential_directive():
    """Verify Chatty receives directives from Mikel Irastorza and dispatches C-Suite actions with digital seal."""
    directive = "Chatty, audita el balance Pacioli, revisa la ciberseguridad y optimiza el trading bot"
    order = enterprise_hierarchy.dispatch_presidential_directive(directive, issuer="Mikel Irastorza")

    assert order["issuer"] == "Mikel Irastorza"
    assert order["directive"] == directive
    assert order["order_id"].startswith("ORD-")
    assert len(order["digital_seal"]) == 64  # SHA-256 hex string

    # Check presidential response formatting
    response = order["response"]
    assert "¡A sus órdenes, Presidente Mikel! He recibido su directiva para NovusMundus:" in response
    assert directive in response

    # Check dispatched C-Suite actions
    actions = order["actions_dispatched"]
    assert len(actions) >= 2
    director_ids = [a["director_id"] for a in actions]
    assert "TITAN" in director_ids or "AEGIS" in director_ids or "HYPATIA" in director_ids

    for act in actions:
        assert "director_id" in act
        assert "director_name" in act
        assert "action" in act
        assert act["status"] == "COMPLETED"


def test_chatty_coo_alias_and_orders_log():
    """Verify alias dispatch_presidential_order works and logs are queryable."""
    directive = "Compilar Gemini Notebook con métricas de Sharpe y verificar slides"
    order1 = enterprise_hierarchy.dispatch_presidential_order(directive, issuer="Mikel Irastorza")
    assert order1["order_id"].startswith("ORD-")

    logs = enterprise_hierarchy.get_executive_orders_log()
    assert len(logs) >= 1
    recent_directives = [o["directive"] for o in logs]
    assert directive in recent_directives


# ---------------------------------------------------------------------------
# 3. HTTP SERVER ENDPOINTS INTEGRATION TESTS
# ---------------------------------------------------------------------------

@pytest.fixture()
def live_server():
    """Run NetGUI server with daemon on an ephemeral port in background thread."""
    netgui_server.GLOBAL_PIPELINE_DAEMON.start()
    server = ThreadingHTTPServer(("127.0.0.1", 0), netgui_server.NetGUIHandler)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://{host}:{port}", host, port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2.0)


def test_http_pipeline_daemon_status_and_control(live_server):
    """Test /api/pipeline/daemon/status and /api/pipeline/daemon/control endpoints."""
    _, host, port = live_server
    conn = http.client.HTTPConnection(host, port, timeout=5)

    # 1. GET status
    conn.request("GET", "/api/pipeline/daemon/status")
    res = conn.getresponse()
    assert res.status == 200
    data = json.loads(res.read().decode())
    assert data["ok"] is True
    assert "cycles_completed" in data
    assert "littles_law_compliant" in data
    assert "pacioli_compliant" in data
    assert data["littles_law_compliant"] is True

    # 2. POST control: force_cycle
    payload = json.dumps({"action": "force_cycle"}).encode()
    conn.request("POST", "/api/pipeline/daemon/control", body=payload, headers={"Content-Type": "application/json"})
    res2 = conn.getresponse()
    assert res2.status == 200
    data2 = json.loads(res2.read().decode())
    assert data2["ok"] is True
    assert data2["result"]["status"] == "cycle_executed"

    # 3. POST control: pause
    payload_pause = json.dumps({"action": "pause"}).encode()
    conn.request("POST", "/api/pipeline/daemon/control", body=payload_pause, headers={"Content-Type": "application/json"})
    res3 = conn.getresponse()
    assert res3.status == 200
    data3 = json.loads(res3.read().decode())
    assert data3["ok"] is True
    assert data3["telemetry"]["running"] is False

    # 4. POST control: resume
    payload_resume = json.dumps({"action": "resume"}).encode()
    conn.request("POST", "/api/pipeline/daemon/control", body=payload_resume, headers={"Content-Type": "application/json"})
    res4 = conn.getresponse()
    assert res4.status == 200
    data4 = json.loads(res4.read().decode())
    assert data4["ok"] is True
    assert data4["telemetry"]["running"] is True

    # 5. POST control: invalid action
    payload_inv = json.dumps({"action": "explode_server"}).encode()
    conn.request("POST", "/api/pipeline/daemon/control", body=payload_inv, headers={"Content-Type": "application/json"})
    res5 = conn.getresponse()
    assert res5.status == 400
    conn.close()


def test_http_chatty_command_and_orders(live_server):
    """Test /api/chatty/command and /api/chatty/orders endpoints."""
    _, host, port = live_server
    conn = http.client.HTTPConnection(host, port, timeout=5)

    # 1. POST command
    directive_text = "Chatty, audita el enjambre C-Suite y verifica el ledger contable"
    payload = json.dumps({"directive": directive_text, "issuer": "Mikel Irastorza"}).encode()
    conn.request("POST", "/api/chatty/command", body=payload, headers={"Content-Type": "application/json"})
    res = conn.getresponse()
    assert res.status == 200
    data = json.loads(res.read().decode())
    assert data["ok"] is True
    assert data["order_id"].startswith("ORD-")
    assert len(data["digital_seal"]) == 64
    assert directive_text in data["response"]

    # 2. GET orders log
    conn.request("GET", "/api/chatty/orders")
    res2 = conn.getresponse()
    assert res2.status == 200
    data2 = json.loads(res2.read().decode())
    assert data2["ok"] is True
    orders = data2["orders"]
    assert len(orders) >= 1
    assert any(o["order_id"] == data["order_id"] for o in orders)
    conn.close()


def test_http_store_talent_placement_and_checkout(live_server):
    """Test candidate profile intake and store checkout for PROD-05-CAREER-PLACEMENT with Pacioli balance."""
    _, host, port = live_server
    conn = http.client.HTTPConnection(host, port, timeout=5)

    # 1. Candidate intake
    candidate_payload = json.dumps({
        "full_name": "Iker Zubizarreta",
        "email": "iker.z@euskadi-tech.io",
        "target_role": "Senior Data Engineer",
        "experience_years": "6",
        "linkedin_url": "https://linkedin.com/in/iker-tech",
        "github_url": "https://github.com/iker-z",
        "bio": "Especialista en pipelines Spark Declarative y BigQuery ELT."
    }).encode()

    conn.request("POST", "/api/store/submit-profile", body=candidate_payload, headers={"Content-Type": "application/json"})
    res = conn.getresponse()
    assert res.status == 200
    cand_data = json.loads(res.read().decode())
    assert cand_data["ok"] is True
    assert cand_data["candidate_id"].startswith("TALENT-")
    assert cand_data["full_name"] == "Iker Zubizarreta"
    assert len(cand_data["intake_seal"]) == 64

    # 2. Query candidates list
    conn.request("GET", "/api/store/candidates")
    res_cand = conn.getresponse()
    assert res_cand.status == 200
    cand_list = json.loads(res_cand.read().decode())
    assert cand_list["ok"] is True
    assert any(c["candidate_id"] == cand_data["candidate_id"] for c in cand_list["candidates"])

    # 3. Checkout PROD-05-CAREER-PLACEMENT
    order_payload = json.dumps({
        "customer_name": "Iker Zubizarreta",
        "customer_email": "iker.z@euskadi-tech.io",
        "tax_id": "ES12345678Z",
        "payment_method": "transfer",
        "items": [
            {
                "id": "PROD-05-CAREER-PLACEMENT",
                "name": "Acelerador de Carrera & Colocación Laboral Tech",
                "price_cents": 35000,
                "quantity": 1
            }
        ]
    }).encode()

    conn.request("POST", "/api/store/checkout", body=order_payload, headers={"Content-Type": "application/json"})
    res_order = conn.getresponse()
    assert res_order.status == 200
    order_data = json.loads(res_order.read().decode())
    assert order_data["ok"] is True
    assert order_data["invoice_id"].startswith("INV-")

    # Pacioli arithmetic verification:
    # Subtotal 350,00 € (35000 cents), IVA 21% = 73,50 € (7350 cents), Total = 423,50 € (42350 cents)
    assert order_data["subtotal_eur"] == 350.0
    assert order_data["vat_eur"] == 73.5
    assert order_data["total_eur"] == 423.5
    assert len(order_data["digital_seal"]) == 64
    conn.close()


def test_cybersecurity_audit_ciso_aegis_and_endpoint(live_server):
    """Test CISO Aegis Cybersecurity Engine and /api/security/audit endpoint."""
    from cybersecurity_audit_agent import GLOBAL_SECURITY_ENGINE

    # 1. Direct engine execution
    report = GLOBAL_SECURITY_ENGINE.run_full_security_audit()
    assert report.overall_score == 100
    assert report.security_grade.startswith("A+")
    assert report.total_checks == 8
    assert report.passed_checks == 8
    assert report.failed_checks == 0
    assert report.cve_vulnerabilities_found == 0
    assert len(report.digital_seal) == 64

    # 2. HTTP GET /api/security/audit
    _, host, port = live_server
    conn = http.client.HTTPConnection(host, port, timeout=5)
    conn.request("GET", "/api/security/audit")
    res = conn.getresponse()
    assert res.status == 200
    data = json.loads(res.read().decode())
    assert data["ok"] is True
    assert data["report"]["overall_score"] == 100
    assert data["report"]["passed_checks"] == 8

    # 3. HTTP POST /api/security/audit/run
    conn.request("POST", "/api/security/audit/run", body=b"{}", headers={"Content-Type": "application/json"})
    res2 = conn.getresponse()
    assert res2.status == 200
    data2 = json.loads(res2.read().decode())
    assert data2["ok"] is True
    assert data2["report"]["overall_score"] == 100
    conn.close()
