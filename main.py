from services.api_service import Server
from OrganizeSync import OrganizzeSync
from services.organizze_service import Organizze_Service
from Report import Report
from helpers.logger_helper import Logger


def start():
    logger = Logger()
    organizze_service = Organizze_Service(logger)
    organizze = OrganizzeSync(organizze_service, logger)
    #Report(organizze, organizze_service).daily()
    Server(organizze)

start()