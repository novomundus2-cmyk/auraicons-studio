"""Regression tests for the security fixes, the export ordering bug and the core math."""

from __future__ import annotations

import http.client
import json
import sqlite3
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import enterprise_hierarchy
import numpy as np
import pytest
import route_optimizer

import agent
import build_database
import netgui_server
from scientific_analytics import StatsMonoid, shannon_entropy_bits


# --------------------------------------------------------------------------- agent: SQL
@pytest.fixture()
def agent_env(tmp_paths, monkeypatch):
    monkeypatch.setattr(agent, "PATHS", tmp_paths)
    return tmp_paths


def _users(paths) -> int:
    with sqlite3.connect(paths.db_path) as conn:
        return conn.execute("SELECT COUNT(*) FROM dim_users").fetchone()[0]


def test_select_and_with_work(agent_env):
    assert json.loads(agent.query_project_database("SELECT COUNT(*) FROM dim_users"))["rows"] == [[1]]
    assert json.loads(agent.query_project_database("WITH x AS (SELECT 7 a) SELECT a FROM x"))["rows"] == [[7]]


@pytest.mark.parametrize(
    "sql",
    [
        "DROP TABLE dim_users",
        "DELETE FROM dim_users",
        "UPDATE dim_users SET full_name='x'",
        "SELECT 1; DROP TABLE dim_users",
        "WITH x AS (SELECT 1) DELETE FROM dim_users",  # passes the text filter, stopped by the authorizer
        "ATTACH DATABASE '/tmp/evil.db' AS e",
        "PRAGMA query_only = OFF",
    ],
)
def test_destructive_sql_is_rejected_and_data_survives(agent_env, sql):
    agent.query_project_database(sql)
    assert _users(agent_env) == 1


# --------------------------------------------------------------------------- agent: paths
@pytest.mark.parametrize("name", ["../../evil", "a/b", "..", "x" * 200, "", "a b"])
def test_unsafe_notebook_names_rejected(agent_env, name):
    with pytest.raises(ValueError):
        agent.create_study_notebook(name, "t")
    with pytest.raises(ValueError):
        agent.add_notebook_cell(name, "code", "print(1)")


def test_safe_notebook_name_stays_inside_notebooks_dir(agent_env):
    agent.create_study_notebook("mi_nota-1", "Título")
    created = list(agent_env.notebooks_dir.iterdir())
    assert [p.name for p in created] == ["mi_nota-1.ipynb"]


# --------------------------------------------------------------------------- export ordering
def test_export_returns_newest_windows_not_oldest(tmp_paths, monkeypatch):
    monkeypatch.setattr(build_database, "PATHS", tmp_paths)
    with sqlite3.connect(tmp_paths.db_path) as conn:
        conn.executemany(
            "INSERT INTO streaming_window_sinks VALUES ('w','w','cat',1,1.0,1.0,0,?)",
            [(f"2026-01-01 00:{i // 60:02d}:{i % 60:02d}",) for i in range(150)],
        )
        build_database.export_categorized_folders_and_bridge(conn)
    rows = json.loads(
        (tmp_paths.categories_dir / "02_gold_analytics" / "streaming_window_sinks.json").read_text()
    )
    assert len(rows) == 100
    assert rows[0]["saved_at"] == "2026-01-01 00:02:29"  # newest of the 150, not row #1


# --------------------------------------------------------------------------- HTTP server
@pytest.fixture()
def server(tmp_paths, monkeypatch):
    monkeypatch.setattr(netgui_server, "PATHS", tmp_paths)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), netgui_server.ArchifyNetGUIHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield httpd.server_address[1]
    httpd.shutdown()
    httpd.server_close()


def _request(port: int, method: str, path: str):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    conn.request(method, path)
    resp = conn.getresponse()
    body = resp.read()
    headers = {k.lower(): v for k, v in resp.getheaders()}
    conn.close()
    return resp.status, headers, body


def test_static_allowlist(server):
    assert _request(server, "GET", "/index.html")[0] == 200
    assert _request(server, "GET", "/cv.html")[0] == 200
    assert _request(server, "GET", "/cv_printable.html")[0] == 200
    assert _request(server, "GET", "/evernote.html")[0] == 200
    assert _request(server, "GET", "/netgui_server.py")[0] == 404
    assert _request(server, "GET", "/__pycache__/")[0] == 404
    assert _request(server, "GET", "/%2e%2e/DOSSIER_NOTEBOOKLM_MIKEL.md")[0] == 404


