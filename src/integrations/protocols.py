from typing import Protocol

class ConversationClient(Protocol):
    async def send_message(
        self,
        type: str,
        contact_id: str,
        message: str
    ):
        ...
