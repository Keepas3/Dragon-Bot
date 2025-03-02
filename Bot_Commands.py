from tokenize import Double
import discord
import os
import logging
import praw
import csv
from discord.ext import commands
from discord import app_commands
import logging.handlers
from datetime import datetime, timedelta, timezone
import requests
import random
 


TOKEN = os.getenv('DISCORD_TOKEN')
#For recieving posts on reddit
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')
user_agent = os.getenv('user_agent')
#Clash of Clans stuff
api_key = os.getenv('COC_api_key2')
clan_tag = '#2QQ2VCU82'.replace('#','%23')


class LevelFilter(logging.Filter):
    def __init__(self, level):
        self.level= level

    def filter(self, record):
        return record.levelno == self.level

def format_datetime(dt_str):
    if not dt_str:
        return "N/A"
    try: 
        dt = datetime.strptime(dt_str, '%Y%m%dT%H%M%S.%fZ').replace(tzinfo=timezone.utc)
        # Convert to Eastern Standard Time (EST)
        est = dt.astimezone(timezone(timedelta(hours=-5)))
        return est.strftime('%Y-%m-%d %H:%M:%S %p EST')
    except ValueError:
        return "N/A"
def format_month_day_year(dt_str):
    if not dt_str:
        return "N/A"
    try: 
        dt = datetime.strptime(dt_str, '%Y%m%dT%H%M%S.%fZ').replace(tzinfo=timezone.utc)
        # Convert to Eastern Standard Time (EST)
        est = dt.astimezone(timezone(timedelta(hours=-5)))
        return est.strftime('%m-%d-%Y')
    except ValueError:
        return "N/A"



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
#GUILD_ID = discord.Object(id ='1318971913069920356') # used for only development server
#other_ID = discord.Object(id = '1197262432935088249') # RISENXCHAMPIONS
async def clear_commands():
    try:
       # await bot.tree.clear_commands(guild = None)
        print("Executed")
    except Exception as e:
        print({e})
@bot.event
async def on_ready():
    await bot.tree.sync() # Remove GUILD ID if using global guild = GUILD_ID
    await bot.change_presence(activity=discord.Game(name='With Fire'))
    print(f'Logged in as {bot.user}!')
  #  print(f"Synced Commands to {GUILD_ID.id}")

@bot.tree.command(name ="announce", description ="Make an announcement")
async def announce(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)


@bot.tree.command(name = "stats", description = "Stats of the bot") #guild = GUILD_ID
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

@bot.tree.command(name = "4k", description = "I Caught you")
async def fourK(interaction: discord.Interaction):
    await interaction.response.send_message(
    f"""** 
I caught you in 4K
8K UHD surround sound 16 Gigs ram, HDR GEFORCE RTX, TI-80 texas instruments,Triple A duracell battery ultrapower100 
Cargador Compatible iPhone 1A 5 W 1400 + Cable 100% 1 Metro Blanco Compatible iPhone 5 5 C 5S 6 SE 6S 7 8 X XR XS 
XS MAX GoPro hero 1 2 terrabyte xbox series x Dell UltraSharp 49Curved Monitor - U4919DW Sony HDC-3300R 
2/3 CCD HD Super Motion Color Camera, 1080p Resolution Toshiba EM131A5C-SS Microwave Oven. **""" 
)

@bot.tree.command(name="flipcoin", description="Flip coin (heads or tails)")
async def flip(interaction: discord.Interaction):
    integer1 = random.randint(1,2)
    if integer1 == 1:
        await interaction.response.send_message("The coin flips to... Heads!!!")
    elif integer1 == 2:
        await interaction.response.send_message("The coin flips to... Tails!!!")

def check_coc_clan_tag(clan_tag): 
  #  api_key = 'YOUR_API_KEY' # Replace with your actual API key 
    url = f'https://api.clashofclans.com/v1/clans/{clan_tag}' 
    headers = { 'Authorization': f'Bearer {api_key}', 'Accept': 'application/json' } 
    response = requests.get(url, headers=headers) 
    if response.status_code == 200: 
        return True # Valid clan tag 
    elif response.status_code == 404: 
        return False

