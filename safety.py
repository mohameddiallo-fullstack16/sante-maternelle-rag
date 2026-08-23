"""
Détection de signes de danger dans la question de l'utilisateur.

Filtre basé sur des mots-clés (racines courtes), en complément du LLM :
une liste de racines est déterministe et vérifiable, contrairement à une
détection laissée entièrement au jugement du modèle.
"""

SIGNES_DANGER = {
    "grossesse": [
        "saign",
        "convuls",
        "respir",
    ],
    "enfant": [
        "inconscient",
        "diarrh",
        "deshydrat",
        "déshydrat",
        "fievre",
        "fièvre",
    ],
}

MOTS_CLES_URGENCE = sorted({
    mot for categorie in SIGNES_DANGER.values() for mot in categorie
})


def detecter_signes_danger(texte: str) -> list:
    """Retourne les mots-clés de danger détectés dans le texte (insensible à la casse)."""
    texte_normalise = texte.lower()
    return [mot for mot in MOTS_CLES_URGENCE if mot in texte_normalise]


def construire_alerte(signes: list) -> str:
    """Construit l'instruction de sécurité à injecter dans le prompt système."""
    if not signes:
        return ""
    liste = ", ".join(sorted(set(signes)))
    return f"""
ALERTE SÉCURITÉ — SIGNES DE DANGER DÉTECTÉS ({liste})

Tu DOIS commencer ta réponse par une recommandation claire et immédiate de consulter
en urgence un poste de santé, une sage-femme, un médecin, ou d'appeler les services
compétents — AVANT toute autre information.
Ne minimise jamais la situation. Ne pose aucun diagnostic. Ne propose aucun traitement.
"""