
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.manager_agent import ManagerAgent
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.fact_checker_agent import FactCheckerAgent
from agents.writer_agent import WriterAgent

from backend.database import (
    initialize_database,
    create_research_run,
    update_research_run,
)
from backend.report_generator import generate_all_formats


def execute_research(run_id, topic):
    try:
        manager = ManagerAgent()
        researcher = ResearchAgent()
        analyst = AnalysisAgent()
        fact_checker = FactCheckerAgent()
        writer = WriterAgent()

        print(f"[Run {run_id}] Manager Agent started")
        update_research_run(run_id, status="running_manager")
        plan = manager.create_plan(topic)
        update_research_run(run_id, research_plan=plan)

        print(f"[Run {run_id}] Research Agent started")
        update_research_run(run_id, status="running_research")
        research = researcher.research(topic)
        update_research_run(run_id, research_notes=research)

        print(f"[Run {run_id}] Analysis Agent started")
        update_research_run(run_id, status="running_analysis")
        analysis = analyst.analyze(topic, research)
        update_research_run(run_id, analysis=analysis)

        print(f"[Run {run_id}] Fact Checker Agent started")
        update_research_run(run_id, status="running_fact_check")
        fact_check = fact_checker.check(topic, research, analysis)
        update_research_run(run_id, fact_check=fact_check)

        print(f"[Run {run_id}] Writer Agent started")
        update_research_run(run_id, status="running_writer")
        final_report = writer.write_report(
            topic, plan, research, analysis, fact_check
        )

        reports_folder = PROJECT_ROOT / "reports"
        md_path, pdf_path, docx_path = generate_all_formats(
            topic, final_report, reports_folder
        )

        update_research_run(
            run_id,
            status="completed",
            final_report=final_report,
            markdown_path=str(md_path),
            pdf_path=str(pdf_path),
            docx_path=str(docx_path),
            completed_at=datetime.now().astimezone(),
        )

        print(f"[Run {run_id}] Completed successfully")

    except Exception as error:
        message = f"{type(error).__name__}: {error}"
        print(f"[Run {run_id}] Failed: {message}")

        try:
            update_research_run(
                run_id,
                status="failed",
                error_message=message[:4000],
                completed_at=datetime.now().astimezone(),
            )
        except Exception as db_error:
            print(f"[Run {run_id}] Could not save failure: {db_error}")


def start_research(topic):
    initialize_database()
    return create_research_run(topic)
