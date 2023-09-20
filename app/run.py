import uvicorn

from app.main import app

if __name__ == "__run__":
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)