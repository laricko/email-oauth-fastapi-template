from fastapi import FastAPI

from api.auth import router as auth_router
from api.emails import router as emails_router

app = FastAPI(title="Mailzen backend")
app.include_router(auth_router)
app.include_router(emails_router)