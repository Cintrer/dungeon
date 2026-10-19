# Dungeon as a Service — starter

Squelette fourni pour le projet bonus du module Python Backend & FastAPI.

## Installation (à faire une seule fois)

Prérequis : Python 3.10 ou plus récent (`python --version`).

```bash
# 1. Créer et activer un environnement virtuel
python -m venv .venv
# Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# macOS / Linux :
source .venv/bin/activate

# 2. Installer les dépendances
pip install -r requirements.txt
```

## Lancer l'API

Depuis la racine du projet (le dossier qui contient `app/`) :

```bash
fastapi dev app/main.py
```

Ouvrez ensuite http://127.0.0.1:8000/docs : la route `GET /health` doit répondre
`{"status": "ok", ...}`. Si c'est le cas, vous êtes prêts.

## Authentification et héros

Les routes `/heroes` nécessitent un jeton Bearer. Créez d'abord un compte avec
`POST /auth/register`, puis connectez-vous avec `POST /auth/login` en envoyant
un formulaire `username` / `password`. Le jeton renvoyé est valable deux heures.
Dans Swagger, cliquez sur **Authorize** pour l'utiliser ; chaque compte ne voit
et ne peut modifier que ses propres héros.

Pour conserver les jetons valides entre redémarrages, définissez une variable
d'environnement `SECRET_KEY` stable et confidentielle avant de lancer l'API.
Sans cette variable, une clé aléatoire de développement est générée au démarrage.

Les combats se font avec `POST /heroes/{id}/attack` et le repos avec
`POST /heroes/{id}/rest`. Le repos restaure les PV après une pause asynchrone
de trois secondes et est indisponible pendant un combat.

## Structure

```
app/
  main.py              point d'entrée, branchement des routers
  database.py          connexion SQLite (FOURNI)
  models/              tables SQLModel
  schemas/             schémas Pydantic d'entrée et de sortie
  domain/              classes métier (Heros, Guerrier, Mage, Voleur)
  services/            logique du jeu
    dungeon_map.py     lecture de la carte (FOURNI)
  routes/              routers FastAPI
data/dungeon_map.json  carte du donjon (FOURNI, ne pas modifier)
client/play.py         client terminal (BONUS)
```

## Réinitialiser la partie

Arrêtez le serveur et supprimez le fichier `dungeon.db` : il sera recréé au prochain lancement.
À faire aussi si vous ajoutez une colonne à une table (SQLite ne met pas à jour une table existante).

---

<!-- À COMPLÉTER PAR LE GROUPE AVANT LE RENDU -->

## Notre rendu

- **Membres du groupe :**
- **Lien du dépôt Git :**
- **Palier atteint :** (1, 2, 3 ou 4)
- **Bonus réalisés :**
- **Ce qui ne fonctionne pas / difficultés :**
