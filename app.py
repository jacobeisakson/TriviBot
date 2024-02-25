import nextcord
from nextcord.ext import commands
import json

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
async def ask(ctx, question_index: int):
    # Adjust the index to start at 1
    question_index -= 1
    questions = list(trivia_questions.keys())
    if 0 <= question_index < len(questions):
        question = questions[question_index]
        await ask_question(ctx, question)
    else:
        await ctx.send("Invalid question index. Please provide a valid index within the range of available questions.")


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

    # Save updated trivia questions to the JSON file
    save_questions(trivia_questions)

    await ctx.send("Question added to the trivia bank.")

# Slash command to list current questions in the trivia bank
@client.slash_command(name="list_questions", description="List current questions in the trivia bank")
async def list_questions(ctx):
    if trivia_questions:
        questions_list = "\n".join([f"{index + 1}. {question}" for index, question in enumerate(trivia_questions.keys())])
        await ctx.send(f"Current questions in the trivia bank:\n{questions_list}")
    else:
        await ctx.send("The trivia bank is empty.")


# Run the client
client.run(bot_token)
