
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


def main():
    print("=" * 70)
    print("              MULTI-AGENT RESEARCH SYSTEM")
    print("=" * 70)

    try:
        initialize_database()
        print("\nPostgreSQL connected successfully.")
    except Exception as error:
        print(f"\nDatabase connection failed: {error}")
        print("Check your PostgreSQL service and .env settings.")
        return

    topic = input("\nEnter your research topic: ").strip()

    if not topic:
        print("Error: Please enter a research topic.")
        return

    try:
        run_id = create_research_run(topic)
        print(f"\nResearch run ID: {run_id}")
    except Exception as error:
        print(f"Could not create database record: {error}")
        return

    try:
        manager = ManagerAgent()
        researcher = ResearchAgent()
        analyst = AnalysisAgent()
        fact_checker = FactCheckerAgent()
        writer = WriterAgent()

        print("\n[1/5] Manager Agent is creating a research plan...")
        plan = manager.create_plan(topic)
        update_research_run(run_id, research_plan=plan)
        print(plan)

        print("\n[2/5] Research Agent is researching the topic...")
        research = researcher.research(topic)
        update_research_run(run_id, research_notes=research)
        print("\nResearch completed.")

        print("\n[3/5] Analysis Agent is analyzing the research...")
        analysis = analyst.analyze(topic, research)
        update_research_run(run_id, analysis=analysis)
        print("\nAnalysis completed.")

        print("\n[4/5] Fact Checker Agent is reviewing the information...")
        fact_check = fact_checker.check(topic, research, analysis)
        update_research_run(run_id, fact_check=fact_check)
        print("\nFact-check review completed.")

        print("\n[5/5] Writer Agent is creating the final report...")
        final_report = writer.write_report(
            topic,
            plan,
            research,
            analysis,
            fact_check,
        )

        reports_folder = PROJECT_ROOT / "reports"

        print("\nGenerating Markdown, PDF and Word files...")
        md_path, pdf_path, docx_path = generate_all_formats(
            topic,
            final_report,
            reports_folder,
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

        print("\n" + "=" * 70)
        print("                 RESEARCH COMPLETE")
        print("=" * 70)
        print(f"\nDatabase record ID: {run_id}")
        print(f"Markdown: {md_path}")
        print(f"PDF:      {pdf_path}")
        print(f"DOCX:     {docx_path}")

    except Exception as error:
        error_message = f"{type(error).__name__}: {error}"

        try:
            update_research_run(
                run_id,
                status="failed",
                error_message=error_message[:4000],
                completed_at=datetime.now().astimezone(),
            )
        except Exception as db_error:
            print(f"\nCould not save failure status: {db_error}")

        print(f"\nResearch failed: {error_message}")
        print(f"Run ID {run_id} has been marked as failed if the database was available.")
        raise


if __name__ == "__main__":
    main()