@bot.tree.command(name = 'setclantag')
async def set_clan_tag(interaction: discord.Interaction, new_tag: str):
    if check_coc_clan_tag(new_tag.replace('#', '%23')):
        global clan_tag
        clan_tag = new_tag.replace('#', '%23')
        await interaction.response.send_message(f'Clan tag has been updated to {new_tag}')
    else:
        await interaction.response.send_message(f"Not a valid Clan ID") 

@set_clan_tag.error 
async def set_clan_tag_error(interaction: discord.Interaction, error): 
    if isinstance(error, app_commands.MissingRole): 
        await interaction.response.send_message("You don't have permission to use this command.") 
    else:
        await interaction.response.send_message(f"An error occurred: {error}")                  

@bot.tree.command(name = "clean", description ='Clean messages from the bot')
async def clean(interaction : discord.Interaction, limit: int =2):
    await interaction.response.defer()
    if limit < 2 or limit >10:
        limit = 2
    deleted = await interaction.channel.purge(limit =limit)
    await interaction.followup.send(f"Deleted {len(deleted)} messages")



@bot.tree.command(name = "playerinfo", description = "Get player's general information")
async def player_info(interaction: discord.Interaction, player_tag: str):
   # player_tag = '#LOLLG98LJ'.replace('#', '%23')
    player_tag = player_tag.replace('#', '%23')
    if not api_key:
        raise ValueError("API KEY NOT FOUND")
    url = f'https://api.clashofclans.com/v1/players/{player_tag}' 
    headers = { 
        'Authorization': f'Bearer {api_key}', 
        'Accept': 'application/json' 
    } 
    response = requests.get(url, headers=headers) 
    if response.status_code == 200: 
        player_data = response.json() 
        labels = [label for label in player_data['labels']]
        filtered_labels = ', '.join([f"{label['name']}" for label in labels])

        player_information = (
            f"** Player Information **\n" 
            f"```yaml\n"
            f"Name: {player_data['name']}\n" 
            f"Tag: {player_data['tag']}\n"
            f"THLVL: {player_data['townHallLevel']}\n" 
            f"Trophies: {player_data['trophies']}\n" 
            f"Best Trophies: {player_data['bestTrophies']}\n"
            f"{filtered_labels}"
            f"```\n"

    )
        await interaction.response.send_message(f"{player_information}")
    else: 
        await interaction.response.send_message(f"Error getting player information")

@bot.tree.command(name="playertroops", description="Get a player's troop levels") 
@app_commands.describe(player_tag="The user's tag", village="The type of village: home, builder or both")
async def player_troops(interaction: discord.Interaction, player_tag: str, village: str ="home"): 
    player_tag = player_tag.replace('#', '%23') 
    url = f'https://api.clashofclans.com/v1/players/{player_tag}' 
    headers = { 'Authorization': f'Bearer {api_key}', 
    'Accept': 'application/json' 
    }

    response = requests.get(url, headers=headers) 
    if response.status_code == 200: 
        player_data = response.json() 
        name = f"Name: {player_data['name']}\n"

        exclude_words = ['super', 'sneaky', 'ice golem', 'inferno']

        def is_valid_troop(troop): 
            return all(word not in troop['name'].lower() for word in exclude_words)
            
        if village.lower() == 'builder': 
             filtered_troops = [troop for troop in player_data['troops'] if troop['village'] == 'builderBase' and is_valid_troop(troop)]
        elif village.lower() == 'home': 
            filtered_troops = [troop for troop in player_data['troops'] if troop['village'] == 'home' and is_valid_troop(troop)]
        else: 
            filtered_troops = [troop for troop in player_data['troops'] if is_valid_troop(troop)]

      #  filtered_troops = [troop for troop in player_data['troops'] if 'super' not in troop['name'].lower()]

        troops = '\n'.join([f"{troop['name']}: Level {troop['level']} {'(MAXED)' if troop['level'] == troop['maxLevel'] else ''}"
        for troop in filtered_troops])

        troop_information = ( 
            f"```yaml\n" 
            f"Name: {player_data['name']}\n"
            f"Tag: {player_data['tag']}\n"
            f"**Troop Levels**\n" 
            f"{troops}\n" 
            f"```\n" 
        )
        await interaction.response.send_message(f" {name}{troop_information}") 
    else: 
        await interaction.response.send_message(f'Error: {response.status_code}, {response.text}') 



