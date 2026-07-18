#!/bin/bash
# Script Redis - Demonstration des operations pour notre projet de messagerie
# Executer avec : docker exec -it redis-messagerie redis-cli < script_redis.sh
# Ou copier les commandes une par une dans redis-cli pour les captures

echo "  SCRIPT REDIS - Operations de messagerie"

# 1. CONNEXION ET VERIFICATION 
echo ""
echo " 1. Verification de la connexion "
PING

# 2. ENVOI DE MESSAGES (LPUSH)
echo ""
echo " 2. Envoi de messages avec LPUSH "
LPUSH queue:mamadou "msg_001|ldji|1721300000|Salut Mamadou, tu es dispo demain ?"
LPUSH queue:mamadou "msg_002|momar|1721300100|Hey, on se voit a l'ufr ?"
LPUSH queue:mamadou "msg_003|ldji|1721300200|N'oublie pas le TP de demain"

LPUSH queue:ldji "msg_004|mamadou|1721300300|Oui je suis dispo, a quelle heure ?"
LPUSH queue:ldji "msg_005|momar|1721300400|Tu as fini le rapport ?"

LPUSH queue:momar "msg_006|mamadou|1721300500|Merci pour ton aide !"
LPUSH queue:momar "msg_007|ldji|1721300600|On fait un point ce soir ?"

# 3. CONSULTER LES FILES (KEYS)
echo ""
echo " 3. Lister les files actives "
KEYS queue:*

# 4. NOMBRE DE MESSAGES (LLEN) 
echo ""
echo " 4. Compter les messages en attente "
LLEN queue:mamadou
LLEN queue:ldji
LLEN queue:momar

# 5. LIRE LES MESSAGES (LRANGE) 
echo ""
echo " 5. Lire les messages de mamadou (sans supprimer)"
LRANGE queue:mamadou 0 -1

echo ""
echo " 5b. Lire les messages de ldji "
LRANGE queue:ldji 0 -1

# 6. LIRE EN FIFO (RPOP)
echo ""
echo " 6. Lire le message le plus ancien de mamadou (RPOP = FIFO)"
RPOP queue:mamadou

echo ""
echo " Verification : il reste 2 messages "
LLEN queue:mamadou

# 7. STATISTIQUES (INCR / GET)
echo ""
echo " 7. Compteurs de statistiques "
SET stats:total_messages 7
INCR stats:total_messages
GET stats:total_messages

SET stats:messages_envoyes:mamadou 3
SET stats:messages_envoyes:ldji 2
SET stats:messages_envoyes:momar 2
GET stats:messages_envoyes:mamadou

# 8. EXPIRATION TTL (EXPIRE / TTL) 
echo ""
echo " 8. Definir un TTL sur la file de momar (30 secondes)"
EXPIRE queue:momar 30
TTL queue:momar

echo ""
echo " TTL de mamadou (pas de TTL defini)"
TTL queue:mamadou

# 9. SUPPRESSION (DEL) 
echo ""
echo " 9. Vider la file de momar "
DEL queue:momar
LLEN queue:momar

# 10. INFORMATIONS SYSTEME
echo ""
echo " 10. Informations Redis "
DBSIZE
INFO memory
INFO keyspace


