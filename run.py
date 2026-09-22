import os

import uvicorn
from app.main import app
from app.persistence.repository import initialize_database

initialize_database()

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8000")),
        reload=False,
        access_log=False,
    )
