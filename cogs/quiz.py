import random
import unicodedata
import discord
from discord.ext import commands

from database import get_animals, get_players

def normalize(text):
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")

def build_questions(animal, animals):
    fields = [
        ("habitat", f"Où vit **{animal['name']}** ?"),
        ("diet", f"Quel est le régime alimentaire de **{animal['name']}** ?"),
        ("rarity", f"Quelle est la rareté de **{animal['name']}** ?"),
    ]
    
    questions = []
    
    for field, text in fields:
        correct = animal[field]
        
        wrong = list({a[field] for a in animals} - {correct})

        if not wrong:
            continue

        random.shuffle(wrong)

        options = [correct] + wrong[:3]
        random.shuffle(options)

        questions.append((text, options, correct))

    random.shuffle(questions)
    return questions


class QuizView(discord.ui.View):

    def __init__(self, author, options, correct):
        super().__init__(timeout=30)

        self.author = author
        self.correct = correct
        self.result = None   # True = bonne réponse, False = mauvaise, None = pas de réponse

        for option in options:
            button = discord.ui.Button(label=option, style=discord.ButtonStyle.primary)
            button.callback = self.make_callback(option)
            self.add_item(button)

    def make_callback(self, option):
        async def callback(interaction: discord.Interaction):
            # seul le joueur qui a lancé le quiz peut répondre
            if interaction.user.id != self.author.id:
                await interaction.response.send_message(
                    "Ce quiz n'est pas pour toi !", ephemeral=True
                )
                return

            self.result = (option == self.correct)

            # griser les boutons + vert/rouge
            for item in self.children:
                item.disabled = True
                if item.label == self.correct:
                    item.style = discord.ButtonStyle.success
                elif item.label == option:
                    item.style = discord.ButtonStyle.danger

            await interaction.response.edit_message(view=self)
            self.stop()

        return callback


class Quiz(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quiz")
    async def quiz(self, ctx, *, nom: str = None):

        if nom is None:
            await ctx.send("Utilisation : `!quiz <nom de l'animal>` (ex : `!quiz renard`)")
            return

        animals = get_animals()
        players = get_players()

        collection = players.get(str(ctx.author.id), {}).get("collection", {})

        # trouver l'animal demandé
        animal = None
        for a in animals:
            if normalize(nom) in normalize(a["name"]):
                animal = a
                break

        if animal is None:
            await ctx.send(f"Je ne connais pas d'animal qui s'appelle « {nom} ».")
            return

        # le joueur doit posséder l'animal
        if str(animal["id"]) not in collection:
            await ctx.send(
                f"{ctx.author.mention}, tu ne possèdes pas encore {animal['emoji']} "
                f"**{animal['name']}**. Continue de `!pull` !"
            )
            return

        questions = build_questions(animal, animals)

        if not questions:
            await ctx.send("Pas assez d'animaux pour créer un quiz.")
            return

        score = 0

        for number, (text, options, correct) in enumerate(questions, start=1):
            embed = discord.Embed(
                title = f"{animal['emoji']} Quiz : {animal['name']} ({number}/{len(questions)})",
                description = text,
                color = discord.Color.blurple()
            )

            view = QuizView(ctx.author, options, correct)
            message = await ctx.send(embed=embed, view=view)

            await view.wait()

            # pas de réponse dans les 30 secondes
            if view.result is None:
                for item in view.children:
                    item.disabled = True
                await message.edit(view=view)
                await ctx.send("⏰ Temps écoulé, quiz terminé.")
                return

            if view.result:
                score += 1

        embed = discord.Embed(
            title = "🏁 Quiz terminé !",
            description = f"{ctx.author.mention}, ton score : **{score}/{len(questions)}**",
            color = discord.Color.green()
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Quiz(bot))