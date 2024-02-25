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
serverId = "insert serverId here"
bot_token = "insert token here"

@client.event
async def on_ready():
    print("bot logged in as: {bot.user.name}")
    print("-----------------------------")

# Trivia questions dictionary
trivia_questions = {}

# User scores dictionary
user_scores = {}

# Function to ask trivia questions
async def ask_question(ctx, question):
    if question in trivia_questions:
        # Construct the message content
        message_content = question
        # Check if the question has an image URL
        if "image_url" in trivia_questions[question]:
            # Create a Discord embed with the image
            embed = nextcord.Embed()
            embed.set_image(url=trivia_questions[question]["image_url"])
            # Send the message content along with the embed
            await ctx.send(embed=embed, content=message_content)
        else:
            # Send the message content if no image URL is provided
            await ctx.send(message_content)

        # Check if the question has a video URL
        if "video_url" in trivia_questions[question]:
            await ctx.send(trivia_questions[question]['video_url'])

    else:
        await ctx.send("Sorry, I don't have that question.")

# Slash command to ask a random trivia question
@client.slash_command(name="trivia", description="Ask a random trivia question")
async def trivia(ctx):
    import random
    question = random.choice(list(trivia_questions.keys()))
    await ask_question(ctx, question)

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


# Run the client
client.run(bot_token)