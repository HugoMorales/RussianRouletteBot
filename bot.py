import os, discord, logging, random, sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv, dotenv_values

class Bot(discord.Client):

    #function to check if the message contains any twitter/x link
    def is_twitter_link(message:str) -> bool:
        #exception list, mostly links that also end in X for some reason
        #Thanks for the stupid name, Elon
        list_exceptions = [
            "firefox.com",
            "xbox.com",
            "dropbox.com",
            "dualsensex.com"
        ]

        #Checking if the link is an exception
        is_exception = False
        for exception in list_exceptions:
            if(exception in message):
                is_exception = True
                break

        return ("x.com" in message or "twitter.com" in message) and not is_exception

    async def on_ready(self):
        discord.utils.setup_logging(level=logging.INFO, root=False)
        print(f'Logged on as {self.user}!')
        
        #Set the game
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Roleta Russa"))

    async def on_message(self, message:discord.message.Message):
        #First, check if the message contains a twitter link
        if(Bot.is_twitter_link(message.content)):
            #Getting the author's name, nickname has priority
            author_name = message.author.nick if message.author.nick else message.author.name

            #If it does, rolls a dice using random to check if user will be timed out
            d6 = random.randint(1,6)
            
            #Member gets timed out
            if(d6 == 6):
                try:
                    user_id = message.author.id
                    
                    #Creating connection to sqlite database
                    cursor_db = sqlite3.connect("timeout_users.db").cursor()
                    #Checking if user ins in the db
                    row_timeout_user = cursor_db.execute(f"SELECT * FROM timeout_users where user_id = {user_id}").fetchone()
                    
                    #User got timed out in the past
                    if(not row_timeout_user):
                        #Insert a line with the user id and the default timeout
                        cursor_db.execute(f"INSERT INTO timeout_users VALUES ({user_id}, 0)")
                        cursor_db.connection.commit()

                    #Gets the last timeout_minutes from database and add more 10 minutes
                    row_timeout_user = cursor_db.execute(f"SELECT * FROM timeout_users where user_id = {user_id}").fetchone()
                    timeout_minutes = row_timeout_user[1] + 10

                    #Creating a timedelta for the timeout function
                    timeout_until = datetime.now().astimezone() + timedelta(minutes=timeout_minutes)
                    timeout_reason = "Twitter link"

                    #Timing out the user
                    await message.author.timeout(timeout_until, reason=timeout_reason)
                    await message.reply(f"{author_name} tomou timeout de {timeout_minutes} minutos por postar link do twitter")

                    #Updating the database
                    cursor_db.execute(f"UPDATE timeout_users SET timeout_minutes = {timeout_minutes} WHERE user_id == {user_id}")
                    cursor_db.connection.commit()
                    cursor_db.connection.close()

                    print(f'{author_name} timed out, message: {message.content}')

                except Exception as e:
                    logging.error(f"Error timing out {author_name}: {e}")
                    print(f"Error timing out {author_name}: {e}")

            else:
                print(f"{author_name} got lucky and rolled a {d6}, message: {message.content}")



load_dotenv(".env")

#Config client
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

#Running the bot
client = Bot(intents=intents)
client.run(os.getenv("TOKEN"))



# print(is_twitter_link("https://x.com/LordKnightBB/status/1884740338947895719"))
# print(is_twitter_link("https://fixvx.com/Q2Q_KANO/status/1884628108680310784"))
# print(is_twitter_link("https://vxtwitter.com/JWonggg/status/1884387433413820428"))
# print(is_twitter_link("https://bsky.app/profile/nintendousa.bsky.social/post/3lgw3fhg6bk27"))
# print(is_twitter_link("https://bskyx.app/profile/nintendousa.bsky.social/post/3lgw3fhg6bk27"))