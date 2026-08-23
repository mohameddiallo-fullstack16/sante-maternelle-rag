"""
Client Mistral : génération d'embeddings et génération de texte en streaming.
"""

from mistralai.client import Mistral 
from config import MISTRAL_API_KEY, MODELE_CHAT, MODELE_EMBEDDING

if not MISTRAL_API_KEY:
    raise RuntimeError(
        "MISTRAL_API_KEY n'est pas définie. "
        "Définis la variable d'environnement avant de lancer l'application."
    )

client = Mistral(api_key=MISTRAL_API_KEY)


def generer_embeddings(textes: list) -> list:
    """Génère les embeddings Mistral pour une liste de textes (traitement par lot)."""
    reponse = client.embeddings.create(
        model=MODELE_EMBEDDING,
        inputs=textes,
    )
    return [item.embedding for item in reponse.data]


def generer_embedding_unique(texte: str) -> list:
    """Génère l'embedding d'un seul texte (typiquement la question de l'utilisateur)."""
    return generer_embeddings([texte])[0]


def stream_reponse(messages: list, temperature: float, max_tokens: int):
    """Génère une réponse en streaming, yield le texte accumulé à chaque fragment."""
    stream = client.chat.stream(
        model=MODELE_CHAT,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    texte = ""
    for event in stream:
        if (
            hasattr(event, "data")
            and event.data
            and event.data.choices
            and event.data.choices[0].delta.content
        ):
            texte += event.data.choices[0].delta.content
            yield texte