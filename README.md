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
│   │   └── mentor.py          # Modèle Mentor
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── users.py           # Routes pour les utilisateurs
│   │   ├── events.py          # Routes pour les événements
│   │   └── mentors.py         # Routes pour le mentorat
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
   python -c "from app.database import engine, Base; from app.models import User, Event, Mentor; Base.metadata.create_all(bind=engine)"
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

### Mentorat (`/mentors`)
- `POST /mentors/` - Créer une relation de mentorat
- `GET /mentors/` - Lister toutes les relations
- `GET /mentors/{mentor_id}` - Récupérer une relation
- `GET /mentors/user/{user_id}/mentoring` - Étudiants mentés par un utilisateur
- `GET /mentors/user/{user_id}/sponsored` - Mentors d'un utilisateur
- `PUT /mentors/{mentor_id}` - Modifier une relation
- `DELETE /mentors/{mentor_id}` - Supprimer une relation

## Modèles de données

### User
- `id` (INT, PK)
- `name` (VARCHAR)
- `email` (VARCHAR, unique)
- `password` (VARCHAR, hashé)
- `level` (VARCHAR)

### Event
- `id` (INT, PK)
- `titre` (VARCHAR)
- `desc` (TEXT)
- `cat` (VARCHAR)
- `attendance` (VARCHAR)
- `lieu` (VARCHAR)
- `datedebut` (DATE)
- `datefin` (DATE)

### Mentor
- `id` (INT, PK)
- `mentor_id` (INT, FK vers User)
- `sponsored_id` (INT, FK vers User)
- `subject` (VARCHAR)
- `description` (TEXT)

## Exemples d'utilisation

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
    "titre": "Conférence IA",
    "desc": "Introduction à l\'intelligence artificielle",
    "cat": "conférence",
    "attendance": "50",
    "lieu": "Amphithéâtre A",
    "datedebut": "2024-01-15",
    "datefin": "2024-01-15"
  }'
```

### Créer une relation de mentorat
```bash
curl -X POST "http://localhost:8000/mentors/" \
  -H "Content-Type: application/json" \
  -d '{
    "mentor_id": 1,
    "sponsored_id": 2,
    "subject": "Mathématiques",
    "description": "Aide en calcul différentiel"
  }'
```

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
python -c "from app.database import engine, Base; from app.models import User, Event, Mentor; Base.metadata.create_all(bind=engine)"

# Se connecter à PostgreSQL
psql postgres://postgres:password@localhost:5432/campus_db

# Lancer l'API
uvicorn main:app --reload
```

## Développement

- L'application utilise SQLAlchemy pour l'ORM
- Pydantic pour la validation des données
- FastAPI pour l'API REST
- Hachage des mots de passe avec bcrypt