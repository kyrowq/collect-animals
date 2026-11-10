import discord
from discord.ext import commands

from database import get_animals, get_players
from style import get_rarity, find_animal, get_image


class Description(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="description", aliases=["desc", "info"])
    async def description(self, ctx, *, nom: str = None):

        if nom is None:
            await ctx.send("Utilisation : `!description <nom de l'animal>` (ex : `!description panda`)")
            return

        animals = get_animals()
        players = get_players()

        collection = players.get(str(ctx.author.id), {}).get("collection", {})

        animal = find_animal(nom, animals)

        if animal is None:
            await ctx.send(f"Je ne connais pas d'animal qui s'appelle « {nom} ».")
            return

        if str(animal["id"]) not in collection:
            embed = discord.Embed(
                title = "🔒 Animal inconnu",
                description = "Tu ne possèdes pas encore cet animal.\nContinue de `!pull` pour le découvrir !",
                color = discord.Color.dark_grey()
            )
            await ctx.send(embed=embed)
            return

        rarity = get_rarity(animal["rarity"])
        count = collection[str(animal["id"])]

        file, image_url = get_image(animal)

        if image_url:
            title = animal["name"]
        else:
            title = f"{animal['emoji']}  {animal['name']}"

        embed = discord.Embed(
            title = title,
            description = f"{rarity['stars']}  **{rarity['name'].upper()}**\n\n{animal['description']}",
            color = rarity["color"]
        )

        if image_url:
            embed.set_image(url=image_url)

        embed.add_field(name="🌍 Habitat", value=animal["habitat"], inline=True)
        embed.add_field(name="🍖 Régime", value=animal["diet"], inline=True)
        embed.add_field(name="📦 Exemplaires", value=f"x{count}", inline=True)

        if animal.get("fact"):
            embed.add_field(name="💡 Le savais-tu ?", value=animal["fact"], inline=False)

        embed.set_author(
            name = f"Fiche de {ctx.author.display_name}",
            icon_url = ctx.author.display_avatar.url
        )
        embed.set_footer(text=f"Animal n°{animal['id']}  •  !quiz {animal['name'].lower()} pour t'entraîner")

        await ctx.send(embed=embed, file=file)


async def setup(bot):
    await bot.add_cog(Description(bot))