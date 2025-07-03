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

def detectar_tipo_projeto(ideia, area):
    """Detecta se é projeto tecnológico ou de processo usando IA"""
    
    prompt_deteccao = f"""
    Analise a seguinte ideia e determine se é um projeto TECNOLÓGICO ou de PROCESSO:
    
    ÁREA: {area}
    IDEIA: "{ideia}"
    
    CRITÉRIOS:
    - TECNOLÓGICO: Envolve desenvolvimento de software, apps, sistemas, automação digital, APIs, dashboards, etc.
    - PROCESSO: Envolve mudanças de procedimentos, formulários físicos, workflows manuais, treinamentos, políticas, etc.
    
    Responda apenas com: "TECNOLÓGICO" ou "PROCESSO"
    """
    
    try:
        resposta = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt_deteccao}],
            temperature=0.1,
            max_tokens=20
        )
        
        resultado = resposta.choices[0].message.content.strip().upper()
        return "TECNOLÓGICO" if "TECNOLÓGICO" in resultado else "PROCESSO"
        
    except Exception:
        # Fallback: usa palavras-chave para detectar
        palavras_tech = ['app', 'sistema', 'software', 'digital', 'automação', 'api', 'dashboard', 'site', 'plataforma']
        palavras_processo = ['formulário', 'papel', 'procedimento', 'manual', 'treinamento', 'política', 'workflow']
        
        ideia_lower = ideia.lower()
        
        score_tech = sum(1 for palavra in palavras_tech if palavra in ideia_lower)
        score_processo = sum(1 for palavra in palavras_processo if palavra in ideia_lower)
        
        return "TECNOLÓGICO" if score_tech > score_processo else "PROCESSO"

def calcular_pontuacao_nps(ideia, area, foco):
    """Calcula pontuação de 0-100 baseada no impacto no NPS usando IA"""
    
    prompt_nps = f"""
    Como especialista em NPS (Net Promoter Score), avalie esta ideia de 0 a 100 pontos:
    
    CONTEXTO CARGLASS:
    - Empresa de reparo automotivo
    - Foco em experiência do cliente
    - NPS atual precisa melhorar
    - Clientes valorizam: rapidez, transparência, qualidade, conveniência
    
    IDEIA PARA AVALIAR:
    Área: {area}
    Foco: {foco}
    Descrição: "{ideia}"
    
    CRITÉRIOS DE PONTUAÇÃO:
    90-100: Impacto TRANSFORMADOR no NPS (revoluciona experiência do cliente)
    70-89: Impacto ALTO no NPS (melhora significativa na experiência)
    50-69: Impacto MÉDIO no NPS (melhora perceptível para o cliente)
    30-49: Impacto BAIXO no NPS (melhora interna com reflexo indireto)
    0-29: Impacto MÍNIMO no NPS (benefício principalmente interno)
    
    EXEMPLOS DE ALTO IMPACTO:
    - App para cliente acompanhar reparo em tempo real (95 pontos)
    - Sistema de agendamento online inteligente (88 pontos)
    - Comunicação proativa sobre status do serviço (82 pontos)
    
    RESPONDA APENAS COM O NÚMERO (0-100) E UMA JUSTIFICATIVA DE 1 LINHA:
    Formato: "85 - Justificativa aqui"
    """
    
    try:
        resposta = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt_nps}],
            temperature=0.2,
            max_tokens=100
        )
        
        resultado = resposta.choices[0].message.content.strip()
        
        # Extrai o número da resposta
        match = re.search(r'(\d+)', resultado)
        if match:
            pontuacao = int(match.group(1))
            # Extrai justificativa
            justificativa = resultado.split('-', 1)[1].strip() if '-' in resultado else "Avaliação automática"
            return min(max(pontuacao, 0), 100), justificativa
        else:
            return 50, "Avaliação padrão"
            
    except Exception:
        # Fallback baseado em palavras-chave
        palavras_alto_nps = ['cliente', 'experiência', 'acompanhar', 'transparência', 'comunicação', 'rapidez']
        palavras_medio_nps = ['processo', 'qualidade', 'eficiência', 'automação']
        
        ideia_lower = ideia.lower()
        score_alto = sum(1 for palavra in palavras_alto_nps if palavra in ideia_lower)
        score_medio = sum(1 for palavra in palavras_medio_nps if palavra in ideia_lower)
        
        if score_alto >= 2:
            return 75, "Alto impacto potencial na experiência do cliente"
        elif score_medio >= 1:
            return 55, "Impacto médio na operação e indiretamente no cliente"
        else:
            return 35, "Impacto principalmente interno"

