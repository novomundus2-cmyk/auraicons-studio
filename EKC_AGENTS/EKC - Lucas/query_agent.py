#!/usr/bin/env python3
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "lucas.db")

def query_agent():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    print("=" * 70)
    print("EKC (ElektriKubercisC) · Lucas")
    print("=" * 70)
    
    cur.execute("SELECT * FROM agent_identity;")
    row = dict(cur.fetchone())
    for k, v in row.items():
        print(f"  {k}: {v}")
        
    print("")
    print("[Últimas Tareas en Cola]")
    for t in cur.execute("SELECT task_id, directive_title, status, execution_latency_ms FROM task_queue LIMIT 5"):
        print(f"  • [{t['status']}] {t['task_id']}: {t['directive_title']} ({t['execution_latency_ms']}ms)")
        
    print("")
    print("[Registros de Dominio: system_vital_diagnostics]")
    for d in cur.execute("SELECT * FROM system_vital_diagnostics LIMIT 5"):
        print(f"  • {dict(d)}")
        
    conn.close()

if __name__ == "__main__":
    query_agent()
