import random
import time

import discord
from discord.ext import commands

from database import get_animals, get_players, save_players
from style import RARITIES, get_rarity, normalize, get_image


class Pulls(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cooldown = 300   # 5 minutes

    def draw_animal(self, animals):
        """Tire UN animal : d'abord une rareté (pondérée), puis un animal de cette rareté."""
        by_rarity = {}
        for animal in animals:
            by_rarity.setdefault(normalize(animal["rarity"]), []).append(animal)

        keys = [k for k in RARITIES if k in by_rarity]

        if not keys:
            return random.choice(animals)

        chosen = random.choices(
            keys,
            weights = [RARITIES[k]["weight"] for k in keys],
            k = 1
        )[0]

        return random.choice(by_rarity[chosen])

    @commands.command(name="pull")
    async def pull(self, ctx):
        animals = get_animals()
        players = get_players()

        if not animals:
            await ctx.send("Aucun animal disponible dans animals.json.")
            return

        player_id = str(ctx.author.id)
        now = time.time()

        if player_id not in players:
            players[player_id] = {"collection": {}, "last_pull": 0}

        player = players[player_id]

        # cooldown
        elapsed = now - player["last_pull"]

        if elapsed < self.cooldown:
            remaining = int(self.cooldown - elapsed)
            minutes, seconds = divmod(remaining, 60)

            embed = discord.Embed(
                title = "⏳ Patience, dresseur !",
                description = f"Ton prochain pull sera disponible dans **{minutes} min {seconds:02d} s**.",
                color = discord.Color.red()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
            return

        # tirage d'UN animal
        animal = self.draw_animal(animals)
        animal_id = str(animal["id"])

        is_new = animal_id not in player["collection"]
        player["collection"][animal_id] = player["collection"].get(animal_id, 0) + 1
        count = player["collection"][animal_id]

        player["last_pull"] = now
        save_players(players)

        # la carte
        rarity = get_rarity(animal["rarity"])

        file, image_url = get_image(animal)

        # avec une image, on enlève l'emoji du titre
        if image_url:
            title = animal["name"]
        else:
            title = f"{animal['emoji']}  {animal['name']}"

        embed = discord.Embed(
            title = title,
            description = f"{rarity['stars']}  **{rarity['name'].upper()}**\n\n*{animal['description']}*",
            color = rarity["color"]
        )

        if image_url:
            embed.set_image(url=image_url)

        embed.set_author(
            name = f"🎁 {ctx.author.display_name} a obtenu un animal !",
            icon_url = ctx.author.display_avatar.url
        )

        embed.add_field(name="🌍 Habitat", value=animal["habitat"], inline=True)
        embed.add_field(name="🍖 Régime", value=animal["diet"], inline=True)
        embed.add_field(
            name = "📦 Exemplaires",
            value = "✨ **Nouveau !**" if is_new else f"x{count}",
            inline = True
        )

        embed.set_footer(
            text = f"Collection : {len(player['collection'])}/{len(animals)} animaux  •  Prochain pull dans 5 min"
        )

        # petite fanfare pour les légendaires
        content = None
        if normalize(animal["rarity"]) == "legendaire":
            content = "🌟 **LÉGENDAIRE !!!** 🌟"

        await ctx.send(content=content, embed=embed, file=file)

async def setup(bot):
    await bot.add_cog(Pulls(bot))