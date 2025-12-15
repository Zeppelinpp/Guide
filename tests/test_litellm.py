import litellm
from src.settings import settings


response = litellm.completion(
    model="dashscope/qwen-turbo",
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ],
    api_key=settings.qwen_config["api_key"],
    stream=True
)

for chunk in response:
    model = chunk.model
    if not chunk.choices[0].finish_reason:
        content = chunk.choices[0].delta.content
        print(content, end="", flush=True)
    else:
        print()
        break
