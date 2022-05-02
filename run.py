from flightmapper_back import app
import uvicorn
import os

host = os.getenv("HOST", "127.0.0.1")
port = os.getenv("PORT", 5000)

if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port, log_level="info")
