import discord
from discord.ext import commands

from style import RARITIES, ORDER


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["aide"])
    async def show_help(self, ctx):
        embed = discord.Embed(
            title = "🐾 Collect-Animals : Aide",
            description = "Collectionne des animaux, découvre leurs secrets et teste tes connaissances !",
            color = discord.Color.blurple()
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(
            name = "🎁 `!pull`",
            value = "Obtiens **1 animal** aléatoire. Disponible toutes les **5 minutes**.",
            inline = False
        )
        embed.add_field(
            name = "📚 `!collection`",
            value = "Affiche tes animaux, rangés par rareté.",
            inline = False
        )
        embed.add_field(
            name = "📖 `!description <animal>`",
            value = "Affiche la fiche complète d'un animal que tu possèdes.\nEx : `!description panda`",
            inline = False
        )
        embed.add_field(
            name = "🧠 `!quiz <animal>`",
            value = "Lance un quiz à choix multiples sur un de tes animaux.\nEx : `!quiz renard`",
            inline = False
        )

        total = sum(r["weight"] for r in RARITIES.values())
        rates = "\n".join(
            f"{RARITIES[k]['icon']} {RARITIES[k]['name']} {RARITIES[k]['stars']} : **{RARITIES[k]['weight'] / total * 100:.0f}%**"
            for k in ORDER
        )

        embed.add_field(name="🎲 Probabilités de tirage", value=rates, inline=False)

        embed.set_footer(text="Bonne chasse, dresseur ! 🌟")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))