import os
from openai import OpenAI
import yagmail
from dotenv import load_dotenv

# Carregando variáveis de ambiente de forma segura
load_dotenv()

# Inicializando o cliente da OpenAI com minha chave
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Essa função é responsável por transformar uma ideia simples em algo mais estruturado,
# do jeitinho que a gente gostaria de receber se fosse tocar o projeto de verdade.
def estruturar_ideia(nome, area, ideia_curta):
    prompt = f"""
    Um colaborador da Carglass chamado {nome}, da área de {area}, enviou essa ideia:

    "{ideia_curta}"

    Agora, transforme isso numa proposta completa e prática, incluindo:
    1. Descrição detalhada da ideia
    2. Por que essa ideia faz sentido (justificativa)
    3. Etapas para implementar (passos claros)
    4. Possíveis dificuldades e como superar
    5. Benefícios e como medir o impacto (métricas)

    Escreva como se fosse para ser apresentada à liderança. Seja claro, objetivo e encorajador.
    """

    resposta = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=900,
    )

    return resposta.choices[0].message.content.strip()

# Essa função envia a proposta por e-mail assim que ela é gerada.
# A ideia é que o responsável já receba tudo redondo, sem precisar ajustar nada.
def enviar_email(nome, area, proposta):
    assunto = f"💡 Nova Ideia MindGlass - {nome} ({area})"
    corpo = f"Nova sugestão recebida pelo MindGlass 👇\n\n{proposta}"

    yag = yagmail.SMTP(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
    yag.send(to=os.getenv("EMAIL_DESTINO"), subject=assunto, contents=corpo)
