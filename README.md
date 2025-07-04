# Campus Life API

API FastAPI pour gérer la vie dans un campus d'étudiants - événements et système de mentorat.

## Fonctionnalités

- **Gestion des utilisateurs** : Inscription, authentification, profils
- **Gestion des événements** : Création, modification, suppression d'événements campus
- **Système de mentorat** : Relations entre mentors et étudiants sponsorisés

## Structure du projet

```
backend/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py            # Modèle User
│   │   ├── event.py           # Modèle Event
│   │   ├── mentoring.py       # Modèle Mentoring
│   │   ├── classroom.py       # Modèle Classroom
│   │   └── presence.py        # Modèle Presence
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py            # Routes d'authentification
│   │   ├── users.py           # Routes pour les utilisateurs
│   │   ├── events.py          # Routes pour les événements
│   │   ├── mentoring.py       # Routes pour le mentorat
│   │   ├── classrooms.py      # Routes pour les salles de classe
│   │   └── presences.py       # Routes pour les présences
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.py            # Utilitaires d'authentification
│   │   └── helpers.py         # Utilitaires génériques
│   ├── __init__.py
│   ├── database.py            # Configuration PostgreSQL
│   └── schemas.py             # Schémas Pydantic
├── main.py                    # Application FastAPI principale
├── requirements.txt           # Dépendances Python
├── env.example               # Variables d'environnement
└── README.md
```

## Installation

1. **Cloner le projet**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration de l'environnement**
   ```bash
   cp env.example .env
   # Modifier .env selon votre configuration PostgreSQL
   ```

5. **Créer la base de données (si nécessaire)**
   ```bash
   # Se connecter à PostgreSQL
   psql postgres
   
   # Créer la base de données
   CREATE DATABASE campus_db;
   
   # Quitter
   \q
   ```

6. **Créer les tables**
   ```bash
   python -c "from app.database import engine, Base; from app.models import User, Event, Mentoring, Classroom, Presence; Base.metadata.create_all(bind=engine)"
   ```

### Option 2 : Installation avec Docker (Recommandée)

1. **Cloner le projet**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Déployer avec Docker Compose**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

3. **Vérifier le déploiement**
   ```bash
   docker-compose ps
   curl http://localhost:8000/
   ```

## Lancement

```bash
# Lancer le serveur de développement
uvicorn main:app --reload

# Ou directement avec Python
python main.py
```

L'API sera disponible sur `http://localhost:8000`

## Documentation API

- **Documentation interactive** : http://localhost:8000/docs
- **Documentation alternative** : http://localhost:8000/redoc

## Endpoints disponibles

### Authentification (`/auth`)
- `POST /auth/register` - S'inscrire
- `POST /auth/login` - Se connecter (form-data)
- `POST /auth/login-json` - Se connecter (JSON)
- `GET /auth/me` - Obtenir ses informations
- `PUT /auth/me` - Modifier ses informations

### Utilisateurs (`/users`)
- `POST /users/` - Créer un utilisateur
- `GET /users/` - Lister tous les utilisateurs
- `GET /users/{user_id}` - Récupérer un utilisateur
- `PUT /users/{user_id}` - Modifier un utilisateur
- `DELETE /users/{user_id}` - Supprimer un utilisateur

### Événements (`/events`)
- `POST /events/` - Créer un événement
- `GET /events/` - Lister tous les événements
- `GET /events/{event_id}` - Récupérer un événement
- `GET /events/upcoming/` - Événements à venir
- `PUT /events/{event_id}` - Modifier un événement
- `DELETE /events/{event_id}` - Supprimer un événement

### Mentorat (`/mentoring`)
- `POST /mentoring/` - Créer une relation de mentorat
- `GET /mentoring/` - Lister toutes les relations
- `GET /mentoring/{mentoring_id}` - Récupérer une relation
- `GET /mentoring/user/{user_id}/mentoring` - Étudiants mentés par un utilisateur
- `GET /mentoring/user/{user_id}/sponsored` - Mentors d'un utilisateur
- `PUT /mentoring/{mentoring_id}` - Modifier une relation
- `DELETE /mentoring/{mentoring_id}` - Supprimer une relation

