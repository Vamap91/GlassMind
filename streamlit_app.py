import streamlit as st
from utils import estruturar_ideia, enviar_email

# Configurando título da página e visual
st.set_page_config(page_title="MindGlass - Ideias com IA", layout="centered")

# Título e chamada
st.markdown("<h1 style='text-align: center;'>💡 MindGlass</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Sua ideia, com a força da inteligência artificial. Vamos transformar juntos?</p>", unsafe_allow_html=True)
st.divider()

# Criando formulário simples e leve
with st.form("formulario_mindglass"):
    nome = st.text_input("👤 Seu nome")
    area = st.selectbox("🏢 Área onde você trabalha", ["TI", "RH", "Financeiro", "Atendimento", "Loja", "Oficina", "Marketing", "Outra"])
    ideia_curta = st.text_area("💭 Compartilhe sua ideia (pode ser bem simples!)")

    enviar = st.form_submit_button("🚀 Enviar para o MindGlass")

# Se o usuário clicar no botão:
if enviar:
    with st.spinner("🤖 Estamos transformando sua ideia em um projeto incrível..."):
        proposta = estruturar_ideia(nome, area, ideia_curta)
        enviar_email(nome, area, proposta)

    st.success("🎉 Sua ideia foi enviada com sucesso para a equipe!")
    st.balloons()

    st.subheader("✨ Olha como a IA organizou sua sugestão:")
    st.markdown(proposta)
