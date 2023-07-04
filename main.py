from services.api_service import Server
from OrganizeSync import OrganizzeSync
from Report import Report


def start():
    organizze = OrganizzeSync()
    Report(organizze).daily_general()
    #Server(organizze)

start()