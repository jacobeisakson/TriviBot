import nextcord
from nextcord.ext import commands
import time
import os
import sys

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

# Client setup
client = commands.Bot(command_prefix="!", intents=intents)
serverId = 1207143734655848480
bot_token = "MTIwNzE0MzQ1MjE2NTQwNjgwMA.GsF22F.YI2shsI5RF7Ve2Er6upp-10y97GD-YxiNaAI98"

# Trivia questions dictionary
trivia_questions = {}

# User scores dictionary
user_scores = {}

# Trivia participant role ID (replace with your role ID)
participant_role_id = 1211416127356411934

# Function to check if user is a participant
async def is_participant(ctx):
    print("getting role")
    participant_role = await ctx.guild.get_role(participant_role_id)
    print("got role")
    return participant_role in ctx.author.roles

# Function to ask trivia questions
async def ask_question(ctx, question):
    await ctx.send(question)
    if question in trivia_questions:
        if "image_url" in trivia_questions[question]:
            await ctx.send(trivia_questions[question]["image_url"])
        if "video_url" in trivia_questions[question]:
            await ctx.send(trivia_questions[question]["video_url"])
    start_time = time.time()
    try:
        answer = trivia_questions[question]["answer"]
        response = await client.wait_for("message", check=lambda message: message.author == ctx.author and is_participant(ctx), timeout=30)
        end_time = time.time()
        if response.content.lower() == answer.lower():
            user_id = str(ctx.author.id)
            if user_id not in user_scores:
                user_scores[user_id] = 0
            time_difference = end_time - start_time
            # Calculate points based on time difference
            points = max(1, int(10 - time_difference))
            user_scores[user_id] += points
            await ctx.send(f"Correct! You earned {points} points. Your total score: {user_scores[user_id]}")
        else:
            await ctx.send("Incorrect! The correct answer is: " + answer)
    except KeyError:
        await ctx.send("Sorry, I don't have that question.")

# Slash command to ask a specific trivia question
@client.slash_command(name="ask", description="Ask a specific trivia question")
async def ask(ctx, question: str):
    if question in trivia_questions:
        await ask_question(ctx, question)
    else:
        await ctx.send("Sorry, that question is not in the trivia bank.")

# Slash command to add a question to the trivia bank
@client.slash_command(name="add_question", description="Add a question to the trivia bank")
async def add_question(ctx, question: str, answer: str, image_url: str = None, video_url: str = None, prompt: str = None):
    # Check if both question and answer are provided
    if not question or not answer:
        await ctx.send("Please provide both question and answer.")
        return

    # Add question and answer to the trivia bank
    trivia_questions[question] = {"answer": answer}

    # Handle image attachment
    if image_url:
        trivia_questions[question]["image_url"] = image_url

    # Handle video attachment
    if video_url:
        trivia_questions[question]["video_url"] = video_url

    # Handle prompt
    if prompt:
        trivia_questions[question]["prompt"] = prompt

    await ctx.send("Question added to the trivia bank.")

# Slash command to list current questions in the trivia bank
@client.slash_command(name="list_questions", description="List current questions in the trivia bank")
async def list_questions(ctx):
    if trivia_questions:
        questions_list = "\n".join(trivia_questions.keys())
        await ctx.send(f"Current questions in the trivia bank:\n{questions_list}")
    else:
        await ctx.send("The trivia bank is empty.")

# Slash command to add a player to the participant role
@client.slash_command(name="add_participant", description="Add a player to the participant role")
async def add_participant(ctx, member: nextcord.Member):
    participant_role = ctx.guild.get_role(participant_role_id)
    await member.add_roles(participant_role)
    await ctx.send(f"{member.mention} has been added to the participant role.")

# Slash command to print participating players' scores
@client.slash_command(name="print_participant_scores", description="Print participating players' scores")
async def print_participant_scores(ctx):
    participant_role = ctx.guild.get_role(participant_role_id)
    participants = [member for member in ctx.guild.members if participant_role in member.roles]
    scores_message = "Participant Scores:\n"
    for participant in participants:
        user_id = str(participant.id)
        score = user_scores.get(user_id, 0)
        scores_message += f"{participant.name}: {score}\n"
    await ctx.send(scores_message)

# Run the client
client.run("MTIwNzE0MzQ1MjE2NTQwNjgwMA.GsF22F.YI2shsI5RF7Ve2Er6upp-10y97GD-YxiNaAI98")
