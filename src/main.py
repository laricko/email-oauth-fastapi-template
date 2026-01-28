from fastapi import FastAPI

from api.auth import router

app = FastAPI(title="Mailzen backend")
app.include_router(router)
