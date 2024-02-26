import nextcord
from nextcord.ext import commands
import json
import time
import asyncio

intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

# File path for storing trivia questions
QUESTIONS_FILE = "trivia_questions.json"

# Client setup
client = commands.Bot(command_prefix="!", intents=intents)
serverId = 1207143734655848480
bot_token = "MTIwNzE0MzQ1MjE2NTQwNjgwMA.GH-a0s.ChhpIUkKCvdvHiMpLLjChjSV8TEdS1l6ylDV3w"

@client.event
async def on_ready():
    print(f"bot logged in as: {client.user.name}")
    print("-----------------------------")

# Function to load trivia questions from a JSON file
def load_questions():
    try:
        with open(QUESTIONS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Function to save trivia questions to a JSON file
def save_questions(questions):
    with open(QUESTIONS_FILE, "w") as file:
        json.dump(questions, file, indent=4)

# Load trivia questions when the bot starts
trivia_questions = load_questions()

# Trivia participants dictionary with opt-in flag
participants = {}

@client.slash_command(name="ask", description="Ask a specific trivia question")
async def ask(ctx, question_index: int):
    # Adjust the index to start at 1
    question_index -= 1
    questions = list(trivia_questions.keys())
    if 0 <= question_index < len(questions):
        question = questions[question_index]
        await ask_question(ctx, question)
    else:
        await ctx.send("Invalid question index. Please provide a valid index within the range of available questions.")


# Function to ask trivia questions
async def ask_question(ctx, question):
    if question in trivia_questions:
        # Send a message in the server's text channel indicating that the question is being asked
        await ctx.send(f"Asking trivia question: {question}")

        # Send the question to all participants via direct messages with an embed
        for user_id in participants:
            try:
                user = await client.fetch_user(int(user_id))
                embed = nextcord.Embed(title="Trivia Question", description=question)
                # Check if the question has an image URL
                if "image_url" in trivia_questions[question]:
                    embed.set_image(url=trivia_questions[question]["image_url"])
                # Check if the question has a video URL
                if "video_url" in trivia_questions[question]:
                    embed.add_field(name="Video URL", value=trivia_questions[question]['video_url'], inline=False)
                await user.send(embed=embed)
            except nextcord.NotFound:
                pass

        # Wait for responses
        await asyncio.sleep(30)  # Adjust the time limit as needed

        # Check answers and update scores
        correct_answer = trivia_questions[question]["answer"]
        for user_id in participants:
            try:
                user = await client.fetch_user(int(user_id))
                dm_channel = user.dm_channel
                if dm_channel is None:
                    dm_channel = await user.create_dm()

                async for message in dm_channel.history(limit=5):
                    if message.author == client.user:
                        continue
                    if message.content.strip().lower() == correct_answer.lower():
                        participants[user_id]["score"] += 1
                        await dm_channel.send("Correct! You earned 1 point.")
                        break
                else:
                    await dm_channel.send("Time's up! The correct answer was: " + correct_answer)
            except nextcord.NotFound:
                pass

        # Print all scores to DMs
        score_list = []
        for user_id, data in participants.items():
            try:
                user = await client.fetch_user(int(user_id))
                score_list.append(f"{user.name}: {data['score']} points")
            except nextcord.NotFound:
                pass

        if score_list:
            scores_message = "\n".join(score_list)
            for user_id in participants:
                try:
                    user = await client.fetch_user(int(user_id))
                    await user.send("Current scores:\n" + scores_message)
                except nextcord.NotFound:
                    pass
        else:
            await ctx.send("No players have participated in the trivia game yet.")
    else:
        await ctx.send("Sorry, I don't have that question.")



# Function for players to opt-in to trivia
@client.slash_command(name="join_trivia", description="Join the trivia game")
async def join_trivia(ctx):
    user_id = str(ctx.user.id)  # Get the ID of the user who invoked the command
    if user_id not in participants:
        participants[user_id] = {"joined": True, "score": 0}
        await ctx.send("You have joined the trivia game!")
    else:
        await ctx.send("You are already in the trivia game!")


# Function to add a question to the trivia bank
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

    # Save updated trivia questions to the JSON file
    save_questions(trivia_questions)

    await ctx.send("Question added to the trivia bank.")

# Function to list current questions in the trivia bank
@client.slash_command(name="list_questions", description="List current questions in the trivia bank")
async def list_questions(ctx):
    if trivia_questions:
        questions_list = "\n".join([f"{index + 1}. {question}" for index, question in enumerate(trivia_questions.keys())])
        await ctx.send(f"Current questions in the trivia bank:\n{questions_list}")
    else:
        await ctx.send("The trivia bank is empty.")

# Function to print participant's scores
@client.slash_command(name="list_scores", description="List participating players and their scores")
async def list_scores(ctx):
    if not participants:
        await ctx.send("No players have participated in the trivia game yet.")
        return

    score_list = []
    for user_id, data in participants.items():
        try:
            user = await client.fetch_user(int(user_id))
            score_list.append(f"{user.name}: {data['score']} points")
        except nextcord.NotFound:
            # Skip if the user couldn't be found (possibly left the server)
            pass

    if score_list:
        scores_message = "\n".join(score_list)
        await ctx.send("Current scores:\n" + scores_message)
    else:
        await ctx.send("No players have participated in the trivia game yet.")


# Run the client
client.run(bot_token)