@bot.tree.command(name ="playerheroes", description = "Get a player's heroes/equipments")
@app_commands.describe(player_tag = "The User's tag")
async def player_heroes(interaction: discord.Interaction, player_tag: str):
    playertag = player_tag.replace('#','%23')
    url = f'https://api.clashofclans.com/v1/players/{playertag}'
    headers ={ 'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
    }
    response = requests.get(url, headers =headers)
    if response.status_code == 200:
        player_data = response.json()
        name = player_data.get('name')
      

        #Creates a list that iterates over each hero in player_data heroes
        filtered_heroes = [hero for hero in player_data['heroes'] if hero['village'] != 'builderBase'] 
        #Makes a list and iterates through each hero only if they have an associated equipment to them in the heroequipment then goes through until the last equip
        filtered_equipment = [equipment for hero in player_data['heroes'] if 'equipment' in hero for equipment in hero['equipment']]

        #Iterates through each hero in filteredheroes and adds formatted string of heroname and level
        hero_details = '\n'.join([f"{hero['name']}: Level {hero['level']} {'(MAXED)' if hero['level'] == hero['maxLevel'] else ''}" 
        for hero in filtered_heroes]) 
        #Iterates through each equip in filteredequipment and adds formatted string of equipname and level
        equipment_details = '\n'.join([f"{equip['name']}: Level {equip['level']} {'(MAXED)' if equip['level'] == equip['maxLevel'] else ''}" 
        for equip in filtered_equipment])


        hero_information = (
            f"```yaml\n"
            f"Name: {name} \n"
            f"Tag: {player_data['tag']}\n"
            f"** Hero Levels **\n"
            f"{hero_details}\n"
            f"** Equipment Levels **\n"
            f"{equipment_details}\n"
            f"```\n"
        )
        await interaction.response.send_message(f'{hero_information}')
    else:
        await interaction.response.send_message(f'Error: {response.status_code}, {response.text}')

@bot.tree.command(name = "playerspells", description = "Get player's spell levels")
@app_commands.describe(player_tag = "The user's tag")
async def player_spells(interaction: discord.Interaction, player_tag: str):
    playertag = player_tag.replace('#', '%23')
    url= f'https://api.clashofclans.com/v1/players/{playertag}'
    headers ={ 'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
    }
    response = requests.get(url, headers =headers)
    if response.status_code == 200:
        player_data = response.json()
        name = player_data.get('name')
      

        #Iterates through the player_data spells and takes each index of spell and adds it to our list of spells
        #The first spell is the variable that will hold each individual item from the list as you iterate through it. It's the name you assign to each element in the list during the iteration.
        #The second spell is part of the expression for spell in player_data['spells'], where player_data['spells'] is the list you're iterating over.
        filtered_spells = [spell for spell in player_data['spells']] 
        #Makes a list and iterates through each spell  
        spell_details = '\n'.join([f"{spell['name']}: Level {spell['level']} {'(MAXED)' if spell['level'] == spell['maxLevel'] else ''}"
         for spell in filtered_spells]) 

        spell_information = (
            f"```yaml\n"
            f"Name: {name} \n"
            f"Tag: {player_data['tag']}\n"
            f"{spell_details}\n"
            f"```\n"
        )
        await interaction.response.send_message(f'{spell_information}')
    else:
        await interaction.response.send_message(f'Error: {response.status_code}, {response.text}')

#Lists all clan members in clan 
@bot.tree.command(name="clanmembers", description="Get all member info of the clan") 
async def clan_members(interaction: discord.Interaction): 
    await interaction.response.defer() # Defer the interaction to allow time for processing
    url = f'https://api.clashofclans.com/v1/clans/{clan_tag}'
    headers = { 'Authorization': f'Bearer {api_key}', 
    'Accept': 'application/json' 
    }
    response = requests.get(url, headers=headers) 
    if response.status_code == 200: 
        clan_data = response.json() 
        member_list = "```yaml\n** Members Ranked by Trophies: ** \n" 
        for member in clan_data['memberList']:
            role = member['role']
            if role in ['coLeader', 'leader', 'elder']:
                role = role.upper()
            member_list += ( 
            f"{member['clanRank']}. {member['name']}, Role: {role}, TH: {member['townHallLevel']}\n" 

            ) 
        member_list += "```"
        await interaction.followup.send(member_list)
    else: 
        await interaction.response.send_message(f'Error: {response.status_code}, {response.text}')   
              

