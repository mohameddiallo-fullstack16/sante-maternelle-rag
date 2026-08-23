"""
Interface Gradio de l'assistant santé maternelle et infantile.
"""

import gradio as gr

from config import AVERTISSEMENT, TEMPERATURE_DEFAUT, MAX_TOKENS_DEFAUT, TOP_K_DEFAUT
from vector_store import obtenir_collection
from rag_pipeline import repondre
from historique import (
    generer_id,
    sauvegarder_conversation,
    charger_conversation,
    lister_conversations,
)

collection = obtenir_collection(reinitialiser=False)

SUJETS_COUVERTS = [
    "Grossesse", "Nouveau-né", "Vaccination", "Nutrition",
    "Paludisme", "Hygiène", "Allaitement",
]


def soumettre_message(message, history, conv_id):
    if not message or not message.strip():
        return "", history, conv_id
    if not conv_id:
        conv_id = generer_id()
    history = history + [{"role": "user", "content": message}]
    return "", history, conv_id


def afficher_alerte(texte_alerte):
    if not texte_alerte:
        return ""
    return f'<div class="banniere-urgence">{texte_alerte}</div>'


def repondre_et_sauvegarder(history, conv_id):
    h = history
    for h, src, alerte in repondre(history, collection, TEMPERATURE_DEFAUT, MAX_TOKENS_DEFAUT, TOP_K_DEFAUT):
        yield h, src, afficher_alerte(alerte), conv_id
    sauvegarder_conversation(conv_id, h)


def rafraichir_historique():
    conversations = lister_conversations()
    choix = [(c["titre"], c["id"]) for c in conversations]
    return gr.update(choices=choix, value=None)


def charger_dans_interface(conv_id_selectionne):
    if not conv_id_selectionne:
        return [], "", "", conv_id_selectionne
    messages = charger_conversation(conv_id_selectionne)
    return messages, "", "", conv_id_selectionne


def nouvelle_conversation():
    return [], "", "", None, gr.update(value=None)


theme_sante = gr.themes.Base(
    primary_hue="teal",
    secondary_hue="orange",
    neutral_hue="stone",
    font=["Inter", "ui-sans-serif", "system-ui"],
).set(
    body_background_fill="#FAF7F2",
    body_background_fill_dark="#FAF7F2",
    body_text_color="#2B2620",
    body_text_color_dark="#2B2620",
    body_text_color_subdued="#6B6459",
    background_fill_primary="#FFFFFF",
    background_fill_primary_dark="#FFFFFF",
    background_fill_secondary="#F3EEE4",
    background_fill_secondary_dark="#F3EEE4",
    block_background_fill="#FFFFFF",
    block_background_fill_dark="#FFFFFF",
    block_border_color="#E4DDD1",
    block_border_color_dark="#E4DDD1",
    block_label_text_color="#6B6459",
    border_color_primary="#E4DDD1",
    border_color_primary_dark="#E4DDD1",
    input_background_fill="#FFFFFF",
    input_background_fill_dark="#FFFFFF",
    input_border_color="#E4DDD1",
    button_primary_background_fill="#0F7A6C",
    button_primary_text_color="#FFFFFF",
    button_primary_background_fill_hover="#12977F",
    button_secondary_background_fill="#FFFFFF",
    button_secondary_background_fill_dark="#FFFFFF",
    button_secondary_text_color="#2B2620",
    button_secondary_border_color="#E4DDD1",
)

