from fastapi import FastAPI
from routes.organizze_route import organizze_router
import uvicorn

class Server():
    
    def __init__(self) -> None:
        self.api = FastAPI(title='OrganizzeSync', 
                           description='API de sincronização com o Organizze', 
                           version='1.0.0')
        self.api.include_router(organizze_router)
        uvicorn.run(self.api, port=6556, host='0.0.0.0')