#All the info you get is start and end date :(
@bot.tree.command(name ="goldpass", description= "Information about start/end of current gold pass")
async def goldpass(interaction: discord.Interaction):
    await interaction.response.defer()
    url = f'https://api.clashofclans.com/v1/goldpass/seasons/current'
    headers = {
        'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code ==200:
        gold_pass_data = response.json()
        
        start = gold_pass_data.get('startTime')
        end = gold_pass_data.get('endTime')

        start_date = format_datetime(start)
        end_date = format_datetime(end)
        pass_info = (
            f"** Gold Pass: **\n"
            f"```yaml\n"
           # f"Current Gold Pass Season: {gold_pass_data['name']}\n"
            f"Start Date:{start_date}\n"
            f"End Date:{end_date}\n"
            f"```"

        )
        await interaction.followup.send(pass_info)
    else: 
        await interaction.followup.send(f"Error retrieving gold pass information: {response.status_code}, {response.text}")
    
@bot.tree.command(name ="lookupclans", description = "search for clans")
@app_commands.describe(clanname = "The clan's name", war_frequency = "Filter by war frequency (always)", min_members = "Filter by minimum num. of members", 
max_members = "Filter by maximum num. of members", minclan_level = "Filter by clan Level", limits="Number of clans to return (default 1, max 3)")
async def lookup_clans(interaction: discord.Interaction, clanname: str, war_frequency: str = None, min_members: int = None, 
max_members: int = None, minclan_level: int = None , limits: int=1
):
    if limits <1 or limits > 3:
        limits = 1

    await interaction.response.defer()
    url = f'https://api.clashofclans.com/v1/clans?name={clanname}'
    if war_frequency:
        url+= f'&warFrequency={war_frequency}'
    if min_members:
        url+= f'&minMembers={min_members}'
    if max_members:
        url+= f'&maxMembers={max_members}'
    if minclan_level:
        url+= f'&minClanLevel={minclan_level}' 
    if limits:
        url+=f'&limit={limits}'

    headers = { 'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
    }
    response = requests.get(url, headers= headers)
    if response.status_code == 200:
        clan_data = response.json()
        if 'items'in clan_data:
            clans = clan_data['items']
            clan_info_list = []

            for clan in clans: 
                clan_info = (
                   f"```yaml\n"
                   f"Clan Name: {clan['name']}\n" 
                   f"Clan Level: {clan['clanLevel']}\n" 
                   f"Members: {clan['members']}\n" 
                   f"Type: {clan['type']}\n" 
                   f"War Frequency: {clan['warFrequency']}\n" 
                   f"War Wins: {clan['warWins']}\n" 
                   f"War Log Public? {clan['isWarLogPublic']}\n"
                   f"Location: {clan['location']['name'] if 'location' in clan else 'N/A'}\n" 
                   f"```"
                )
                clan_info_list.append(clan_info)
                clan_info_formatted = "\n".join(clan_info_list)
               
        else:
            clan_info_formatted = "No clans found matching this criteria"

    else:
        clan_info_formatted= "Failed to retrieve clans. Please try again Later."

    await interaction.followup.send(clan_info_formatted)



@bot.tree.command(name="lookupmember", description="Get Clan info for a specific user") 
async def user_info(interaction: discord.Interaction, username: str): 
    await interaction.response.defer() # Defer the interaction to allow time for processing 
    url = f'https://api.clashofclans.com/v1/clans/{clan_tag}' 
    headers = { 'Authorization': f'Bearer {api_key}', 
    'Accept': 'application/json' 
    } 
    response = requests.get(url, headers=headers) 
    if response.status_code == 200: 
        clan_data = response.json() 
        user_found = False

        for member in clan_data['memberList']: 
            if member['name'].lower() == username.lower(): 
                member_info = ( f"** Member Information: **\n" 
                f"```yaml\n"
                f"Player Tag: {member['tag']}\n" 
                f"{member['clanRank']}. {member['name']}\n" 
                f"Role: {member['role']}\n" 
                f"TownHall Level: {member['townHallLevel']}\n" 
                f"Trophies: {member['trophies']} | {member['league']['name']}\n"
                f"Builderbase Trophies: {member['builderBaseTrophies']} | {member['builderBaseLeague']['name']}\n" 
                f"Donations: {member['donations']} | Donations Received: {member['donationsReceived']}\n" 
                f"```\n"
                ) 
                chunks = [member_info[i:i + 2000] for i in range(0, len(member_info), 2000)] 
                for chunk in chunks: 
                    await interaction.followup.send(chunk) 

                user_found = True 
                break
        if not user_found: 
            await interaction.followup.send(f'User "{username}" not found in the clan.') 
    else: 
        await interaction.followup.send(f'Error: {response.status_code}, {response.text}')
                
@bot.tree.command(name="claninfo", description="Retrieve information about the clan")
async def clanInfo(interaction: discord.Interaction):
    await interaction.response.defer()  # Defer the interaction to allow time for processing
    if not api_key:
        raise ValueError("API KEY NOT FOUND")
    url = f'https://api.clashofclans.com/v1/clans/{clan_tag}'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
  #  print(f"Response status: {response.status_code}, Response text: {response.text}")  # Debugging print statement
    if response.status_code == 200:
        clan_data = response.json()
        
        clan_info = (
            f"```yaml\n"
            f"Name: {clan_data['name']}\n"
            f"Tag: {clan_data['tag']}\n"
            f"Clan Level: {clan_data['clanLevel']}\n"
            f"Clan Points: {clan_data['clanPoints']}\n"
            f"Members: {clan_data['members']} / 50\n"
            f"Description: {clan_data['description']}\n"
            f"Required Trophies: {clan_data['requiredTrophies']}\n"
            f"Win/loss ratio: {clan_data['warWins']} / {clan_data['warLosses']}\n"
            f"Location: {clan_data['location']['name']}\n"
            f"```\n"
        )

        await interaction.followup.send(clan_info)
    elif response.status_code == 404:
        await interaction.followup.send("No information found for the specified clan.")
    else:
        await interaction.followup.send(f"Error retrieving clan info: {response.status_code}, {response.text}")





@bot.tree.command(name="capitalraid", description="Retrieve information about on current capital raid")
async def capitalRaid(interaction: discord.Interaction):
    await interaction.response.defer()  # Defer the interaction to allow time for processing
    if not api_key:
        raise ValueError("API KEY NOT FOUND")
    url = f'https://api.clashofclans.com/v1/clans/{clan_tag}/capitalraidseasons'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
  #  print(f"Response status: {response.status_code}, Response text: {response.text}")  # Debugging print statement
    if response.status_code == 200:
        raid_data = response.json()
        seasons = raid_data.get('items', [])
        
        if not seasons:
            await interaction.followup.send("No capital raid seasons found for the specified clan.")
            return

        raid_info_list = []
        for i, entry in enumerate(seasons[:1]):  # Limit to the first season
            state = entry.get('state','N/A' )
            start_time = format_datetime(entry.get('startTime', 'N/A'))
            end_time = format_datetime(entry.get('endTime', 'N/A'))
            capitalTotalLoot = entry.get('capitalTotalLoot')
         #   attack_log = entry.get('attacks', [])

            members = entry.get('members', [])
            attacks = 0
          #  print(f"Members: {members}")
            member_loot_stats = {}
            member_attacks = {}
            for member in members:
               # attacker = attack.get('members', {})
                member_name = member.get('name', 'N/A')
              #  print(f"Attacker info: {attacker}")  # Debugging print statement
                total_loot = member.get('capitalResourcesLooted', 0)
                attacks = member.get('attacks', 0)

                if member_name in member_loot_stats:
                    member_loot_stats[member_name] += total_loot
                else:
                    member_loot_stats[member_name] = total_loot

                if member_name in member_attacks:
                    member_attacks[member_name] += attacks
                else:
                    member_attacks[member_name] = attacks


          #  print(f"Member loot stats: {member_loot_stats}")  # Debugging print statement

            sorted_member_stats = sorted(member_loot_stats.items(), key=lambda x: x[1], reverse = True)

            numbered_member_stats = "\n".join( 
                [f"{idx + 1}. {member}: {loot} loot, {member_attacks.get(member, 0)} attack(s)" 
                for idx, (member, loot) in enumerate(sorted_member_stats)] 
                )

            
            raid_info = (
               # f"**Season #{i + 1}**\n"
                f"```yaml\n"
                f"Status: {state}\n"
                f"Start Time: {start_time}\n"
                f"End Time: {end_time}\n"
                f"Total Loot Obtained: {capitalTotalLoot}\n"
                f"Member Loot Stats:\n{numbered_member_stats}\n"
                f"```\n"
            )
            raid_info_list.append(raid_info)
        
        chunk_size = 2000
        raid_info_message = "\n".join(raid_info_list)
        for i in range(0, len(raid_info_message), chunk_size):
            await interaction.followup.send(raid_info_message[i:i+chunk_size])
    elif response.status_code == 404:
        await interaction.followup.send("No capital raid seasons found for the specified clan.")
    else:
        await interaction.followup.send(f"Error retrieving capital raid seasons: {response.status_code}, {response.text}")

        
@bot.tree.command(name="previousraids", description="Retrieve information about capital raid seasons for the clan")
@app_commands.describe(limit = "The number of raids to retrieve (default:2, max:5)")
async def previous_raids(interaction: discord.Interaction, limit: int =2):
    await interaction.response.defer()  # Defer the interaction to allow time for processing
    if not api_key:
        raise ValueError("API KEY NOT FOUND")
    url = f'https://api.clashofclans.com/v1/clans/{clan_tag}/capitalraidseasons'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    print(f"Response status: {response.status_code}, Response text: {response.text}")  # Debugging print statement
    if response.status_code == 200:
        raid_data = response.json()
        seasons = raid_data.get('items', [])
        
        if not seasons:
            await interaction.followup.send("No capital raid seasons found for the specified clan.")
            return

        raid_info_list = []
        limit = max(2,min(limit,5))
        for i, entry in enumerate(seasons[:limit]):  # Limit to the first 5 seasons for brevity
            state = entry.get('state','N/A' )
            start_time = format_month_day_year(entry.get('startTime', 'N/A'))
            end_time = format_month_day_year(entry.get('endTime', 'N/A'))
            capitalTotalLoot = entry.get('capitalTotalLoot')
            reward = entry.get('offensiveReward') + entry.get('defensiveReward')
            if reward ==0:
                reward = 'N/A'

            raid_info = (
                f"```yaml\n"
                f"** Raid#{i+1} **\n"
                f"Status: {state}\n"
                f"Start time to End time: {start_time} - {end_time}\n"
                f"Capital Loot Obtained: {capitalTotalLoot}\n"
                f"Total Attacks: {entry.get('totalAttacks')} | Districts Destroyed: {entry.get('enemyDistrictsDestroyed')}\n"
                f"Raid Medals Earned: {reward}\n"
                f"```\n"
            )
            raid_info_list.append(raid_info)
        
        chunk_size = 2000
        raid_info_message = "\n".join(raid_info_list)
        for i in range(0, len(raid_info_message), chunk_size):
            await interaction.followup.send(raid_info_message[i:i+chunk_size])
    elif response.status_code == 404:
        await interaction.followup.send("No capital raid seasons found for the specified clan.")
    else:
        await interaction.followup.send(f"Error retrieving capital raid seasons: {response.status_code}, {response.text}")

@bot.tree.command(name="warlog", description="Retrieve the war log for the specified clan")
@app_commands.describe(limit = "The number of wars to retrieve (default 1, max 5)" )
async def warLog(interaction: discord.Interaction, limit: int=1):
    await interaction.response.defer()  # Defer the interaction to allow time for processing
    if not api_key:
        raise ValueError("API KEY NOT FOUND")
    url = f'https://api.clashofclans.com/v1/clans/{clan_tag}/warlog'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        war_log = response.json()
        war_entries = war_log.get('items', [])
        
        end_time = war_log.get('endTime')
        end_date = format_datetime(end_time)
     #   end_time = format_datetime(war_log.get('endTime', ''))
        if not war_entries:
            await interaction.followup.send("No war log entries found for the specified clan.")
            return

        limit = max(1,min(limit, 5))
        war_entries = war_entries[:limit]

        war_info_list = [
            (
                f'```yaml\n'
                f"** War#{i + 1} **\n"
                f"Result: {entry['result']}\n"
                f"Team Size: {entry['teamSize']}\n"
                f"Opponent: {entry['opponent']['name']} (Tag: {entry['opponent']['tag']})\n"
                f"Clan Stars: {entry['clan']['stars']}, Clan Destruction: {entry['clan']['destructionPercentage']}%\n"
                f"Opponent Stars: {entry['opponent']['stars']}, Opponent Destruction: {entry['opponent']['destructionPercentage']}%\n"
                f"Exp Gained: {entry['clan']['expEarned']}, Clan Level: {entry['clan'].get('clanLevel', 'N/A')}\n"
                f"End Date: {format_datetime(entry.get('endTime', 'N/A'))}\n" 
                f"```\n"
            )
            for i, entry in enumerate(war_entries)
        ]

        war_info_message = "\n".join(war_info_list)
        
        await interaction.followup.send(war_info_message)
    elif response.status_code == 404:
        await interaction.followup.send("No war log found for the specified clan.")
    else:
        await interaction.followup.send(f"Error retrieving war log: {response.status_code}, {response.text}")



@bot.tree.command(name = "currentwar", description = "Recieve information about current war")
async def warInfo(interaction:discord.Interaction):
    await interaction.response.defer() # Defer the interaction to allow time for processing 
    
    if not api_key:
        raise ValueError("API KEY NOT FOUND")
    url = f'https://api.clashofclans.com/v1/clans/{clan_tag}/currentwar' 
    headers = { 'Authorization': f'Bearer {api_key}', 
    'Accept': 'application/json' 
    } 
    response = requests.get(url, headers=headers) 
   # print(f"Response status: {response.status_code}, Response text: {response.text}") # Debugging print statement
    if response.status_code == 200: 
        war_data = response.json() 

        if war_data['state'] == 'inWar' or war_data['state'] == 'warEnded':
            start_time = format_datetime(war_data.get('startTime', 'N/A'))
            end_time = format_datetime(war_data.get('endTime', 'N/A'))
            numofAttacks = war_data['teamSize'] * 2
            # clan_badges = war_data['clan']['badgeUrls']
            # medium_badge_url = clan_badges['medium']
            war_info = (
                f'```yaml\n'
                f"**Current War Information**\n"
                f"State: {war_data['state']}\n"
                f"Start Time: {start_time}\n"
                f"End Time: {end_time}\n"
                f"War Size: {war_data['teamSize']}\n" 
                f"Clan: {war_data['clan']['name']} (Tag: {war_data['clan']['tag']})\n"                
                f"Opponent: {war_data['opponent']['name']} (Tag: {war_data['opponent']['tag']})\n" 
                f"Clan Stars: {war_data['clan']['stars']} (Attacks: {war_data['clan']['attacks']}/{numofAttacks})\n" 
                f"Opponent Stars: {war_data['opponent']['stars']} (Attacks: {war_data['opponent']['attacks']}/{numofAttacks})\n" 
                f"Clan Destruction Percentage: {war_data['clan']['destructionPercentage']}%\n" 
                f"Opponent Destruction Percentage: {war_data['opponent']['destructionPercentage']}%\n"
                f"```\n"

        )
        if war_data['state'] == 'notInWar':
            war_info = (
                f"```yaml\n"
                f"**Current War Information**\n"
                f"State: {war_data['state']}\n"
                f"```\n"
            )

        await interaction.followup.send(war_info)
    elif response.status_code == 404: 
        await interaction.followup.send("No current war found for the specified clan.")
    else:
        await interaction.followup.send(f"Error retrieving current war info: {response.status_code}, {response.text}")


@bot.tree.command(name = "cwlcurrent", description = "Recieve information about current war")
async def warInfo(interaction:discord.Interaction):
    await interaction.response.defer() # Defer the interaction to allow time for processing 
    if not api_key:
        raise ValueError("API KEY NOT FOUND")
    url = f'https://api.clashofclans.com/v1/clans/{clan_tag}/currentwar/leaguegroup' 
    headers = { 'Authorization': f'Bearer {api_key}', 
    'Accept': 'application/json' 
    } 
    response = requests.get(url, headers=headers) 
  #  print(f"Response status: {response.status_code}, Response text: {response.text}") # Debugging print statement
    if response.status_code == 200: 
        war_data = response.json() 

        if 'state' in war_data and war_data['state'] == 'inWar': 
            if 'clans' in war_data: 
                clan_info = "\n".join([ f"Clan{i+1}: {clan['name']} (Tag: {clan['tag']})" 
                for i, clan in enumerate(war_data['clans'])
                ])
                war_info = ( 
                f'```yaml\n' 
                f"**Current CWL Information**\n" 
                f"State: {war_data['state']}\n" 
                f"Season: {war_data['season']}\n" 
                f"{clan_info}\n" 
                f"```\n"
            )
             
            else: 
                war_info = ( 
                f'```yaml\n' f"**Current War Information**\n" 
                f"State: {war_data['state']}\n" 
                f"No clans data available.\n" f"```\n" 
                ) 

        elif 'state' in war_data and war_data['state'] == 'notInWar': 
            war_info = ( f'```yaml\n' 
            f"**Current War Information**\n" 
            f"State: {war_data['state']}\n" 
            f"```\n"

            )
            
        await interaction.followup.send(war_info)
    elif response.status_code == 404: 
        await interaction.followup.send("Currently not in CWL. ")
    else:
        await interaction.followup.send(f"Error retrieving current war info: {response.status_code}, {response.text}")


@bot.tree.command(name = "cwlclansearch", description = "Search up other clans in CWL")
@app_commands.describe(clanname = "The clan's name")
async def CWL_clan_search(interaction: discord.Interaction, clanname: str):
    await interaction.response.defer()
    url = f'https://api.clashofclans.com/v1/clans/{clan_tag}/currentwar/leaguegroup'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        war_data = response.json()
        clan_found = False

        for clan in war_data.get('clans', []):
            if clan['name'].lower() == clanname.lower():
                clan_found = True
                sorted_members = sorted(clan['members'], key=lambda member: member['townHallLevel'], reverse=True)
                member_info = "\n".join([
                    f"Member{i+1}: {member['name']} (TH Level: {member['townHallLevel']})"
                   # for member in clan['members']
                    for i, member in enumerate(sorted_members)
                ])
                war_info = (
                    f'```yaml\n'
                    f"**CWL Clan Search Result**\n"
                    f"Clan: {clan['name']} (Tag: {clan['tag']})\n"
                    f"Members:\n{member_info}\n"
                    f"```\n"
                )
                await interaction.followup.send(war_info)
                break
        
        if not clan_found:
            await interaction.followup.send(f"Clan '{clanname}' not found in the current CWL.")
        elif response.status_code == 404: 
            await interaction.followup.send("Currently not in CWL.")    
    else:
        await interaction.followup.send(f"Error retrieving CWL information: {response.status_code}, {response.text}")

    

reddit = praw.Reddit(client_id=client_id,client_secret=client_secret, user_agent=user_agent)

@bot.tree.command(name = "receiveposts", description = "Recieve posts from Reddit") #Leaks command specify subreddit , type, and amount
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
        # if severity_rating < 2.0: 
        #     await message.channel.send(f"{message.author.mention}, please avoid using mild inappropriate language.") 
        #     continue
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
                timeout_duration = timedelta(minutes=30) # Timeout duration set to 30 minutes            
                await message.author.timeout(timeout_duration, reason=f"Exceeded limit for {severity_description} language.") 
                await message.channel.send(f"{message.author.mention} has been timed out for {timeout_duration} minutes for using excessive inappropriate language.")  
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

@bot.tree.command(name = "warnings", description = "Get the number of warnings for a specific user")
@app_commands.describe(user = "The user to check warnings for")
async def checkwarnings(interaction: discord.Interaction, user: discord.User):
    user_id = user.id
    if user_id in user_warnings:
        warnings_count = user_warnings[user_id]
    else:
        warnings_count = 2
    await interaction.response.send_message(f"{user.mention} has {warnings_count} warning(s).")

@bot.tree.command(name = "adjustwarnings", description = "Adjust amount of warnings for a user")
@app_commands.describe(user = "The user to adjust warnings for", warnings = "The number of remaining warnings to set")
async def adjustwarnings(interaction: discord.Interaction, user: discord.User, warnings: int):
    user_id = user.id
    user_warnings[user_id] = warnings
    await interaction.response.send_message(f"{user.mention} now has {warnings} remaining warning(s).")


bot.run(TOKEN)