def estruturar_ideia_avancada(dados, preview_mode=False):
    """Gera proposta estruturada usando GPT-4 com diferenciação por tipo de projeto"""
    
    nome = dados["nome"]
    area = dados["area"]
    ideia = dados["ideia"]
    nivel = dados["nivel"]
    foco = dados["foco"]
    problema = dados.get("problema", "")
    recursos = dados.get("recursos", "")
    prazo = dados.get("prazo", "")
    
    # Detecta tipo de projeto
    tipo_projeto = detectar_tipo_projeto(ideia, area)
    
    # Calcula pontuação NPS
    pontuacao_nps, justificativa_nps = calcular_pontuacao_nps(ideia, area, foco)
    
    # Armazena no dados para uso posterior
    dados["tipo_projeto"] = tipo_projeto
    dados["pontuacao_nps"] = pontuacao_nps
    dados["justificativa_nps"] = justificativa_nps
    
    if preview_mode:
        prompt = f"""
        CONTEXTO: Você é um consultor sênior da Carglass especializado em estruturação de projetos.
        
        TAREFA: Gere um PREVIEW executivo da ideia do colaborador {nome} da área {area}.
        
        TIPO DE PROJETO DETECTADO: {tipo_projeto}
        PONTUAÇÃO NPS: {pontuacao_nps}/100 - {justificativa_nps}
        
        IDEIA: "{ideia}"
        FOCO: {foco}
        {f"PROBLEMA A RESOLVER: {problema}" if problema else ""}
        
        FORMATO DE SAÍDA (PREVIEW):
        ## 🎯 **Resumo Executivo**
        [Descrição clara em 2-3 linhas]
        
        ## 📊 **Impacto no NPS**
        [Como esta ideia pode melhorar a experiência do cliente]
        
        ## ⚡ **Implementação**
        [Abordagem simplificada em 2-3 pontos]
        
        Mantenha conciso e focado. Este é apenas um preview.
        """
    else:
        if tipo_projeto == "TECNOLÓGICO":
            prompt = f"""
            CONTEXTO: Você é um consultor sênior da Carglass especializado em estruturação de projetos de inovação TECNOLÓGICA.
            
            MISSÃO: Transformar a ideia do colaborador {nome} ({area}) em uma proposta TECNOLÓGICA COMPLETA e EXECUTÁVEL.
            
            INFORMAÇÕES IMPORTANTES:
            - TIPO: Projeto TECNOLÓGICO
            - PONTUAÇÃO NPS: {pontuacao_nps}/100 - {justificativa_nps}
            - FOCO DA EMPRESA: Melhorar NPS através de tecnologia
            
            ENTRADA:
            - **Ideia:** "{ideia}"
            - **Foco:** {foco}
            - **Nível:** {nivel}
            {f"- **Problema atual:** {problema}" if problema else ""}
            {f"- **Recursos disponíveis:** {recursos}" if recursos else ""}
            {f"- **Prazo desejado:** {prazo}" if prazo else ""}
            
            FORMATO DE SAÍDA OBRIGATÓRIO:
            
            # 🎯 **PROJETO TECNOLÓGICO: [Nome do Projeto]**
            
            ## 📊 **1. IMPACTO NO NPS ({pontuacao_nps}/100)**
            **Justificativa:** {justificativa_nps}
            
            **Como melhorará o NPS:**
            - [Benefício direto para o cliente]
            - [Melhoria na experiência]
            - [Resultado esperado no NPS]
            
            ## 📋 **2. RESUMO EXECUTIVO**
            [Descrição clara e objetiva do projeto tecnológico]
            
            ## 🎯 **3. PROBLEMA & OPORTUNIDADE**
            - **Problema identificado:** [Problema atual]
            - **Oportunidade tecnológica:** [Como a tecnologia resolve]
            - **Impacto no cliente:** [Benefício direto]
            
            ## 🏗️ **4. ARQUITETURA TECNOLÓGICA**
            ### **Stack Recomendado:**
            - **Frontend:** [React/Vue/Angular]
            - **Backend:** [Node.js/Python/Java]
            - **Database:** [PostgreSQL/MongoDB]
            - **Cloud:** [AWS/Azure/GCP]
            - **Mobile:** [Se aplicável]
            
            ### **Arquitetura Simplificada:**
            ```
            [Diagrama da arquitetura]
            ```
            
            ## 📂 **5. ESTRUTURA DE DESENVOLVIMENTO**
            ### **Organização do Código:**
            ```
            {ideia.split()[0].lower()}-project/
            ├── README.md
            ├── package.json
            ├── src/
            │   ├── components/
            │   ├── services/
            │   ├── utils/
            │   └── tests/
            ├── backend/
            │   ├── api/
            │   ├── models/
            │   └── config/
            └── deploy/
            ```
            
            ## 📅 **6. CRONOGRAMA DE DESENVOLVIMENTO**
            ### **Sprint 1-2: Setup e Fundação (2 semanas)**
            - [ ] Configuração do ambiente
            - [ ] Arquitetura base
            - [ ] Prototipagem
            
            ### **Sprint 3-6: Desenvolvimento Core (4 semanas)**
            - [ ] Funcionalidades principais
            - [ ] Integração com sistemas
            - [ ] Testes unitários
            
            ### **Sprint 7-8: Finalização e Deploy (2 semanas)**
            - [ ] Testes de integração
            - [ ] Deploy em produção
            - [ ] Monitoramento
            
            ## 🎯 **7. MÉTRICAS DE SUCESSO**
            - **NPS:** Aumento de [X] pontos
            - **Adoção:** [X]% dos clientes usando
            - **Performance:** [Tempo de resposta]
            - **Qualidade:** [Taxa de bugs < X%]
            
            ## 💰 **8. ANÁLISE DE INVESTIMENTO**
            ### **Custos de Desenvolvimento:**
            - **Equipe:** [X] desenvolvedores por [Y] meses
            - **Infraestrutura:** [Custo cloud mensal]
            - **Ferramentas:** [Licenças necessárias]
            
            ### **ROI Esperado:**
            - **Melhoria NPS:** {pontuacao_nps} pontos
            - **Retenção de clientes:** +[X]%
            - **Payback:** [X] meses
            
            ## ⚠️ **9. RISCOS TECNOLÓGICOS**
            - **Integração:** [Risco] → **Mitigação:** [Solução]
            - **Performance:** [Risco] → **Mitigação:** [Solução]
            - **Segurança:** [Risco] → **Mitigação:** [Solução]
            
            ## 🚀 **10. PRÓXIMOS PASSOS**
            1. **Aprovação técnica** (CTO - 3 dias)
            2. **Prototipagem** (1 semana)
            3. **Formação do squad** (1 semana)
            4. **Kick-off técnico** (Imediato)
            
            ---
            
            **Proposta tecnológica gerada por:** MindGlass V2 | **Autor:** {nome} | **Data:** {datetime.now().strftime("%d/%m/%Y")}
            """
        else:  # PROCESSO
            prompt = f"""
            CONTEXTO: Você é um consultor sênior da Carglass especializado em GESTÃO DE PROCESSOS e melhoria operacional.
            
            MISSÃO: Transformar a ideia do colaborador {nome} ({area}) em uma proposta de MELHORIA DE PROCESSO COMPLETA.
            
            INFORMAÇÕES IMPORTANTES:
            - TIPO: Projeto de PROCESSO (não tecnológico)
            - PONTUAÇÃO NPS: {pontuacao_nps}/100 - {justificativa_nps}
            - FOCO DA EMPRESA: Melhorar NPS através de processos eficientes
            
            ENTRADA:
            - **Ideia:** "{ideia}"
            - **Foco:** {foco}
            - **Nível:** {nivel}
            {f"- **Problema atual:** {problema}" if problema else ""}
            {f"- **Recursos disponíveis:** {recursos}" if recursos else ""}
            {f"- **Prazo desejado:** {prazo}" if prazo else ""}
            
            FORMATO DE SAÍDA OBRIGATÓRIO:
            
            # 📋 **MELHORIA DE PROCESSO: [Nome do Processo]**
            
            ## 📊 **1. IMPACTO NO NPS ({pontuacao_nps}/100)**
            **Justificativa:** {justificativa_nps}
            
            **Como melhorará o NPS:**
            - [Benefício direto para o cliente]
            - [Melhoria na experiência]
            - [Resultado esperado no NPS]
            
            ## 📋 **2. RESUMO EXECUTIVO**
            [Descrição clara da melhoria de processo proposta]
            
            ## 🎯 **3. PROCESSO ATUAL vs PROPOSTO**
            ### **Processo Atual:**
            - [Passo 1 atual]
            - [Passo 2 atual]
            - [Problemas identificados]
            
            ### **Processo Proposto:**
            - [Passo 1 novo]
            - [Passo 2 novo]
            - [Melhorias implementadas]
            
            ## 📋 **4. DOCUMENTAÇÃO NECESSÁRIA**
            ### **Documentos a Criar/Atualizar:**
            - [ ] Manual de procedimentos
            - [ ] Formulários (físicos ou digitais)
            - [ ] Checklist de qualidade
            - [ ] Treinamento para equipe
            
            ### **Fluxograma do Processo:**
            ```
            [Início] → [Etapa 1] → [Etapa 2] → [Validação] → [Fim]
            ```
            
            ## 👥 **5. PLANO DE IMPLEMENTAÇÃO**
            ### **Fase 1: Preparação (1 semana)**
            - [ ] Mapeamento do processo atual
            - [ ] Identificação de stakeholders
            - [ ] Criação da documentação
            
            ### **Fase 2: Treinamento (1 semana)**
            - [ ] Treinamento da equipe
            - [ ] Teste piloto
            - [ ] Ajustes necessários
            
            ### **Fase 3: Implementação (2 semanas)**
            - [ ] Rollout gradual
            - [ ] Monitoramento
            - [ ] Correções
            
            ## 🎯 **6. MÉTRICAS DE PROCESSO**
            - **Tempo de execução:** Redução de [X] para [Y]
            - **Taxa de erro:** Redução de [X]%
            - **Satisfação da equipe:** [Métrica]
            - **Impacto no NPS:** +[X] pontos
            
            ## 💰 **7. INVESTIMENTO NECESSÁRIO**
            ### **Custos:**
            - **Treinamento:** [X] horas da equipe
            - **Materiais:** [Formulários, equipamentos]
            - **Consultoria:** [Se necessário]
            
            ### **Benefícios:**
            - **Economia de tempo:** [X] horas/mês
            - **Redução de retrabalho:** [X]%
            - **Melhoria NPS:** {pontuacao_nps} pontos
            
            ## ⚠️ **8. RISCOS E RESISTÊNCIAS**
            - **Resistência à mudança:** → **Mitigação:** [Comunicação e treinamento]
            - **Falta de adesão:** → **Mitigação:** [Acompanhamento próximo]
            - **Problemas na transição:** → **Mitigação:** [Implementação gradual]
            
            ## 🚀 **9. PRÓXIMOS PASSOS**
            1. **Aprovação gerencial** (Gestor da área - 2 dias)
            2. **Mapeamento detalhado** (1 semana)
            3. **Criação de documentos** (1 semana)
            4. **Início da implementação** (2 semanas)
            
            ## 👥 **10. EQUIPE NECESSÁRIA**
            - **Líder do processo:** [Perfil necessário]
            - **Analista de processos:** [Se necessário]
            - **Representantes da área:** [Participação]
            - **Treinador:** [Para capacitação]
            
            ---
            
            **Proposta de processo gerada por:** MindGlass V2 | **Autor:** {nome} | **Data:** {datetime.now().strftime("%d/%m/%Y")}
            """
    
    try:
        resposta = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system", 
                    "content": f"Você é um consultor especializado em projetos {'tecnológicos' if tipo_projeto == 'TECNOLÓGICO' else 'de processo'} focado em melhorar NPS. Seja específico e prático."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=2500 if not preview_mode else 800,
        )
        
        return resposta.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Erro ao processar com IA: {str(e)}"

