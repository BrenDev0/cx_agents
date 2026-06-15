from httpx import AsyncClient
from .appointments import AppointmentsClient
from .conversations import ConversationsClient

class GoHighLevelClient:
    def __int__(
        self,
        pit: str
    ):
        self.http = AsyncClient(
            base_url="https://services.leadconnectorhq.com",
            headers={
                "Authorization": f"Bearer {pit}",
                "Version": "v3",
            },
        )

        self.appointments = AppointmentsClient(http=self.http)
        self.conversations = ConversationsClient(http=self.http)