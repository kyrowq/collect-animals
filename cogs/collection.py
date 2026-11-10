import discord
from discord.ext import commands

from database import get_animals, get_players
from style import RARITIES, ORDER, normalize, progress_bar


class Collection(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="collection")
    async def collection(self, ctx):
        animals = get_animals()
        players = get_players()

        collection = players.get(str(ctx.author.id), {}).get("collection", {})

        if not collection:
            await ctx.send(f"{ctx.author.mention}, ta collection est vide. Tape `!pull` !")
            return

        owned = [a for a in animals if str(a["id"]) in collection]

        embed = discord.Embed(
            title = f"📚 Collection de {ctx.author.display_name}",
            description = (
                f"{progress_bar(len(owned), len(animals))}  "
                f"**{len(owned)}/{len(animals)}** animaux découverts"
            ),
            color = discord.Color.green()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

        for key in ORDER:
            rarity = RARITIES[key]

            total = [a for a in animals if normalize(a["rarity"]) == key]
            group = [a for a in owned if normalize(a["rarity"]) == key]

            if not total:
                continue

            if group:
                value = "\n".join(
                    f"{a['emoji']} {a['name']} `x{collection[str(a['id'])]}`"
                    for a in group
                )
            else:
                value = "*Aucun pour l'instant*"

            embed.add_field(
                name = f"{rarity['icon']} {rarity['name']} ({len(group)}/{len(total)})",
                value = value,
                inline = False
            )

        embed.set_footer(text="Utilise !description <animal> pour en savoir plus")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Collection(bot))