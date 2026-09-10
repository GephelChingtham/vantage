MOCK_RED_FLAGS = {
    "flags_detected": ["breadcrumbing", "tactical deflection"],
    "situationship_risk_index": "HIGH",
    "confidence": 0.87,
    "reasoning": "Effort asymmetry + deflection patterns suggest holding-pattern behavior"
}

MOCK_POST_MORTEM = {
    "entropy_shift_date": "2024-01-18",
    "deflection_frequency_index": 0.73,
    "boundary_directive": "Effort asymmetry indicates holding pattern. Recommendation: Establish explicit communication cadence or discontinue.",
    "confidence": 0.81
}

async def mock_red_flags(messages_text: str) -> dict:
    return MOCK_RED_FLAGS

async def mock_post_mortem(metrics: dict) -> dict:
    return MOCK_POST_MORTEM
