"""
Chargement du corpus documentaire (.txt) et préparation des chunks finaux.
"""

import os
import csv
import hashlib

from config import DOSSIER_DONNEES, CHEMIN_METADATA, CHUNK_SIZE
from chunking import decouper_texte

SEUIL_DEJA_CHUNK = int(CHUNK_SIZE * 1.3)


def charger_metadata(chemin: str = CHEMIN_METADATA) -> dict:
    """Charge metadata.csv et retourne un dict {id_document: ligne_csv}."""
    metadonnees = {}
    with open(chemin, encoding="utf-8") as f:
        lecteur = csv.DictReader(f)
        for ligne in lecteur:
            metadonnees[ligne["id"]] = ligne
    return metadonnees


def charger_documents(dossier: str = DOSSIER_DONNEES) -> list:
    """Lit tous les .txt, associe le titre du catalogue si dispo, ignore les doublons."""
    metadonnees = charger_metadata()
    documents = []
    empreintes_vues = set()

    for nom_fichier in os.listdir(dossier):
        if not nom_fichier.endswith(".txt"):
            continue

        chemin_fichier = os.path.join(dossier, nom_fichier)
        with open(chemin_fichier, encoding="utf-8") as f:
            texte = f.read().strip()

        if not texte:
            continue

        empreinte = hashlib.md5(texte.encode("utf-8")).hexdigest()
        if empreinte in empreintes_vues:
            continue
        empreintes_vues.add(empreinte)

        id_document = nom_fichier.removesuffix(".txt")
        infos = metadonnees.get(id_document)

        if infos:
            titre = infos["titre"]
            theme = infos["domain"]
        else:
            titre = nom_fichier
            theme = ""

        documents.append({"source": titre, "theme": theme, "texte": texte})

    return documents


def preparer_chunks(documents: list) -> list:
    """Transforme les documents en chunks prêts à indexer."""
    chunks = []
    idx = 0

    for doc in documents:
        if len(doc["texte"]) <= SEUIL_DEJA_CHUNK:
            morceaux = [doc["texte"]]
        else:
            morceaux = decouper_texte(doc["texte"])

        for morceau in morceaux:
            chunks.append({
                "id": f"chunk_{idx:04d}",
                "source": doc["source"],
                "theme": doc["theme"],
                "texte": morceau,
            })
            idx += 1

    return chunks


if __name__ == "__main__":
    documents = charger_documents()
    print(f"{len(documents)} documents chargés (après déduplication).")

    chunks = preparer_chunks(documents)
    print(f"{len(chunks)} chunks prêts à indexer.")
    print(f"\nExemple (chunk 0, source: {chunks[0]['source']}) :")
    print(chunks[0]["texte"][:200])