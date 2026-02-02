import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
from utils.logger import logger
from api.client import frp_client

class MonitorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_status_message = None
        self.monitor_channel = None
        self.update_server_status.start()
    
    @app_commands.command(name="monitor", description="查看伺服器監控狀態")
    @app_commands.describe(action="選擇動作")
    async def monitor_status(
        self,
        interaction: discord.Interaction,
        action: str = None
    ):
        """查看伺服器監控狀態"""
        user = interaction.user
        logger.log_command(user.id, "monitor", action or "view")
        
        await interaction.response.defer(ephemeral=False)
        
        try:
            nodes = await asyncio.wait_for(
                frp_client.get_nodes(),
                timeout=10.0
            )
            
            if not nodes:
                await interaction.followup.send("📭 暫無節點信息")
                return
            
            embed = discord.Embed(
                title="🖥️ TaiwanFRP 伺服器監控面板",
                color=discord.Color.blue(),
                description="實時伺服器狀態監控"
            )
            
            online_count = 0
            total_ports = 0
            
            for node in nodes:
                node_name = node.get('name', '未知')
                node_ip = node.get('ip', 'N/A')
                ports = node.get('availablePorts', [])
                available_ports_count = len(ports)
                
                # 簡單判定節點是否在線（有可用端口則判定為在線）
                is_online = available_ports_count > 0
                if is_online:
                    online_count += 1
                total_ports += available_ports_count
                
                status_emoji = "🟢" if is_online else "🔴"
                ports_str = ', '.join(map(str, ports[:5]))
                if available_ports_count > 5:
                    ports_str += f", 等 {available_ports_count - 5} 個端口"
                
                value = f"{status_emoji} **IP**: `{node_ip}`\n"
                value += f"**可用端口**: {available_ports_count}\n"
                value += f"**端口列表**: {ports_str if ports_str else '無'}"
                
                embed.add_field(name=node_name, value=value, inline=False)
            
            embed.add_field(
                name="📊 統計信息",
                value=f"**在線節點**: {online_count}/{len(nodes)}\n**總可用端口**: {total_ports}",
                inline=False
            )
            
            embed.set_footer(text="最後更新於命令執行時")
            await interaction.followup.send(embed=embed)
            logger.log_tunnel_check(user.id, "monitor", f"查看監控面板 - {online_count}/{len(nodes)} 節點在線")
        
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ 獲取監控信息超時")
            logger.log_error("monitor_timeout", "get_nodes", user.id)
        except Exception as e:
            await interaction.followup.send(f"❌ 錯誤: {str(e)}")
            logger.log_error("monitor_error", str(e), user.id)
    
    @tasks.loop(minutes=5)
    async def update_server_status(self):
        """定期更新伺服器狀態（需要配置頻道ID）"""
        try:
            # 這裡需要通過環境變量或配置文件設定監控頻道
            # 暫時註解，避免錯誤
            pass
        except Exception as e:
            logger.error_logger.error(f"更新伺服器狀態失敗: {e}")
    
    @update_server_status.before_loop
    async def before_update_server_status(self):
        """等待機器人準備就緒"""
        await self.bot.wait_until_ready()
    
    @app_commands.command(name="frp_stats", description="查看 TaiwanFRP 統計信息")
    async def frp_statistics(self, interaction: discord.Interaction):
        """查看 TaiwanFRP 統計信息"""
        user = interaction.user
        logger.log_command(user.id, "frp_stats")
        
        await interaction.response.defer(ephemeral=False)
        
        try:
            nodes = await asyncio.wait_for(
                frp_client.get_nodes(),
                timeout=10.0
            )
            
            # 統計數據
            total_nodes = len(nodes)
            online_nodes = sum(1 for n in nodes if n.get('availablePorts', []))
            total_available_ports = sum(len(n.get('availablePorts', [])) for n in nodes)
            
            embed = discord.Embed(
                title="📈 TaiwanFRP 服務統計",
                color=discord.Color.blurple(),
                description="全球伺服器統計信息"
            )
            
            embed.add_field(name="🌍 總節點數", value=str(total_nodes), inline=True)
            embed.add_field(name="🟢 在線節點", value=str(online_nodes), inline=True)
            embed.add_field(name="📊 在線率", value=f"{(online_nodes/total_nodes*100):.1f}%", inline=True)
            
            embed.add_field(
                name="🔌 可用端口",
                value=str(total_available_ports),
                inline=True
            )
            
            # 列出各節點詳細信息
            embed.add_field(name="🏢 節點詳情", value="─" * 20, inline=False)
            
            for node in nodes:
                node_name = node.get('name', '未知')
                available_ports = len(node.get('availablePorts', []))
                is_online = available_ports > 0
                status = "🟢 在線" if is_online else "🔴 離線"
                
                value = f"{status} - 可用端口: {available_ports}"
                embed.add_field(name=node_name, value=value, inline=True)
            
            embed.set_footer(text="數據每次查詢時即時更新")
            await interaction.followup.send(embed=embed)
            logger.log_tunnel_check(user.id, "stats", "查看統計信息")
        
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ 獲取統計信息超時")
            logger.log_error("stats_timeout", "frp_stats", user.id)
        except Exception as e:
            await interaction.followup.send(f"❌ 錯誤: {str(e)}")
            logger.log_error("stats_error", str(e), user.id)
    
    @app_commands.command(name="service_status", description="查看 TaiwanFRP 服務狀態")
    async def service_status_command(self, interaction: discord.Interaction):
        """查看各節點的詳細監控信息（客戶端數、流量等）"""
        user = interaction.user
        logger.log_command(user.id, "service_status")
        
        await interaction.response.defer(ephemeral=False)
        
        try:
            monitor_data = await asyncio.wait_for(
                frp_client.get_frp_monitor_status(),
                timeout=10.0
            )
            
            if not monitor_data or 'result' not in monitor_data:
                await interaction.followup.send("❌ 無法獲取監控數據")
                return
            
            result = monitor_data.get('result', {})
            stats = monitor_data.get('stats', {})
            
            embed = discord.Embed(
                title="🔧 TaiwanFRP 實時監控面板",
                color=discord.Color.blue(),
                description="全球節點運行狀態與流量統計"
            )
            
            # 統計信息
            total_clients = 0
            total_connections = 0
            total_traffic_in = 0
            total_traffic_out = 0
            online_servers = 0
            total_servers = len(result)
            
            # 遍歷每個服務器節點
            for server_name, server_data_list in result.items():
                if not server_data_list:
                    continue
                
                data = server_data_list[0]  # 每個節點只有一條記錄
                is_online = data.get('is_online', 0)
                
                if is_online:
                    online_servers += 1
                
                client_counts = data.get('client_counts', 0)
                cur_conns = data.get('cur_conns', 0)
                tcp_count = data.get('tcp_count', 0)
                udp_count = data.get('udp_count', 0)
                traffic_in = data.get('total_traffic_in', 0)
                traffic_out = data.get('total_traffic_out', 0)
                
                total_clients += client_counts
                total_connections += cur_conns
                total_traffic_in += traffic_in
                total_traffic_out += traffic_out
                
                # 節點狀態
                status_emoji = "🟢" if is_online else "🔴"
                
                # 節點詳細信息
                node_info = f"{status_emoji} **狀態**: {'在線' if is_online else '離線'}\n"
                node_info += f"👥 **客戶端**: {client_counts} | 📊 **連接**: {cur_conns}\n"
                node_info += f"🔄 **TCP**: {tcp_count} | 📡 **UDP**: {udp_count}\n"
                node_info += f"📥 **入站**: {frp_client.format_traffic(traffic_in)}\n"
                node_info += f"📤 **出站**: {frp_client.format_traffic(traffic_out)}"
                
                embed.add_field(name=server_name, value=node_info, inline=False)
            
            # 全局統計
            embed.add_field(
                name="📊 全局統計",
                value=f"🌍 **在線節點**: {online_servers}/{total_servers}\n"
                      f"👥 **總客戶端**: {total_clients}\n"
                      f"🔗 **活躍連接**: {total_connections}\n"
                      f"📥 **總入站流量**: {frp_client.format_traffic(total_traffic_in)}\n"
                      f"📤 **總出站流量**: {frp_client.format_traffic(total_traffic_out)}",
                inline=False
            )
            
            # 版本信息
            version_info = stats.get('version', {})
            if version_info:
                versions_str = ", ".join([f"{v}: {count}" for v, count in version_info.items()])
                embed.add_field(name="🔖 版本分佈", value=versions_str, inline=False)
            
            embed.set_footer(text="數據實時更新 | 來源: redbean0721 監控 API")
            
            await interaction.followup.send(embed=embed)
            logger.log_command(user.id, "service_status", f"查看監控 - {online_servers}/{total_servers} 節點在線")
        
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ 獲取監控數據超時")
            logger.log_error("service_timeout", "service_status", user.id)
        except Exception as e:
            await interaction.followup.send(f"❌ 錯誤: {str(e)}")
            logger.log_error("service_error", str(e), user.id)

async def setup(bot):
    cog = MonitorCog(bot)
    await bot.add_cog(cog)
    logger.main_logger.info("📌 MonitorCog 命令已註冊: /monitor, /frp_stats, /service_status")
