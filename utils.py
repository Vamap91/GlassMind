import streamlit as st
from openai import OpenAI
import yagmail
from supabase import create_client
from datetime import datetime

# 🔑 OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✉️ E-mail
def enviar_email(nome, area, proposta):
    assunto = f"💡 Nova Ideia - {nome} ({area})"
    corpo = f"Ideia gerada pelo MindGlass:\n\n{proposta}"
    yag = yagmail.SMTP(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASS"])
    yag.send(to=st.secrets["EMAIL_DESTINO"], subject=assunto, contents=corpo)

# 🧠 IA transforma a ideia
def estruturar_ideia(nome, area, ideia_curta):
    prompt = f"""
    O colaborador {nome}, da área de {area}, enviou a seguinte sugestão:

    "{ideia_curta}"

    Por favor, transforme essa ideia em uma proposta bem estruturada com:
    1. Descrição detalhada
    2. Justificativa
    3. Etapas para implementação
    4. Desafios e como superar
    5. Impacto esperado e métricas sugeridas

    Escreva de forma clara e objetiva.
    """

    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=900,
    )

    return resposta.choices[0].message.content.strip()

# 💾 Supabase
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def salvar_ideia_supabase(nome, area, ideia, proposta):
    data = {
        "nome": nome,
        "area": area,
        "ideia_original": ideia,
        "proposta_gerada": proposta,
        "data_envio": datetime.utcnow().isoformat()
    }

    response = supabase.table("ideias").insert(data).execute()
    return response
