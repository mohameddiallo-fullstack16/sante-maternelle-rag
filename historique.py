"""
Sauvegarde et chargement des conversations.
Chaque conversation = un fichier JSON. Le dossier de stockage est configurable
via la variable d'environnement DOSSIER_CONVERSATIONS à pointer vers un
stockage persistant une fois déployé sur Hugging Face Spaces.
"""

import os
import json
from datetime import datetime

from config import DOSSIER_CONVERSATIONS

os.makedirs(DOSSIER_CONVERSATIONS, exist_ok=True)


def generer_id() -> str:
    """Identifiant unique basé sur l'horodatage (triable chronologiquement)."""
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def generer_titre(history: list) -> str:
    """Construit un titre court à partir du premier message utilisateur."""
    for message in history:
        if message["role"] == "user":
            texte = message["content"]
            if isinstance(texte, list):
                texte = " ".join(b.get("text", "") for b in texte if isinstance(b, dict))
            texte = texte.strip()
            return texte[:50] + ("..." if len(texte) > 50 else "")
    return "Nouvelle conversation"


def sauvegarder_conversation(conv_id: str, history: list) -> None:
    """Sauvegarde (ou met à jour) une conversation sur le disque."""
    chemin = os.path.join(DOSSIER_CONVERSATIONS, f"{conv_id}.json")
    donnees = {
        "id": conv_id,
        "titre": generer_titre(history),
        "date": datetime.now().isoformat(),
        "messages": history,
    }
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)


def charger_conversation(conv_id: str) -> list:
    """Recharge les messages d'une conversation depuis le disque."""
    chemin = os.path.join(DOSSIER_CONVERSATIONS, f"{conv_id}.json")
    with open(chemin, encoding="utf-8") as f:
        donnees = json.load(f)
    return donnees["messages"]


def lister_conversations() -> list:
    """Retourne [{'id':..., 'titre':...}, ...], la plus récente en premier."""
    fichiers = sorted(
        (f for f in os.listdir(DOSSIER_CONVERSATIONS) if f.endswith(".json")),
        reverse=True,
    )
    conversations = []
    for nom_fichier in fichiers:
        try:
            with open(os.path.join(DOSSIER_CONVERSATIONS, nom_fichier), encoding="utf-8") as f:
                donnees = json.load(f)
            conversations.append({"id": donnees["id"], "titre": donnees["titre"]})
        except Exception:
            continue
    return conversations