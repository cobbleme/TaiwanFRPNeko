# 🚀 TaiwanFRP Discord Bot

一個功能豐富的 Discord 機器人，用於管理和監控 TaiwanFRP 代理隧道。提供實時隧道管理、服務監控和流量統計功能。

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Discord.py](https://img.shields.io/badge/discord.py-2.0+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ 功能特性

### 帳戶管理
- **綁定帳戶** - 安全地綁定 TaiwanFRP 帳戶到 Discord 用戶
- **解綁帳戶** - 快速解綁帳戶
- **查看帳戶信息** - 檢查綁定的帳戶詳情
- **密碼加密存儲** - 使用加密方式安全保存用戶認證信息

### 隧道管理
- **查看隧道列表** - 實時顯示所有隧道配置
  - 隧道名稱
  - 協議類型（TCP/UDP/KCP）
  - 本地端口 & 遠端端口
  - 所在節點

- **檢查隧道狀態** - 詳細的隧道運行狀態
- **查看節點列表** - 全球可用的 FRP 節點和端口信息

### 服務監控
- **實時監控面板** - 使用 redbean0721 API 的高級監控
  - 每個節點的在線/離線狀態
  - 客戶端連接數統計
  - TCP/UDP 隧道數計數
  - 實時流量統計（入站/出站）
  - 全球聚合統計信息

- **統計信息** - 查看全球節點統計
  - 在線節點數
  - 可用端口總數
  - 節點狀態詳情

- **幫助命令** - 完整的命令使用說明

## 🛠️ 技術棧

- **Python 3.8+** - 編程語言
- **discord.py 2.0+** - Discord API 封裝
- **aiohttp** - 異步 HTTP 客戶端
- **python-dotenv** - 環境變量管理

## 📦 安裝

### 前置要求
- Python 3.8 或更高版本
- pip 包管理器
- Discord Bot Token

### 步驟

1. **克隆倉庫**
```bash
git clone https://github.com/yourusername/twfrpbot.git
cd twfrpbot
```

2. **創建虛擬環境（推薦）**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **安裝依賴**
```bash
pip install -r requirements.txt
```

4. **配置環境變量**
創建 `.env` 文件並添加：
```env
DISCORD_TOKEN=your_bot_token_here
```

5. **運行機器人**
```bash
python bot.py
```

## ⚙️ 配置

### 環境變量

```env
# Discord Bot Token
DISCORD_TOKEN=your_bot_token_here

# 其他可選配置
LOG_LEVEL=INFO
```

### 數據存儲

用戶數據存儲在 `data/users.json`：
```json
{
  "user_id": {
    "username": "frp_username",
    "password": "encrypted_password"
  }
}
```

## 🎯 使用指南

### 命令列表

| 命令 | 描述 | 執行位置 |
|------|------|--------|
| `/bind` | 綁定 TaiwanFRP 帳戶 | 私訊 |
| `/unbind` | 解綁帳戶 | 私訊 |
| `/info` | 查看綁定帳戶信息 | 私訊 |
| `/tunnels` | 查看所有隧道 | 私訊 |
| `/status <隧道名>` | 檢查隧道狀態 | 私訊 |
| `/nodes` | 查看可用節點 | 私訊 |
| `/monitor` | 伺服器監控面板 | 公開頻道 |
| `/frp_stats` | TaiwanFRP 統計信息 | 公開頻道 |
| `/service_status` | 實時監控面板 | 公開頻道 |
| `/help` | 顯示幫助信息 | 任何地方 |

### 快速開始

1. **綁定帳戶**
```
/bind
```
- 機器人會在私訊中引導您輸入 TaiwanFRP 帳戶名和密碼
- 密碼會被安全加密存儲

2. **查看隧道**
```
/tunnels
```
- 顯示所有隧道的詳細配置
- 包含協議、端口、節點等信息

3. **監控服務**
```
/service_status
```
- 查看全球節點實時狀態
- 顯示客戶端連接數和流量統計

## 📁 項目結構

```
twfrpbot/
├── bot.py                 # 主程序入口
├── requirements.txt       # Python 依賴
├── .env                  # 環境變量配置（不上傳）
├── .env.example          # 環境變量模板
│
├── api/
│   ├── __init__.py
│   └── client.py         # TaiwanFRP API 客戶端
│
├── cogs/
│   ├── account.py        # 帳戶管理 Cog
│   ├── proxy.py          # 隧道管理 Cog
│   └── monitor.py        # 服務監控 Cog
│
├── utils/
│   ├── encryption.py     # 密碼加密工具
│   └── logger.py         # 日誌記錄工具
│
└── data/
    ├── users.json        # 用戶數據存儲
    └── logs/             # 日誌文件目錄
```

## 🔧 API 集成

### TaiwanFRP API
- **login** - 帳戶驗證
- **list_tunnels** - 獲取隧道列表
- **get_frpc_ini** - 獲取配置文件
- **check_tunnel** - 檢查隧道狀態

### 第三方 API
- **redbean0721 監控 API** - 實時服務監控
- **uptime.taiwanfrp.me** - 服務狀態頁面

## 🔒 安全性

- ✅ 密碼加密存儲（AES 加密）
- ✅ 敏感信息不會在日誌中顯示
- ✅ 支持超時和錯誤重試機制
- ✅ 完整的審計日誌記錄

## 📊 日誌記錄

機器人記錄所有重要操作：
- 命令執行日誌 (`logs/main.log`)
- 錯誤日誌 (`logs/error.log`)
- 用戶活動追蹤

日誌位置：`data/logs/`

## 🚀 部署

### Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
```

### 傳統部署

推薦使用 `systemd` 或 `pm2` 管理進程。

## 🤝 貢獻

歡迎貢獻！請按以下步驟：

1. Fork 本倉庫
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交改動 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📝 更新日誌

### v1.0.0 (2026-02-02)
- ✨ 初始版本發布
- 🎯 完整的帳戶綁定系統
- 🔍 實時隧道監控
- 📊 全球服務監控面板
- 📈 流量統計和節點監控

## 🐛 已知問題

- 第一次同步命令可能需要 15-30 秒才能在 Discord 中顯示
- 某些舊版本 Discord 客戶端可能需要重啟才能看到新命令

## 💡 常見問題

**Q: 我的密碼安全嗎？**
A: 是的。密碼使用 AES-256 加密存儲，並且只在與 API 通信時使用。

**Q: 機器人可以編輯我的隧道配置嗎？**
A: 當前版本只支持查看。編輯功能將在未來版本中推出。

**Q: 如何報告問題？**
A: 請在 GitHub Issues 中詳細描述問題，包含日誌和重現步驟。

## 📄 License

本項目採用 MIT License - 詳見 [LICENSE](LICENSE) 文件

## 📞 支持

- 📧 Email: support@example.com
- 🔗 Discord: [Join Our Server](https://discord.gg/example)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/twfrpbot/issues)

## 🙏 致謝

- TaiwanFRP 提供的 FRP 服務
- redbean0721 的監控 API
- discord.py 社區的支持

---

**Made with ❤️ for the FRP community**

⭐ 如果這個項目對你有幫助，請給個 Star！
