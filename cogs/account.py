import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from utils.encryption import pwd_manager
from utils.logger import logger
from api.client import frp_client

class AccountCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def _wait_for_input(self, interaction: discord.Interaction, prompt, timeout=60.0, max_retries=2, hide_input=False):
        """通用輸入等待函數，帶重試機制"""
        user = interaction.user
        dm_channel = user.dm_channel or await user.create_dm()
        
        for attempt in range(max_retries):
            try:
                await dm_channel.send(prompt)
                
                def check(message):
                    return message.author == user and message.channel == dm_channel
                
                msg = await self.bot.wait_for("message", check=check, timeout=timeout)
                content = msg.content.strip()
                
                # 隱藏密碼訊息
                if hide_input:
                    try:
                        await msg.delete()
                    except:
                        pass
                
                return content
            
            except asyncio.TimeoutError:
                remaining = max_retries - attempt - 1
                if remaining > 0:
                    await dm_channel.send(f"⏱️ 超時，請在 {timeout} 秒內回覆。剩餘嘗試次數：{remaining}")
                else:
                    await dm_channel.send("❌ 超時次數過多，已取消操作")
                    logger.log_error("input_timeout", f"用戶多次超時", user.id)
                return None
            except Exception as e:
                logger.log_error("input_error", str(e), user.id)
                await dm_channel.send("❌ 發生錯誤，請重試")
                return None
        
        return None
    
    @app_commands.command(name="bind", description="綁定您的 TaiwanFRP 帳號")
    async def bind_account(self, interaction: discord.Interaction):
        """綁定 TaiwanFRP 帳號（私訊執行）"""
        user = interaction.user
        logger.log_command(user.id, "bind")
        
        # 延遲回應以獲取DM頻道
        await interaction.response.defer(ephemeral=True)
        
        # 確保用戶有DM頻道
        try:
            dm_channel = user.dm_channel or await user.create_dm()
        except:
            await interaction.followup.send("❌ 無法打開私訊，請檢查隱私設定", ephemeral=True)
            logger.log_bind_attempt(user.id, "unknown", False, "無法打開DM")
            return
        
        await interaction.followup.send("✅ 已在私訊中發送指令流程", ephemeral=True)
        
        # 檢查是否已綁定
        existing = pwd_manager.get_credentials(user.id)
        if existing:
            await dm_channel.send(f"⚠️ 您已綁定帳號: `{existing['username']}`\n如需更改，請先執行 `/unbind`")
            return
        
        await dm_channel.send("🔐 開始綁定 TaiwanFRP 帳號...\n*您的密碼將被安全加密存儲*")
        
        # 要求輸入帳號
        username = await self._wait_for_input(
            interaction,
            "請輸入您的 TaiwanFRP **帳號**:",
            timeout=60.0,
            max_retries=2
        )
        if not username:
            return
        
        # 要求輸入密碼
        password = await self._wait_for_input(
            interaction,
            "請輸入您的 TaiwanFRP **密碼**:",
            timeout=60.0,
            max_retries=2,
            hide_input=True
        )
        if not password:
            return
        
        # 驗證帳號密碼
        await dm_channel.send("🔍 正在驗證帳號...")
        try:
            is_valid = await asyncio.wait_for(
                frp_client.login(username, password),
                timeout=10.0
            )
            
            if not is_valid:
                await dm_channel.send("❌ 帳號或密碼錯誤，請檢查後重試")
                logger.log_bind_attempt(user.id, username, False, "帳號或密碼錯誤")
                return
            
            # 保存加密的認證信息
            pwd_manager.save_credentials(user.id, username, password)
            await dm_channel.send("✅ 帳號綁定成功！您現在可以使用代理監控命令了。")
            logger.log_bind_attempt(user.id, username, True)
        
        except asyncio.TimeoutError:
            await dm_channel.send("❌ API 驗證超時，請檢查網絡連線後重試")
            logger.log_error("api_timeout", "login 驗證超時", user.id)
        except Exception as e:
            await dm_channel.send(f"❌ 驗證失敗: {str(e)}")
            logger.log_error("bind_error", str(e), user.id)
    
    @app_commands.command(name="unbind", description="解綁您的 TaiwanFRP 帳號")
    async def unbind_account(self, interaction: discord.Interaction):
        """解綁 TaiwanFRP 帳號"""
        user = interaction.user
        logger.log_command(user.id, "unbind")
        
        await interaction.response.defer(ephemeral=True)
        pwd_manager.remove_credentials(user.id)
        
        await interaction.followup.send("✅ 帳號已解綁", ephemeral=True)
        logger.log_unbind(user.id)
    
    @app_commands.command(name="info", description="查看綁定的帳號信息")
    async def account_info(self, interaction: discord.Interaction):
        """查看綁定的帳號信息"""
        user = interaction.user
        logger.log_command(user.id, "info")
        
        await interaction.response.defer(ephemeral=True)
        creds = pwd_manager.get_credentials(user.id)
        
        if not creds:
            await interaction.followup.send("❌ 您還未綁定任何帳號，請使用 `/bind` 綁定", ephemeral=True)
            return
        
        embed = discord.Embed(title="帳號信息", color=discord.Color.blue())
        embed.add_field(name="TaiwanFRP 帳號", value=f"`{creds['username']}`", inline=False)
        embed.set_footer(text="密碼已安全加密存儲，不會顯示")
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="help", description="顯示所有可用命令")
    async def show_help(self, interaction: discord.Interaction):
        """顯示所有可用命令"""
        user = interaction.user
        logger.log_command(user.id, "help")
        
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(
            title="📖 TaiwanFRP Bot 命令幫助",
            color=discord.Color.gold(),
            description="所有可用命令列表"
        )
        
        commands_info = [
            ("**/bind**", "綁定您的 TaiwanFRP 帳號（私訊執行）"),
            ("**/unbind**", "解綁帳號（私訊執行）"),
            ("**/info**", "查看綁定的帳號信息（私訊執行）"),
            ("**/tunnels**", "查看您的所有隧道（私訊執行）"),
            ("**/status <隧道名稱>**", "檢查特定隧道的狀態（私訊執行）"),
            ("**/nodes**", "查看可用的節點列表（私訊執行）"),
            ("**/monitor**", "查看伺服器監控狀態（公開頻道）"),
            ("**/frp_stats**", "查看 TaiwanFRP 統計信息（公開頻道）"),
            ("**/service_status**", "查看 TaiwanFRP 實時監控面板（公開頻道）"),
            ("**/help**", "顯示此幫助信息"),
        ]
        
        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        embed.set_footer(text="💡 提示: 大部分命令需要先綁定帳號")
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    cog = AccountCog(bot)
    await bot.add_cog(cog)
    logger.main_logger.info("📌 AccountCog 命令已註冊: /bind, /unbind, /info, /help")