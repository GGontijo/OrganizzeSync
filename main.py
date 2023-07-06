from services.api_service import Server
from organizzesync import OrganizzeSync
from services.organizze_service import Organizze_Service
from report import Report
from helpers.logger_helper import Logger
import asyncio


async def run_report(report: Report):
    report.schedule()

    while True:
        report.run_scheduled()
        await asyncio.sleep(15)


async def run_api_server(api_server: Server):
    await api_server.start()


async def main():
    logger = Logger()
    organizze_service = Organizze_Service(logger)
    organizze = OrganizzeSync(organizze_service, logger)
    
    report = Report(organizze, organizze_service)
    api_server = Server(organizze)
    
    tasks = [run_report(report), run_api_server(api_server)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())