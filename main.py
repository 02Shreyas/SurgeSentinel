from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(title="SurgeSentinel API")

# (Optional but useful) allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # later you can restrict this to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple health-check route
@app.get("/")
def read_root():
    return {"message": "SurgeSentinel backend is running 🎯"}
