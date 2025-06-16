import streamlit as st
from openai import OpenAI
import yagmail
import json
import re
from datetime import datetime
import hashlib

# 🔑 Conectando ao OpenAI com modelo mais avançado
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def validar_entrada(nome, ideia):
    """Valida as entradas do usuário"""
    if not nome or len(nome.strip()) < 2:
        return {"valido": False, "erro": "Nome deve ter pelo menos 2 caracteres"}
    
    if not ideia or len(ideia.strip()) < 10:
        return {"valido": False, "erro": "Ideia deve ter pelo menos 10 caracteres"}
    
    if len(ideia.strip()) > 2000:
        return {"valido": False, "erro": "Ideia muito longa (máximo 2000 caracteres)"}
    
    # Verifica caracteres especiais maliciosos
    if re.search(r'[<>{}[\]\\]', ideia):
        return {"valido": False, "erro": "Caracteres especiais não permitidos"}
    
    return {"valido": True, "erro": None}

def estruturar_ideia_avancada(dados, preview_mode=False):
    """Gera proposta estruturada usando GPT-4 com prompt avançado"""
    
    nome = dados["nome"]
    area = dados["area"]
    ideia = dados["ideia"]
    nivel = dados["nivel"]
    foco = dados["foco"]
    problema = dados.get("problema", "")
    recursos = dados.get("recursos", "")
    prazo = dados.get("prazo", "")
    
    # Prompt inteligente baseado no nível
    if preview_mode:
        prompt = f"""
        CONTEXTO: Você é um consultor sênior da Carglass especializado em estruturação de projetos.
        
        TAREFA: Gere um PREVIEW executivo da ideia do colaborador {nome} da área {area}.
        
        IDEIA: "{ideia}"
        FOCO: {foco}
        {f"PROBLEMA A RESOLVER: {problema}" if problema else ""}
        
        FORMATO DE SAÍDA (PREVIEW):
        ## 🎯 **Resumo Executivo**
        [Descrição clara em 2-3 linhas]
        
        ## 💡 **Valor Agregado**
        [Principal benefício em 1 linha]
        
        ## ⚡ **Implementação**
        [Abordagem simplificada em 2-3 pontos]
        
        Mantenha conciso e focado. Este é apenas um preview.
        """
    else:
        prompt = f"""
        CONTEXTO: Você é um consultor sênior da Carglass especializado em estruturação de projetos de inovação.
        
        MISSÃO: Transformar a ideia do colaborador {nome} ({area}) em uma proposta COMPLETA e EXECUTÁVEL.
        
        ENTRADA:
        - **Ideia:** "{ideia}"
        - **Foco:** {foco}
        - **Nível:** {nivel}
        {f"- **Problema atual:** {problema}" if problema else ""}
        {f"- **Recursos disponíveis:** {recursos}" if recursos else ""}
        {f"- **Prazo desejado:** {prazo}" if prazo else ""}
        
        FORMATO DE SAÍDA OBRIGATÓRIO:
        
        # 🎯 **PROPOSTA: [Nome do Projeto]**
        
        ## 📋 **1. RESUMO EXECUTIVO**
        [Descrição clara e objetiva em 3-4 linhas sobre o que é o projeto]
        
        ## 🎯 **2. PROBLEMA & OPORTUNIDADE**
        - **Problema identificado:** [Descreva o problema]
        - **Oportunidade:** [Qual oportunidade isso representa]
        - **Impacto esperado:** [Benefícios quantificáveis]
        
        ## 🏗️ **3. ESTRUTURA TÉCNICA SUGERIDA**
        ### **Tecnologias Recomendadas:**
        - **Frontend:** [Tecnologia sugerida]
        - **Backend:** [Tecnologia sugerida]
        - **Banco de Dados:** [Tecnologia sugerida]
        - **Infraestrutura:** [Cloud/On-premise]
        
        ### **Arquitetura Simplificada:**
        ```
        [Diagrama textual da arquitetura]
        ```
        
        ## 📂 **4. ESTRUTURA DE DESENVOLVIMENTO**
        ### **Organização do Repositório:**
        ```
        projeto-nome/
        ├── README.md
        ├── requirements.txt
        ├── app/
        │   ├── main.py
        │   ├── models/
        │   ├── views/
        │   └── utils/
        ├── tests/
        ├── docs/
        └── deploy/
        ```
        
        ### **Metodologia Sugerida:**
        - **Framework:** [Scrum/Kanban]
        - **Sprints:** [Duração sugerida]
        - **Ferramentas:** [GitHub, Jira, etc.]
        
        ## 📅 **5. CRONOGRAMA DETALHADO**
        ### **Fase 1: Planejamento (Semana 1-2)**
        - [ ] Definição de requisitos
        - [ ] Prototipagem
        - [ ] Validação com stakeholders
        
        ### **Fase 2: Desenvolvimento (Semana 3-8)**
        - [ ] Setup do ambiente
        - [ ] Desenvolvimento core
        - [ ] Testes unitários
        - [ ] Integração
        
        ### **Fase 3: Deploy e Validação (Semana 9-10)**
        - [ ] Deploy em ambiente de teste
        - [ ] Testes de usuário
        - [ ] Correções e melhorias
        - [ ] Go-live
        
        ## 🎯 **6. MÉTRICAS DE SUCESSO**
        - **KPI Principal:** [Métrica principal]
        - **KPIs Secundários:** [Outras métricas]
        - **Métodos de Medição:** [Como medir]
        
        ## 💰 **7. ANÁLISE DE VIABILIDADE**
        ### **Investimento Estimado:**
        - **Desenvolvimento:** [Estimativa de horas/valor]
        - **Infraestrutura:** [Custos mensais]
        - **Manutenção:** [Custos recorrentes]
        
        ### **ROI Projetado:**
        - **Economia esperada:** [Valor]
        - **Payback:** [Tempo]
        
        ## ⚠️ **8. RISCOS & MITIGAÇÕES**
        - **Risco 1:** [Descrição] → **Mitigação:** [Como resolver]
        - **Risco 2:** [Descrição] → **Mitigação:** [Como resolver]
        
        ## 🚀 **9. PRÓXIMOS PASSOS IMEDIATOS**
        1. **Aprovação da proposta** (Responsável: Liderança)
        2. **Formação do time** (Responsável: RH/TI)
        3. **Refinamento de requisitos** (Responsável: {nome})
        4. **Kick-off do projeto** (Prazo: 2 semanas)
        
        ## 👥 **10. EQUIPE SUGERIDA**
        - **Product Owner:** [Perfil]
        - **Desenvolvedores:** [Quantidade e perfil]
        - **Designer:** [Se necessário]
        - **DevOps:** [Se necessário]
        
        ---
        
        **Proposta gerada por:** MindGlass V2 | **Autor da ideia:** {nome} | **Data:** {datetime.now().strftime("%d/%m/%Y")}
        """
    
    try:
        resposta = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Modelo mais avançado
            messages=[
                {
                    "role": "system", 
                    "content": "Você é um consultor sênior especializado em estruturação de projetos de inovação para empresas. Seja preciso, prático e focado em resultados executáveis."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.3,  # Mais determinístico
            max_tokens=2500 if not preview_mode else 800,
        )
        
        return resposta.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Erro ao processar com IA: {str(e)}"

def gerar_json_proposta(dados, proposta):
    """Gera JSON estruturado com todos os dados da proposta"""
    try:
        # Gera ID único para a proposta
        proposta_id = hashlib.md5(f"{dados['nome']}{dados['ideia']}{datetime.now()}".encode()).hexdigest()[:8]
        timestamp = datetime.now()
        
        # Extrai informações estruturadas da proposta (parsing básico)
        proposta_estruturada = extrair_estrutura_proposta(proposta)
        
        json_proposta = {
            "metadata": {
                "id": proposta_id,
                "versao": "2.0",
                "timestamp": timestamp.isoformat(),
                "data_criacao": timestamp.strftime("%d/%m/%Y %H:%M:%S"),
                "sistema": "MindGlass V2",
                "status": "processado"
            },
            "autor": {
                "nome": dados["nome"],
                "area": dados["area"],
                "area_detalhada": dados.get("area", "").split(" - ")[0] if " - " in dados.get("area", "") else dados.get("area", "")
            },
            "entrada": {
                "ideia_original": dados["ideia"],
                "nivel_detalhamento": dados.get("nivel", "Intermediário"),
                "foco_principal": dados.get("foco", "Não especificado"),
                "problema_contexto": dados.get("problema", ""),
                "recursos_disponiveis": dados.get("recursos", ""),
                "prazo_desejado": dados.get("prazo", ""),
                "caracteres_ideia": len(dados["ideia"].strip()),
                "palavras_chave": extrair_palavras_chave(dados["ideia"])
            },
            "saida": {
                "proposta_completa": proposta,
                "resumo_executivo": proposta_estruturada.get("resumo", ""),
                "tecnologias_sugeridas": proposta_estruturada.get("tecnologias", []),
                "cronograma_estimado": proposta_estruturada.get("cronograma", ""),
                "investimento_estimado": proposta_estruturada.get("investimento", ""),
                "riscos_identificados": proposta_estruturada.get("riscos", []),
                "metricas_sucesso": proposta_estruturada.get("metricas", [])
            },
            "analise": {
                "complexidade": avaliar_complexidade(dados["ideia"]),
                "categoria_projeto": classificar_projeto(dados["ideia"], dados.get("foco", "")),
                "viabilidade_tecnica": "Alta",  # Poderia ser calculada
                "impacto_estimado": calcular_impacto(dados.get("foco", "")),
                "prioridade_sugerida": sugerir_prioridade(dados)
            },
            "proximos_passos": {
                "acao_imediata": "Análise pela liderança",
                "responsavel_proximo": "Liderança da área",
                "prazo_resposta": "5 dias úteis",
                "etapas_aprovacao": [
                    "Revisão técnica",
                    "Validação de recursos",
                    "Aprovação orçamentária",
                    "Formação de equipe"
                ]
            },
            "integracoes": {
                "pode_integrar_sistemas_existentes": True,
                "sistemas_relacionados": identificar_sistemas_relacionados(dados["area"]),
                "apis_necessarias": [],
                "dependencias_externas": []
            }
        }
        
        return json_proposta
        
    except Exception as e:
        st.error(f"Erro ao gerar JSON: {str(e)}")
        return None

def extrair_estrutura_proposta(proposta):
    """Extrai informações estruturadas da proposta gerada pela IA"""
    estrutura = {
        "resumo": "",
        "tecnologias": [],
        "cronograma": "",
        "investimento": "",
        "riscos": [],
        "metricas": []
    }
    
    try:
        linhas = proposta.split('\n')
        secao_atual = ""
        
        for linha in linhas:
            linha_clean = linha.strip()
            
            # Identifica seções
            if "RESUMO EXECUTIVO" in linha_clean.upper():
                secao_atual = "resumo"
            elif "TECNOLOGIAS RECOMENDADAS" in linha_clean.upper():
                secao_atual = "tecnologias"
            elif "CRONOGRAMA" in linha_clean.upper():
                secao_atual = "cronograma"
            elif "INVESTIMENTO" in linha_clean.upper():
                secao_atual = "investimento"
            elif "RISCOS" in linha_clean.upper():
                secao_atual = "riscos"
            elif "MÉTRICAS" in linha_clean.upper():
                secao_atual = "metricas"
            
            # Extrai conteúdo baseado na seção
            elif secao_atual == "resumo" and linha_clean and not linha_clean.startswith('#'):
                if estrutura["resumo"]:
                    estrutura["resumo"] += " " + linha_clean
                else:
                    estrutura["resumo"] = linha_clean
            
            elif secao_atual == "tecnologias" and "**" in linha_clean:
                tech = linha_clean.replace("*", "").replace("-", "").strip()
                if tech:
                    estrutura["tecnologias"].append(tech)
                    
    except Exception:
        pass  # Se falhar, retorna estrutura vazia
    
    return estrutura

def extrair_palavras_chave(texto):
    """Extrai palavras-chave da ideia"""
    # Lista de palavras comuns para filtrar
    stop_words = {'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'da', 'do', 'das', 'dos', 
                  'para', 'por', 'com', 'em', 'na', 'no', 'nas', 'nos', 'que', 'se', 'é', 'são', 
                  'ter', 'tem', 'foi', 'ser', 'estar', 'esse', 'essa', 'isso', 'isso', 'como', 'mais'}
    
    palavras = re.findall(r'\b\w+\b', texto.lower())
    palavras_filtradas = [p for p in palavras if len(p) > 3 and p not in stop_words]
    
    # Retorna as 5 palavras mais frequentes (simulação)
    return list(set(palavras_filtradas))[:5]

def avaliar_complexidade(ideia):
    """Avalia complexidade baseada em palavras-chave"""
    palavras_alta_complexidade = ['integração', 'machine learning', 'ia', 'blockchain', 'microserviços', 'big data']
    palavras_media_complexidade = ['automação', 'dashboard', 'relatório', 'api', 'mobile']
    
    ideia_lower = ideia.lower()
    
    if any(palavra in ideia_lower for palavra in palavras_alta_complexidade):
        return "Alta"
    elif any(palavra in ideia_lower for palavra in palavras_media_complexidade):
        return "Média"
    else:
        return "Baixa"

def classificar_projeto(ideia, foco):
    """Classifica o tipo de projeto"""
    categorias = {
        "Automação": ["automação", "automatizar", "robô", "bot"],
        "Dashboard/BI": ["dashboard", "relatório", "análise", "dados", "métricas"],
        "Mobile": ["app", "mobile", "celular", "smartphone"],
        "Integração": ["integrar", "conectar", "sincronizar", "api"],
        "UX/Interface": ["interface", "experiência", "usuário", "design"],
        "Processo": ["processo", "workflow", "fluxo", "otimizar"]
    }
    
    ideia_lower = ideia.lower()
    for categoria, palavras in categorias.items():
        if any(palavra in ideia_lower for palavra in palavras):
            return categoria
    
    return foco if foco != "Não especificado" else "Geral"

def calcular_impacto(foco):
    """Calcula impacto estimado baseado no foco"""
    impactos = {
        "Redução de Custos": "Alto",
        "Experiência do Cliente": "Alto", 
        "Automação": "Médio",
        "Melhoria de Processo": "Médio",
        "Nova Tecnologia": "Baixo",
        "Inovação": "Baixo"
    }
    return impactos.get(foco, "Médio")

def sugerir_prioridade(dados):
    """Sugere prioridade baseada em múltiplos fatores"""
    pontos = 0
    
    # Baseado no foco
    if dados.get("foco") in ["Redução de Custos", "Experiência do Cliente"]:
        pontos += 3
    elif dados.get("foco") in ["Automação", "Melhoria de Processo"]:
        pontos += 2
    else:
        pontos += 1
    
    # Baseado no prazo
    if dados.get("prazo") == "Urgente (1 mês)":
        pontos += 3
    elif dados.get("prazo") == "Curto (3 meses)":
        pontos += 2
    
    # Baseado na área
    if dados.get("area", "").startswith("TI"):
        pontos += 1
    
    if pontos >= 5:
        return "Alta"
    elif pontos >= 3:
        return "Média"
    else:
        return "Baixa"

def identificar_sistemas_relacionados(area):
    """Identifica sistemas que podem estar relacionados baseado na área"""
    sistemas_por_area = {
        "TI": ["Sistema ERP", "Active Directory", "Monitoramento"],
        "RH": ["Sistema RH", "Portal do Colaborador", "Avaliação"],
        "Financeiro": ["ERP Financeiro", "BI Financeiro", "Contas a Pagar"],
        "Atendimento": ["CRM", "Sistema de Tickets", "Chat"],
        "Loja": ["PDV", "Estoque", "CRM Loja"],
        "Oficina": ["Sistema Oficina", "Ordens de Serviço", "Estoque Peças"],
        "Marketing": ["CRM Marketing", "Analytics", "Email Marketing"]
    }
    
    area_base = area.split(" - ")[0] if " - " in area else area
    return sistemas_por_area.get(area_base, ["Sistema Geral"])

def salvar_json_proposta(json_proposta):
    """Salva o JSON da proposta"""
    try:
        # Em ambiente real, salvaria em banco de dados ou storage
        # Por enquanto, apenas mostra no Streamlit
        
        json_formatado = json.dumps(json_proposta, indent=2, ensure_ascii=False)
        
        # Mostra no Streamlit para debug/visualização
        with st.expander("📄 JSON Gerado (Clique para visualizar)"):
            st.code(json_formatado, language="json")
        
        # Aqui você poderia salvar em arquivo, banco de dados, etc.
        # Exemplo de salvamento em arquivo:
        # with open(f"propostas/proposta_{json_proposta['metadata']['id']}.json", "w", encoding="utf-8") as f:
        #     json.dump(json_proposta, f, indent=2, ensure_ascii=False)
        
        return json_proposta['metadata']['id']
        
    except Exception as e:
        st.error(f"Erro ao salvar JSON: {str(e)}")
        return None

def enviar_email_estruturado(dados, proposta, json_proposta=None):
    """Envia email com estrutura completa ensinando lógica de criação"""
    
    nome = dados["nome"]
    area = dados["area"]
    
    # Assunto mais descritivo
    assunto = f"🚀 NOVA PROPOSTA ESTRUTURADA - {nome} ({area}) | MindGlass V2"
    
    # Adiciona informações do JSON se disponível
    json_info = ""
    if json_proposta:
        json_info = f"""
═══════════════════════════════════════════════════════════════
📊 DADOS ESTRUTURADOS (JSON):
═══════════════════════════════════════════════════════════════

🆔 ID da Proposta: {json_proposta['metadata']['id']}
📈 Complexidade: {json_proposta['analise']['complexidade']}
🎯 Categoria: {json_proposta['analise']['categoria_projeto']}
⚡ Prioridade: {json_proposta['analise']['prioridade_sugerida']}
💰 Impacto: {json_proposta['analise']['impacto_estimado']}

🔗 JSON Completo: Arquivo anexo ou sistema interno
"""
    
    # Corpo do email ensinando a lógica
    corpo_email = f"""
═══════════════════════════════════════════════════════════════
🎯 PROPOSTA ESTRUTURADA - MINDGLASS V2
═══════════════════════════════════════════════════════════════

📋 METADADOS DO PROJETO:
• Autor: {nome}
• Área: {area}
• Data: {datetime.now().strftime("%d/%m/%Y às %H:%M")}
• Nível: {dados.get('nivel', 'Intermediário')}
• Foco: {dados.get('foco', 'Não especificado')}
{json_info}
═══════════════════════════════════════════════════════════════
📝 IDEIA ORIGINAL (INPUT):
═══════════════════════════════════════════════════════════════

"{dados['ideia']}"

═══════════════════════════════════════════════════════════════
🧠 PROPOSTA ESTRUTURADA (OUTPUT IA):
═══════════════════════════════════════════════════════════════

{proposta}

═══════════════════════════════════════════════════════════════
🎓 LÓGICA DE ESTRUTURAÇÃO DE PROJETOS - APRENDA CONOSCO!
═══════════════════════════════════════════════════════════════

Este email foi gerado automaticamente seguindo nossa metodologia
de estruturação de projetos de inovação. Veja como funciona:

🔄 **PROCESSO DE TRANSFORMAÇÃO:**

1. **CAPTURA INTELIGENTE**
   ✓ Coletamos ideia simples do colaborador
   ✓ Validamos entrada e contexto
   ✓ Enriquecemos com dados adicionais

2. **PROCESSAMENTO IA**
   ✓ Usamos GPT-4 Turbo para análise avançada
   ✓ Aplicamos templates de estruturação
   ✓ Geramos proposta executável

3. **ESTRUTURAÇÃO JSON**
   ✓ Convertemos para formato estruturado
   ✓ Adicionamos metadados e análises
   ✓ Categorizamos e priorizamos automaticamente

4. **ENTREGA ESTRUTURADA**
   ✓ Formato padrão para todas as propostas
   ✓ Cronograma detalhado
   ✓ Análise de viabilidade técnica
   ✓ Métricas de sucesso definidas

🏗️ **ESTRUTURA PADRÃO DE PROJETOS CARGLASS:**

📋 Resumo Executivo
🎯 Problema & Oportunidade  
🏗️ Estrutura Técnica
📂 Organização do Desenvolvimento
📅 Cronograma Detalhado
🎯 Métricas de Sucesso
💰 Análise de Viabilidade
⚠️ Riscos & Mitigações
🚀 Próximos Passos
👥 Equipe Sugerida

💡 **METODOLOGIA APLICADA:**
• Design Thinking para entender o problema
• Lean Startup para validação rápida
• Scrum para execução ágil
• DevOps para entrega contínua

🔧 **STACK TECNOLÓGICO PADRÃO:**
• Frontend: React/Vue.js
• Backend: Python/Node.js
• Database: PostgreSQL/MongoDB
• Cloud: AWS/Azure
• CI/CD: GitHub Actions
• Monitoramento: DataDog/New Relic

═══════════════════════════════════════════════════════════════
📊 PRÓXIMAS AÇÕES RECOMENDADAS:
═══════════════════════════════════════════════════════════════

1. **ANÁLISE INICIAL** (Liderança - 2 dias)
   • Revisar proposta estruturada
   • Validar alinhamento estratégico
   • Decidir sobre continuidade

2. **REFINAMENTO** (Product Owner - 1 semana)
   • Detalhar requisitos específicos
   • Validar premissas técnicas
   • Definir critérios de aceite

3. **APROVAÇÃO** (Comitê - 1 semana)
   • Apresentar business case
   • Aprovar orçamento
   • Definir timeline

4. **KICK-OFF** (Time - 2 semanas)
   • Formar equipe
   • Setup do ambiente
   • Iniciar desenvolvimento

═══════════════════════════════════════════════════════════════
🎯 MÉTRICAS DE ACOMPANHAMENTO:
═══════════════════════════════════════════════════════════════

Para garantir o sucesso, sugerimos acompanhar:

📈 **Métricas de Produto:**
• Taxa de adoção pelos usuários
• Tempo de execução de tarefas
• Satisfação do cliente (NPS)
• Redução de erros/retrabalho

📊 **Métricas de Projeto:**
• Velocity da equipe
• Burn-down das sprints
• Qualidade do código (coverage)
• Tempo de deploy

💰 **Métricas de Negócio:**
• ROI do projeto
• Redução de custos
• Aumento de receita
• Eficiência operacional

═══════════════════════════════════════════════════════════════
🤝 COMO RESPONDER A ESTA PROPOSTA:
═══════════════════════════════════════════════════════════════

✅ **SE APROVAR:**
• Responda com "APROVADO" + próximos passos
• Defina sponsor do projeto
• Aloque recursos necessários

🔄 **SE PRECISAR DE AJUSTES:**
• Especifique mudanças necessárias
• Solicite nova versão via MindGlass
• Mantenha {nome} no loop

❌ **SE REJEITAR:**
• Explique motivos da rejeição
• Sugira melhorias para próximas ideias
• Reconheça o esforço do colaborador

═══════════════════════════════════════════════════════════════

Este email foi gerado automaticamente pelo MindGlass V2
Desenvolvido por Vinícius Augusto | Carglass Innovation Lab

💡 Quer saber mais sobre nossa metodologia? 
📧 Entre em contato conosco!

═══════════════════════════════════════════════════════════════
"""
    
    # Envio do email
    try:
        yag = yagmail.SMTP(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASS"])
        yag.send(
            to=st.secrets["EMAIL_DESTINO"],
            subject=assunto,
            contents=corpo_email
        )
    except Exception as e:
        raise Exception(f"Erro ao enviar email: {str(e)}")

def salvar_historico(dados, proposta):
    """Salva histórico da proposta"""
    try:
        # Gera JSON estruturado
        json_proposta = gerar_json_proposta(dados, proposta)
        
        if json_proposta:
            # Salva o JSON
            proposta_id = salvar_json_proposta(json_proposta)
            
            # Log de sucesso
            st.success(f"📝 Proposta {proposta_id} processada e JSON gerado!")
            
            return proposta_id, json_proposta
        else:
            return None, None
        
    except Exception as e:
        st.error(f"Erro ao salvar histórico: {str(e)}")
        return None, None
