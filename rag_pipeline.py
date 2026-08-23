"""
Orchestration du pipeline RAG complet : sécurité, recherche, prompt, génération.
Contrairement au DevAI Assistant, le RAG est ici TOUJOURS actif (pas de case à cocher).
"""

from config import TEMPERATURE_DEFAUT, MAX_TOKENS_DEFAUT, TOP_K_DEFAUT, SEUIL_PERTINENCE
from safety import detecter_signes_danger, construire_alerte
from prompts import construire_prompt_systeme
from vector_store import rechercher
from llm_client import stream_reponse


def _texte(contenu):
    """Normalise le contenu d'un message Gradio (str ou liste de blocs) en texte brut."""
    if isinstance(contenu, str):
        return contenu
    if isinstance(contenu, list):
        return " ".join(
            bloc.get("text", "")
            for bloc in contenu
            if isinstance(bloc, dict) and bloc.get("type") == "text"
        )
    return str(contenu) if contenu is not None else ""


def repondre(history, collection, temperature=TEMPERATURE_DEFAUT, max_tokens=MAX_TOKENS_DEFAUT, top_k=TOP_K_DEFAUT):
    """Génère une réponse en streaming pour le dernier message utilisateur."""
    if not history or history[-1]["role"] != "user":
        yield history, "", ""
        return

    question = _texte(history[-1]["content"])

    # 1. Détection de danger
    signes = detecter_signes_danger(question)
    alerte = construire_alerte(signes)

    # 2. Recherche documentaire
    tous_extraits = rechercher(question, collection, k=int(top_k))
    extraits = [e for e in tous_extraits if e["score"] >= SEUIL_PERTINENCE]

    contexte = "\n\n".join(
        f"[Extrait {i+1} — source : {e['source']}]\n{e['texte']}"
        for i, e in enumerate(extraits)
    )

    # 3. Prompt système complet
    system_content = construire_prompt_systeme(contexte, alerte)

    api_messages = [{"role": "system", "content": system_content}]
    for msg in history:
        api_messages.append({"role": msg["role"], "content": _texte(msg["content"])})

    # 4. Texte des sources à afficher
    if extraits:
        sources_texte = "\n\n".join(
            f"📄 {e['source']}" + (f" ({e['theme']})" if e["theme"] else "") +
            f" — pertinence {e['score']:.0%}\n{e['texte'][:300]}..."
            for e in extraits
        )
    else:
        sources_texte = "Aucune source pertinente trouvée dans la documentation indexée."

    alerte_affichee = (
        "🚨 Signe de gravité détecté — orientation vers un professionnel de santé recommandée."
        if signes else ""
    )

    # 5. Génération en streaming
    history = history + [{"role": "assistant", "content": ""}]
    for texte in stream_reponse(api_messages, temperature, max_tokens):
        history[-1]["content"] = texte
        yield history, sources_texte, alerte_affichee