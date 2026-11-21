import discord
from discord.ext import commands
from config import token
from logic import Pokemon, Wizard, Fighter
import random

# Setting up intents for the bot
intents = discord.Intents.default()  # Getting the default settings
intents.messages = True              # Allowing the bot to process messages
intents.message_content = True       # Allowing the bot to read message content
intents.guilds = True                # Allowing the bot to work with servers (guilds)

# Creating a bot with a defined command prefix and activated intents
bot = commands.Bot(command_prefix='!', intents=intents)

# An event that is triggered when the bot is ready to run
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')  # Outputs the bot's name to the console

# The '!go' command
@bot.command()
async def go(ctx):
    author = ctx.author.name  # Dapatkan nama pengguna yang menggunakan perintah
    if author not in Pokemon.pokemons:  # Periksa apakah pengguna ini memiliki Pokémon 
        chance = random.randint(1, 3)  # Menghasilkan angka acak dari 1 hingga 3
        # Buat objek Pokémon tergantung pada nomor acak
        if chance == 1:
            pokemon = Pokemon(author)  # Membuat Pokémon standar
        elif chance == 2:
            pokemon = Wizard(author)  # Membuat Pokémon Wizard 
        elif chance == 3:
            pokemon = Fighter(author)  # Membuat Pokémon Fighter 
        await ctx.send(await pokemon.info())  # Mengirim informasi tentang Pokémon 
        image_url = await pokemon.show_img()  # Mendapatkan URL gambar Pokémon
        if image_url:
            embed = discord.Embed()  # Membuat pesan yang disematkan (embed)
            embed.set_image(url=image_url)  # Menyematkan gambar ke dalam pesan
            await ctx.send(embed=embed)  # Mengirim sematan dengan gambar
        else:
            await ctx.send("Gagal menampilkan gambar Pokémon.")  # Melaporkan kesalahan jika kami tidak dapat memuat gambar Pokémon 
    else:
        await ctx.send("Kamu berhasil mendapatkan Pokémon!")  # Menginformasikan kepada pengguna bahwa Pokémon telah dibuat

@bot.command()
async def attack(ctx):
    target = ctx.message.mentions[0] if ctx.message.mentions else None  # Mendapatkan pengguna yang disebutkan dalam pesan
    if target:  # Memeriksa apakah ada pengguna yang disebutkan
        # Memeriksa apakah yang diserang dan yang bertahan memiliki Pokémon 
        if target.name in Pokemon.pokemons and ctx.author.name in Pokemon.pokemons:
            enemy = Pokemon.pokemons[target.name]  # Mendapatkan Pokémon pemain bertahan
            attacker = Pokemon.pokemons[ctx.author.name]  # Mendapatkan Pokémon penyerang 
            result = await attacker.attack(enemy)  # Melakukan serangan dan mendapatkan hasilnya
            await ctx.send(result)  # Mengirimkan hasil serangan
        else:
            await ctx.send("Kedua player harus memiliki Pokémon untuk memulai pertempuran!")  # Mengumumkan bahwa setidaknya salah satu petarung tidak memiliki Pokémon 
    else:
        await ctx.send("Tentukan pengguna yang ingin Kalian serang dengan menyebut mereka.")  # Meminta untuk menyebutkan pengguna untuk menyerang
# Running the bot

# Perintah '!stats' untuk melihat statistik Pokémon
@bot.command()
async def stats(ctx):
    author = ctx.author.name
    
    # Cek apakah pengguna sudah memiliki Pokémon
    if author in Pokemon.pokemons.keys():
        pokemon = Pokemon.pokemons[author]
        
        # Pastikan nama sudah dimuat
        if not pokemon.name:
            pokemon.name = await pokemon.get_name()
            
        # Ambil data statistik dari method logic.py
        pokemon_data = await pokemon.get_stats()
        image_url = await pokemon.show_img()
        
        if pokemon_data:
            # Membuat Discord Embed yang menarik
            embed = discord.Embed(
                title=f"Statistik Pokémon: {pokemon.name.capitalize()}",
                color=discord.Color.green()
            )
            
            if image_url:
                embed.set_thumbnail(url=image_url) # Menampilkan gambar di sudut kanan embed
                
            # Menambahkan Tipe Pokémon
            types_str = ", ".join([t.capitalize() for t in pokemon_data["types"]])
            embed.add_field(name="🧬 Tipe", value=types_str, inline=False)
            
            # Menambahkan Base Stats (HP, Attack, Defense, dll.)
            stats_text = ""
            for stat_name, stat_value in pokemon_data["stats"].items():
                stats_text += f"**{stat_name.replace('-', ' ').title()}**: {stat_value}\n"
            embed.add_field(name="📊 Base Stats", value=stats_text, inline=False)
            
            # Menambahkan Tinggi & Berat
            embed.add_field(name="📏 Ukuran", value=f"Tinggi: {pokemon_data['height']} | Berat: {pokemon_data['weight']}", inline=False)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("Gagal mengambil data statistik Pokémon dari server.")
    else:
        await ctx.send("Kamu belum memiliki Pokémon! Ketik `!go` terlebih dahulu untuk membuat Pokémon.")

# Perintah '!remove' untuk menghapus Pokémon saat ini
@bot.command()
async def remove(ctx):
    author = ctx.author.name
    
    # Cek apakah pengguna memiliki Pokémon di dalam dictionary
    if author in Pokemon.pokemons:
        # Hapus data Pokémon milik pelatih tersebut
        del Pokemon.pokemons[author]
        await ctx.send("🗑️ Pokémon kamu berhasil dihapus! Ketik `!go` untuk mendapatkan Pokémon baru.")
    else:
        await ctx.send("Kamu belum memiliki Pokémon, jadi tidak ada yang bisa dihapus.")

@bot.command()
async def feed(ctx):
    author = ctx.author.name
    if author in Pokemon.pokemons:
        pokemon = Pokemon.pokemons[author]
        response = await pokemon.feed()
        await ctx.send(response)
    else:
        await ctx.send("You don't have pokemon, please make it first with !go")

# Running the bot
bot.run(token)