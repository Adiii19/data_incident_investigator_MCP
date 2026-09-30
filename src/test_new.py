from context_manager import ContextManager


messages = [
    {"role": "system", "content": "System"},
    {"role": "user", "content": "Question"},
]

for i in range(20):
    messages.append(
        {
            "role": "tool",
            "content": f"Result {i}",
        }
    )

manager = ContextManager(
    max_messages=6
)

messages = manager.trim(messages)

for message in messages:
    print(message)