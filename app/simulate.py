"""
Script de simulation d'echanges de messages entre utilisateurs.
Genere des conversations realistes pour tester le systeme.
"""

import sys
import os
import time
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.messagerie import (
    envoyer_message,
    lire_messages,
    lire_message_suivant,
    compter_messages,
    vider_file,
    definir_expiration,
    obtenir_ttl,
    lister_utilisateurs,
    obtenir_statistiques
)
from app.config import get_connection

UTILISATEURS = ["mamadou", "ldji", "momar"]

MESSAGES = [
    "Salut, comment ca va ?",
    "Tu es disponible pour une reunion demain ?",
    "J'ai termine le rapport, je te l'envoie.",
    "Merci pour ton aide !",
    "On se retrouve a la cafeteria a midi ?",
    "As-tu recu mon dernier mail ?",
    "Le projet avance bien, on est dans les temps.",
    "Peux-tu relire mon code avant le merge ?",
    "Bonne idee, je suis d'accord.",
    "N'oublie pas la deadline de vendredi.",
    "Je serai en retard ce matin.",
    "Le serveur est down, tu peux verifier ?",
    "Super travail sur la presentation !",
    "On fait un point a 15h ?",
    "J'ai un bug bizarre, tu peux m'aider ?",
    "Le client a valide la maquette.",
    "Je prends ma pause, a tout de suite.",
    "Tu as vu le nouveau framework ?",
    "La base de donnees est restauree.",
    "Reunion d'equipe reportee a jeudi.",
]


def simulation_envois(nb_messages=20):
    """Simule l'envoi de messages entre utilisateurs."""
    print("\n" + "=" * 60)
    print("  SIMULATION - Envoi de messages")
    print("=" * 60)

    for i in range(nb_messages):
        expediteur = random.choice(UTILISATEURS)
        destinataire = random.choice([u for u in UTILISATEURS if u != expediteur])
        contenu = random.choice(MESSAGES)

        msg_id = envoyer_message(expediteur, destinataire, contenu)
        print(f"  [{i+1:02d}] {expediteur} -> {destinataire} : {contenu[:40]}...")
        time.sleep(0.1)

    print(f"\n  {nb_messages} messages envoyes avec succes.")


def simulation_lecture():
    """Simule la lecture des messages par chaque utilisateur."""
    print("\n" + "=" * 60)
    print("  SIMULATION - Lecture des messages")
    print("=" * 60)

    for user in UTILISATEURS:
        nb = compter_messages(user)
        if nb > 0:
            print(f"\n  [{user}] a {nb} message(s) en attente :")
            messages = lire_messages(user, supprimer=False)
            for msg in messages[:3]:
                print(f"    De {msg['expediteur']}: {msg['contenu'][:50]}")
            if len(messages) > 3:
                print(f"    ... et {len(messages) - 3} autre(s)")
        else:
            print(f"\n  [{user}] aucun message.")


def simulation_fifo():
    """Demonstre le comportement FIFO de la file."""
    print("\n" + "=" * 60)
    print("  SIMULATION - Demonstration FIFO")
    print("=" * 60)

    vider_file("test_fifo")

    print("\n  Envoi de 5 messages dans l'ordre :")
    for i in range(1, 6):
        msg = f"Message numero {i}"
        envoyer_message("systeme", "test_fifo", msg)
        print(f"    LPUSH -> {msg}")
        time.sleep(0.05)

    print("\n  Lecture FIFO (RPOP) :")
    for i in range(5):
        msg = lire_message_suivant("test_fifo")
        if msg:
            print(f"    RPOP  <- {msg['contenu']}")

    print("\n  Les messages sont bien lus dans l'ordre d'envoi (FIFO).")


