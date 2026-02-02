import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

# 機器人配置
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot 已上線: {bot.user}")
    logger.main_logger.info(f"✅ Bot 已上線: {bot.user}")
    
    # 加載 Cogs（必須先加載，才能同步其中的 slash 命令）
    try:
        logger.main_logger.info("🔄 開始加載 Cogs...")
        await bot.load_extension("cogs.account")
        logger.main_logger.info("✅ AccountCog 已加載")
        await bot.load_extension("cogs.proxy")
        logger.main_logger.info("✅ ProxyCog 已加載")
        await bot.load_extension("cogs.monitor")
        logger.main_logger.info("✅ MonitorCog 已加載")
        logger.main_logger.info("✅ 所有 Cogs 已加載")
    except Exception as e:
        logger.error_logger.error(f"加載 Cogs 失敗: {e}")
        raise
    
    # 同步斜線指令
    try:
        logger.main_logger.info("🔄 開始同步斜線指令...")
        synced = await bot.tree.sync()
        logger.main_logger.info(f"✅ 已同步 {len(synced)} 個斜線指令")
        print(f"✅ 已同步 {len(synced)} 個斜線指令")
        
        # 逐一輸出每個命令
        for cmd in synced:
            logger.main_logger.info(f"  📌 命令已註冊: /{cmd.name} - {cmd.description}")
    except Exception as e:
        logger.error_logger.error(f"同步斜線指令失敗: {e}")
        raise

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """全局應用命令錯誤處理"""
    if isinstance(error, app_commands.CheckFailure):
        logger.main_logger.warning(f"❌ 命令檢查失敗: {interaction.command.name} (用戶: {interaction.user.id})")
        await interaction.response.send_message("❌ 您沒有權限執行此命令", ephemeral=True)
    else:
        logger.error_logger.error(f"命令錯誤 - {interaction.command.name}: {str(error)}")
        await interaction.response.send_message("❌ 發生未預期的錯誤，已記錄日誌", ephemeral=True)

@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    """前缀命令的全局錯誤處理 - 忽略 CommandNotFound 錯誤"""
    if isinstance(error, commands.CommandNotFound):
        # 靜默忽略，不記錄日誌
        return
    
    # 其他錯誤記錄
    logger.error_logger.error(f"前缀命令錯誤: {str(error)}")

# 運行
if __name__ == "__main__":
    try:
        logger.main_logger.info("🚀 正在啟動機器人...")
        bot.run(os.getenv("DISCORD_TOKEN"))
    except Exception as e:
        logger.error_logger.critical(f"機器人啟動失敗: {str(e)}")
        raise