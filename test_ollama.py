from ollama import chat

response = chat(
    model="qwen2.5:7b",
    messages=[
        {
            "role": "user",
            "content": "Explain what an AI agent is in very simple words."
        }
    ]
)

print("\nAI RESPONSE:\n")
print(response["message"]["content"])