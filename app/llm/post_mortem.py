import os
from app.llm.mocks import mock_post_mortem

async def generate_post_mortem(directness: float, effort: dict, flags: dict) -> dict:
    if os.getenv("USE_MOCKED_LLM", "true").lower() == "true":
        return await mock_post_mortem({
            "directness": directness,
            "effort": effort,
            "flags": flags
        })
    
    from anthropic import Anthropic
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": f"Generate post-mortem:\n{str(effort)}"
            }
        ]
    )
    import json
    result = json.loads(response.content[0].text)
    return result
