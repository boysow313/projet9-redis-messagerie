# Projet 9 — Système de gestion de files d'attente pour une application de messagerie

Système de messagerie instantanée utilisant Redis pour gérer les files d'attente de messages entre utilisateurs. Chaque utilisateur possède une file de messages (liste Redis) qu'il peut consulter, vider ou enrichir.

## Technologies

- **Redis 7** (via Docker) — stockage des files de messages
- **Python 3** — logique applicative
- **Docker Compose** — déploiement de Redis

## Architecture

```
projet9-redis-messagerie/
├── app/
│   ├── __init__.py
│   ├── config.py           # Configuration de connexion Redis
│   ├── messagerie.py       # Fonctions de gestion des files de messages
│   ├── main.py             # Interface console interactive
│   └── simulation.py         # Simulation automatique d'échanges
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Prérequis

- Docker et Docker Compose
- Python 3.10+

## Installation et lancement

### 1. Démarrer Redis

```bash
docker compose up -d
docker exec -it redis-messagerie redis-cli ping
# Réponse attendue : PONG
```

### 2. Installer les dépendances Python

```bash
python3 -m venv venv
source venv/bin/activate.fish   # ou source venv/bin/activate (bash)
pip install -r requirements.txt
```

### 3. Lancer l'application interactive

```bash
python3 -m app.main
```

### 4. Lancer le simulateur

```bash
python3 -m app.simulate
```

Le simulateur permet de :
1. Envoyer des messages aléatoires entre utilisateurs
2. Lire les messages de chaque utilisateur
3. Démontrer le comportement FIFO (LPUSH/RPOP)
4. Démontrer l'expiration TTL
5. Mesurer les performances (1000 messages)
6. Afficher les statistiques globales

## Structures Redis utilisées

| Clé | Type | Usage |
|-----|------|-------|
| `queue:<utilisateur>` | Liste | File de messages (LPUSH/RPOP = FIFO) |
| `stats:total_messages` | String | Compteur global |
| `stats:messages_envoyes:<user>` | String | Compteur par expéditeur |
| `stats:messages_recus:<user>` | String | Compteur par destinataire |

## Commandes Redis utiles

```bash
docker exec -it redis-messagerie redis-cli
```

```redis
KEYS queue:*                -- Voir les files actives
LRANGE queue:mamadou 0 -1   -- Contenu de la file de Mamadou
LRANGE queue:ldji 0 -1      -- Contenu de la file de Ldji
LRANGE queue:momar 0 -1     -- Contenu de la file de Momar
LLEN queue:mamadou          -- Nombre de messages de Mamadou
LLEN queue:ldji             -- Nombre de messages de Ldji
LLEN queue:momar            -- Nombre de messages de Momar
TTL queue:test_ttl          -- TTL restant
INFO memory                 -- Utilisation mémoire
INFO keyspace               -- Info sur les bases
DBSIZE                      -- Nombre total de clés
MONITOR                     -- Commandes en temps réel
```

## Persistance

Redis est configuré avec la persistance AOF (`--appendonly yes`, `--appendfsync everysec`). Les données survivent aux redémarrages du conteneur.

## Arrêter le projet

```bash
docker compose down       # Arrêter Redis (données conservées)
docker compose down -v    # Arrêter et supprimer les données
```
