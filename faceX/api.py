from fastapi import FastAPI, status, HTTPException
from routers import posts, users, auth, votes, comments
from utils.database_connect import connection
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "https://www.google.com",
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    conn = connection()
except Exception:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to reach Database")

@app.get("/", status_code=status.HTTP_200_OK)
def home():
    return {"Success": "This is a Home Page!"}

@app.get("/contact", status_code=status.HTTP_200_OK)
def contact():
    return {"Success": "This is a Contact Page!"}

@app.get("/support", status_code=status.HTTP_200_OK)
def support():
    return {"Success": "This is a Support Page!"}

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(votes.router)
app.include_router(comments.router)