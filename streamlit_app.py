import streamlit as st
from utils import (
    estruturar_ideia_avancada, 
    enviar_email_estruturado, 
    validar_entrada, 
    salvar_historico, 
    gerar_json_proposta,
    detectar_tipo_projeto,
    calcular_pontuacao_nps,
    classificar_categoria_nps
)
import time

# 🎨 Configuração da interface
st.set_page_config(
    page_title="MindGlass V2 – Ideias Inteligentes com Foco em NPS", 
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
    .nps-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        margin: 0.5rem;
        color: white;
    }
    .nps-high { background: linear-gradient(45deg, #28a745, #20c997); }
    .nps-medium { background: linear-gradient(45deg, #ffc107, #fd7e14); }
    .nps-low { background: linear-gradient(45deg, #6c757d, #495057); }
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
    .nps-analysis {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<h1 class="main-header">💡 MindGlass V2</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Transformando suas ideias em projetos estruturados e executáveis</p>', unsafe_allow_html=True)

# Sidebar com informações
with st.sidebar:
    st.header("ℹ️ Como funciona")
    st.markdown("""
    **1.** Descreva sua ideia (seja natural!)
    **2.** IA analisa e estrutura automaticamente
    **3.** Detecta se é projeto tecnológico ou de processo
    **4.** Gera proposta profissional completa
    **5.** Email enviado com estrutura executável
    """)
    
    st.divider()
    st.header("🎯 O que você recebe")
    st.markdown("""
    - Proposta estruturada profissionalmente
    - Análise de viabilidade e impacto
    - Cronograma detalhado
    - Estrutura técnica ou de processo
    - Métricas de sucesso
    - JSON estruturado para acompanhamento
    """)
    
    st.divider()
    st.header("🔍 Tipos de Projeto")
    st.markdown("""
    **🏗️ TECNOLÓGICO:**
    - Apps e sistemas
    - Automação digital
    - Dashboards e APIs
    
    **📋 PROCESSO:**
    - Formulários e procedimentos
    - Workflows manuais
    - Melhoria operacional
    """)
    
    st.divider()
    st.header("💡 Dicas para Sucesso")
    st.markdown("""
    - Seja específico sobre o problema
    - Pense no benefício para a empresa
    - Considere a experiência do usuário
    - Mencione recursos disponíveis
    """)


# Layout em colunas
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Conte sua ideia")
    
    # Formulário principal
    with st.form("formulario_mindglass_v2_enhanced"):
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
        st.info("💡 **Dica:** Seja natural e específico! Qualquer ideia é válida - nossa IA vai estruturar profissionalmente.")
        
        ideia_curta = st.text_area(
            "Descreva sua ideia (tecnológica ou de processo)",
            placeholder="Ex: Que tal se os clientes pudessem acompanhar o reparo em tempo real? OU Podemos simplificar o processo de check-in na oficina?",
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
                ["Experiência do Cliente", "Redução de Custos", "Melhoria de Processo", 
                 "Nova Tecnologia", "Inovação", "Automação", "Análise de Dados"]
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
    st.header("📊 Análise em Tempo Real")
    
    # Validação em tempo real
    if nome and ideia_curta:
        validacao = validar_entrada(nome, ideia_curta)
        if validacao["valido"]:
            st.success("✅ Informações válidas")
            
            # Análise preliminar
            if len(ideia_curta.strip()) > 20:
                tipo_detectado = detectar_tipo_projeto(ideia_curta, area)
                st.info(f"🔍 **Tipo detectado:** {tipo_detectado}")
                
                # Análise de potencial (sem mostrar NPS)
                palavras_impacto = ['cliente', 'experiência', 'acompanhar', 'transparência', 'tempo real', 'automação', 'melhorar', 'otimizar']
                score_impacto = sum(1 for palavra in palavras_impacto if palavra.lower() in ideia_curta.lower())
                
                if score_impacto >= 3:
                    st.success("🎯 **Potencial:** Alto impacto")
                elif score_impacto >= 1:
                    st.info("📈 **Potencial:** Médio impacto")
                else:
                    st.warning("💡 **Potencial:** Pode ser mais específico")
        else:
            st.error(f"❌ {validacao['erro']}")
    
    # Contador de caracteres
    if ideia_curta:
        char_count = len(ideia_curta.strip())
        if char_count < 20:
            st.warning(f"📝 {char_count} caracteres - Muito curto para análise")
        elif char_count < 100:
            st.info(f"📝 {char_count} caracteres - Pode detalhar mais")
        else:
            st.success(f"📝 {char_count} caracteres - Ótimo para análise!")
    
    # Dicas baseadas no foco
    if foco_principal:
        st.subheader("💡 Dicas")
        if foco_principal == "Experiência do Cliente":
            st.info("🎯 **Dica:** Mencione como isso melhora a experiência")
        elif foco_principal == "Redução de Custos":
            st.info("💰 **Dica:** Detalhe que processos serão otimizados")
        elif foco_principal == "Melhoria de Processo":
            st.info("⚡ **Dica:** Explique o processo atual vs o proposto")
        elif foco_principal == "Automação":
            st.info("🤖 **Dica:** Descreva que tarefas serão automatizadas")
        elif foco_principal == "Nova Tecnologia":
            st.info("🔧 **Dica:** Explique que problema a tecnologia resolve")
        else:
            st.info("💡 **Dica:** Seja específico sobre o benefício esperado")

# Processamento do Preview
if gerar_preview:
    if not nome or not ideia_curta:
        st.error("⚠️ Preencha pelo menos nome e ideia para gerar o preview.")
    else:
        validacao = validar_entrada(nome, ideia_curta)
        if not validacao["valido"]:
            st.error(f"❌ {validacao['erro']}")
        else:
            with st.spinner("🧠 Analisando sua ideia e gerando preview estruturado..."):
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
                
                # Detecta tipo e calcula NPS (mas não mostra detalhes)
                tipo_projeto = detectar_tipo_projeto(ideia_curta, area)
                pontuacao_nps, justificativa_nps = calcular_pontuacao_nps(ideia_curta, area, foco_principal)
                
                # Adiciona aos dados
                preview_data["tipo_projeto"] = tipo_projeto
                preview_data["pontuacao_nps"] = pontuacao_nps
                preview_data["justificativa_nps"] = justificativa_nps
                
                # Mostra apenas análise básica (sem NPS)
                st.info(f"🔍 **Análise:** Projeto {tipo_projeto} detectado")
                
                # Gera preview
                proposta_preview = estruturar_ideia_avancada(preview_data, preview_mode=True)
                
                st.markdown('<div class="preview-box">', unsafe_allow_html=True)
                st.subheader("👁️ Preview da Proposta")
                st.markdown(proposta_preview)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Feedback motivador (sem mencionar NPS)
                st.success("✨ **Excelente!** Sua ideia tem potencial para gerar impacto positivo!")
                st.info("💡 **Dica:** Se ficou bom, clique em 'Estruturar e Enviar' para receber a versão completa!")

# Processamento Final
if enviar_final:
    if not nome or not ideia_curta:
        st.error("⚠️ Preencha pelo menos nome e ideia para continuar.")
    else:
        validacao = validar_entrada(nome, ideia_curta)
        if not validacao["valido"]:
            st.error(f"❌ {validacao['erro']}")
        else:
            with st.spinner("🚀 Estruturando sua ideia com análise inteligente..."):
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
                
                # Detecta tipo e calcula NPS (em background)
                tipo_projeto = detectar_tipo_projeto(ideia_curta, area)
                pontuacao_nps, justificativa_nps = calcular_pontuacao_nps(ideia_curta, area, foco_principal)
                
                # Adiciona análise aos dados
                dados_completos["tipo_projeto"] = tipo_projeto
                dados_completos["pontuacao_nps"] = pontuacao_nps
                dados_completos["justificativa_nps"] = justificativa_nps
                
                # Mostra apenas tipo de projeto (sem NPS)
                st.info(f"🔍 **Projeto {tipo_projeto}** detectado e sendo estruturado...")
                
                # Gera proposta completa
                proposta_completa = estruturar_ideia_avancada(dados_completos)
                
                # Gera JSON estruturado
                json_proposta = None
                try:
                    json_proposta = gerar_json_proposta(dados_completos, proposta_completa)
                    
                    if json_proposta:
                        st.success("📄 Proposta estruturada e dados organizados!")
                        
                        # Mostra métricas básicas (sem NPS)
                        col_json1, col_json2, col_json3 = st.columns(3)
                        with col_json1:
                            st.metric("🆔 ID", json_proposta['metadata']['id'])
                        with col_json2:
                            st.metric("🔍 Tipo", json_proposta['analise']['tipo_projeto'])
                        with col_json3:
                            st.metric("📈 Complexidade", json_proposta['analise']['complexidade'])
                            
                except Exception as e:
                    st.warning(f"⚠️ Erro ao gerar dados estruturados: {str(e)}")
                
                try:
                    # Envia email (com pontuação NPS no título para liderança)
                    enviar_email_estruturado(dados_completos, proposta_completa, json_proposta)
                    
                    # Salva no histórico
                    proposta_id, json_salvo = salvar_historico(dados_completos, proposta_completa)
                    
                    # Feedback de sucesso (sem mencionar NPS)
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown(f"### 🎉 Proposta Enviada com Sucesso!")
                    st.markdown(f"""
                    **{nome}**, sua ideia foi estruturada e enviada profissionalmente!
                    
                    🔍 **Tipo:** Projeto {tipo_projeto}
                    📧 **Email enviado para:** Liderança Carglass  
                    📋 **Nível:** {nivel_detalhamento}  
                    🎯 **Foco:** {foco_principal}  
                    ⏱️ **Processado em:** {time.strftime("%H:%M:%S")}
                    📄 **ID da Proposta:** {proposta_id if proposta_id else "Gerado"}
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Animação de sucesso
                    st.balloons()
                    st.success("🎊 **PARABÉNS!** Sua ideia foi transformada em uma proposta executável!")
                    
                    # Próximos passos (sem mencionar NPS)
                    st.subheader("🎯 Próximos Passos")
                    st.info("📋 **Expectativa:** A liderança analisará sua proposta e retornará em breve com feedback")
                    st.markdown("""
                    **O que acontece agora:**
                    - ✅ Sua proposta foi enviada com estrutura completa
                    - 📊 Análise de viabilidade será realizada
                    - 👥 Equipe técnica avaliará implementação
                    - 💬 Feedback será enviado diretamente para você
                    """)
                    
                    # Mostra resumo da proposta
                    with st.expander("📋 Resumo da Proposta Enviada"):
                        st.markdown(proposta_completa[:500] + "...")
                        st.info("💌 **A versão completa foi enviada por email com estrutura detalhada de projeto!**")
                    
                    # Mostra informações técnicas básicas
                    if json_proposta:
                        with st.expander("🔧 Detalhes Técnicos da Análise"):
                            col_analise1, col_analise2 = st.columns(2)
                            
                            with col_analise1:
                                st.markdown("**📊 Análise do Projeto:**")
                                st.write(f"• **Tipo:** {json_proposta['analise']['tipo_projeto']}")
                                st.write(f"• **Complexidade:** {json_proposta['analise']['complexidade']}")
                                st.write(f"• **Categoria:** {json_proposta['analise']['categoria_projeto']}")
                                
                            with col_analise2:
                                st.markdown("**⚡ Características:**")
                                st.write(f"• **Viabilidade:** {json_proposta['analise']['viabilidade_tecnica']}")
                                st.write(f"• **Impacto:** {json_proposta['analise']['impacto_estimado']}")
                                st.write(f"• **Prioridade:** {json_proposta['analise']['prioridade_sugerida']}")
                    
                    # Motivação para próximas ideias
                    st.subheader("💡 Continue Inovando!")
                    st.success("Sua participação é valiosa! Continue enviando ideias - cada contribuição ajuda a Carglass a evoluir.")
                    
                except Exception as e:
                    st.error(f"⚠️ Erro ao processar: {str(e)}")
                    st.info("🔧 Nossa equipe foi notificada. Tente novamente em alguns minutos.") if pontuacao_nps >= 50 else "warning"
                    
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown(f"### {emoji_sucesso} Proposta Enviada com Sucesso!")
                    st.markdown(f"""
                    **{nome}**, sua ideia foi estruturada e enviada com foco no NPS!
                    
                    📊 **Pontuação NPS:** {pontuacao_nps}/100 ({categoria_nps})
                    🔍 **Tipo:** Projeto {tipo_projeto}
                    📧 **Email enviado para:** Liderança Carglass  
                    📋 **Nível:** {nivel_detalhamento}  
                    🎯 **Foco:** {foco_principal}  
                    ⏱️ **Processado em:** {time.strftime("%H:%M:%S")}
                    📄 **JSON ID:** {proposta_id if proposta_id else "Não gerado"}
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Animação baseada na pontuação
                    if pontuacao_nps >= 80:
                        st.balloons()
                        st.success("🎉 **PARABÉNS!** Sua ideia tem potencial TRANSFORMADOR para o NPS!")
                    elif pontuacao_nps >= 65:
                        st.balloons()
                        st.info("🎊 **MUITO BOM!** Sua ideia pode ter ALTO IMPACTO no NPS!")
                    elif pontuacao_nps >= 45:
                        st.info("👏 **BOM TRABALHO!** Sua ideia tem MÉDIO IMPACTO no NPS.")
                    else:
                        st.warning("💡 **DICA:** Para maior impacto no NPS, foque mais na experiência direta do cliente.")
# Seção educativa
st.divider()
st.header("🎓 Aprenda sobre Estruturação de Projetos")

col_edu1, col_edu2, col_edu3 = st.columns(3)

with col_edu1:
    st.subheader("🔍 Tipos de Projeto")
    st.markdown("""
    **🏗️ TECNOLÓGICO:**
    - Apps e sistemas
    - Automação digital
    - Dashboards e relatórios
    - Integração de sistemas
    
    **📋 PROCESSO:**
    - Procedimentos e formulários
    - Workflows manuais
    - Melhoria operacional
    - Treinamentos e capacitação
    """)

with col_edu2:
    st.subheader("🎯 Como Ter Sucesso")
    st.markdown("""
    **Para ideias impactantes:**
    - Foque no problema específico
    - Pense no usuário final
    - Considere a viabilidade
    - Mencione benefícios claros
    - Seja específico nos detalhes
    """)

with col_edu3:
    st.subheader("🚀 Processo de Avaliação")
    st.markdown("""
    **Etapas de análise:**
    - Viabilidade técnica
    - Impacto no negócio
    - Recursos necessários
    - Cronograma estimado
    - Retorno sobre investimento
    """)

# Exemplos de ideias bem-sucedidas
st.subheader("💡 Exemplos de Ideias Bem Estruturadas")

col_ex1, col_ex2 = st.columns(2)

with col_ex1:
    st.markdown("""
    **🏗️ PROJETOS TECNOLÓGICOS:**
    - App para acompanhamento de serviços
    - Dashboard de indicadores em tempo real
    - Sistema de agendamento automatizado
    - Integração com fornecedores
    """)

with col_ex2:
    st.markdown("""
    **📋 PROJETOS DE PROCESSO:**
    - Simplificação do check-in
    - Novo fluxo de aprovação
    - Melhoria na comunicação interna
    - Padronização de procedimentos
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>MindGlass V2</strong> | Desenvolvido por Vinícius Paschoa | Carglass Innovation Lab</p>
    <p>💡 <em>Transformando ideias em projetos executáveis desde 2024</em></p>
    <p>🎯 <em>Toda ideia é valiosa - nossa IA estrutura profissionalmente para você</em></p>
</div>
""", unsafe_allow_html=True)
