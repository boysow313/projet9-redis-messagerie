import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))# pour importer le dossier app correctement 

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


def afficher_menu():
    print("   SYSTEME DE MESSAGERIE - Files d'attente Redis")
    print("  1. Envoyer un message")
    print("  2. Lire mes messages (sans supprimer)")
    print("  3. Lire le message suivant (supprime de la file)")
    print("  4. Vider ma file de messages")
    print("  5. Definir un TTL sur ma file")
    print("  6. Voir le TTL de ma file")
    print("  7. Lister les utilisateurs actifs")
    print("  8. Statistiques globales")
    print("  9. Changer d'utilisateur")
    print("  0. Quitter")

def main():
    print("  Bienvenue dans le systeme de messagerie Redis !")

    utilisateur = input("\nEntrez votre nom d'utilisateur : ").strip()
    if not utilisateur:
        print("Nom d'utilisateur invalide.")
        return

    print(f"\nConnecte en tant que : {utilisateur}")
    nb = compter_messages(utilisateur)
    if nb > 0:
        print(f"Vous avez {nb} messages en attente !")

    while True:
        afficher_menu()
        choix = input(f"\n[{utilisateur}] Votre choix : ").strip()

        if choix == "1":
            destinataire = input("  Destinataire : ").strip()
            contenu = input("  Message : ").strip()
            if destinataire and contenu:
                msg_id = envoyer_message(utilisateur, destinataire, contenu)
                print(f"  Message envoye ! (ID: {msg_id})")
            else:
                print("  Destinataire ou message invalide.")

        elif choix == "2":
            messages = lire_messages(utilisateur, supprimer=False)
            if not messages:
                print("  Aucun message en attente.")
            else:
                print(f"\n  --- {len(messages)} message(s) ---")
                for i, msg in enumerate(messages, 1):
                    print(f"  [{i}] De: {msg['expediteur']} | {msg['date']}")
                    print(f"      {msg['contenu']}")
                    print()

        elif choix == "3":
            msg = lire_message_suivant(utilisateur)
            if msg is None:
                print("  Aucun message en attente.")
            else:
                print(f"\n  De: {msg['expediteur']} | {msg['date']}")
                print(f"  Message: {msg['contenu']}")
                print(f"  (Message retire de la file)")

        elif choix == "4":
            confirm = input("  Confirmer la suppression ? (oui/non) : ").strip()
            if confirm.lower() == "oui":
                count = vider_file(utilisateur)
                print(f"  File videe ({count} messages supprimes).")
            else:
                print("  Annule.")

        elif choix == "5":
            try:
                duree = int(input("  Duree en secondes : ").strip())
                definir_expiration(utilisateur, duree)
                print(f"  TTL defini : {duree} secondes")
            except ValueError:
                print("  Duree invalide.")

        elif choix == "6":
            ttl = obtenir_ttl(utilisateur)
            if ttl == -2:
                print("  Aucune file existante.")
            elif ttl == -1:
                print("  Pas de TTL defini (file permanente).")
            else:
                print(f"  TTL restant : {ttl} secondes")

        elif choix == "7":
            users = lister_utilisateurs()
            if not users:
                print("  Aucun utilisateur actif.")
            else:
                print(f"  Utilisateurs actifs ({len(users)}) :")
                for u in users:
                    nb = compter_messages(u)
                    print(f"    - {u} ({nb} messages)")

        elif choix == "8":
            stats = obtenir_statistiques()
            print(f"\n   Statistiques globales :")
            print(f"  Total messages envoyes : {stats['total_messages_envoyes']}")
            print(f"  Utilisateurs actifs    : {stats['utilisateurs_actifs']}")
            print(f"  Files actives :")
            for user, info in stats["files_actives"].items():
                ttl_str = f"{info['ttl']}s" if info['ttl'] > 0 else "permanent"
                print(f"    - {user}: {info['messages_en_attente']} msg ({ttl_str})")

        elif choix == "9":
            utilisateur = input("\nNouveau nom d'utilisateur : ").strip()
            if not utilisateur:
                print("Nom invalide, conserve l'ancien.")
            else:
                nb = compter_messages(utilisateur)
                print(f"Connecte en tant que : {utilisateur}")
                if nb > 0:
                    print(f"Vous avez {nb} message(s) en attente !")

        elif choix == "0":
            print("\nAu revoir !")
            break

        else:
            print("  Choix invalide.")


if __name__ == "__main__":
    main()
