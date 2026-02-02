import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from utils.encryption import pwd_manager
from utils.logger import logger
from api.client import frp_client

class ProxyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="tunnels", description="查看您的隧道列表")
    async def list_tunnels(self, interaction: discord.Interaction):
        """查看您的隧道列表"""
        user = interaction.user
        logger.log_command(user.id, "tunnels")
        
        await interaction.response.defer(ephemeral=True)
        
        creds = pwd_manager.get_credentials(user.id)
        if not creds:
            await interaction.followup.send("❌ 您還未綁定帳號，請先執行 `/bind`", ephemeral=True)
            return
        
        try:
            # 先獲取基本隧道列表
            tunnels_basic = await asyncio.wait_for(
                frp_client.list_tunnels(creds['username'], creds['password']),
                timeout=10.0
            )
            
            if not tunnels_basic:
                await interaction.followup.send("📭 您目前沒有任何隧道", ephemeral=True)
                logger.log_tunnel_check(user.id, "none", "無隧道")
                return
            
            # 為每個節點獲取詳細配置
            tunnels_detailed = {}
            for tunnel_basic in tunnels_basic:
                node_name = tunnel_basic.get('node', '未知')
                try:
                    detailed = await asyncio.wait_for(
                        frp_client.list_tunnels_detailed(
                            creds['username'],
                            creds['password'],
                            node_name
                        ),
                        timeout=10.0
                    )
                    for tunnel_detail in detailed:
                        tunnels_detailed[tunnel_detail['name']] = tunnel_detail
                except:
                    pass
            
            embed = discord.Embed(
                title=f"🌐 您的隧道列表 ({len(tunnels_basic)})",
                color=discord.Color.green(),
                description=f"帳號: `{creds['username']}`"
            )
            
            for tunnel_basic in tunnels_basic:
                tunnel_name = tunnel_basic.get('name', '未知')
                node = tunnel_basic.get('node', '未知')
                
                # 從詳細配置中提取信息
                tunnel_detail = tunnels_detailed.get(tunnel_name, {})
                local_port = tunnel_detail.get('local_port', 'N/A')
                remote_port = tunnel_detail.get('remote_port', 'N/A')
                protocol = tunnel_detail.get('protocol', 'N/A')
                tunnel_type = tunnel_detail.get('type', 'tcp')
                
                if protocol == 'N/A':
                    protocol = f"{tunnel_type.upper()}"
                
                value = f"**協議**: {protocol}\n**節點**: {node}\n**本地**: :{local_port} → **遠端**: :{remote_port}"
                embed.add_field(name=tunnel_name, value=value, inline=False)
            
            embed.set_footer(text="使用 /status <隧道名稱> 查看詳細狀態")
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.log_tunnel_check(user.id, f"list_all", f"成功獲取 {len(tunnels_basic)} 個隧道")
        
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ 獲取隧道列表超時", ephemeral=True)
            logger.log_error("tunnel_timeout", "list_tunnels", user.id)
        except Exception as e:
            await interaction.followup.send(f"❌ 錯誤: {str(e)}", ephemeral=True)
            logger.log_error("tunnel_error", str(e), user.id)
    
    @app_commands.command(name="status", description="檢查特定隧道的狀態")
    @app_commands.describe(tunnel_name="隧道名稱")
    async def check_tunnel_status(self, interaction: discord.Interaction, tunnel_name: str):
        """檢查隧道狀態"""
        user = interaction.user
        logger.log_command(user.id, "status", tunnel_name)
        
        await interaction.response.defer(ephemeral=True)
        
        creds = pwd_manager.get_credentials(user.id)
        if not creds:
            await interaction.followup.send("❌ 您還未綁定帳號，請先執行 `/bind`", ephemeral=True)
            return
        
        try:
            # 先獲取隧道列表找到對應隧道
            tunnels = await asyncio.wait_for(
                frp_client.list_tunnels(creds['username'], creds['password']),
                timeout=10.0
            )
            
            tunnel_info = None
            for tunnel in tunnels:
                if tunnel.get('name') == tunnel_name:
                    tunnel_info = tunnel
                    break
            
            if not tunnel_info:
                await interaction.followup.send(f"❌ 找不到隧道 `{tunnel_name}`", ephemeral=True)
                logger.log_tunnel_check(user.id, tunnel_name, "not_found")
                return
            
            # 檢查隧道狀態
            status_info = await asyncio.wait_for(
                frp_client.check_tunnel(
                    creds['username'],
                    creds['password'],
                    tunnel_name,
                    tunnel_info.get('protocol', 'tcp'),
                    tunnel_info.get('node', 'unknown')
                ),
                timeout=10.0
            )
            
            is_online = status_info.get('status') == 'online'
            status_emoji = "🟢" if is_online else "🔴"
            
            embed = discord.Embed(
                title=f"{status_emoji} 隧道狀態: {tunnel_name}",
                color=discord.Color.green() if is_online else discord.Color.red()
            )
            
            embed.add_field(name="狀態", value="線上 ✅" if is_online else "離線 ❌", inline=True)
            embed.add_field(name="協議", value=tunnel_info.get('protocol', 'N/A'), inline=True)
            embed.add_field(name="節點", value=tunnel_info.get('node', 'N/A'), inline=True)
            embed.add_field(name="本地", value=f":{tunnel_info.get('local_port', 'N/A')}", inline=True)
            embed.add_field(name="遠端", value=f":{tunnel_info.get('remote_port', 'N/A')}", inline=True)
            
            if 'info' in status_info:
                info_text = str(status_info['info'])[:200]
                embed.add_field(name="詳細信息", value=f"```{info_text}```", inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.log_tunnel_check(user.id, tunnel_name, "online" if is_online else "offline")
        
        except asyncio.TimeoutError:
            await interaction.followup.send(f"❌ 檢查狀態超時", ephemeral=True)
            logger.log_error("status_timeout", f"檢查 {tunnel_name} 超時", user.id)
        except Exception as e:
            await interaction.followup.send(f"❌ 錯誤: {str(e)}", ephemeral=True)
            logger.log_error("status_error", str(e), user.id)
    
    @app_commands.command(name="nodes", description="查看可用的節點")
    async def list_nodes(self, interaction: discord.Interaction):
        """查看可用的節點"""
        user = interaction.user
        logger.log_command(user.id, "nodes")
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            nodes = await asyncio.wait_for(
                frp_client.get_nodes(),
                timeout=10.0
            )
            
            if not nodes:
                await interaction.followup.send("📭 暫無可用節點", ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"🌍 可用節點 ({len(nodes)})",
                color=discord.Color.blue()
            )
            
            for node in nodes:
                node_name = node.get('name', '未知')
                node_ip = node.get('ip', 'N/A')
                ports_str = ', '.join(map(str, node.get('availablePorts', [])))
                
                value = f"**IP**: `{node_ip}`\n**可用端口**: {ports_str if ports_str else '無可用端口'}"
                embed.add_field(name=node_name, value=value, inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ 獲取節點列表超時", ephemeral=True)
            logger.log_error("nodes_timeout", "get_nodes", user.id)
        except Exception as e:
            await interaction.followup.send(f"❌ 錯誤: {str(e)}", ephemeral=True)
            logger.log_error("nodes_error", str(e), user.id)

async def setup(bot):
    cog = ProxyCog(bot)
    await bot.add_cog(cog)
    logger.main_logger.info("📌 ProxyCog 命令已註冊: /tunnels, /status, /nodes")
