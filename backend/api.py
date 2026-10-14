
from pathlib import Path

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from psycopg.rows import dict_row

from backend.database import get_connection, initialize_database
from backend.research_service import start_research, execute_research

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = FastAPI(
    title="Multi-Agent AI Researcher",
    description="Research, analyze, and generate reports using local AI agents.",
    version="1.0.0",
)


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=300)


@app.on_event("startup")
def startup():
    initialize_database()


@app.get("/")
def home():
    page = FRONTEND_DIR / "index.html"
    if not page.exists():
        raise HTTPException(
            status_code=404,
            detail="Dashboard file not found in the frontend folder.",
        )
    return FileResponse(page)


@app.get("/api/health")
def health():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return {"status": "ok", "database": "connected"}
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed. Check PostgreSQL and .env.",
        )


@app.get("/api/stats")
def stats():
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE status = 'completed') AS completed,
                    COUNT(*) FILTER (WHERE status = 'failed') AS failed,
                    COUNT(*) FILTER (
                        WHERE status NOT IN ('completed', 'failed')
                    ) AS active
                FROM research_runs
            """)
            return cur.fetchone()


@app.get("/api/runs")
def list_runs():
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT id, topic, status, created_at, completed_at,
                       markdown_path, pdf_path, docx_path, error_message
                FROM research_runs
                ORDER BY created_at DESC
                LIMIT 100
            """)
            return cur.fetchall()


@app.get("/api/runs/{run_id}")
def run_details(run_id: int):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, topic, status, research_plan, research_notes,
                       analysis, fact_check, final_report,
                       markdown_path, pdf_path, docx_path,
                       error_message, created_at, completed_at
                FROM research_runs
                WHERE id = %s
                """,
                (run_id,),
            )
            result = cur.fetchone()

    if result is None:
        raise HTTPException(status_code=404, detail="Research run not found.")

    return result


@app.post("/api/research", status_code=202)
def create_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    topic = request.topic.strip()

    if len(topic) < 3:
        raise HTTPException(
            status_code=400,
            detail="Please enter a topic with at least 3 characters.",
        )

    try:
        run_id = start_research(topic)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Could not create a research run. Check PostgreSQL settings.",
        )

    background_tasks.add_task(execute_research, run_id, topic)

    return {
        "id": run_id,
        "topic": topic,
        "status": "started",
        "message": "Research started. You can monitor its progress on the dashboard.",
    }


@app.get("/api/runs/{run_id}/download/{file_format}")
def download_report(run_id: int, file_format: str):
    allowed = {
        "pdf": "pdf_path",
        "docx": "docx_path",
        "md": "markdown_path",
    }

    if file_format not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Supported formats are pdf, docx, and md.",
        )

    column = allowed[file_format]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT {column} FROM research_runs WHERE id = %s",
                (run_id,),
            )
            row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Research run not found.")

    path_value = row[0]
    if not path_value:
        raise HTTPException(
            status_code=404,
            detail="This report is not available yet.",
        )

    report_path = Path(path_value).resolve()
    reports_root = (PROJECT_ROOT / "reports").resolve()

    if not report_path.is_relative_to(reports_root):
        raise HTTPException(status_code=403, detail="Invalid report path.")

    if not report_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="The report file could not be found on disk.",
        )

    return FileResponse(
        path=report_path,
        filename=report_path.name,
    )
