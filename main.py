from services.api_service import Server
from organizzesync import OrganizzeSync
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
    #organizze_service = Organizze_Service(logger)
    #organizze = OrganizzeSync(organizze_service, logger)5
    #report = Report(organizze, organizze_service)
    #report.monthly_expenses()
    a = B3_Service(logger, "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IlZ4Q2VKMmtweTdwN1EzeEJTQ3cyREt3Y291T3RXUm82SXF3SjJXLUF3UWciLCJ0eXAiOiJKV1QifQ.eyJvaWQiOiIxNDkxMjAzNy1lMzFiLTQzNDgtOTg2Yi01NDY3ZjdlZGUwNDUiLCJ0aWQiOiJhYTVhYzcwNS04NzNiLTRhZmMtYTI5ZC1mMGFkYjg5Y2NmNWMiLCJub25jZSI6InJCVE41a1F1d2hGWTA0VW1IWHlXdHZMVkNqQUtBRDZkYUFzejhqcXQiLCJzY3AiOiJSZWFkLkFsbCIsImF6cCI6IjcxMWIwNjc3LTM2NzItNDQ2NC1iMTgzLTc2NzM0ZmIyMTkwNyIsInZlciI6IjEuMCIsImlhdCI6MTY4ODg0NjY4MiwiYXVkIjoiODAyMzQ4ZTYtNmYyMy00ZDk5LTk0NDUtNDU4MzY4NjFjZGY0IiwiZXhwIjoxNjg4ODUwMjgyLCJpc3MiOiJodHRwczovL2IzaW52ZXN0aWRvci5iMmNsb2dpbi5jb20vYWE1YWM3MDUtODczYi00YWZjLWEyOWQtZjBhZGI4OWNjZjVjL3YyLjAvIiwibmJmIjoxNjg4ODQ2NjgyfQ.lCZXi4XFzFSXT0jM56ZXqhI4v1SDxGJA9ygbyj_h0mQqRfuuRV5yNbrIzpoXixgTtwlrO4AkaOVd1VkisDtDA061NYrH8P47hnlnTSSmNM08lQxVK1fn3Zr0guk2OElNXHLiDYxnV1XDzODgCgeOuvyKaHT9BvP6Zn5IBROWaXZzNpQG5i8m3EpL4sH9JKahc6CFDdZtPjV5otLn3zetboXZXmpzjNGjdSa4Jwlr3PVZdE5gglxUZhBrtquo0-Iu37TwtvuTLj1eYgdrxeQnZRg5FWoChLgovmcJguy4iowi-tMoXRsBUu_6tAqIrlDhy-hJEK6uQPaTGgIXds-1yQ")
    b = a.get_movimentacoes('2023-01-01', '2023-07-07')
    print(b)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    #dev()