### Salles de classe (`/classrooms`)
- `POST /classrooms/` - Créer une salle de classe
- `GET /classrooms/` - Lister toutes les salles
- `GET /classrooms/{classroom_id}` - Récupérer une salle
- `GET /classrooms/{classroom_id}/with-presences` - Salle avec présences
- `PUT /classrooms/{classroom_id}` - Modifier une salle
- `DELETE /classrooms/{classroom_id}` - Supprimer une salle

### Présences (`/presences`)
- `POST /presences/` - Enregistrer une présence
- `GET /presences/` - Lister les présences (avec filtres)
- `GET /presences/{presence_id}` - Récupérer une présence
- `GET /presences/classroom/{classroom_id}/occupancy` - Occupation d'une salle
- `GET /presences/user/{user_id}/history` - Historique d'un utilisateur
- `PUT /presences/{presence_id}` - Modifier une présence
- `DELETE /presences/{presence_id}` - Supprimer une présence

### Analyse d'Affluence (`/presences/analytics`)
- `GET /presences/analytics/overview` - Vue d'ensemble de l'affluence
- `GET /presences/analytics/classroom/{classroom_id}/trends` - Tendances par salle
- `GET /presences/analytics/real-time` - Affluence en temps réel
- `GET /presences/analytics/peak-times` - Heures de pointe

### Participations aux Événements (`/event-participations`)
- `POST /event-participations/` - Participer à un événement
- `GET /event-participations/` - Lister les participations (avec filtres)
- `GET /event-participations/event/{event_id}/participants` - Participants d'un événement
- `GET /event-participations/event/{event_id}/participant-count` - Nombre de participants
- `GET /event-participations/user/{user_id}/events` - Événements d'un utilisateur
- `PUT /event-participations/{participation_id}` - Modifier une participation
- `DELETE /event-participations/{participation_id}` - Supprimer une participation
- `POST /event-participations/{event_id}/cancel` - Annuler sa participation

## Modèles de données

### User
- `id` (INT, PK)
- `name` (VARCHAR)
- `email` (VARCHAR, unique)
- `password` (VARCHAR, hashé)
- `level` (VARCHAR)

### Event
- `id` (INT, PK)
- `title` (VARCHAR)
- `description` (TEXT)
- `category` (VARCHAR)
- `attendance` (VARCHAR)
- `place` (VARCHAR)
- `image_url` (VARCHAR, nullable) - URL de l'image de l'événement
- `date_start` (DATE)
- `date_end` (DATE)

### Mentoring
- `id` (INT, PK)
- `mentor_id` (INT, FK vers User)
- `sponsored_id` (INT, FK vers User)
- `subject` (VARCHAR)
- `description` (TEXT)

### Classroom
- `id` (INT, PK)
- `name` (VARCHAR)
- `capacity` (INT)

### Presence
- `id` (INT, PK)
- `presence` (BOOLEAN)
- `classroom_id` (INT, FK vers Classroom)
- `user_id` (INT, FK vers User)
- `timestamp` (DATETIME)

### EventParticipation
- `id` (INT, PK)
- `event_id` (INT, FK vers Event)
- `user_id` (INT, FK vers User)
- `is_attending` (BOOLEAN, default: True)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

## Exemples d'utilisation

### S'inscrire
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "level": "étudiant"
  }'
```

### Se connecter
```bash
curl -X POST "http://localhost:8000/auth/login-json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

### Obtenir ses informations (avec token)
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Créer un utilisateur
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "level": "étudiant"
  }'
```

### Créer un événement
```bash
curl -X POST "http://localhost:8000/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Conférence IA",
    "description": "Introduction à l\'intelligence artificielle",
    "category": "conférence",
    "attendance": "50",
    "place": "Amphithéâtre A",
    "image_url": "https://example.com/images/ai-conference.jpg",
    "date_start": "2024-01-15",
    "date_end": "2024-01-15"
  }'
