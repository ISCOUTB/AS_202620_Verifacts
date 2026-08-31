import uvicorn
from app.main import app
from app.persistence.repository import initialize_database

initialize_database()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)
