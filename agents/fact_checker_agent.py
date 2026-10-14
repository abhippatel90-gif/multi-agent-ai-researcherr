from ollama import chat


class FactCheckerAgent:

    def __init__(self):
        self.name = "Fact Checker Agent"
        self.model = "qwen2.5:7b"

    def check(self, topic, research, analysis):

        prompt = f"""
You are the Fact Checker Agent in a multi-agent research system.

Your responsibility is to critically review research and analysis
before the final report is written.

RESEARCH TOPIC:
{topic}

================ RESEARCH ================

{research}

================ ANALYSIS ================

{analysis}

================ YOUR TASK ================

Review the information above.

Identify:

1. Claims that appear reliable
2. Claims that may be uncertain
3. Claims that require external verification
4. Possible contradictions
5. Possible unsupported statements
6. Missing important information
7. Recommendations for improving the final report

IMPORTANT:

You do NOT have access to a guaranteed external source in this stage.

Therefore, do NOT pretend that you have verified facts on the internet.

Clearly distinguish between:
- Supported by the provided research
- Potentially uncertain
- Requires external verification

Return a structured fact-checking report.
"""

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

    agent = FactCheckerAgent()

    topic = input("Enter a topic: ")

    sample_research = """
    AI is increasingly being used in healthcare for medical imaging,
    disease prediction, drug discovery and clinical decision support.
    """

    sample_analysis = """
    AI can potentially improve healthcare efficiency and assist
    medical professionals with decision-making.
    """

    print("\n" + "=" * 60)
    print("FACT CHECKER AGENT")
    print("=" * 60)

    result = agent.check(
        topic,
        sample_research,
        sample_analysis
    )

    print(result)