```

### Créer une relation de mentorat
```bash
curl -X POST "http://localhost:8000/mentoring/" \
  -H "Content-Type: application/json" \
  -d '{
    "mentor_id": 1,
    "sponsored_id": 2,
    "subject": "Mathématiques",
    "description": "Aide en calcul différentiel"
  }'
```

### Créer une salle de classe
```bash
curl -X POST "http://localhost:8000/classrooms/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Amphithéâtre A",
    "capacity": 150
  }'
```

### Enregistrer une présence
```bash
curl -X POST "http://localhost:8000/presences/" \
  -H "Content-Type: application/json" \
  -d '{
    "presence": true,
    "classroom_id": 1,
    "email": "john@example.com"
  }'
```

### Vérifier l'occupation d'une salle
```bash
curl -X GET "http://localhost:8000/presences/classroom/1/occupancy"
```

### Analyser l'affluence globale
```bash
# Vue d'ensemble sur les 7 derniers jours
curl -X GET "http://localhost:8000/presences/analytics/overview"

# Vue d'ensemble sur une période spécifique
curl -X GET "http://localhost:8000/presences/analytics/overview?start_date=2024-01-01&end_date=2024-01-31"
```

### Tendances d'affluence par salle
```bash
# Tendances sur 30 jours pour la salle 1
curl -X GET "http://localhost:8000/presences/analytics/classroom/1/trends"

# Tendances sur 7 jours
curl -X GET "http://localhost:8000/presences/analytics/classroom/1/trends?days=7"
```

### Affluence en temps réel
```bash
# Occupation actuelle de toutes les salles
curl -X GET "http://localhost:8000/presences/analytics/real-time"
```

### Heures de pointe
```bash
# Heures de pointe globales sur 30 jours
curl -X GET "http://localhost:8000/presences/analytics/peak-times"

# Heures de pointe pour une salle spécifique
curl -X GET "http://localhost:8000/presences/analytics/peak-times?classroom_id=1"

# Heures de pointe sur 7 jours
curl -X GET "http://localhost:8000/presences/analytics/peak-times?days=7"
```

### Participer à un événement
```bash
curl -X POST "http://localhost:8000/event-participations/" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "email": "john@example.com"
  }'
```

### Voir les participants d'un événement
```bash
curl -X GET "http://localhost:8000/event-participations/event/1/participants"
```

### Obtenir le nombre de participants
```bash
curl -X GET "http://localhost:8000/event-participations/event/1/participant-count"
```

### Voir les événements d'un utilisateur
```bash
curl -X GET "http://localhost:8000/event-participations/user/1/events"
```

### Annuler sa participation
```bash
curl -X POST "http://localhost:8000/event-participations/1/cancel?email=john@example.com"

## Base de données

L'application utilise PostgreSQL comme base de données principale.

### Configuration par défaut :
- **Host** : localhost
- **Port** : 5432
- **Database** : campus_db
- **Username** : postgres
- **Password** : password

### Commandes utiles :

```bash
# Créer les tables
python -c "from app.database import engine, Base; from app.models import User, Event, Mentoring, Classroom, Presence; Base.metadata.create_all(bind=engine)"

# Se connecter à PostgreSQL
psql postgres://postgres:password@localhost:5432/campus_db

# Lancer l'API
uvicorn main:app --reload
```

## Docker

### Commandes Docker utiles :

```bash
# Construire l'image
docker-compose build

# Démarrer les services
docker-compose up -d

# Voir les logs
docker-compose logs -f api
docker-compose logs -f postgres

# Arrêter les services
docker-compose down

# Redémarrer l'API
docker-compose restart api

# Voir l'état des services
docker-compose ps

# Nettoyer (supprimer volumes)
docker-compose down -v
```

## Développement

- L'application utilise SQLAlchemy pour l'ORM
- Pydantic pour la validation des données
- FastAPI pour l'API REST
- Hachage des mots de passe avec bcrypt