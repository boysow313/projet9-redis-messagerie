import time
from app.config import get_connection

r = get_connection()


def generer_id_message():
    """Genere un identifiant unique base sur le timestamp."""
    return f"msg_{int(time.time() * 1000)}"


def envoyer_message(expediteur, destinataire, contenu):
    """
    Envoie un message d'un utilisateur a un autre.
    Le message est ajoute en tete de la file du destinataire (LPUSH).
    """
    msg_id = generer_id_message()
    message = f"{msg_id}|{expediteur}|{int(time.time())}|{contenu}"

    cle_file = f"queue:{destinataire}"
    r.lpush(cle_file, message)

    r.incr(f"stats:messages_envoyes:{expediteur}")
    r.incr(f"stats:messages_recus:{destinataire}")
    r.incr("stats:total_messages")

    return msg_id


def lire_messages(utilisateur, supprimer=False):
    """
    Lit tous les messages de la file d'un utilisateur.
    Si supprimer=True, les messages sont retires (RPOP).
    Sinon, consultation sans suppression (LRANGE).
    """
    cle_file = f"queue:{utilisateur}"
    messages = []

    if supprimer:
        while True:
            msg = r.rpop(cle_file)
            if msg is None:
                break
            messages.append(_parser_message(msg))
    else:
        raw_messages = r.lrange(cle_file, 0, -1)
        for msg in raw_messages:
            messages.append(_parser_message(msg))

    return messages


def lire_message_suivant(utilisateur):
    """Lit et retire le message le plus ancien (FIFO via RPOP)."""
    cle_file = f"queue:{utilisateur}"
    msg = r.rpop(cle_file)
    if msg is None:
        return None
    return _parser_message(msg)


def compter_messages(utilisateur):
    """Retourne le nombre de messages en attente."""
    cle_file = f"queue:{utilisateur}"
    return r.llen(cle_file)


def vider_file(utilisateur):
    """Supprime tous les messages de la file."""
    cle_file = f"queue:{utilisateur}"
    count = r.llen(cle_file)
    r.delete(cle_file)
    return count


def definir_expiration(utilisateur, duree_secondes):
    """Definit un TTL sur la file de messages."""
    cle_file = f"queue:{utilisateur}"
    r.expire(cle_file, duree_secondes)
    return duree_secondes


def obtenir_ttl(utilisateur):
    """Retourne le TTL restant (-1 si pas de TTL, -2 si inexistante)."""
    cle_file = f"queue:{utilisateur}"
    return r.ttl(cle_file)


def lister_utilisateurs():
    """Liste tous les utilisateurs ayant une file active."""
    cles = r.keys("queue:*")
    return [cle.replace("queue:", "") for cle in cles]


def obtenir_statistiques():
    """Retourne les statistiques globales."""
    total = r.get("stats:total_messages") or "0"
    utilisateurs = lister_utilisateurs()

    stats = {
        "total_messages_envoyes": int(total),
        "utilisateurs_actifs": len(utilisateurs),
        "files_actives": {}
    }

    for user in utilisateurs:
        stats["files_actives"][user] = {
            "messages_en_attente": compter_messages(user),
            "ttl": obtenir_ttl(user)
        }

    return stats


def rechercher_messages(utilisateur, mot_cle):
    """Recherche les messages contenant un mot-cle."""
    cle_file = f"queue:{utilisateur}"
    raw_messages = r.lrange(cle_file, 0, -1)
    resultats = []

    for msg in raw_messages:
        parsed = _parser_message(msg)
        if mot_cle.lower() in parsed["contenu"].lower():
            resultats.append(parsed)

    return resultats


def _parser_message(raw):
    """Parse un message brut en dictionnaire."""
    parties = raw.split("|", 3)
    return {
        "id": parties[0],
        "expediteur": parties[1],
        "timestamp": int(parties[2]),
        "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(parties[2]))),
        "contenu": parties[3]
    }
