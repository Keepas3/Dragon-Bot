from tokenize import Double
import discord
import os
import logging
import praw
import csv
from discord.ext import commands
from discord import app_commands
import logging.handlers
from datetime import timedelta 


TOKEN = os.getenv('DISCORD_TOKEN')
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')
user_agent = os.getenv('user_agent')


class LevelFilter(logging.Filter):
    def __init__(self, level):
        self.level= level

    def filter(self, record):
        return record.levelno == self.level

def setup_logging(): # Set up loggers 
    logger = logging.getLogger('discord') 
    logger.setLevel(logging.DEBUG) 
    info_handler = logging.handlers.RotatingFileHandler( 
        filename='info.log', 
        encoding='utf-8', 
        maxBytes=32 * 1024 * 1024, # 32 MiB 
        backupCount=5 
        ) 
    info_handler.setLevel(logging.INFO) 
    info_handler.addFilter(LevelFilter(logging.INFO)) 

    warning_handler = logging.handlers.RotatingFileHandler( 
        filename='warning.log', 
        encoding='utf-8', 
        maxBytes=32 * 1024 * 1024, # 32 MiB 
        backupCount=5 
        ) 
    warning_handler.setLevel(logging.WARNING) 
    warning_handler.addFilter(LevelFilter(logging.WARNING)) 

    debug_handler = logging.handlers.RotatingFileHandler( 
        filename='debug.log', 
        encoding='utf-8', 
        maxBytes=32 * 1024 * 1024, # 32 MiB 
        backupCount=5 
        ) 
    
    debug_handler.setLevel(logging.DEBUG) 
    debug_handler.addFilter(LevelFilter(logging.DEBUG)) 

    dt_fmt = '%Y-%m-%d %H:%M:%S' 
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{') 
    info_handler.setFormatter(formatter) 
    warning_handler.setFormatter(formatter) 
    debug_handler.setFormatter(formatter) 
    logger.addHandler(info_handler) 
    logger.addHandler(warning_handler) 
    logger.addHandler(debug_handler) 

    return logger 

logger = setup_logging()


intents = discord.Intents.default()
intents.messages = True  # Enable the message intent
intents.message_content = True
intents.presences = True  # Enable the presence intent

bot = commands.Bot(command_prefix="!", intents=intents)
#bot.tree = discord.app_commands.CommandTree(bot)
GUILD_ID = discord.Object(id ='1318971913069920356') # used for only development server
other_ID = discord.Object(id = '1197262432935088249') # RISENXCHAMPIONS
@bot.event
async def on_ready():
    await bot.tree.sync(guild = GUILD_ID) # Remove GUILD ID if using global
    print(f'Logged in as {bot.user}!')
    print(f"Synced Commands to {GUILD_ID.id}")

@bot.tree.command(name = "stats", description = "Stats of the bot", guild = GUILD_ID)
async def stats(interaction: discord.Interaction):
    server_count =len(bot.guilds)
    user_count = len(bot.users)
    stats_message = (
        f"**Bot Statistics**\n" 
        f"Servers: {server_count}\n" 
        f"Users: {user_count}\n"
    )
    print(f"Sending stats: {stats_message}") # Debugging print statement
    await interaction.response.send_message(stats_message)

@bot.tree.command(name = "4k", description = "I Caught you", guild=GUILD_ID)
async def fourK(interaction: discord.Interaction):
    await interaction.response.send_message(
    f"""** 
I caught you in 4K
8K UHD surround sound 16 Gigs ram, HDR GEFORCE RTX, TI-80 texas instruments,Triple A duracell battery ultrapower100 
Cargador Compatible iPhone 1A 5 W 1400 + Cable 100% 1 Metro Blanco Compatible iPhone 5 5 C 5S 6 SE 6S 7 8 X XR XS 
XS MAX GoPro hero 1 2 terrabyte xbox series x Dell UltraSharp 49Curved Monitor - U4919DW Sony HDC-3300R 
2/3 CCD HD Super Motion Color Camera, 1080p Resolution Toshiba EM131A5C-SS Microwave Oven. **""" 
)



reddit = praw.Reddit(client_id=client_id,client_secret=client_secret, user_agent=user_agent)

@bot.tree.command(name = "receiveposts", description = "Recieve posts from Reddit", guild = GUILD_ID) #Leaks command specify subreddit , type, and amount
@app_commands.describe(subreddit_name="Name of the subreddit", post_type="Type of posts: hot, new, top", limit="Number of posts to retrieve (Max:8)")
async def receive_posts(interaction: discord.Interaction, subreddit_name: str, post_type: str ='hot', limit: int=3 ):
    subreddit = reddit.subreddit(subreddit_name) 
    
    if post_type.lower() == 'new':
        posts = subreddit.new(limit =8 )
    elif post_type.lower() == 'top':
        posts = subreddit.top(limit =8 )
    else:
        posts =subreddit.hot(limit =8 )
    non_pinned_posts = [post for post in posts if not post.stickied][:limit]
    if len(non_pinned_posts) < limit:
        response = f"**Only {len(non_pinned_posts)} {post_type.capitalize()} Posts in r/{subreddit_name} available:**\n"
    else: 
        response = f"**Top {limit} {post_type.capitalize()} Posts in r/{subreddit_name}:**\n"

    await interaction.response.send_message(response) 
    for post in non_pinned_posts: 
        embed = discord.Embed(title=post.title, url=post.url) 
        if post.thumbnail and post.thumbnail.startswith("http"): 
            embed.set_image(url=post.thumbnail) 
        await interaction.followup.send(embed=embed) 

inappropriate_words = {}
with open('profanity_en.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        primary_word = row['text'].strip().lower()
      #  words = [row['canonical_form_1'].strip().lower(), row['canonical_form_2'].strip().lower()]
        
        inappropriate_words[primary_word] = {
            'severity_rating': float(row['severity_rating']),
            'severity_description': row['severity_description']
        } 
        # alternate_words = [ 
        #     row['canonical_form_1'].strip().lower(), 
        #     row.get('canonical_form_2', '').strip().lower(), 
        #     row.get('canonical_form_3', '').strip().lower() 
        # ]
        # alternate_word = row['canonical_form_1'].strip().lower()
        # alternate_word2 = row['canonical_form_2'].strip().lower()

        # for alt_word in alternate_words: 
        #     if alt_word and alt_word != primary_word: 
        #         inappropriate_words[alt_word] = inappropriate_words[primary_word]
#print("Inappropriate words loaded:", inappropriate_words) 

user_scores = {}   
user_warnings ={}     
@bot.event
async def on_message(message):
    if "error" in message.content.lower():
        logger.error(f'Message from {message.author}: {message.content}')
        print("Sent to error log")
    elif "warn" in message.content.lower():
        logger.warning(f'Message from {message.author}: {message.content}')
    else:
        logger.info(f'Message from {message.author}: {message.content}')   

    if message.author ==bot.user:
        return
    
    message_words = set(word.strip().lower() for word in message.content.split()) 
    detected_words = inappropriate_words.keys() & message_words

    
    severity_limits = { 
        'Strong': 2,
        'Severe': 2
    }

    for word in detected_words: 
        severity_rating = inappropriate_words[word]['severity_rating'] 
        severity_description = inappropriate_words[word]['severity_description']
      #  severity = inappropriate_words[word]['severity_description'] 

        user_id =message.author.id
        if severity_rating < 2.0: 
            await message.channel.send(f"{message.author.mention}, please avoid using mild inappropriate language.") 
            continue
        if user_id not in user_scores:
            user_scores[user_id] =0
        if user_id not in user_warnings:
            user_warnings[user_id] = severity_limits[severity_description] if severity_description in severity_limits else float('inf')

            user_scores[user_id] += severity_rating
        
        if severity_description in severity_limits:
            remaining_warnings = user_warnings[user_id] 
            remaining_warnings -= 1 
            if remaining_warnings <0:
                remaining_warnings = 0


            user_warnings[user_id] = remaining_warnings
            # limit = severity_limits[severity_description]
            # remaining_warnings = round((limit - user_scores[user_id]) / severity_rating)    
            # user_warnings[user_id] = remaining_warnings    
        else:
            remaining_warnings = float('inf')
       # user_warnings[user_id] = remaining_warnings
        if remaining_warnings > 0:
            if severity_description == 'Strong': 
                await message.channel.send(f"{message.author.mention}, this is a warning! Strong inappropriate language is not tolerated. You have {remaining_warnings} warnings left.") 
            elif severity_description == 'Severe': 
                await message.channel.send(f"{message.author.mention}, this is a serious warning! Severe inappropriate language will not be tolerated. You have {remaining_warnings} warnings left.") 
    
        if remaining_warnings < 1:
            await message.channel.send(f"{message.author.mention}, you have exceeded the limit for using {severity_description} language.")
            try: 
                timeout_duration = timedelta(minutes=1) # Timeout duration set to 10 minutes            
                await message.author.timeout(timeout_duration, reason=f"Exceeded limit for {severity_description} language.") 
                await message.channel.send(f"{message.author.mention} has been timed out for 1 minutes for using excessive inappropriate language.")  
                user_warnings[user_id] = 1
                remaining_warnings = 1.0
            except discord.Forbidden:
                await message.channel.send(f"I do not have permission to timeout {message.author.mention}.")  
                user_warnings[user_id] = 1
                remaining_warnings = 1.0
            except discord.HTTPException:
                await message.channel.send(f"Failed to timeout {message.author.mention} due to an error.")

        break
        
        
    print(f'Message from {message.author}: {message.content}')
    await bot.process_commands(message)

@bot.tree.command(name = "warnings", description = "Get the number of warnings for a specific user", guild = GUILD_ID)
@app_commands.describe(user = "The user to check warnings for")
async def checkwarnings(interaction: discord.Interaction, user: discord.User):
    user_id = user.id
    if user_id in user_warnings:
        warnings_count = user_warnings[user_id]
    else:
        warnings_count = 2
    await interaction.response.send_message(f"{user.mention} has {warnings_count} warning(s).")

@bot.tree.command(name = "adjustwarnings", description = "Adjust amount ofwarnings for a user", guild = GUILD_ID)
@app_commands.describe(user = "The user to adjust warnings for", warnings = "The number of remaining warnings to set")
async def adjustwarnings(interaction: discord.Interaction, user: discord.User, warnings: int):
    user_id = user.id
    user_warnings[user_id] = warnings
    await interaction.response.send_message(f"{user.mention} now has {warnings} remaining warning(s).")


bot.run(TOKEN)