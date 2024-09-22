import discord
from discord.ext import commands
import os
import requests
from discord.ext import commands, tasks
from dotenv import load_dotenv
import aiohttp
from config import Config
from datetime import datetime

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)
token = os.getenv('bot_token')
prefix = Config.prefix

# Crear instancia del bot
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())

# Definir variables del bot
bot.setup = False

# URL de la página de colecciones en Scryfall
url = 'https://api.scryfall.com/sets'

params = {
    'name': 'Foundation'  # 'fuzzy' permite buscar por coincidencias aproximadas
}

response = requests.get(url, params=params)

# Evento cuando el bot se conecta
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    if not tryScryScrape.is_running():
        tryScryScrape.start()

# Un conjunto para almacenar IDs de sets vistos
seen_sets = set()

# Función para obtener sets de Scryfall
async def fetch_scryfall_sets():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()  # Convertimos la respuesta a formato JSON
                return data['data']  # Devolver los sets
            else:
                print(f"Error: {response.status}")
                return None

# Tarea que se ejecuta cada 10 minutos
@tasks.loop(minutes=10)
async def tryScryScrape():
    channel = bot.get_channel(Config.channel_notices_id)

    dateToday = datetime.today().date()

    sets_data = await fetch_scryfall_sets()
    
    if sets_data:
        for card_set in sets_data:
            set_release_date = datetime.strptime(card_set['released_at'], '%Y-%m-%d').date()

            # Verificar si la fecha de lanzamiento es anterior a hoy
            if set_release_date < dateToday:
                continue
            
            set_id = card_set['id']
            set_name = card_set['name']

            # Verificar si el set ya ha sido visto
            if set_id not in seen_sets:
                seen_sets.add(set_id)
                
                embed = discord.Embed(
                    title="Nueva colección",
                    description=f"__{set_name}__",
                    color=0xDE330C
                )
                embed.add_field(
                    name="Fecha de lanzamiento:",
                    value=f"{card_set['released_at']}",
                    inline=False
                )
                embed.add_field(
                    name="Número de cartas:\n",
                    value=f"{card_set['card_count']}",
                    inline=True
                )
                embed.add_field(
                    name="Tipo de colleción:",
                    value=f"{card_set['set_type']}",
                    inline=True
                )
                embed.add_field(
                    name=f"Más información en nuestra página web",
                    value=f"[MTG Canarias](https://mtgcanarias.com/)", 
                    inline=False
                )
                embed.set_thumbnail(
                    url="https://mtgcanarias.com/wp-content/uploads/2023/03/loguito.png"
                )
                embed.set_image(
                    url="https://images.ctfassets.net/s5n2t79q9icq/5p96VsqUFOFydvLm9q0d9j/db8816b162d484efb1a2d476252658f6/MTG_Meta-ShareImage.jpg"
                )
                embed.set_footer(
                    text="MTG-Canarias",
                    icon_url="https://yt3.googleusercontent.com/oO0NdBych3qL79hrzfj4e7jijDJYdy9mrEKnB1tBNSnu6FvFi4XOg2fPuYpWVf5x1xWdZOC1VA=s900-c-k-c0x00ffffff-no-rj", 

                )
                await channel.send("@everyone")
                await channel.send(embed=embed)

bot.run(token)