css = """
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

.gradio-container {
    max-width: 1400px !important;
    background: #FAF7F2 !important;
}
.dark .gradio-container {
    background: #FAF7F2 !important;
}
footer { display: none !important; }

#sidebar {
    min-width: 260px !important;
    max-width: 280px !important;
    background: #F3EEE4 !important;
    border-radius: 14px !important;
    padding: 16px !important;
}

#titre h1, #titre h2 {
    font-family: 'Lora', serif !important;
    font-weight: 700 !important;
    color: #0F7A6C !important;
    margin-bottom: 2px !important;
}
#sous-titre {
    color: #6B6459;
    font-size: 14.5px;
    margin-bottom: 14px;
}

.badges-sujets {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 16px;
}
.badge-sujet {
    background: #E7F3F0;
    color: #0F7A6C;
    border: 1px solid #C7E4DD;
    border-radius: 999px;
    padding: 5px 13px;
    font-size: 12.5px;
    font-weight: 600;
}

.bandeau-avertissement {
    background: #FFF4E9;
    border-left: 4px solid #D97A3F;
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 14px;
    line-height: 1.55;
    color: #4A3B2A;
    margin-bottom: 14px;
    height: auto !important;
    overflow: visible !important;
    white-space: normal !important;
}

.banniere-urgence {
    background: #FBEAE6;
    border-left: 4px solid #C4432B;
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 15px;
    font-weight: 600;
    line-height: 1.5;
    color: #8A2E1C;
    margin-bottom: 12px;
    height: auto !important;
    overflow: visible !important;
}

#chatbot-principal {
    border-radius: 14px !important;
    border: 1px solid #E4DDD1 !important;
    background: #FFFFFF !important;
}

button { border-radius: 10px !important; font-weight: 600 !important; }
textarea { border-radius: 10px !important; }

#panneau-historique input[type="radio"] {
    display: none !important;
}
#panneau-historique label {
    display: block !important;
    border-radius: 10px !important;
    padding: 10px 12px !important;
    margin-bottom: 4px !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    cursor: pointer !important;
    font-size: 13.5px !important;
    color: #4A3B2A !important;
}
#panneau-historique label:hover {
    background: #E9E2D4 !important;
}

#zone-sources textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 13.5px !important;
    line-height: 1.6 !important;
}

"""
js_forcer_mode_clair = """
function() {
    document.body.classList.remove('dark');
    document.documentElement.classList.remove('dark');
}
"""
with gr.Blocks(title="Assistant Santé Maternelle et Infantile", theme=theme_sante, css=css, analytics_enabled=False) as demo:

    conv_id_state = gr.State(value=None)

    with gr.Row():

        with gr.Column(scale=1, elem_id="sidebar"):
            nouvelle_btn = gr.Button("+ Nouvelle conversation", variant="primary")
            liste_historique = gr.Radio(
                choices=[], label="Conversations", interactive=True, elem_id="panneau-historique"
            )

        with gr.Column(scale=4):
            with gr.Column(elem_id="titre"):
                gr.Markdown("## 🌿 Assistant Santé Maternelle et Infantile")
                gr.Markdown(
                    '<div id="sous-titre">Informations communautaires fiables, basées sur des documents officiels '
                    '(OMS, UNICEF, Ministère de la Santé du Sénégal)</div>'
                )

            gr.HTML(
                '<div class="badges-sujets">' +
                "".join(f'<span class="badge-sujet">{s}</span>' for s in SUJETS_COUVERTS) +
                '</div>'
            )

            gr.HTML(f'<div class="bandeau-avertissement">⚠️ {AVERTISSEMENT.replace("⚠️ ", "")}</div>')

            alerte_banniere = gr.HTML("")

            chatbot = gr.Chatbot(
                elem_id="chatbot-principal",
                show_label=False,
                height=520,
                placeholder="Pose ta question sur la santé maternelle ou infantile...",
            )

            msg_input = gr.Textbox(
                placeholder="Ex : Quels sont les signes de danger pendant la grossesse ?",
                lines=2,
                show_label=False,
            )
            envoyer = gr.Button("Envoyer", variant="primary")

            with gr.Accordion("📚 Sources utilisées pour la dernière réponse", open=False):
                sources = gr.Textbox(elem_id="zone-sources", show_label=False, lines=8, interactive=False)

    envoyer.click(
        soumettre_message, [msg_input, chatbot, conv_id_state], [msg_input, chatbot, conv_id_state]
    ).then(
        repondre_et_sauvegarder, [chatbot, conv_id_state], [chatbot, sources, alerte_banniere, conv_id_state]
    ).then(
        rafraichir_historique, outputs=[liste_historique]
    )

    msg_input.submit(
        soumettre_message, [msg_input, chatbot, conv_id_state], [msg_input, chatbot, conv_id_state]
    ).then(
        repondre_et_sauvegarder, [chatbot, conv_id_state], [chatbot, sources, alerte_banniere, conv_id_state]
    ).then(
        rafraichir_historique, outputs=[liste_historique]
    )

    nouvelle_btn.click(
        nouvelle_conversation, outputs=[chatbot, sources, alerte_banniere, conv_id_state, liste_historique]
    )

    liste_historique.select(
        charger_dans_interface, inputs=[liste_historique], outputs=[chatbot, sources, alerte_banniere, conv_id_state]
    )

    demo.load(None, None, None, js=js_forcer_mode_clair)
    demo.load(rafraichir_historique, outputs=[liste_historique])


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)