import streamlit as st
from openai import OpenAI
import yagmail

# Puxando os dados direto do secrets do Streamlit Cloud
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def estruturar_ideia(nome, area, ideia_curta):
    prompt = f"""
    O colaborador {nome}, da área de {area}, enviou a seguinte ideia:

    "{ideia_curta}"

    Transforme isso em uma proposta detalhada com:
    1. Descrição da ideia
    2. Justificativa
    3. Etapas de implementação
    4. Desafios e como superá-los
    5. Impacto esperado e métricas
    """

    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=800,
    )

    return resposta.choices[0].message.content.strip()

def enviar_email(nome, area, proposta):
    assunto = f"Ideia do MindGlass - {nome} ({area})"
    corpo = f"Ideia recebida:\n\n{proposta}"

    yag = yagmail.SMTP(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASS"])
    yag.send(to=st.secrets["EMAIL_DESTINO"], subject=assunto, contents=corpo)

