"""
Indexation et recherche dans ChromaDB.
"""

import chromadb

from config import DOSSIER_CHROMA, NOM_COLLECTION, TOP_K_DEFAUT
from llm_client import generer_embeddings, generer_embedding_unique

TAILLE_BATCH = 48


def obtenir_collection(reinitialiser: bool = False):
    """Retourne la collection ChromaDB (créée si elle n'existe pas encore)."""
    client_chroma = chromadb.PersistentClient(path=DOSSIER_CHROMA)

    if reinitialiser:
        try:
            client_chroma.delete_collection(NOM_COLLECTION)
        except Exception:
            pass

    return client_chroma.get_or_create_collection(
        name=NOM_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def indexer_chunks(chunks: list, collection, batch_size: int = TAILLE_BATCH) -> None:
    """Vectorise et indexe les chunks par lots (batch_size à la fois)."""
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        textes = [c["texte"] for c in batch]

        embeddings = generer_embeddings(textes)

        collection.add(
            ids=[c["id"] for c in batch],
            documents=textes,
            embeddings=embeddings,
            metadatas=[{"source": c["source"], "theme": c["theme"]} for c in batch],
        )
        print(f"  Batch {i // batch_size + 1}/{(len(chunks) - 1) // batch_size + 1} indexé ({len(batch)} chunks)")

    print(f"\nTerminé : {collection.count()} chunks dans ChromaDB.")


def rechercher(question: str, collection, k: int = TOP_K_DEFAUT) -> list:
    """Recherche les k chunks les plus pertinents pour une question."""
    vecteur = generer_embedding_unique(question)

    resultats = collection.query(
        query_embeddings=[vecteur],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    if not resultats["ids"][0]:
        return []

    return [
        {
            "texte": resultats["documents"][0][i],
            "source": resultats["metadatas"][0][i].get("source", "inconnue"),
            "theme": resultats["metadatas"][0][i].get("theme", ""),
            "score": round(1 - resultats["distances"][0][i], 3),
        }
        for i in range(len(resultats["ids"][0]))
    ]


if __name__ == "__main__":
    from data_loader import charger_documents, preparer_chunks

    documents = charger_documents()
    chunks = preparer_chunks(documents)[:5]

    collection = obtenir_collection(reinitialiser=True)
    indexer_chunks(chunks, collection)

    resultats = rechercher("grossesse", collection, k=2)
    print("\nTest de recherche sur 'grossesse' :")
    for r in resultats:
        print(f"  [{r['score']}] {r['source']} — {r['texte'][:80]}...")