from httpx import AsyncClient
from .appointments import AppointmentsClient
from .conversations import GHLConversationsClient

class GoHighLevelClient:
    def __init__(
        self,
        http: AsyncClient,
        pit: str,
        location_id: str
    ) -> None:
        self.http = http
        self.headers = {
            "Authorization": f"Bearer {pit}",
            "Version": "v3",
        }
        self._location_id = location_id

        self.appointments = AppointmentsClient(
            http=self.http,
            headers=self.headers,
            location_id=location_id
        )

        self.conversations = GHLConversationsClient(
            http=self.http,
            headers=self.headers,
            location_id=location_id
        )