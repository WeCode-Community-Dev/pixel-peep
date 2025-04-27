from fastapi import FastAPI
from fastapi import UploadFile,File
from fastapi.middleware.cors import CORSMiddleware
from services.image_compare import img_classification

origins = [
    "http://localhost:5173",
    "http://localhost:5174"
]
app = FastAPI(
    title="Pixel-Peep API",
    description="API for Detect duplicates, edited, and pirated versions of an image.",
    version="1.0.0",   
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/images")
async def uploadfiles(images:list[UploadFile ]=File(...)):

    groups=await img_classification(images)

    return {"message": "file uploaded",'groups':groups}






    