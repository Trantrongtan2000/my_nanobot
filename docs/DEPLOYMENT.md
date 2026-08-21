# DEPLOYMENT GUIDE: NANOBOT NOOA HYBRID

## 1. Raspberry Pi Local Host (Edge)
```bash
# 1. Clone / Pull repository
git clone https://github.com/Trantrongtan2000/my_nanobot.git
cd my_nanobot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run automated test suite
pytest tests/

# 4. Start Nanobot Coordinator
python -c "from nanobot.agents.coordinator import NanobotCoordinator; bot = NanobotCoordinator(); print(bot.process_message('Tra cứu cân MS4980 Da Liễu'))"
```

## 2. Cloudflare Computer Edge Deployment
```bash
cd cloudflare
npm install
wrangler deploy
```
