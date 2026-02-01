from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api.auth import router as auth_router
from api.emails import router as emails_router
from errors import ClientError

app = FastAPI(title="Mailzen backend")
app.include_router(auth_router)
app.include_router(emails_router)


@app.exception_handler(ClientError)
async def client_error_handler(request, exc: ClientError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )
