from ollama import chat


class ManagerAgent:

    def __init__(self):
        self.name = "Manager Agent"
        self.model = "qwen2.5:7b"

    def create_plan(self, topic):

        prompt = f"""
You are the Manager Agent of a multi-agent research system.

The user wants a research report about:

{topic}

Your job is NOT to write the report.

Instead, create a clear research plan for other AI agents.

Break the task into 4-6 specific research tasks.

For each task explain:
- What needs to be researched
- What information should be collected
- Why the information is important

Return ONLY the research plan.
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

    agent = ManagerAgent()

    topic = input("Enter a research topic: ")

    print("\n" + "=" * 60)
    print("MANAGER AGENT")
    print("=" * 60)

    plan = agent.create_plan(topic)

    print(plan)