def gerar_json_proposta(dados, proposta):
    """Gera JSON estruturado com pontuação NPS e tipo de projeto"""
    try:
        # Gera ID único
        proposta_id = hashlib.md5(f"{dados['nome']}{dados['ideia']}{datetime.now()}".encode()).hexdigest()[:8]
        timestamp = datetime.now()
        
        # Extrai estrutura da proposta
        proposta_estruturada = extrair_estrutura_proposta(proposta)
        
        json_proposta = {
            "metadata": {
                "id": proposta_id,
                "versao": "2.1",
                "timestamp": timestamp.isoformat(),
                "data_criacao": timestamp.strftime("%d/%m/%Y %H:%M:%S"),
                "sistema": "MindGlass V2 - Enhanced",
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
                "tipo_projeto": dados.get("tipo_projeto", "TECNOLÓGICO"),
                "pontuacao_nps": dados.get("pontuacao_nps", 50),
                "justificativa_nps": dados.get("justificativa_nps", ""),
                "categoria_nps": classificar_categoria_nps(dados.get("pontuacao_nps", 50)),
                "complexidade": avaliar_complexidade(dados["ideia"]),
                "categoria_projeto": classificar_projeto(dados["ideia"], dados.get("foco", "")),
                "viabilidade_tecnica": "Alta" if dados.get("tipo_projeto") == "PROCESSO" else "Média",
                "impacto_estimado": calcular_impacto_por_nps(dados.get("pontuacao_nps", 50)),
                "prioridade_sugerida": sugerir_prioridade_nps(dados)
            },
            "nps_analysis": {
                "pontuacao_total": dados.get("pontuacao_nps", 50),
                "categoria": classificar_categoria_nps(dados.get("pontuacao_nps", 50)),
                "justificativa": dados.get("justificativa_nps", ""),
                "potencial_melhoria": calcular_potencial_melhoria(dados.get("pontuacao_nps", 50)),
                "areas_impacto": identificar_areas_impacto_nps(dados["ideia"])
            },
            "proximos_passos": {
                "acao_imediata": "Análise de impacto no NPS",
                "responsavel_proximo": "Liderança + Equipe de CX",
                "prazo_resposta": "3 dias úteis",
                "etapas_aprovacao": [
                    "Validação de impacto no NPS",
                    "Análise de viabilidade",
                    "Aprovação orçamentária",
                    "Implementação"
                ]
            }
        }
        
        return json_proposta
        
    except Exception as e:
        st.error(f"Erro ao gerar JSON: {str(e)}")
        return None

