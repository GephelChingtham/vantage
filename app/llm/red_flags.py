import os
from app.llm.mocks import mock_red_flags

async def analyze_red_flags(messages_text: str) -> dict:
    if os.getenv("USE_MOCKED_LLM", "true").lower() == "true":
        return await mock_red_flags(messages_text)
    
    from anthropic import Anthropic
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": f"Analyze for red flags:\n{messages_text}"
            }
        ]
    )
    import json
    result = json.loads(response.content[0].text)
    return result
