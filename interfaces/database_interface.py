from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    '''Interface de alto nível que faz a integração com o banco de dados SQLite'''

    @abstractmethod
    def select(self, query: str):
        pass

    @abstractmethod
    def update(self, query: str):
        pass

    @abstractmethod
    def delete(self, query: str):
        pass

    @abstractmethod
    def insert(self, query: str):
        pass