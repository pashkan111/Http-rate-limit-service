from fastapi import FastAPI
import uvicorn
from db import init_db


app = FastAPI()

@app.on_event('startup')
async def on_startup():
    await init_db()


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True, port=8000, host='0.0.0.0')