from typing import Protocol

class ConversationClient(Protocol):
    async def send_message(
        self,
        channel: str,
        contact_id: str,
        message: str
    ):
        ...
