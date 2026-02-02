import aiohttp
import json
import re

class TaiwanFRPClient:
    def __init__(self, base_url="https://taiwanfrp.ddns.net"):
        self.base_url = base_url
        self.session = None
    
    async def _get_session(self):
        """獲取或創建 aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """關閉 session"""
        if self.session:
            await self.session.close()
    
    async def login(self, username: str, password: str) -> bool:
        """登入驗證"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/login"
            async with session.post(
                url,
                json={"username": username, "password": password}
            ) as resp:
                # 根據 HTTP 狀態碼判斷 - 200 表示成功，其他表示失敗
                if resp.status == 200:
                    return True
                else:
                    text = await resp.text()
                    print(f"❌ 登入失敗: HTTP {resp.status} - {text[:200]}")
                    return False
        except Exception as e:
            print(f"❌ 登入失敗: {e}")
            return False
    
    async def list_tunnels(self, username: str, password: str) -> list:
        """獲取代理列表"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/list_tunnels"
            async with session.post(
                url,
                json={"username": username, "password": password}
            ) as resp:
                if resp.status != 200:
                    print(f"❌ 獲取代理列表失敗: HTTP {resp.status}")
                    return []
                
                data = await resp.json()
                print(f"📋 API 返回的隧道數據: {json.dumps(data, ensure_ascii=False, indent=2)}")
                
                # 嘗試多種可能的字段名稱
                tunnels = data.get("tunnels", []) or data.get("data", []) or []
                
                if tunnels:
                    print(f"✅ 成功獲取 {len(tunnels)} 個隧道")
                    for tunnel in tunnels:
                        print(f"  - 隧道數據: {tunnel}")
                
                return tunnels
        except Exception as e:
            print(f"❌ 獲取代理列表失敗: {e}")
            return []
    
    async def check_tunnel(self, username: str, password: str, 
                          tunnel_name: str, protocol: str, node_name: str) -> dict:
        """檢查隧道狀態"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/check_tunnel"
            async with session.post(
                url,
                json={
                    "username": username,
                    "password": password,
                    "tunnelName": tunnel_name,
                    "protocol": protocol,
                    "nodeName": node_name
                }
            ) as resp:
                if resp.status != 200:
                    print(f"❌ 檢查隧道失敗: {resp.status}")
                    return {"status": "error"}
                
                return await resp.json()
        except Exception as e:
            print(f"❌ 檢查隧道失敗: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_nodes(self) -> list:
        """獲取節點列表"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/nodes.json"
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"❌ 獲取節點列表失敗: {resp.status}")
                    return []
                
                data = await resp.json()
                return data.get("nodes", [])
        except Exception as e:
            print(f"❌ 獲取節點列表失敗: {e}")
            return []
    
    async def get_frpc_ini(self, username: str, password: str, node_name: str) -> str:
        """獲取 frpc.ini 配置文件"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/get_frpc_ini"
            async with session.get(
                url,
                params={
                    "username": username,
                    "password": password,
                    "nodeName": node_name
                }
            ) as resp:
                if resp.status != 200:
                    print(f"❌ 獲取 frpc.ini 失敗: HTTP {resp.status}")
                    return ""
                
                return await resp.text()
        except Exception as e:
            print(f"❌ 獲取 frpc.ini 失敗: {e}")
            return ""
    
    def parse_frpc_ini(self, ini_content: str) -> dict:
        """解析 frpc.ini 內容，提取隧道配置"""
        tunnels = {}
        lines = ini_content.split('\n')
        current_tunnel = None
        
        for line in lines:
            line = line.strip()
            
            # 跳過空行和註釋
            if not line or line.startswith(';') or line.startswith('#'):
                continue
            
            # 檢測隧道區段 [tunnel_name] 或 [tunnel_name,udp]
            if line.startswith('[') and line.endswith(']'):
                tunnel_name = line[1:-1].split(',')[0]  # 去掉 ,udp 後綴
                if tunnel_name.lower() != 'common':
                    if tunnel_name not in tunnels:
                        tunnels[tunnel_name] = {
                            'name': tunnel_name,
                            'type': 'tcp',
                            'local_ip': '',
                            'local_port': '',
                            'remote_port': '',
                            'protocol': ''
                        }
                    current_tunnel = tunnel_name
            elif current_tunnel and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'type':
                    tunnels[current_tunnel]['type'] = value
                elif key == 'local_ip':
                    tunnels[current_tunnel]['local_ip'] = value
                elif key == 'local_port':
                    tunnels[current_tunnel]['local_port'] = value
                elif key == 'remote_port':
                    tunnels[current_tunnel]['remote_port'] = value
                elif key == 'protocol':
                    tunnels[current_tunnel]['protocol'] = value
        
        return list(tunnels.values())
    
    async def get_service_status(self) -> dict:
        """獲取 TaiwanFRP 服務狀態"""
        try:
            session = await self._get_session()
            url = "https://uptime.taiwanfrp.me/status/service"
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"❌ 獲取服務狀態失敗: HTTP {resp.status}")
                    return {}
                
                html = await resp.text()
                return self.parse_service_status(html)
        except Exception as e:
            print(f"❌ 獲取服務狀態失敗: {e}")
            return {}
    
    async def get_frp_monitor_status(self) -> dict:
        """從 redbean0721 API 獲取詳細的 FRP 監控數據"""
        try:
            session = await self._get_session()
            url = "https://api.redbean0721.com/api/frp/monitor/query?version=0.63.0&node=all&num=11"
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"❌ 獲取 FRP 監控數據失敗: HTTP {resp.status}")
                    return {}
                
                data = await resp.json()
                print(f"✅ 成功獲取 FRP 監控數據")
                return data
        except Exception as e:
            print(f"❌ 獲取 FRP 監控數據失敗: {e}")
            return {}
    
    def format_traffic(self, bytes_value: int) -> str:
        """將字節轉換為可讀的流量格式"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.2f} PB"

# 全局實例
frp_client = TaiwanFRPClient()