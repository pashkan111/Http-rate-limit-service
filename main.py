from fastapi import FastAPI
import uvicorn
from db import init_db
from src.auth.routes import router


app = FastAPI()

@app.on_event('startup')
async def on_startup():
    await init_db()


app.include_router(router)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True, port=8089, host='0.0.0.0')