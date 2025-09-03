import uvicorn
from fastapi import FastAPI
from h11 import Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from src.api.routers.auth_router import router as auth
from src.api.routers.resumes_router import router as resume
app = FastAPI()


app.mount("/static", StaticFiles(directory="frontend"))

app.include_router(auth)
app.include_router(resume)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




if __name__ == "__main__":
    uvicorn.run(app)