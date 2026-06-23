from typing_extensions import TypedDict


class IntentDefinition(TypedDict):
    description: str

INTENT_REGISTRY: dict[str, IntentDefinition] = {
    "fallback": {
        "description": "The user's intent is unclear and more information is needed.",
    },
    "plain_llm": {
        "description": "The user is making casual conversation or asking for a general response that does not require tools or business knowledge.",
    },
    "rag": {
        "description": "The user is asking about business-specific services, products, policies, pricing, FAQs, or stored knowledge.",
    },
    "appointments": {
        "description": "The user wants to book, cancel, reschedule, or ask about an appointment.",
    },
}


def build_available_intents(
    *,
    has_appointments: bool,
    has_rag: bool
) -> dict[str, IntentDefinition]:
    intents = {
        "fallback": INTENT_REGISTRY["fallback"],
        "plain_llm": INTENT_REGISTRY["plain_llm"]
    }

    if has_rag:
        intents["rag"] = INTENT_REGISTRY["rag"]
    
    if has_appointments:
        intents["appointments"] = INTENT_REGISTRY["appointments"]

    return intents


def format_intents_for_prompt(intents: dict[str, IntentDefinition]) -> str:
    return "\n".join(
        f"- {label}: {intent['description']}"
        for label, intent in intents.items()
    )
