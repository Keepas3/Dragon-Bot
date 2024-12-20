from tokenize import Double
import discord
import os
import logging
import praw
import csv
from discord.ext import commands
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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command(name = 'stats')
async def stats(ctx):
    server_count =len(bot.guilds)
    user_count = len(bot.users)
    stats_message = (
        f"**Bot Statistics**\n" 
        f"Servers: {server_count}\n" 
        f"Users: {user_count}\n"
    )
    await ctx.send(stats_message)

reddit = praw.Reddit(client_id=client_id,client_secret=client_secret, user_agent=user_agent)

@bot.command(name = 'leaks') #Leaks command specify subreddit , type, and amount
async def leaks(ctx, subreddit_name: str, post_type: str ='hot', limit: int=3 ):
    subreddit = reddit.subreddit(subreddit_name) 
    
    if post_type.lower() == 'new':
        posts = subreddit.new(limit =10 )
    elif post_type.lower() == 'top':
        posts = subreddit.top(limit =10 )
    else:
        posts =subreddit.hot(limit =10 )
    non_pinned_posts = [post for post in posts if not post.stickied][:limit]
    if len(non_pinned_posts) < limit:
        response = f"**Only {len(non_pinned_posts)} {post_type.capitalize()} Posts in r/{subreddit_name} available:**\n"
    else: 
        response = f"**Top {limit} {post_type.capitalize()} Posts in r/{subreddit_name}:**\n"
    await ctx.send(response) 
    for post in non_pinned_posts: 
        embed = discord.Embed(title=post.title, url=post.url) 
        if post.thumbnail and post.thumbnail.startswith("http"): 
            embed.set_image(url=post.thumbnail) 
            await ctx.send(embed=embed)

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
        alternate_words = [ 
            row['canonical_form_1'].strip().lower(), 
            row.get('canonical_form_2', '').strip().lower(), 
            row.get('canonical_form_3', '').strip().lower() 
            ]
        # alternate_word = row['canonical_form_1'].strip().lower()
        # alternate_word2 = row['canonical_form_2'].strip().lower()

        for alt_word in alternate_words: 
            if alt_word and alt_word != primary_word: 
                inappropriate_words[alt_word] = inappropriate_words[primary_word]
   

user_scores = {}        
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
        'Strong': 20,
        'Severe': 9
    }

    for word in detected_words: 
        severity_rating = inappropriate_words[word]['severity_rating'] 
        severity_description = inappropriate_words[word]['severity_description']
      #  severity = inappropriate_words[word]['severity_description'] 
        user_id =message.author.id
        if user_id not in user_scores:
            user_scores[user_id] =0
        user_scores[user_id] += severity_rating
        if severity_description in severity_limits and user_scores[user_id] > severity_limits[severity_description]:
            await message.channel.send(f"{message.author.mention}, you have exceeded the limit for using {severity_description} language. Further action will be taken.") 
            timeout_duration = timedelta(minutes=10) # Timeout duration set to 10 minutes            
            await message.author.timeout(timeout_duration, reason=f"Exceeded limit for {severity_description} language.") 
            await message.channel.send(f"{message.author.mention} has been timed out for 10 minutes for using excessive inappropriate language.")            

        if severity_description == 'Mild': 
            await message.channel.send(f"{message.author.mention}, please avoid using mild inappropriate language. Your current score is {user_scores[user_id]}.") 
        elif severity_description == 'Strong': 
            await message.channel.send(f"{message.author.mention}, this is a warning! Strong inappropriate language is not tolerated. Your current score is {user_scores[user_id]}.") 
        elif severity_description == 'Severe': 
            await message.channel.send(f"{message.author.mention}, this is a serious warning! Severe inappropriate language will not be tolerated. Your current score is {user_scores[user_id]}.") 
        break


    print(f'Message from {message.author}: {message.content}')
    await bot.process_commands(message)



bot.run(TOKEN)