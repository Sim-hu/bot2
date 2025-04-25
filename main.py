import discord
from discord.ext import commands, tasks
import asyncio
import aiohttp
import logging
import signal
import sys
import os
from dotenv import load_dotenv
#from database import setup_database
#from betting import BettingCog
from toramskill import ToramSkillCog
#from music import MusicCog
#from vcrandom import VCRandomCog 
#from yomiage import YomiageCog
#from makevc import MakeVC
#from remind import RemindCog
#from roll import RollCog
from datetime import datetime

# Load the .env file
load_dotenv()

# Get the token and admin user ID
TOKEN = os.getenv('DISCORD_TOKEN')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '589736597935620097'))
print(f"Token loaded: {'Yes' if TOKEN else 'No'}")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix='-', intents=intents, help_command=None)

# Status update task
@tasks.loop(minutes=5)
async def update_status():
    try:
        total_users = sum(guild.member_count for guild in bot.guilds)
        status = f"/help_toram | {len(bot.guilds)}サーバー | {total_users}ユーザー"
        await bot.change_presence(activity=discord.Game(name=status))
    except Exception as e:
        print(f"Error updating status: {e}")

# Log file management task
@tasks.loop(minutes=500)
async def reset_log_file():
    try:
        # Close the current log handlers
        for handler in logging.getLogger().handlers[:]:
            handler.close()
            logging.getLogger().removeHandler(handler)
        
        # Reset the log file
        with open('bot_commands.log', 'w', encoding='utf-8') as f:
            f.write(f"Log file reset at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Reinitialize logging
        setup_logging()
    except Exception as e:
        print(f"Error resetting log file: {e}")

def setup_logging():
    logging.basicConfig(filename='bot_commands.log', 
                       level=logging.INFO,
                       format='%(asctime)s:%(levelname)s:%(message)s',
                       encoding='utf-8')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print("All cogs have been loaded.")
    # Start the status update and log reset tasks
    update_status.start()
    reset_log_file.start()
    await bot.tree.sync()
    print("Custom status has been set and tasks started.")

@bot.event
async def on_command(ctx):
    command_name = ctx.command.name
    author = ctx.author
    guild = ctx.guild.name if ctx.guild else "DM"
    channel = ctx.channel.name if isinstance(ctx.channel, discord.TextChannel) else "DM"

@bot.command(name='s')
async def server_list(ctx):
    """
    サーバーリストを表示するコマンド（管理者専用）
    """
    # 管理者チェック
    if ctx.author.id != ADMIN_USER_ID:
        await ctx.send("このコマンドは管理者専用です。", delete_after=10)
        return

    # サーバー情報を収集
    server_info = []
    total_members = 0
    
    for guild in bot.guilds:
        members = guild.member_count
        total_members += members
        
        # サーバー情報を整形
        info = f"サーバー名: {guild.name}\n"
        info += f"サーバーID: {guild.id}\n"
        info += f"メンバー数: {members}人\n"
        info += f"オーナー: {guild.owner}\n"
        info += f"作成日: {guild.created_at.strftime('%Y/%m/%d')}\n"
        info += "-" * 40 + "\n"
        server_info.append(info)

    # ヘッダー情報
    header = f"```\n総サーバー数: {len(bot.guilds)}\n"
    header += f"総メンバー数: {total_members}人\n"
    header += "=" * 40 + "\n"

    # フッター
    footer = "```"

    # メッセージを分割して送信（Discordの文字制限に対応）
    message = header
    for info in server_info:
        if len(message) + len(info) + len(footer) > 1900:  # Discord の文字制限に余裕を持たせる
            await ctx.send(message + footer)
            message = "```\n" + info
        else:
            message += info
    
    if message:
        await ctx.send(message + footer)

async def setup_cogs():
    #setup_database()
    #await bot.add_cog(BettingCog(bot))
    #await bot.add_cog(MusicCog(bot))
    
    # Cogが既に読み込まれているかチェックする
    if not bot.get_cog("ToramSkillCog"):
        await bot.add_cog(ToramSkillCog(bot))
    
    #await bot.add_cog(VCRandomCog(bot)) 
    #await bot.add_cog(YomiageCog(bot))
    #await bot.add_cog(MakeVC(bot))
    #await bot.add_cog(RemindCog(bot))
    #await bot.add_cog(RollCog(bot))

async def main():
    retry_count = 0
    max_retries = 5
    base_delay = 5  # 秒単位

    while retry_count < max_retries:
        try:
            await setup_cogs()
            if not TOKEN:
                raise ValueError("No token found. Make sure DISCORD_TOKEN is set in your .env file.")
            await bot.start(TOKEN)
            break  # 成功したらループを抜ける
        except discord.errors.HTTPException as e:
            if e.status == 429:  # レート制限エラー
                retry_delay = base_delay * (2 ** retry_count)  # 指数バックオフ
                print(f"Rate limited by Discord. Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_count += 1
            else:
                print(f"HTTP Error: {e}")
                break
        except discord.errors.LoginFailure:
            print("Failed to login. Please check your token.")
            break
        except aiohttp.ClientConnectionError:
            print("Failed to connect to Discord. Please check your internet connection.")
            retry_delay = base_delay * (2 ** retry_count)
            print(f"Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
            retry_count += 1
        except asyncio.CancelledError:
            print("Bot is shutting down...")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # 特定のCogエラーの場合は続行する
            if "already loaded" in str(e):
                print("Continuing despite Cog loading error...")
                # すでに読み込まれているCogがあるので、そのままボットを起動する
                try:
                    await bot.start(TOKEN)
                    break
                except Exception as inner_e:
                    print(f"Failed to start bot after Cog error: {inner_e}")
            break
    
    # いずれの場合も、最終的にはタスクをキャンセルして終了
    try:
        if update_status.is_running():
            update_status.cancel()
        if reset_log_file.is_running():
            reset_log_file.cancel()
        if not bot.is_closed():
            await bot.close()
    except Exception as e:
        print(f"Error during shutdown: {e}")
    print("Bot has been shut down.")

def signal_handler(sig, frame):
    print("Shutdown signal received. Closing bot...")
    asyncio.create_task(bot.close())

if __name__ == "__main__":
    setup_logging()

    if sys.platform != 'win32':
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, signal_handler)
    else:
        print("Running on Windows. Use Ctrl+C to stop the bot.")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Shutting down...")
    finally:
        print("Program has exited cleanly.")