from ollama import chat

import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.web_search import web_search


class ResearchAgent:

    def __init__(self):

        self.name = "Research Agent"
        self.model = "qwen2.5:7b"

    def search_web(self, topic):

        print("\n🔎 Research Agent is searching the web...")

        queries = [
            f"{topic} overview",
            f"{topic} latest developments",
            f"{topic} applications benefits risks"
        ]

        all_results = []

        for query in queries:

            print(f"\nSearching: {query}")

            results = web_search(
                query,
                max_results=3
            )

            all_results.extend(results)

        return all_results

    def research(self, topic):

        # Step 1: Search the web
        search_results = self.search_web(topic)

        # Step 2: Convert search results into text
        sources_text = ""

        for result in search_results:

            sources_text += f"""
TITLE: {result['title']}
URL: {result['url']}
SNIPPET: {result['snippet']}

"""

        # Step 3: Give the web information to the LLM
        prompt = f"""
You are a professional Research Agent
inside a multi-agent AI research system.

RESEARCH TOPIC:
{topic}

The system performed real web searches and returned
the following search results:

================ WEB SEARCH RESULTS ================

{sources_text}

================ END SEARCH RESULTS =================

Your task is to create structured research notes.

Include:

1. Introduction
2. Key facts
3. Important concepts
4. Current developments
5. Real-world applications
6. Advantages
7. Disadvantages
8. Risks and limitations
9. Important observations
10. Sources used

IMPORTANT RULES:

- Use ONLY information supported by the provided search results.
- Do not invent facts.
- Do not invent sources.
- Do not claim that you visited a website if you only received its search result.
- Preserve source URLs where possible.
- If information is uncertain, clearly mention that it requires verification.
- Do not write the final polished report.
- These are research notes for other agents.

Make the research clear, structured and useful.
"""

        print("\n🧠 Research Agent is analyzing the search results...")

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]


if __name__ == "__main__":

    agent = ResearchAgent()

    topic = input("Enter a research topic: ")

    print("\n" + "=" * 60)
    print("RESEARCH AGENT")
    print("=" * 60)

    result = agent.research(topic)

    print("\n" + "=" * 60)
    print("RESEARCH RESULT")
    print("=" * 60)

    print(result)