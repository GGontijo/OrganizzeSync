from helpers.config_helper import Config
from OrganizeSync import Organizze_Service
import requests

class Telegram_Service:

    def __init__(self):
        _config = Config()
        _config_data = _config.get_config("telegram")
        _token = _config_data["token"]
        _url = _config_data["url"]
        self.group_chat_id = _config_data["group_chat_id"]
        self.url_base = f'{_url}{_token}/'

    def send_basic_response(self, message: str):
        link_requisicao = f'{self.url_base}sendMessage?chat_id={self.group_chat_id}&text={message}'
        requests.get(link_requisicao)

    def send_import_error(self, lat: str, long: str, description: str, reason: str = None):
        location_map = f'http://www.google.com/maps/place/{lat},{long}'
        message = f'Erro ao importar a notificação {description}: {location_map} - Motivo: {reason}'
        link_requisicao = f'{self.url_base}sendMessage?chat_id={self.group_chat_id}&text={message}'
        requests.get(link_requisicao)

    