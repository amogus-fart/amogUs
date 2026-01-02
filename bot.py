import discord # type: ignore
import google.generativeai as genai # type: ignore
import gspread as gsheets # type: ignore
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
intents.message_content = True

genai.configure(api_key=GEMINI_KEY)
gemini = genai.GenerativeModel('gemini-2.5-flash')

creds_dict = json.loads(GOOGLE_CREDS_JSON)
gc = gsheets.service_account_from_dict(creds_dict)
sh = gc.open_by_key("1qjtkaB2nqfL5cBqO50Gtqr6gaFdZ067vgG7BtKKp-Ak")
sheet_history = sh.sheet1
sheet_calendar = sh.worksheet("calendario")

async def tarefa_principal():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    print("--- starting new day ---")

    day_name = None
    task = None
    category_log = "UNKNOWN"

    today = datetime.datetime.now().strftime("%d/%m")
    all_events = sheet_calendar.get_all_values()

    for row in all_events:
        if row[0] == today:
            day_name = row[1]
            if len(row) > 2 and row[2].strip():
                category_log = "DIA"
                task = f"""
                Cria uma pergunta relativa ao tema do dia de hoje (cada dia tem um tema):
                "{day_name}"
                Contexto sobre o dia: {row[2]}
                A tua pergunta TEM de ser sobre este evento/tema específico e usar o contexto fornecido. Não te esqueças que as respostas possíveis serão o nome de cada participante.
                """
                break

    # ANUNCIAR DIA
    await channel.send(f"# 📅 {day_name}")

    print(">> reading history sheet...")
    question_history = sheet_history.col_values(1)

    if not task:
        roll = random.randint(1,5)
        if roll == 1:
            category_log = "GENÉRICA"
            task = """Cria uma pergunta GENÉRICA de situação do dia-a-dia, azar ou comportamento social. Lembra-te que os participantes não interagem uns com os outros pessoalmente (apenas online).
            EXEMPLOS: "Quem é mais provável de ser atropelado por uma trotinete?", "Quem é o mais provável de repetir um ano na universidade?"
            """
        elif roll == 2:
            category_log = "PESSOAL"
            task = """Cria uma pergunta engraçada que inclua o nome de pelo menos um dos participantes.
            EXEMPLOS: "Quem é o mais provável de dar uma chapada ao Bruno?", "Quem é que gosta mais do Tomás?"
            """
        elif roll == 3 or roll == 4:
            category_log = "INTERESSES"
            task = f"""Cria uma pergunta baseada num destes interesses.
            LISTA DE INTERESSES:
            {INTERESTS}
            EXEMPLOS: "Quem é o mais provável de se borrar todo no FNAF?", "Quem é que grita mais nas calls?"
            """
        else:
            category_log = "LORE"
            task  = f"""Cria uma pergunta baseada numa destas palavras/coisas (fazem parte da 'lore' do grupo).
            {LORE}
            EXEMPLOS: "Quem é o mais parecido com o Pêssego?", "Quem é o mais provável de tibitar amanhã?"
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
        answers = ["Gemini", "Geminii", "Geminiii", "Geminiiii", "Geminiiiii"]

    print(f">> creating poll: {question_text}")
    poll = discord.Poll(question=question_text,duration=datetime.timedelta(hours=23))

    for answer in answers:
        poll.add_answer(text=answer)
        
    await channel.send(poll=poll)

    print(">> saving history...")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet_history.append_row([question_text, timestamp, category_log])

    print("--- FOI CARALHO? ---")
    await client.close()

@client.event
async def on_ready():
    await tarefa_principal()


client.run(DISCORD_TOKEN)

