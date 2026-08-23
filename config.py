import os
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
print("Cle API chargee." if MISTRAL_API_KEY else "Attention : aucune cle detectee.")
MODELE_CHAT = "mistral-small-latest"
MODELE_EMBEDDING = "mistral-embed"

TEMPERATURE_DEFAUT = 0.15
MAX_TOKENS_DEFAUT = 1400

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
TOP_K_DEFAUT = 4
SEUIL_PERTINENCE = 0.3

RACINE_PROJET = os.path.dirname(os.path.abspath(__file__))
DOSSIER_DONNEES = os.path.join(RACINE_PROJET, "data")
CHEMIN_METADATA = os.path.join(DOSSIER_DONNEES, "metadata.csv")
DOSSIER_CHROMA = os.path.join(RACINE_PROJET, "chroma_db")
NOM_COLLECTION = "sante_maternelle_infantile"

DOSSIER_CONVERSATIONS = os.environ.get(
    "DOSSIER_CONVERSATIONS", os.path.join(RACINE_PROJET, "conversations")
)

AVERTISSEMENT = (
    "⚠️ Ce chatbot fournit des informations générales de santé. "
    "Il ne remplace pas un professionnel de santé. En cas de signe grave ou de doute, "
    "consultez rapidement un poste de santé, une sage-femme, un médecin ou appelez les "
    "services compétents."
)