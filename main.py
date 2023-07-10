from services.api_service import Server
from organizzesync import OrganizzeSync
from investments import Investments
from services.organizze_service import Organizze_Service
from report import Report
from helpers.logger_helper import Logger
from services.b3_service import B3_Service
import asyncio


async def start_report(organizze: OrganizzeSync, organizze_service: Organizze_Service):
    report = Report(organizze, organizze_service)
    report.schedule()
    while True:
        report.run_scheduled()
        await asyncio.sleep(15)


def start_server(organizze: OrganizzeSync):
    server = Server(organizze)
    server.start()


async def main():
    logger = Logger()
    organizze_service = Organizze_Service(logger)
    organizze = OrganizzeSync(organizze_service, logger)

    report_task = asyncio.create_task(start_report(organizze, organizze_service))
    server_task = asyncio.get_event_loop().run_in_executor(None, start_server, organizze)

    await asyncio.gather(report_task, server_task)



def dev():
    logger = Logger()
    organizze_service = Organizze_Service(logger)
    organizze = OrganizzeSync(organizze_service, logger)
    #report = Report(organizze, organizze_service)
    #report.monthly_expenses()
    a = Investments(logger, organizze)
    b = a.sync_renda_fixa(1000)
    print(b)

if __name__ == "__main__":
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(main())
    dev()

