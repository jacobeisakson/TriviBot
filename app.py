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
serverId = "serverId"
bot_token = "bot_token"

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
import asyncio

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
            message = await ctx.send(embed=embed, content=message_content)
        else:
            # Send the message content if no image URL is provided
            message = await ctx.send(message_content)

        # Check if the question has a video URL
        if "video_url" in trivia_questions[question]:
            await ctx.send(trivia_questions[question]['video_url'])

        try:
            answer = trivia_questions[question]["answer"]
            start_time = time.time()  # Start timing when the question is asked
            previous_message = None  # To store the previous message
            while True:
                response = await client.wait_for("message", check=lambda message: message.author.id == ctx.user.id, timeout=10)
                if response.content.lower() == answer.lower():
                    user_id = str(ctx.user.id)
                    if user_id not in participants:
                        participants[user_id] = {"joined": True, "score": 0}
                    time_difference = time.time() - start_time
                    # Calculate points based on time difference
                    points = max(1, int(10 - time_difference))
                    participants[user_id]["score"] += points
                    await ctx.send(f"Correct {ctx.user.name}! You earned {points} points.")
                    await list_scores(ctx)
                    break  # Exit the loop once the answer is correct
                else:
                    if previous_message:  # Delete the previous message
                        await previous_message.delete()
                    previous_message = response  # Update previous message
        except asyncio.TimeoutError:
            await ctx.send("Time's up! You didn't answer in time.")
            await list_scores(ctx)
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