def classificar_categoria_nps(pontuacao):
    """Classifica a categoria baseada na pontuação NPS"""
    if pontuacao >= 90:
        return "TRANSFORMADOR"
    elif pontuacao >= 70:
        return "ALTO IMPACTO"
    elif pontuacao >= 50:
        return "MÉDIO IMPACTO"
    elif pontuacao >= 30:
        return "BAIXO IMPACTO"
    else:
        return "IMPACTO MÍNIMO"

def calcular_impacto_por_nps(pontuacao):
    """Calcula impacto baseado na pontuação NPS"""
    if pontuacao >= 70:
        return "Alto"
    elif pontuacao >= 50:
        return "Médio"
    else:
        return "Baixo"

def sugerir_prioridade_nps(dados):
    """Sugere prioridade baseada principalmente no NPS"""
    pontuacao_nps = dados.get("pontuacao_nps", 50)
    
    if pontuacao_nps >= 80:
        return "CRÍTICA"
    elif pontuacao_nps >= 65:
        return "Alta"
    elif pontuacao_nps >= 45:
        return "Média"
    else:
        return "Baixa"

def calcular_potencial_melhoria(pontuacao):
    """Calcula potencial de melhoria no NPS"""
    if pontuacao >= 90:
        return "Potencial de melhoria de 15-20 pontos no NPS"
    elif pontuacao >= 70:
        return "Potencial de melhoria de 10-15 pontos no NPS"
    elif pontuacao >= 50:
        return "Potencial de melhoria de 5-10 pontos no NPS"
    else:
        return "Potencial de melhoria de 2-5 pontos no NPS"