def test_cv_and_dossier_download_endpoints(server):
    status, headers, body = _request(server, "GET", "/cv.pdf")
    assert status == 200
    assert headers["content-type"] == "application/pdf"
    assert 'filename="CV_Mikel_Irastorza.pdf"' in headers["content-disposition"]
    assert len(body) > 100_000

    status, headers, body = _request(server, "GET", "/dossier.pdf")
    assert status == 200
    assert headers["content-type"] == "application/pdf"
    assert 'filename="DOSSIER_NOTEBOOKLM_MIKEL.pdf"' in headers["content-disposition"]

    status, headers, body = _request(server, "GET", "/notebooks.zip")
    assert status == 200
    assert headers["content-type"] == "application/zip"

    # API generation endpoints
    status_cv, headers_cv, _ = _request(server, "GET", "/api/generate-pdf?doc=cv")
    assert status_cv == 200
    assert headers_cv["content-type"] == "application/pdf"

    status_dos, headers_dos, _ = _request(server, "GET", "/api/generate-pdf?doc=dossier")
    assert status_dos == 200
    assert headers_dos["content-type"] == "application/pdf"

    # HEAD request support
    status_head, _headers_head, head_body = _request(server, "HEAD", "/cv.pdf")
    assert status_head == 200
    assert len(head_body) == 0


def test_mutating_routes_reject_get_and_have_no_cors(server):
    for route in ("/api/run-pipeline", "/api/nas-sync"):
        assert _request(server, "GET", route)[0] == 405
    _status, headers, _ = _request(server, "GET", "/api/status")
    assert "access-control-allow-origin" not in headers


def test_server_returns_json_500_instead_of_hanging(server, monkeypatch):
    def boom(*_a, **_k):
        raise RuntimeError("boom")

    monkeypatch.setattr(netgui_server, "run_interconnected_pipeline", boom)
    status, _, body = _request(server, "POST", "/api/run-pipeline")
    assert status == 500 and json.loads(body)["ok"] is False


# --------------------------------------------------------------------------- math
def test_monoid_laws_and_exactness():
    rng = np.random.default_rng(0)
    a, b, c = (StatsMonoid.from_array(rng.normal(size=n)) for n in (50, 70, 90))
    left, right = (a + b) + c, a + (b + c)
    assert left.count == right.count
    assert left.mean == pytest.approx(right.mean) and left.m2 == pytest.approx(right.m2)
    assert StatsMonoid() + a == a == a + StatsMonoid()
    data = rng.normal(size=500)
    parts = [StatsMonoid.from_array(p) for p in np.array_split(data, 7)]
    total = sum(parts[1:], parts[0])
    assert total.mean == pytest.approx(np.mean(data)) and total.variance == pytest.approx(np.var(data))


def test_entropy_of_uniform_partitions_is_log2_k():
    assert shannon_entropy_bits(np.repeat(np.arange(8), 10)) == pytest.approx(3.0)


# --------------------------------------------------------------------------- corporate enterprise
def test_corporate_enterprise_hierarchy_and_routes(tmp_paths, monkeypatch):
    monkeypatch.setattr(enterprise_hierarchy, "PATHS", tmp_paths)
    monkeypatch.setattr(route_optimizer, "PATHS", tmp_paths)
    status = enterprise_hierarchy.get_corporate_status()
    assert status["ok"] is True
    assert status["president"] == "Mikel Irastorza"
    assert status["ceo"] == "Chatty"
    assert status["agents_count"] >= 11
    tiers = {ag["name"]: ag["tier"] for ag in status["agents"]}
    assert tiers["Mikel Irastorza"] == 0
    assert tiers["Chatty"] == 1
    routes = route_optimizer.get_all_routes_telemetry()
    assert len(routes) == 6
    assert all(r["sla_target_ms"] > 0 for r in routes)


def test_corporate_route_self_optimization(tmp_paths, monkeypatch):
    monkeypatch.setattr(route_optimizer, "PATHS", tmp_paths)
    res = route_optimizer.optimize_corporate_route("ROUTE-02-KAFKA", speed_factor=1.5)
    assert res.route_id == "ROUTE-02-KAFKA"
    assert res.status == "AUTOMEJORADA ⚡"
    assert res.optimized_latency_ms < res.current_latency_ms
    assert res.improvement_pct > 0


def test_presidential_directive_dispatch(tmp_paths, monkeypatch):
    monkeypatch.setattr(enterprise_hierarchy, "PATHS", tmp_paths)
    monkeypatch.setattr(route_optimizer, "PATHS", tmp_paths)
    result = enterprise_hierarchy.dispatch_presidential_directive(
        "Chatty: maximizar throughput y verificar el monoide de Welford"
    )
    assert result["ok"] is True
    assert "CTO Titan" in result["assigned_csuite"]
    assert "CSO Hypatia" in result["assigned_csuite"]
    assert "¡A sus órdenes, Presidente Mikel!" in result["chatty_response"]
    assert result["corporate_efficiency_index"] >= 98.0
    with sqlite3.connect(tmp_paths.db_path) as conn:
        order_count = conn.execute("SELECT COUNT(*) FROM corporate_executive_orders").fetchone()[0]
        assert order_count >= 3


