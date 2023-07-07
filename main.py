from services.api_service import Server
from organizzesync import OrganizzeSync
from services.organizze_service import Organizze_Service
from report import Report
from helpers.logger_helper import Logger
import threading


def start_report(organizze: OrganizzeSync, organizze_service: Organizze_Service):
    report = Report(organizze, organizze_service)
    report.schedule()
    report.run_scheduled()


def start_server(organizze: OrganizzeSync):
    Server(organizze)


def start():
    logger = Logger()
    organizze_service = Organizze_Service(logger)
    organizze = OrganizzeSync(organizze_service, logger)

    report_thread = threading.Thread(target=start_report(organizze, organizze_service))
    server_thread = threading.Thread(target=start_server(organizze))

    report_thread.start()
    server_thread.start()

    report_thread.join()
    server_thread.join()


if __name__ == "__main__":
    start()
