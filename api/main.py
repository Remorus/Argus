from fastapi import FastAPI
from api.routes import router
import uvicorn
from config import API_HOST, API_PORT

app = FastAPI(title="Argus IoT API")

# Registramos el router
app.include_router(router)

# Arrancamos uvicorn 
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host = API_HOST,
        PORT = API_PORT,
        reload = True,
        log_level="info"
    )