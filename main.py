from fastapi import FastAPI
from backend.auth.controller import router as auth_router
from backend.firm.controller import router as firm_router
from backend.category.controller import router as category_router
from db.connection import Base, engine


app = FastAPI(title="B2B Backend API", version="0.1.0",openapi_url="/openapi.json", root_path="/api")

app.include_router(auth_router)
app.include_router(firm_router)
app.include_router(category_router)

Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Welcome to B2B Backend API"}
