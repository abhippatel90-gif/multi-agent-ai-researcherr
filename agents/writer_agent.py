
from ollama import chat


class WriterAgent:

    def __init__(self):
        self.name = "Writer Agent"
        self.model = "qwen2.5:7b"

    def write_report(self, topic, plan, research, analysis, fact_check):

        prompt = f"""
You are a professional research report writer.

Write a useful, accurate, well-organized research report about:
{topic}

RESEARCH PLAN:
{plan[:1500]}

RESEARCH NOTES:
{research[:4500]}

ANALYSIS:
{analysis[:2000]}

FACT-CHECK NOTES:
{fact_check[:1500]}

Write the report using these sections:

# Executive Summary
Summarize the topic, major findings, benefits, and main concerns.

# 1. Introduction
Explain the topic, its background, and why it matters.

# 2. How the Technology Works
Explain the main technologies and their roles in simple language.

# 3. Major Applications
Explain practical applications and give examples supported by the research.

# 4. Benefits
Explain the major benefits and who can benefit from the technology.

# 5. Limitations and Challenges
Explain technical limitations, costs, accuracy concerns, and implementation challenges.

# 6. Risks and Ethical Concerns
Discuss privacy, security, bias, transparency, and safety where relevant.

# 7. Real-World Examples
Include only examples supported by the supplied research.

# 8. Future Scope
Describe realistic future developments and remaining challenges.

# 9. Recommendations
Provide practical recommendations based on the research.

# 10. Conclusion
Summarize the main findings without repeating the entire report.

# References
List the relevant original source URLs supplied in the research.

STRICT RULES:
- Write approximately 700-1000 words.
- Use simple, professional English.
- Explain technical terms clearly.
- Avoid repeating the same points in different sections.
- Do not invent facts, statistics, studies, quotations, or URLs.
- Do not claim a source verifies something unless the supplied information supports it.
- If evidence is insufficient, state that the claim requires verification.
- Remove duplicate source URLs from the reference list.
- Preserve valid source URLs exactly as supplied.
- Use Markdown headings and readable paragraphs.
- Return only the final report.
"""

        print("\nWriter Agent is preparing the report...")

        response = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "num_predict": 1200,
                "temperature": 0.2
            }
        )

        report = response["message"]["content"].strip()

        if not report:
            raise RuntimeError("Writer Agent returned an empty report.")

        return report


if __name__ == "__main__":

    agent = WriterAgent()

    topic = input("Enter a research topic: ").strip()

    if topic:
        report = agent.write_report(
            topic,
            "Research the topic and its applications.",
            "Research notes about the topic.",
            "Analysis of the findings.",
            "Some claims may require external verification."
        )

        print("\n" + "=" * 60)
        print("FINAL REPORT")
        print("=" * 60)
        print(report)