def simulation_ttl():
    """Demonstre l'expiration automatique des messages."""
    print("\n" + "=" * 60)
    print("  SIMULATION - Demonstration TTL (expiration)")
    print("=" * 60)

    vider_file("test_ttl")
    envoyer_message("systeme", "test_ttl", "Ce message expirera dans 10 secondes")
    definir_expiration("test_ttl", 10)

    print(f"\n  Message envoye a test_ttl avec TTL = 10s")
    print(f"  Messages en attente : {compter_messages('test_ttl')}")
    print(f"  TTL actuel : {obtenir_ttl('test_ttl')}s")

    print("\n  Attente de 5 secondes...")
    time.sleep(5)
    print(f"  TTL apres 5s : {obtenir_ttl('test_ttl')}s")
    print(f"  Messages en attente : {compter_messages('test_ttl')}")

    print("\n  Attente de 6 secondes supplementaires...")
    time.sleep(6)
    ttl = obtenir_ttl("test_ttl")
    nb = compter_messages("test_ttl")
    print(f"  TTL apres 11s : {ttl} (file expiree)")
    print(f"  Messages en attente : {nb}")

    if nb == 0:
        print("\n  La file a expire automatiquement ! Les messages ont ete supprimes par Redis.")


def simulation_performances():
    """Mesure les performances d'envoi et de lecture."""
    print("\n" + "=" * 60)
    print("  SIMULATION - Mesure des performances")
    print("=" * 60)

    vider_file("test_perf")
    NB_MESSAGES = 1000

    debut = time.time()
    for i in range(NB_MESSAGES):
        envoyer_message("perf_sender", "test_perf", f"Message de performance #{i}")
    duree_envoi = time.time() - debut

    print(f"\n  Envoi de {NB_MESSAGES} messages :")
    print(f"    Duree totale : {duree_envoi:.3f}s")
    print(f"    Debit        : {NB_MESSAGES / duree_envoi:.0f} msg/s")

    debut = time.time()
    messages = lire_messages("test_perf", supprimer=False)
    duree_lecture = time.time() - debut

    print(f"\n  Lecture de {len(messages)} messages (LRANGE) :")
    print(f"    Duree totale : {duree_lecture:.3f}s")
    print(f"    Debit        : {len(messages) / duree_lecture:.0f} msg/s")

    debut = time.time()
    count = 0
    while lire_message_suivant("test_perf"):
        count += 1
    duree_rpop = time.time() - debut

    print(f"\n  Lecture FIFO de {count} messages (RPOP) :")
    print(f"    Duree totale : {duree_rpop:.3f}s")
    print(f"    Debit        : {count / duree_rpop:.0f} msg/s")


def afficher_statistiques():
    """Affiche les statistiques globales."""
    print("\n" + "=" * 60)
    print("  STATISTIQUES GLOBALES")
    print("=" * 60)

    stats = obtenir_statistiques()
    print(f"\n  Total messages envoyes : {stats['total_messages_envoyes']}")
    print(f"  Utilisateurs actifs    : {stats['utilisateurs_actifs']}")

    if stats["files_actives"]:
        print(f"\n  Detail par utilisateur :")
        for user, info in stats["files_actives"].items():
            ttl_str = f"TTL={info['ttl']}s" if info['ttl'] > 0 else "permanent"
            print(f"    {user:12s} : {info['messages_en_attente']:3d} messages ({ttl_str})")


def reinitialiser():
    """Remet a zero toutes les files et statistiques."""
    conn = get_connection()
    conn.flushdb()
    print("\n  Base Redis reinitalisee (FLUSHDB).")


def main():
    print("\n" + "*" * 60)
    print("  SIMULATEUR DE MESSAGERIE REDIS")
    print("*" * 60)

    while True:
        print("\n  1. Envoyer des messages aleatoires (20 messages)")
        print("  2. Lire les messages de chaque utilisateur")
        print("  3. Demonstration FIFO")
        print("  4. Demonstration TTL (expiration)")
        print("  5. Mesure des performances (1000 messages)")
        print("  6. Statistiques globales")
        print("  7. Reinitialiser la base")
        print("  0. Quitter")

        choix = input("\n  Choix : ").strip()

        if choix == "1":
            simulation_envois()
        elif choix == "2":
            simulation_lecture()
        elif choix == "3":
            simulation_fifo()
        elif choix == "4":
            simulation_ttl()
        elif choix == "5":
            simulation_performances()
        elif choix == "6":
            afficher_statistiques()
        elif choix == "7":
            reinitialiser()
        elif choix == "0":
            print("\nFin de la simulation.")
            break
        else:
            print("  Choix invalide.")


if __name__ == "__main__":
    main()
