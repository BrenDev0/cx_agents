from httpx import AsyncClient
from .appointments import AppointmentsClient
from .conversations import GHLConversationsClient

class GoHighLevelClient:
    def __init__(
        self,
        http: AsyncClient,
        pit: str,
    ) -> None:
        self.http = http
        self.headers = {
            "Authorization": f"Bearer {pit}",
            "Version": "v3",
        }

        self.appointments = AppointmentsClient(
            http=self.http,
            headers=self.headers,
        )

        self.conversations = GHLConversationsClient(
            http=self.http,
            headers=self.headers,
        )