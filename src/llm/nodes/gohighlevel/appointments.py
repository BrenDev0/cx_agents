from httpx import AsyncClient
from .utils import generate_headers


BASE_URL = "https://services.leadconnectorhq.com"

async def check_for_existing_appointment_node(
    pit: str,
    contact_id: str
):
    endpoint = f"{BASE_URL}/contacts/{contact_id}/appointments"
    headers = generate_headers(pit=pit)

    try: 
        async with AsyncClient() as client:
            response = await client.get(
                url=endpoint,
                headers=headers
            )

    except Exception as e:
        pass

async def orchestrator_node():
    pass


async def gather_info_node(
    current_info: dict[str, str]
)-> list[str]:
    pass
    

async def get_slots_node(
    calendar_id: str, 
    pit: str, 
    client: AsyncClient,
    start_date: int,
    end_date: int
):
    endpoint = f"{BASE_URL}/calendars/{calendar_id}/free-slots"
    headers = generate_headers(pit=pit)

    query_params = [
        ("startDate", start_date),
        ("endDate", end_date),
        ("timeZone", "")
    ]

    try:
        async with AsyncClient() as client:
            response = await client.get(
                url=endpoint,
                headers=headers,
                params=query_params
            )

    
    except Exception as e:
        pass


async def check_availability_node():
    pass


async def book_appointment_node(
    client: AsyncClient,
    pit: str,
    calendar_id: str,
    location_id: str,
    contact_id: str,
    start_time: str
):
    endpoint = f"{BASE_URL}/calendars/events/appointments"
    headers = generate_headers(pit=pit)
    body = {
       "calendarId": calendar_id,
       "locationId": location_id,
       "contactId": contact_id,
       "startTime": start_time   
    }

    try:
        async with AsyncClient() as client:
            response = await client.post(
                url=endpoint,
                headers=headers,
                json=body
            )

    
    except Exception as e:
        pass


async def update_appointment_node():
    pass


async def cancel_appointment_node():
    pass


async def generate_reply_node():
    pass
