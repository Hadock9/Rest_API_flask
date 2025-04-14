import uvicorn
from . import app

if __name__ == "__main__":
    uvicorn.run("library_api.run:app", host="0.0.0.0", port=5000, reload=True)
