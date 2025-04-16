import streamlit as st
from openai import OpenAI
import yagmail
from supabase import create_client
from datetime import datetime
import socket

# ✅ Verificação de conexão com Supabase (teste de DNS)
try:
    supabase_host = st.secrets["SUPABASE_URL"].replace("https://", "").strip("/")
    ip = socket.gethostbyname(supabase_host)
    st.write("✅ Supabase URL resolvida com sucesso:", ip)
except Exception as e:
    st.warning("❌ Falha ao resolver a URL do Supabase.")
    st.error(f"Erro técnico: {e}")

# 🔑 OpenAI - geração da ideia estruturada
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

# ✉️ E-mail com a proposta
def enviar_email(nome, area, proposta):
    assunto = f"💡 Nova Ideia - {nome} ({area})"
    corpo = f"Ideia gerada pelo MindGlass:\n\n{proposta}"
    yag = yagmail.SMTP(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASS"])
    yag.send(to=st.secrets["EMAIL_DESTINO"], subject=assunto, contents=corpo)

# 🔗 Supabase - gravar no banco
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

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

