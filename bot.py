import discord
import google.generativeai as genai
import gspread as gsheets
import os
import asyncio
import json
import datetime
import random

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
GEMINI_KEY = os.environ["GEMINI_KEY"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
GOOGLE_CREDS_JSON = os.environ["GOOGLE_CREDS_JSON"]

AMIGOS = ["Bernardo", "Bruno", "Rafael", "Rodrigo", "Tomás"]

LORE = """
- Floquita (cadela do Bruno)
- Pêssego (personagem engraçada de AI que diz coisas muito estranhas)
- Amogus Fart (nome do servidor de Discord, onde costumam conversar e onde a tua pergunta será feita)
- Back Home (jogo que o Tomás está a desenvolver há anos, mas parece nunca mais acabar)
- Whatsapp
- Taco Bell
- #pinar (nome de um canal no servidor deles onde enviam screenshots lendários)
- Núria
- Tibitar (verbo sem sentido, usa em contextos sem sentido ex: "quem vai tibitar hoje")
- Cocojambo
- Amogus Summer Fart (quando o Tomás, Bruno, Bernardo e Rodrigo se encontraram em Coimbra)
- "FortniteGame"
- 67
- Tack's (piada com o sobrenome do Rodrigo)
- Craig (amigo antigo)
- Rabo
- LMAO
- Motward (amigo antigo)
"""

INTERESTS = """
- Minecraft
- Fortnite
- Roblox
- Gartic Phone
- FNAF
- Among Us
- Bloons TD 6
- Clash Royale
- Jackbox
- Peak
- Calls no Discord
- Gang Beasts
- Jogos Persona
- Jojo's Bizarre Adventure
- Marvel
- askUs (aplicação onde este jogo se baseou)
- The Weeknd
- Doramas
- Stranger Things
- Falar mal da escola/universidade
- Piadas sexuais
"""

intents = discord.Intents.default()
client = discord.Client(intents=intents)
genai.configure(api_key=GEMINI_KEY)
gemini = genai.GenerativeModel('gemini-2.5-flash')

creds_dict = json.loads(GOOGLE_CREDS_JSON)
gc = gsheets.service_account_from_dict(creds_dict)
sh = gc.open_by_key("1qjtkaB2nqfL5cBqO50Gtqr6gaFdZ067vgG7BtKKp-Ak")
sheet = sh.sheet1

async def tarefa_principal():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    print("--- starting new day ---")
    print(">> reading history sheet...")
    question_history = sheet.col_values(1)

    roll = random.randint(1,5)
    task = ""
    if roll == 1:
        task = """Cria uma pergunta GENÉRICA de situação do dia-a-dia, azar ou comportamento social.
        EXEMPLOS: "Quem é mais provável de ser atropelado por uma trotinete?", "Quem é o mais provável de repetir um ano na universidade?"
        """
    elif roll == 2:
        task = """Cria uma pergunta engraçada que inclua o nome de pelo menos um dos participantes.
        EXEMPLOS: "Quem é o mais provável de dar uma chapada ao Bruno?", "Quem é que gosta mais do Tomás?"
        """
    elif roll == 3:
        task = f"""Cria uma pergunta baseada num destes interesses.
        LISTA DE INTERESSES:
        {INTERESTS}
        EXEMPLOS: "Quem é o mais provável de se borrar todo no FNAF?", "Quem é que grita mais nas calls?"
        """
    elif roll == 4:
        task  = f"""Cria uma pergunta baseada numa destas palavras/coisas (fazem parte da 'lore' do grupo).
        {LORE}
        EXEMPLOS: "Quem é o mais parecido com o Pêssego?", "Quem é o mais provável de tibitar amanhã?"
        """
    else:
        task = f"""Cria uma pergunta absurda, surreal e estúpida (brainrot/shipost).
        Podes misturar escolher coisas da lista de interesses ou da lista da lore, ou até misturar. O objetivo é ser muito engraçado.
        LISTA DE INTERESSES:
        {INTERESTS}
        LISTA DA LORE:
        {LORE}
        EXEMPLOS: "Quem é o mais provável de comer o Craig?" "Quem quer tibitar com o The Weeknd?"
        """

    print(">> asking gemini...")
    prompt = f"""
    Age como um bot de Discord que cria perguntas para o jogo "Quem é mais provável".
    Participantes: 5 amigos portugueses (Bruno, Rodrigo, Tomás, Rafael, Bernardo), ~18 anos. Conhecem se online há ~5 anos, mas já estiveram juntos pessoalmente algumas vezes.
    
    Histórico de perguntas já feitas (NÃO REPETIR):
    {question_history}

    OBJETIVO ATUAL:
    {task}

    REGRAS:
    - Responde apenas com o texto da pergunta (apenas uma única pergunta).
    - Sem aspas. Sem introduções.
    - Português de Portugal. Podes usar calão.
    """

    try:
        response = gemini.generate_content(prompt)
        question_text = response.text.strip()
        answers = AMIGOS
    except Exception as e:
        print(f"gemini error: {e}")
        question_text = "Quem é mais provável ter parado de funcionar hoje?"
        answers = ["Gemini", "Gemini", "Gemini", "Gemini", "Gemini"]

    print(f">> creating poll: {question_text}")
    poll = discord.Poll(question_text, datetime.timedelta(hours=24))

    for answer in answers:
        poll.add_answer(answer)

    print(">> saving history...")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([question_text, timestamp])

    print("--- FOI CARALHO? ---")
    await client.close()

@client.event
async def on_ready():
    await tarefa_principal()


client.run(DISCORD_TOKEN)
