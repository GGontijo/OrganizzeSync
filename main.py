from OrgannizeSync import Organizze_Service
from services.api_service import Server
import asyncio


async def start():
    _organizze_instance = Organizze_Service()
    loop = asyncio.get_event_loop(
        Server.run_server()
    )