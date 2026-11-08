#!/usr/bin/env python3
"""
===============================================================================
MODULE: sync_agents_database.py
LOCATION: CV/04_database_lakehouse/sync_agents_database.py
PURPOSE: Master Relational Database Synchronizer for all 75 Corporate Agents
         Creates and populates:
           - `corporate_agents` (All 75 Canonical Agents)
           - `agent_memories` (Individual Memory Records)
           - `agent_skills` (Granular Skills per Agent)
           - `collective_journal_chain` (Cryptographic Chained Journal)
           - `agent_missions` (Inter-divisional missions)
AUTHOR: Deep Dive Brothers & AuraIcons Data Platform Architecture
===============================================================================
"""

from __future__ import annotations

import json
import sqlite3
import hashlib
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "financial_lakehouse.db"
PRESENTATION_DIR = Path("/Users/mikelirastorza/Desktop/Presentación Mikel Irastorza")
MEMORIES_JSON = PRESENTATION_DIR / "familia_memoria_individual.json"
JOURNAL_JSON = PRESENTATION_DIR / "familia_diario_colectivo.json"

SCHEMA_SQL = """
-- 1. Tabla Maestra de los 75 Agentes
CREATE TABLE IF NOT EXISTS corporate_agents (
    agent_id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    division INTEGER NOT NULL,
    division_name TEXT NOT NULL,
    role TEXT NOT NULL,
    level INTEGER NOT NULL DEFAULT 1,
    xp INTEGER NOT NULL DEFAULT 0,
    work_preferences TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 2. Bóveda de Memorias Individuales por Agente
CREATE TABLE IF NOT EXISTS agent_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    memory_type TEXT NOT NULL CHECK (memory_type IN ('learning', 'note_with_mikel', 'corrected_error', 'custom')),
    content TEXT NOT NULL,
    author TEXT NOT NULL DEFAULT 'Mikel Irastorza',
    sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (agent_id) REFERENCES corporate_agents(agent_id) ON DELETE CASCADE
);

-- 3. Habilidades Especializadas por Agente
CREATE TABLE IF NOT EXISTS agent_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    skill_name TEXT NOT NULL,
    proficiency_level INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (agent_id) REFERENCES corporate_agents(agent_id) ON DELETE CASCADE
);

-- 4. Cadena de Bloques del Diario Colectivo
CREATE TABLE IF NOT EXISTS collective_journal_chain (
    entry_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    mission_title TEXT NOT NULL,
    coordinator TEXT NOT NULL,
    participants_json TEXT NOT NULL,
    decisions_json TEXT NOT NULL,
    lessons_learned_json TEXT NOT NULL,
    celebrated_milestones_json TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    entry_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 5. Misiones Inter-Divisionales
CREATE TABLE IF NOT EXISTS agent_missions (
    mission_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    lead_division INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('briefing', 'draft', 'handoff', 'review', 'completed')),
    xp_awarded INTEGER NOT NULL DEFAULT 50,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Índices de alto rendimiento
CREATE INDEX IF NOT EXISTS idx_corporate_agents_division ON corporate_agents(division);
CREATE INDEX IF NOT EXISTS idx_agent_memories_agent_id ON agent_memories(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_skills_agent_id ON agent_skills(agent_id);
CREATE INDEX IF NOT EXISTS idx_collective_journal_timestamp ON collective_journal_chain(timestamp);
"""

def sync_database():
    print(f"[*] Conectando a SQLite: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(SCHEMA_SQL)

    # 1. Cargar memorias individuales de los 75 agentes
    with open(MEMORIES_JSON, "r", encoding="utf-8") as f:
        memories_data = json.load(f)

    print(f"[*] Sincronizando {len(memories_data)} agentes canónicos...")
    agents_count = 0
    memories_count = 0
    skills_count = 0

    for agent_code, data in memories_data.items():
        agent_id = data.get("agentId", agent_code)
        code = data.get("code", agent_code)
        name = data.get("name", "")
        division = int(data.get("division", 1))
        division_name = data.get("divisionName", "")
        role = data.get("role", "")
        level = int(data.get("level", 1))
        xp = int(data.get("xp", 0))
        work_pref = data.get("workPreferences", "")
        sha256 = data.get("sha256", "")

        cur.execute("""
            INSERT OR REPLACE INTO corporate_agents 
            (agent_id, code, name, division, division_name, role, level, xp, work_preferences, sha256)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (agent_id, code, name, division, division_name, role, level, xp, work_pref, sha256))
        agents_count += 1

        # Sincronizar Skills
        for skill in data.get("skills", []):
            cur.execute("""
                INSERT OR IGNORE INTO agent_skills (agent_id, skill_name, proficiency_level)
                VALUES (?, ?, ?)
            """, (agent_id, skill, level))
            skills_count += 1

        # Sincronizar Aprendizajes
        for item in data.get("learnings", []):
            item_hash = hashlib.sha256(item.encode("utf-8")).hexdigest()
            cur.execute("""
                INSERT INTO agent_memories (agent_id, memory_type, content, author, sha256)
                VALUES (?, 'learning', ?, 'Mikel Irastorza', ?)
            """, (agent_id, item, item_hash))
            memories_count += 1

        # Sincronizar Notas con Mikel
        for item in data.get("notesWithMikel", []):
            item_hash = hashlib.sha256(item.encode("utf-8")).hexdigest()
            cur.execute("""
                INSERT INTO agent_memories (agent_id, memory_type, content, author, sha256)
                VALUES (?, 'note_with_mikel', ?, 'Mikel Irastorza', ?)
            """, (agent_id, item, item_hash))
            memories_count += 1

        # Sincronizar Errores Corregidos
        for item in data.get("correctedErrors", []):
            item_hash = hashlib.sha256(item.encode("utf-8")).hexdigest()
            cur.execute("""
                INSERT INTO agent_memories (agent_id, memory_type, content, author, sha256)
                VALUES (?, 'corrected_error', ?, 'Mikel Irastorza', ?)
            """, (agent_id, item, item_hash))
            memories_count += 1

    # 2. Cargar Diario Colectivo
    with open(JOURNAL_JSON, "r", encoding="utf-8") as f:
        journal_data = json.load(f)

    journal_count = 0
    for entry in journal_data.get("entries", []):
        entry_id = entry.get("id")
        ts = entry.get("timestamp")
        title = entry.get("missionTitle")
        coordinator = entry.get("coordinator")
        participants = json.dumps(entry.get("participants", []), ensure_ascii=False)
        decisions = json.dumps(entry.get("decisions", []), ensure_ascii=False)
        lessons = json.dumps(entry.get("lessonsLearned", []), ensure_ascii=False)
        milestones = json.dumps(entry.get("celebratedMilestones", []), ensure_ascii=False)
        prev_h = entry.get("prevHash")
        entry_h = entry.get("hash")

        cur.execute("""
            INSERT OR REPLACE INTO collective_journal_chain
            (entry_id, timestamp, mission_title, coordinator, participants_json, decisions_json, lessons_learned_json, celebrated_milestones_json, prev_hash, entry_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (entry_id, ts, title, coordinator, participants, decisions, lessons, milestones, prev_h, entry_h))
        journal_count += 1

    conn.commit()
    conn.close()

    print(f"[✓] Sincronización finalizada con éxito:")
    print(f"    - Agentes registrados en base de datos: {agents_count}")
    print(f"    - Habilidades asignadas: {skills_count}")
    print(f"    - Memorias individuales persistidas: {memories_count}")
    print(f"    - Bloques de bitácora colectiva: {journal_count}")

if __name__ == "__main__":
    sync_database()
