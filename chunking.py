from config import CHUNK_SIZE,CHUNK_OVERLAP
def decouper_texte(texte: str, taille: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:    
    # Securite anti-boucle infinie
    if overlap >= taille:
        raise ValueError(f"overlap ({overlap}) doit etre inferieur a taille ({taille})")

    # Decoupage avec chevauchement
    chunks, debut, idx = [], 0, 0
    while debut < len(texte):
        fin = min(debut + taille, len(texte))
        if fin < len(texte):
            coupe = texte.rfind('.', debut, fin)
            if coupe > debut + (taille // 2):   # la coupe doit garder au moins la moitié du chunk
                fin = coupe + 1
        chunk = texte[debut:fin].strip()
        if chunk:
            chunks.append(chunk)
            idx += 1
        nouveau_debut = fin - overlap
        if nouveau_debut <= debut:   # securite absolue anti-boucle infinie
            nouveau_debut = debut + 1
        debut = nouveau_debut

    return chunks



if __name__ == "__main__":
    texte_test = "Ceci est une phrase de test. " * 50
    chunks = decouper_texte(texte_test)
    print(f"Document découpé : {len(chunks)} chunks")
    print(f"Exemple (chunk 0) :\n{chunks[0][:200]}")