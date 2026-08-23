"""
Script d'indexation du corpus documentaire.
A lancer une fois (ou à chaque changement du dossier data/) : python index_corpus.py
"""

from data_loader import charger_documents, preparer_chunks
from vector_store import obtenir_collection, indexer_chunks


def main():
    print("1/3 — Chargement des documents...")
    documents = charger_documents()
    print(f"   {len(documents)} documents chargés (après déduplication).")

    print("2/3 — Préparation des chunks...")
    chunks = preparer_chunks(documents)
    print(f"   {len(chunks)} chunks prêts à indexer.")

    print("3/3 — Indexation dans ChromaDB (peut prendre plusieurs minutes)...")
    collection = obtenir_collection(reinitialiser=True)
    indexer_chunks(chunks, collection)

    print("\nIndexation terminée. Tu peux lancer l'application : python app.py")


if __name__ == "__main__":
    main()