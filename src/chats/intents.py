from typing_extensions import TypedDict
from pydantic import BaseModel, Field


class IntentDefinition(TypedDict):
    description: str



class IntentStructure(BaseModel):
    intent: str = Field(
        description=(
            "The selected intent label. Must be exactly one of the available intent labels "
            "provided in the prompt, such as fallback, plain_llm, rag, or appointments."
        )
    )

    context: str = Field(
        description=(
            "Relevant context extracted from the chat history and latest message that the next "
            "agent needs. Include facts, preferences, dates, services mentioned, appointment details, "
            "or prior user constraints. If there is no relevant context, return an empty string."
        )
    )

    instructions: str = Field(
        description=(
            "Concise instructions for the next agent about how to handle the request. "
            "Do not answer the user here. Do not include internal reasoning. "
            "Only include guidance useful for the next step."
        )
    )


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



def build_intent_classifier_prompt(intent_options: str) -> str:
    return f"""
    You are an intent router for a customer messaging agent.

    Classify the user's latest message using the available intents and the chat history.

    Available intents:
    {intent_options}

    Return a structured response with:
    - intent: exactly one available intent label.
    - context: relevant facts from the latest message and chat history that the next agent needs.
    - instructions: concise guidance for the next agent about how to handle the request.

    Rules:
    - Choose only one of the available intent labels.
    - Use chat history only to resolve references, follow-ups, missing context, and user preferences.
    - Do not choose an intent that is not listed.
    - Do not answer the user.
    - Do not include private reasoning.
    - Do not mention routing, classification, tools, agents, or workflows to the user.
    - Keep context factual and grounded in the conversation.
    - Keep instructions short and actionable.
    - If the message is unclear, choose fallback and explain what needs clarification in instructions.
    """