def identificar_areas_impacto_nps(ideia):
    """Identifica áreas específicas de impacto no NPS"""
    areas = []
    ideia_lower = ideia.lower()
    
    if any(palavra in ideia_lower for palavra in ['acompanhar', 'status', 'tempo real', 'transparência']):
        areas.append("Transparência e Comunicação")
    
    if any(palavra in ideia_lower for palavra in ['rapidez', 'agilidade', 'mais rápido', 'tempo']):
        areas.append("Velocidade de Atendimento")
    
    if any(palavra in ideia_lower for palavra in ['qualidade', 'melhor', 'excelência']):
        areas.append("Qualidade do Serviço")
    
    if any(palavra in ideia_lower for palavra in ['conveniente', 'fácil', 'simples', 'automático']):
        areas.append("Conveniência")
    
    if any(palavra in ideia_lower for palavra in ['atendimento', 'suporte', 'ajuda', 'contato']):
        areas.append("Atendimento ao Cliente")
    
    return areas if areas else ["Experiência Geral"]

def enviar_email_estruturado(dados, proposta, json_proposta=None):
    """Envia email com pontuação NPS no título e conteúdo"""
    
    nome = dados["nome"]
    area = dados["area"]
    pontuacao_nps = dados.get("pontuacao_nps", 50)
    justificativa_nps = dados.get("justificativa_nps", "")
    tipo_projeto = dados.get("tipo_projeto", "TECNOLÓGICO")
    
    # Assunto com pontuação NPS
    categoria_nps = classificar_categoria_nps(pontuacao_nps)
    assunto = f"🎯 NPS {pontuacao_nps}/100 [{categoria_nps}] - {nome} ({area}) | MindGlass V2"
    
    # Emoji baseado na pontuação
    emoji_nps = "🚀" if pontuacao_nps >= 80 else "📈" if pontuacao_nps >= 60 else "📊" if pontuacao_nps >= 40 else "⚡"
    
    # Corpo do email com foco no NPS
    corpo_email = f"""
═══════════════════════════════════════════════════════════════
{emoji_nps} PROPOSTA COM IMPACTO NO NPS - MINDGLASS V2
═══════════════════════════════════════════════════════════════

📊 PONTUAÇÃO NPS: {pontuacao_nps}/100 pontos
🎯 CATEGORIA: {categoria_nps}
📋 TIPO DE PROJETO: {tipo_projeto}
💡 JUSTIFICATIVA: {justificativa_nps}

═══════════════════════════════════════════════════════════════
📋 METADADOS DO PROJETO:
═══════════════════════════════════════════════════════════════

• Autor: {nome}
• Área: {area}
• Data: {datetime.now().strftime("%d/%m/%Y às %H:%M")}
• Tipo: {tipo_projeto}
• Nível: {dados.get('nivel', 'Intermediário')}
• Foco: {dados.get('foco', 'Não especificado')}

{f"🆔 ID da Proposta: {json_proposta['metadata']['id']}" if json_proposta else ""}
{f"📈 Potencial de Melhoria: {json_proposta['nps_analysis']['potencial_melhoria']}" if json_proposta else ""}
{f"🎯 Áreas de Impacto: {', '.join(json_proposta['nps_analysis']['areas_impacto'])}" if json_proposta else ""}

═══════════════════════════════════════════════════════════════
📝 IDEIA ORIGINAL (INPUT):
═══════════════════════════════════════════════════════════════

"{dados['ideia']}"

═══════════════════════════════════════════════════════════════
🧠 PROPOSTA ESTRUTURADA (OUTPUT IA):
═══════════════════════════════════════════════════════════════

{proposta}

═══════════════════════════════════════════════════════════════
📊 ANÁLISE DE IMPACTO NO NPS - METODOLOGIA CARGLASS
═══════════════════════════════════════════════════════════════

🎯 **COMO CALCULAMOS O IMPACTO NO NPS:**

A pontuação de 0-100 é calculada com base nos seguintes critérios:

📈 **FAIXAS DE PONTUAÇÃO:**
• 90-100: TRANSFORMADOR - Revoluciona a experiência do cliente
• 70-89: ALTO IMPACTO - Melhoria significativa e perceptível
• 50-69: MÉDIO IMPACTO - Melhoria moderada na experiência
• 30-49: BAIXO IMPACTO - Benefício indireto para o cliente
• 0-29: IMPACTO MÍNIMO - Benefício principalmente interno

🎯 **CRITÉRIOS DE AVALIAÇÃO:**
• Impacto direto na experiência do cliente
• Melhoria na transparência e comunicação
• Aumento da conveniência e praticidade
• Redução do tempo de espera
• Melhoria na qualidade percebida
• Facilidade de uso e acessibilidade

💡 **PARA ESTA PROPOSTA ({pontuacao_nps}/100):**
Justificativa: {justificativa_nps}

🚀 **POTENCIAL DE RESULTADO:**
{calcular_potencial_melhoria(pontuacao_nps)}

═══════════════════════════════════════════════════════════════
🎓 LÓGICA DE ESTRUTURAÇÃO - PROJETOS {'TECNOLÓGICOS' if tipo_projeto == 'TECNOLÓGICO' else 'DE PROCESSO'}
═══════════════════════════════════════════════════════════════

Este projeto foi classificado como **{tipo_projeto}** e estruturado seguindo
nossa metodologia específica para este tipo de iniciativa.

🔄 **PROCESSO DE ANÁLISE:**

1. **DETECÇÃO DE TIPO**
   ✓ Análise semântica da ideia
   ✓ Identificação de palavras-chave
   ✓ Classificação: Tecnológico vs Processo

2. **AVALIAÇÃO DE NPS**
   ✓ Análise de impacto no cliente
   ✓ Pontuação automática 0-100
   ✓ Justificativa baseada em critérios

3. **ESTRUTURAÇÃO PERSONALIZADA**
   ✓ Template específico para o tipo
   ✓ Foco em resultados de NPS
   ✓ Próximos passos direcionados

{'🏗️ **METODOLOGIA PARA PROJETOS TECNOLÓGICOS:**' if tipo_projeto == 'TECNOLÓGICO' else '📋 **METODOLOGIA PARA PROJETOS DE PROCESSO:**'}

{'• Arquitetura e stack tecnológico' if tipo_projeto == 'TECNOLÓGICO' else '• Mapeamento de processo atual vs proposto'}
{'• Cronograma de desenvolvimento' if tipo_projeto == 'TECNOLÓGICO' else '• Documentação e procedimentos'}
{'• Métricas de performance técnica' if tipo_projeto == 'TECNOLÓGICO' else '• Plano de treinamento e implementação'}
{'• Riscos de integração e segurança' if tipo_projeto == 'TECNOLÓGICO' else '• Gestão de mudança e adesão'}
{'• DevOps e entrega contínua' if tipo_projeto == 'TECNOLÓGICO' else '• Monitoramento e melhoria contínua'}

═══════════════════════════════════════════════════════════════
📊 PRÓXIMAS AÇÕES BASEADAS NO NPS:
═══════════════════════════════════════════════════════════════

{'🚨 **PRIORIDADE CRÍTICA** (NPS 80+)' if pontuacao_nps >= 80 else '⚡ **PRIORIDADE ALTA** (NPS 65-79)' if pontuacao_nps >= 65 else '📈 **PRIORIDADE MÉDIA** (NPS 45-64)' if pontuacao_nps >= 45 else '📋 **PRIORIDADE BAIXA** (NPS <45)'}

1. **ANÁLISE EXECUTIVA** ({'24 horas' if pontuacao_nps >= 80 else '48 horas' if pontuacao_nps >= 65 else '1 semana' if pontuacao_nps >= 45 else '2 semanas'})
   • Validação de impacto no NPS
   • Análise de viabilidade
   • Decisão sobre continuidade

2. **VALIDAÇÃO COM CLIENTES** ({'Imediata' if pontuacao_nps >= 70 else 'Após aprovação interna'})
   • Teste de conceito com clientes
   • Validação de premissas
   • Refinamento da proposta

3. **IMPLEMENTAÇÃO**
   • Formação de equipe
   • Definição de cronograma
   • Início do projeto

═══════════════════════════════════════════════════════════════
🎯 MÉTRICAS DE ACOMPANHAMENTO DO NPS:
═══════════════════════════════════════════════════════════════

📊 **MÉTRICAS PRIMÁRIAS:**
• NPS Score (antes e depois)
• Taxa de recomendação
• Satisfação do cliente (CSAT)
• Tempo de resolução

📈 **MÉTRICAS SECUNDÁRIAS:**
• Taxa de adoção da solução
• Redução de reclamações
• Aumento de avaliações positivas
• Tempo médio de atendimento

💰 **MÉTRICAS DE NEGÓCIO:**
• Retenção de clientes
• Lifetime value (LTV)
• Custo de aquisição (CAC)
• Receita por cliente

═══════════════════════════════════════════════════════════════
🤝 COMO RESPONDER COM FOCO NO NPS:
═══════════════════════════════════════════════════════════════

✅ **SE APROVAR (NPS {pontuacao_nps}/100):**
• Confirme o impacto esperado no NPS
• Defina métricas de acompanhamento
• Estabeleça cronograma de implementação
• Designe responsável pelo projeto

🔄 **SE PRECISAR DE AJUSTES:**
• Especifique como melhorar o impacto no NPS
• Solicite refinamento via MindGlass
• Mantenha {nome} informado

❌ **SE REJEITAR:**
• Explique critérios de NPS não atendidos
• Sugira alternativas para melhorar pontuação
• Oriente sobre tipos de projeto com maior impacto

═══════════════════════════════════════════════════════════════
📞 CONTATOS PARA ACOMPANHAMENTO:
═══════════════════════════════════════════════════════════════

• **Autor da ideia:** {nome} ({area})
• **Equipe de CX:** Para validação de impacto no NPS
• **TI/Processos:** Para implementação {'tecnológica' if tipo_projeto == 'TECNOLÓGICO' else 'de processo'}
• **Liderança:** Para aprovação e recursos

═══════════════════════════════════════════════════════════════

Este email foi gerado automaticamente pelo MindGlass V2 Enhanced
Desenvolvido por Vinícius Augusto | Carglass Innovation Lab

💡 Foco total na melhoria do NPS através de {'tecnologia' if tipo_projeto == 'TECNOLÓGICO' else 'processos eficientes'}!

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

# Funções auxiliares existentes (mantidas)
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
            elif "TECNOLOGIAS" in linha_clean.upper() or "STACK" in linha_clean.upper():
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
        pass
    
    return estrutura

def extrair_palavras_chave(texto):
    """Extrai palavras-chave da ideia"""
    stop_words = {'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'da', 'do', 'das', 'dos', 
                  'para', 'por', 'com', 'em', 'na', 'no', 'nas', 'nos', 'que', 'se', 'é', 'são', 
                  'ter', 'tem', 'foi', 'ser', 'estar', 'esse', 'essa', 'isso', 'como', 'mais'}
    
    palavras = re.findall(r'\b\w+\b', texto.lower())
    palavras_filtradas = [p for p in palavras if len(p) > 3 and p not in stop_words]
    
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
        "Processo": ["processo", "workflow", "fluxo", "otimizar"],
        "Melhoria de Processo": ["formulário", "papel", "procedimento", "manual"]
    }
    
    ideia_lower = ideia.lower()
    for categoria, palavras in categorias.items():
        if any(palavra in ideia_lower for palavra in palavras):
            return categoria
    
    return foco if foco != "Não especificado" else "Geral"

def salvar_json_proposta(json_proposta):
    """Salva o JSON da proposta"""
    try:
        json_formatado = json.dumps(json_proposta, indent=2, ensure_ascii=False)
        
        # Mostra no Streamlit
        with st.expander("📄 JSON Gerado (Clique para visualizar)"):
            st.code(json_formatado, language="json")
        
        return json_proposta['metadata']['id']
        
    except Exception as e:
        st.error(f"Erro ao salvar JSON: {str(e)}")
        return None

def salvar_historico(dados, proposta):
    """Salva histórico da proposta"""
    try:
        json_proposta = gerar_json_proposta(dados, proposta)
        
        if json_proposta:
            proposta_id = salvar_json_proposta(json_proposta)
            st.success(f"📝 Proposta {proposta_id} processada com pontuação NPS {dados.get('pontuacao_nps', 0)}/100!")
            return proposta_id, json_proposta
        else:
            return None, None
        
    except Exception as e:
        st.error(f"Erro ao salvar histórico: {str(e)}")
        return None, None
