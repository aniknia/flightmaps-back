from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# TODO: Restrict origins

origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "http://localhost",
    "http://localhost:8080",
    "http://theflightmapper.com",
    "https://theflighmapper.com",
    "https://flightmapper-front.vercel.app",
    "https://flightmapper-back-production.up.railway.app",
    "https://api.theflightmapper.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from flightmapper_back import routes
