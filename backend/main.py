from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router

app = FastAPI(
    title="AlgebraX API",
    description="Motor de cálculo avanzado de álgebra lineal",
    version="1.0.0"
)

# Configurar CORS para permitir requests desde el frontend (Vue 3)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción se debe restringir al dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "AlgebraX API funcionando correctamente"}
