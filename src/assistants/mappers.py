from .models import Assistant
from .schemas import AssistantResponse, AssistantWebhookSecretResponse

def domain_to_public_schema(domain: Assistant) -> AssistantResponse:
    return AssistantResponse.model_validate(domain, from_attributes=True)


def domain_to_webhook_secret_schema(domain: Assistant, webhook_secret: str) -> AssistantWebhookSecretResponse:
    return AssistantWebhookSecretResponse(
        id=domain.id,
        name=domain.name,
        description=domain.description,
        webhook_id=domain.webhook_id,
        webhook_secret=webhook_secret,
        created_at=domain.created_at
    )