from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api.v1 import auth, graph, jobs, match, report, students, career_paths
from app.api.v1 import jobs
from app.api.v1 import planning

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Career Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(students.router, prefix="/api/v1/students", tags=["students"])
app.include_router(match.router, prefix="/api/v1/match", tags=["match"])
app.include_router(report.router, prefix="/api/v1/report", tags=["report"])
app.include_router(graph.router, prefix="/api/v1/graph", tags=["graph"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(career_paths.router, prefix="/api/v1/career-paths", tags=["career-paths"])
app.include_router(planning.router, prefix="/api/v1/planning", tags=["planning"])

@app.get("/")
def root():
    return {"message": "Career Agent API is running"}