def test_enterprise_rest_endpoints(server):
    status, _, body = _request(server, "GET", "/api/enterprise/status")
    assert status == 200
    data = json.loads(body)
    assert data["ok"] is True
    assert data["president"] == "Mikel Irastorza"

    status_r, _, body_r = _request(server, "GET", "/api/enterprise/routes")
    assert status_r == 200
    assert len(json.loads(body_r)["routes"]) == 6

    status_k, _, body_k = _request(server, "GET", "/api/enterprise/knowledge")
    assert status_k == 200
    assert len(json.loads(body_k)["knowledge"]) >= 4

    conn = http.client.HTTPConnection("127.0.0.1", server, timeout=10)
    post_payload = json.dumps(
        {"directive": "Auditar cero fallos y clean code", "issuer": "Mikel Irastorza · Presidente"}
    )
    conn.request(
        "POST", "/api/enterprise/directive", body=post_payload, headers={"Content-Type": "application/json"}
    )
    resp = conn.getresponse()
    post_body = resp.read()
    conn.close()
    assert resp.status == 200
    post_data = json.loads(post_body)
    assert post_data["ok"] is True
    assert "CISO Aegis" in post_data["assigned_csuite"]


def test_supabase_integration_and_sync(server, tmp_paths, monkeypatch):
    import supabase_sync

    monkeypatch.setattr(supabase_sync, "PATHS", tmp_paths)
    stat = supabase_sync.get_supabase_status()
    assert stat["ok"] is True
    assert stat["rls_enforced"] is True
    assert stat["rls_tables_count"] == 8
    assert stat["schema_ddl_available"] is True

    # Test HTTP GET
    status, _, body = _request(server, "GET", "/api/supabase/status")
    assert status == 200
    data = json.loads(body)
    assert data["ok"] is True
    assert "fact_transactions" in data["rls_tables"]

    # Test HTTP POST sync
    conn = http.client.HTTPConnection("127.0.0.1", server, timeout=10)
    conn.request("POST", "/api/supabase/sync", body="{}", headers={"Content-Type": "application/json"})
    resp = conn.getresponse()
    body_sync = resp.read()
    conn.close()
    assert resp.status == 200
    sync_data = json.loads(body_sync)
    assert sync_data["ok"] is True
    assert sync_data["tables_synced"] >= 4


def test_enterprise_core_ledger_and_concurrency():
    import test_concurrency_ledger

    # Verify that the master SQL exists and is non-empty
    sql_path = Path(__file__).resolve().parent.parent / "04_database_lakehouse" / "enterprise_core_ledger.sql"
    assert sql_path.exists()
    assert sql_path.stat().st_size > 5_000

    if not test_concurrency_ledger.is_docker_available():
        pytest.skip("Docker container 'supabase_db_novus-capital' not active; skipping live PostgreSQL concurrency suite")

    # Execute ledger test suite
    test_concurrency_ledger.test_1_seed_and_double_entry_transfer()
    test_concurrency_ledger.test_2_idempotency_and_replay_protection()
    test_concurrency_ledger.test_3_engine_level_zero_sum_enforcement()
    test_concurrency_ledger.test_4_high_concurrency_race_condition()
    test_concurrency_ledger.test_5_worker_queue_skip_locked()
    test_concurrency_ledger.test_6_tamper_evident_cryptographic_lineage()


def test_gold_nanocluster_physics_and_sutton_chen():
    import numpy as np
    import scientific_analytics as sa

    # 1. Verify Sutton-Chen potential calculation for Gold (Au) atomic cluster
    coords = np.array(
        [
            [0.0, 0.0, 0.0],
            [2.88, 0.0, 0.0],  # Nearest neighbor distance in Au (approx 2.88 Å)
            [1.44, 2.49, 0.0],
        ],
        dtype=np.float64,
    )
    energy = sa.compute_gold_sutton_chen_energy(coords)
    # Binding energy must be strictly negative (attractive/stable bound cluster)
    assert energy < 0.0
    assert -20.0 < energy < -1.0

    # 2. Verify Au20 nanocluster physical metrics and multidisciplinary applications
    metrics = sa.analyze_gold_nanocluster_au20()
    assert metrics.num_atoms == 20
    assert metrics.homo_lumo_gap_ev == 1.77
    assert metrics.lspr_peak_nm == 525.0
    assert metrics.co_activation_barrier_ev == 0.18
    assert metrics.quantum_conductance_us == 77.48
    assert "nanomedicina" in metrics.applications
    assert "computacion_cuantica" in metrics.applications
    assert "catalisis_verde" in metrics.applications
    assert "fotonica_metamateriales" in metrics.applications
    assert "metrologia_cad" in metrics.applications
    assert "finanzas_cuantitativas" in metrics.applications

