import streamlit as st
from utils import estruturar_ideia_avancada, enviar_email_estruturado, validar_entrada, salvar_historico, gerar_json_proposta
import time

# 🎨 Configuração da interface
st.set_page_config(
    page_title="MindGlass V2 – Ideias Inteligentes", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para melhor UX
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .preview-box {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<h1 class="main-header">💡 MindGlass V2</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Transformando ideias em projetos estruturados com IA avançada</p>', unsafe_allow_html=True)

# Sidebar com informações
with st.sidebar:
    st.header("ℹ️ Como funciona")
    st.markdown("""
    **1.** Preencha suas informações
    **2.** Descreva sua ideia (pode ser simples!)
    **3.** Escolha o nível de detalhamento
    **4.** Preview antes de enviar
    **5.** Receba estrutura completa por email
    """)
    
    st.divider()
    st.header("🎯 O que você recebe")
    st.markdown("""
    - Proposta estruturada
    - Análise de viabilidade
    - Cronograma sugerido
    - Estrutura de código
    - Métricas de sucesso
    - JSON estruturado
    - Próximos passos
    """)

# Layout em colunas
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Conte sua ideia")
    
    # Formulário principal
    with st.form("formulario_mindglass_v2"):
        # Informações básicas
        st.subheader("👤 Informações Básicas")
        col_nome, col_area = st.columns(2)
        
        with col_nome:
            nome = st.text_input("Seu nome completo", placeholder="Ex: João Silva")
        
        with col_area:
            areas_detalhadas = [
                "TI - Desenvolvimento", "TI - Infraestrutura", "TI - Dados/BI",
                "RH - Recrutamento", "RH - Treinamento", "RH - Cultura",
                "Financeiro - Controladoria", "Financeiro - Planejamento",
                "Atendimento - SAC", "Atendimento - Vendas",
                "Loja - Operações", "Loja - Comercial",
                "Oficina - Técnica", "Oficina - Qualidade",
                "Marketing - Digital", "Marketing - Produto", "Marketing - Comunicação",
                "Operações", "Qualidade", "Logística", "Jurídico", "Outra"
            ]
            area = st.selectbox("Área de atuação", areas_detalhadas)
        
        # Detalhes da ideia
        st.subheader("💭 Sua Ideia")
        ideia_curta = st.text_area(
            "Descreva sua ideia (seja natural, pode ser bem simples!)",
            placeholder="Ex: Que tal se a gente tivesse um app para os clientes acompanharem o serviço em tempo real?",
            height=120
        )
        
        # Configurações avançadas
        st.subheader("⚙️ Configurações")
        col_nivel, col_foco = st.columns(2)
        
        with col_nivel:
            nivel_detalhamento = st.select_slider(
                "Nível de detalhamento",
                options=["Básico", "Intermediário", "Completo", "Executivo"],
                value="Intermediário"
            )
        
        with col_foco:
            foco_principal = st.selectbox(
                "Foco principal",
                ["Melhoria de Processo", "Nova Tecnologia", "Experiência do Cliente", 
                 "Redução de Custos", "Inovação", "Automação", "Análise de Dados"]
            )
        
        # Contexto adicional (opcional)
        with st.expander("📋 Contexto Adicional (Opcional)"):
            problema_atual = st.text_area("Qual problema isso resolve?", height=80)
            recursos_disponiveis = st.text_input("Recursos que você imagina necessários")
            prazo_desejado = st.selectbox("Prazo esperado", ["Urgente (1 mês)", "Curto (3 meses)", "Médio (6 meses)", "Longo (1 ano+)"])
        
        # Botões
        col_preview, col_enviar = st.columns(2)
        with col_preview:
            gerar_preview = st.form_submit_button("👁️ Gerar Preview", use_container_width=True)
        with col_enviar:
            enviar_final = st.form_submit_button("🚀 Estruturar e Enviar", use_container_width=True, type="primary")

with col2:
    st.header("📊 Status")
    
    # Validação em tempo real
    if nome and ideia_curta:
        validacao = validar_entrada(nome, ideia_curta)
        if validacao["valido"]:
            st.success("✅ Informações válidas")
        else:
            st.error(f"❌ {validacao['erro']}")
    
    # Contador de caracteres
    if ideia_curta:
        char_count = len(ideia_curta.strip())
        if char_count < 20:
            st.warning(f"📝 {char_count} caracteres - Muito curto")
        elif char_count < 100:
            st.info(f"📝 {char_count} caracteres - Pode detalhar mais")
        else:
            st.success(f"📝 {char_count} caracteres - Ótimo!")

# Processamento do Preview
if gerar_preview:
    if not nome or not ideia_curta:
        st.error("⚠️ Preencha pelo menos nome e ideia para gerar o preview.")
    else:
        validacao = validar_entrada(nome, ideia_curta)
        if not validacao["valido"]:
            st.error(f"❌ {validacao['erro']}")
        else:
            with st.spinner("🧠 Gerando preview da sua proposta..."):
                # Simula processamento
                time.sleep(2)
                
                preview_data = {
                    "nome": nome,
                    "area": area,
                    "ideia": ideia_curta,
                    "nivel": nivel_detalhamento,
                    "foco": foco_principal,
                    "problema": problema_atual,
                    "recursos": recursos_disponiveis,
                    "prazo": prazo_desejado
                }
                
                proposta_preview = estruturar_ideia_avancada(preview_data, preview_mode=True)
                
                st.markdown('<div class="preview-box">', unsafe_allow_html=True)
                st.subheader("👁️ Preview da Proposta")
                st.markdown(proposta_preview)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.info("💡 **Dica:** Se ficou bom, clique em 'Estruturar e Enviar' para receber a versão completa por email!")

# Processamento Final
if enviar_final:
    if not nome or not ideia_curta:
        st.error("⚠️ Preencha pelo menos nome e ideia para continuar.")
    else:
        validacao = validar_entrada(nome, ideia_curta)
        if not validacao["valido"]:
            st.error(f"❌ {validacao['erro']}")
        else:
            with st.spinner("🚀 Estruturando sua ideia com IA avançada..."):
                dados_completos = {
                    "nome": nome,
                    "area": area,
                    "ideia": ideia_curta,
                    "nivel": nivel_detalhamento,
                    "foco": foco_principal,
                    "problema": problema_atual,
                    "recursos": recursos_disponiveis,
                    "prazo": prazo_desejado
                }
                
                # Gera proposta completa
                proposta_completa = estruturar_ideia_avancada(dados_completos)
                
                # Gera JSON estruturado ANTES do envio
                json_proposta = None
                try:
                    json_proposta = gerar_json_proposta(dados_completos, proposta_completa)
                    
                    if json_proposta:
                        st.info("📄 JSON estruturado gerado com sucesso!")
                        
                        # Mostra métricas do JSON
                        col_json1, col_json2, col_json3 = st.columns(3)
                        with col_json1:
                            st.metric("🆔 ID Proposta", json_proposta['metadata']['id'])
                        with col_json2:
                            st.metric("📈 Complexidade", json_proposta['analise']['complexidade'])
                        with col_json3:
                            st.metric("⚡ Prioridade", json_proposta['analise']['prioridade_sugerida'])
                            
                except Exception as e:
                    st.warning(f"⚠️ Erro ao gerar JSON: {str(e)}")
                
                try:
                    # Envia email estruturado com JSON
                    enviar_email_estruturado(dados_completos, proposta_completa, json_proposta)
                    
                    # Salva no histórico
                    proposta_id, json_salvo = salvar_historico(dados_completos, proposta_completa)
                    
                    # Feedback de sucesso
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown("### ✅ Sucesso!")
                    st.markdown(f"""
                    **{nome}**, sua ideia foi estruturada e enviada!
                    
                    📧 **Email enviado para:** Liderança Carglass  
                    📊 **Nível:** {nivel_detalhamento}  
                    🎯 **Foco:** {foco_principal}  
                    ⏱️ **Processado em:** {time.strftime("%H:%M:%S")}
                    📄 **JSON ID:** {proposta_id if proposta_id else "Não gerado"}
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.balloons()
                    
                    # Mostra resumo da proposta
                    with st.expander("📋 Resumo da Proposta Enviada"):
                        st.markdown(proposta_completa[:500] + "...")
                        st.info("💌 **A versão completa foi enviada por email com estrutura de projeto detalhada!**")
                    
                    # Mostra informações do JSON se disponível
                    if json_proposta:
                        with st.expander("📊 Análise Automática da Proposta"):
                            col_analise1, col_analise2 = st.columns(2)
                            
                            with col_analise1:
                                st.markdown("**🎯 Categorização:**")
                                st.write(f"• **Categoria:** {json_proposta['analise']['categoria_projeto']}")
                                st.write(f"• **Complexidade:** {json_proposta['analise']['complexidade']}")
                                st.write(f"• **Viabilidade:** {json_proposta['analise']['viabilidade_tecnica']}")
                                
                            with col_analise2:
                                st.markdown("**📈 Priorização:**")
                                st.write(f"• **Prioridade:** {json_proposta['analise']['prioridade_sugerida']}")
                                st.write(f"• **Impacto:** {json_proposta['analise']['impacto_estimado']}")
                                st.write(f"• **Palavras-chave:** {', '.join(json_proposta['entrada']['palavras_chave'][:3])}")
                    
                except Exception as e:
                    st.error(f"⚠️ Erro ao processar: {str(e)}")
                    st.info("🔧 Nossa equipe foi notificada. Tente novamente em alguns minutos.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>MindGlass V2</strong> | Desenvolvido por Vinicius Paschoa | Carglass Innovation Lab</p>
    <p>💡 <em>Transformando ideias em realidade desde 2024</em></p>
</div>
""", unsafe_allow_html=True)
