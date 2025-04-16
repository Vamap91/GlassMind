import streamlit as st
from utils import estruturar_ideia, enviar_email, salvar_ideia_supabase

# 🎨 Configuração visual
st.set_page_config(page_title="MindGlass – Ideias com IA", layout="centered")
st.markdown("<h1 style='text-align: center;'>💡 MindGlass</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Sua ideia, com a força da inteligência artificial. Vamos transformar juntos?</p>", unsafe_allow_html=True)
st.divider()

# 📝 Formulário
with st.form("formulario_mindglass"):
    nome = st.text_input("👤 Seu nome")
    area = st.selectbox("🏢 Área onde você trabalha", ["TI", "RH", "Financeiro", "Atendimento", "Loja", "Oficina", "Marketing", "Outra"])
    ideia_curta = st.text_area("💭 Compartilhe sua ideia (pode ser bem simples!)")
    enviar = st.form_submit_button("🚀 Enviar para o MindGlass")

# 🚀 Processamento
if enviar:
    if not nome or not ideia_curta:
        st.warning("Por favor, preencha seu nome e escreva uma ideia.")
    else:
        with st.spinner("🧠 Pensando com carinho na sua ideia..."):
            proposta = estruturar_ideia(nome, area, ideia_curta)

            try:
                enviar_email(nome, area, proposta)
                salvar_ideia_supabase(nome, area, ideia_curta, proposta)
                st.success("✅ Sua ideia foi enviada com sucesso!")
                st.balloons()
            except Exception as e:
                st.warning("⚠️ Ocorreu um problema ao enviar a ideia.")
                st.text(f"Erro técnico: {e}")

        st.subheader("✨ Veja como sua ideia ficou:")
        st.markdown(proposta)
