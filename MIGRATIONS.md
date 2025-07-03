# Guide des Migrations avec Alembic

Ce projet utilise **Alembic** pour gérer les migrations de base de données de manière professionnelle.

## 🚀 Démarrage Rapide

### 1. **Première initialisation**
```bash
# Générer la première migration (état actuel de la base)
alembic revision --autogenerate -m "Initial migration"

# Appliquer la migration
alembic upgrade head
```

### 2. **Démarrage normal**
```bash
# Utiliser le script de démarrage (applique automatiquement les migrations)
python start.py

# Ou manuellement
alembic upgrade head
uvicorn main:app --reload
```

## 📝 Workflow de Développement

### **Quand tu modifies un modèle :**

1. **Modifie ton modèle** dans `app/models/`
2. **Génère une migration** :
   ```bash
   alembic revision --autogenerate -m "Description du changement"
   ```
3. **Vérifie la migration** générée dans `alembic/versions/`
4. **Applique la migration** :
   ```bash
   alembic upgrade head
   ```

### **Exemples de migrations :**

```bash
# Ajouter un nouveau champ
alembic revision --autogenerate -m "Ajout champ image_url à Event"

# Créer une nouvelle table
alembic revision --autogenerate -m "Création table EventParticipation"

# Modifier un champ existant
alembic revision --autogenerate -m "Modification type champ attendance"
```

## 🔧 Commandes Utiles

### **Génération de migrations**
```bash
# Migration automatique (recommandé)
alembic revision --autogenerate -m "Description"

# Migration manuelle
alembic revision -m "Description"
```

### **Application de migrations**
```bash
# Appliquer toutes les migrations
alembic upgrade head

# Appliquer jusqu'à une version spécifique
alembic upgrade 0001

# Appliquer une migration
alembic upgrade +1
```

### **Annulation de migrations**
```bash
# Revenir à la version précédente
alembic downgrade -1

# Revenir au début
alembic downgrade base

# Revenir à une version spécifique
alembic downgrade 0001
```

### **Informations**
```bash
# Voir l'historique des migrations
alembic history

# Voir l'état actuel
alembic current

# Voir les migrations en attente
alembic show head
```

## 🌐 Déploiement sur Railway

### **Configuration automatique**
Le Dockerfile est configuré pour :
1. Appliquer automatiquement les migrations au démarrage
2. Lancer l'API une fois les migrations terminées

### **Variables d'environnement**
Assure-toi que `DATABASE_URL` est configurée sur Railway :
```
DATABASE_URL=postgresql://user:password@host:port/database
```

### **Déploiement manuel (si nécessaire)**
```bash
# Se connecter à Railway
railway login

# Appliquer les migrations
railway run alembic upgrade head

# Redémarrer l'application
railway up
```

## ⚠️ Bonnes Pratiques

### **Avant de commiter :**
1. ✅ Génère une migration pour tes changements
2. ✅ Teste la migration localement
3. ✅ Vérifie que la migration fonctionne en montée et descente
4. ✅ Commite la migration avec ton code

### **Structure des fichiers :**
```
alembic/
├── versions/           # Fichiers de migration
│   ├── 0001_initial.py
│   ├── 0002_add_image_url.py
│   └── ...
├── env.py             # Configuration de l'environnement
└── script.py.mako     # Template pour les migrations
alembic.ini           # Configuration principale
```

### **En cas de problème :**
```bash
# Voir les logs détaillés
alembic upgrade head --verbose

# Forcer une migration (attention !)
alembic stamp head

# Réinitialiser (perd toutes les données !)
alembic downgrade base
alembic upgrade head
```

## 🎯 Avantages

- **Versioning** : Chaque changement de base est versionné
- **Collaboration** : L'équipe peut partager l'évolution de la base
- **Rollback** : Possibilité de revenir en arrière
- **Automatisation** : Migrations appliquées automatiquement en production
- **Sécurité** : Pas de modification manuelle de la base en production

---

**💡 Conseil :** Utilise toujours `--autogenerate` sauf pour des migrations complexes nécessitant du code SQL personnalisé. 