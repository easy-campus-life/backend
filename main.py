from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import User, Event, Mentoring, Classroom, Presence, EventParticipation
from app.routes import users, events, mentoring, auth, classrooms, presences, event_participations

# Créer les tables dans la base de données
from app.database import Base
Base.metadata.create_all(bind=engine)

# Créer l'application FastAPI
app = FastAPI(
    title="Campus Life API",
    description="API pour gérer la vie dans un campus d'étudiants - événements et mentorat",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(mentoring.router)
app.include_router(classrooms.router)
app.include_router(presences.router)
app.include_router(event_participations.router)

@app.get("/")
def read_root():
    """Page d'accueil de l'API"""
    return {
        "message": "Bienvenue sur l'API Campus Life",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth",
            "users": "/users",
            "events": "/events", 
            "mentoring": "/mentoring",
            "classrooms": "/classrooms",
            "presences": "/presences",
            "event-participations": "/event-participations",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    """Vérification de l'état de l'API"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 