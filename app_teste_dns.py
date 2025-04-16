import streamlit as st
import socket

st.title("🔍 Teste de Conexão com Supabase")

try:
    host = st.secrets["SUPABASE_URL"].replace("https://", "").strip("/")
    ip = socket.gethostbyname(host)
    st.success(f"✅ Conexão bem-sucedida! IP resolvido: {ip}")
except Exception as e:
    st.error("❌ Falha ao resolver o host da Supabase")
    st.text(f"Erro técnico: {e}")
