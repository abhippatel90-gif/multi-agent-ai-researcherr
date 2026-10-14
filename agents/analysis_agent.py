from ollama import chat


class AnalysisAgent:

    def __init__(self):
        self.name = "Analysis Agent"
        self.model = "qwen2.5:7b"

    def analyze(self, topic, research):

        prompt = f"""
You are the Analysis Agent in a multi-agent research system.

The research topic is:

{topic}

The Research Agent produced the following research:

---------------- RESEARCH ----------------

{research}

---------------- END RESEARCH -------------

Your job is to analyze the research.

Create structured analysis containing:

1. Most important findings
2. Key facts and evidence
3. Important patterns or relationships
4. Advantages
5. Disadvantages
6. Risks or limitations
7. Real-world significance
8. Important conclusions

Do not write the final report.

Your output will be passed to another AI agent that will write the final report.

Be analytical, clear, and avoid unnecessary repetition.
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

    agent = AnalysisAgent()

    topic = input("Enter a topic: ")

    sample_research = """
    Artificial Intelligence is increasingly being used in healthcare
    for medical imaging, disease prediction, drug discovery and
    clinical decision support.
    """

    print("\n" + "=" * 60)
    print("ANALYSIS AGENT")
    print("=" * 60)

    result = agent.analyze(topic, sample_research)

    print(result)