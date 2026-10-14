
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "research_agent_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=10,
    )


def initialize_database():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS research_runs (
                    id BIGSERIAL PRIMARY KEY,
                    topic TEXT NOT NULL,
                    status VARCHAR(30) NOT NULL DEFAULT 'started',
                    research_plan TEXT,
                    research_notes TEXT,
                    analysis TEXT,
                    fact_check TEXT,
                    final_report TEXT,
                    markdown_path TEXT,
                    pdf_path TEXT,
                    docx_path TEXT,
                    error_message TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    completed_at TIMESTAMPTZ
                )
            """)


def create_research_run(topic):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO research_runs (topic, status)
                VALUES (%s, 'started')
                RETURNING id
                """,
                (topic,),
            )
            return cur.fetchone()[0]


def update_research_run(run_id, **fields):
    allowed_fields = {
        "status",
        "research_plan",
        "research_notes",
        "analysis",
        "fact_check",
        "final_report",
        "markdown_path",
        "pdf_path",
        "docx_path",
        "error_message",
        "completed_at",
    }

    if not fields:
        return

    invalid_fields = set(fields) - allowed_fields
    if invalid_fields:
        raise ValueError(
            f"Unsupported database fields: {sorted(invalid_fields)}"
        )

    assignments = ", ".join(
        f"{field} = %s" for field in fields
    )
    values = list(fields.values())

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE research_runs SET {assignments} WHERE id = %s",
                (*values, run_id),
            )


def get_recent_runs(limit=20):
    limit = max(1, min(int(limit), 100))

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, topic, status, created_at, completed_at,
                       markdown_path, pdf_path, docx_path, error_message
                FROM research_runs
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            return cur.fetchall()
