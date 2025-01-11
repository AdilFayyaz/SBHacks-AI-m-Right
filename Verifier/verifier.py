from dotenv import load_dotenv
import os

load_dotenv()
my_api_key = os.getenv("CLAUDE_API")


from anthropic import Anthropic

client = Anthropic(
    api_key=my_api_key
)


our_first_message = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Hi there! Please write me a haiku about a pet chicken"}
    ]
)

print(our_first_message.content[0].text)