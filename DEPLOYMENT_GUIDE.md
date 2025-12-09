# 🚀 Quick Deployment Guide

## ✅ Tóm Tắt

**Khi bạn push code lên GitHub (branch `main`), CI/CD sẽ tự động:**
1. Pull code mới về server
2. Cài đặt dependencies
3. Stop services cũ
4. **Start với watchdog auto-restart** 
5. ✅ **Watchdog tự động monitor và restart khi crash!**

## 🎯 Watchdog Tự Động Chạy

Khi deploy xong, watchdog sẽ:
- ✅ **Tự động start** cùng với services
- ✅ **Monitor mỗi 30 giây**
- ✅ **Auto-restart trong 30-60 giây** khi:
  - Process crash
  - Service hang (không respond)
  - Memory usage > 80%
- ✅ **Rate limit**: Max 5 restarts/giờ (tránh infinite loop)
- ✅ **Full logging** vào `logs/watchdog.log`

## 📋 Setup CI/CD (One-Time)

### 1. Add GitHub Secrets

Vào GitHub repo → Settings → Secrets and variables → Actions → New secret:

```
VPS_HOST       = your.server.ip.address
VPS_USER       = your_username
VPS_SSH_KEY    = <your_private_ssh_key>
```

### 2. Ensure .env on Server

SSH vào server và tạo file `.env`:

```bash
cd /srv/poc_elastik
nano .env
```

Paste nội dung:
```bash
DEEPSEEK_API_KEY=sk-xxxxx
OPENAI_API_KEY=sk-xxxxx
ES_HOST=http://localhost:9200
ES_INDEX_NAME=demo_documents
APP_PORT=8000
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

### 3. Ensure Elasticsearch Running

```bash
# Check if running
curl http://localhost:9200

# If not, start it:
docker run -d --name es-demo \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.15.0
```

## 🚀 Deploy Workflow

### Option 1: Auto Deploy (Push to GitHub)
```bash
# Local machine
git add .
git commit -m "Your changes"
git push origin main
```

GitHub Actions sẽ tự động deploy → **Watchdog tự động start!**

### Option 2: Manual Deploy
```bash
# SSH vào server
ssh user@your-server

# Go to project dir
cd /srv/poc_elastik

# Pull latest code
git pull origin main

# Run deploy script (includes watchdog)
./deploy.sh
```

### Option 3: Manual Trigger GitHub Actions
GitHub repo → Actions → "Deploy to Production" → Run workflow

## 📊 Check Status After Deploy

### SSH vào server:
```bash
ssh user@your-server
cd /srv/poc_elastik
```

### Check services:
```bash
# Check if all running
curl http://localhost:8000/health
curl http://localhost:8501

# Check watchdog
ps aux | grep watchdog.sh

# Check process IDs
cat logs/fastapi.pid
cat logs/streamlit.pid
cat logs/watchdog.pid
```

### Monitor logs:
```bash
# Watch watchdog activity
tail -f logs/watchdog.log

# Watch API logs
tail -f logs/fastapi.log

# Watch UI logs
tail -f logs/streamlit.log
```

## 🔍 Verify Auto-Restart Works

### Test 1: Kill FastAPI
```bash
# Kill the process
kill $(cat logs/fastapi.pid)

# Wait 30-60 seconds and check
tail -f logs/watchdog.log
# You'll see: "⚠️ Restarting FastAPI..." → "✓ FastAPI restarted"

# Verify it's back
curl http://localhost:8000/health
```

### Test 2: Check Watchdog Logs
```bash
tail -20 logs/watchdog.log
```

Should see:
```
[2025-12-09 10:30:00] 🔍 Watchdog started - Monitoring services
[2025-12-09 10:30:30] ✓ All services running normally
[2025-12-09 10:31:00] ✓ All services running normally
```

## 🛠️ Management Commands

```bash
# Stop all services (including watchdog)
./stop_demo.sh

# Start all services with watchdog
./start_demo.sh

# Restart everything
./stop_demo.sh && ./start_demo.sh

# Check status
curl http://localhost:8000/health
ps aux | grep -E "uvicorn|streamlit|watchdog"
```

## 🎯 URLs

After deployment, access via:

- **Streamlit UI**: `http://YOUR_SERVER_IP:8501`
- **API Docs**: `http://YOUR_SERVER_IP:8000/docs`
- **Health Check**: `http://YOUR_SERVER_IP:8000/health`

## ⚠️ Troubleshooting

### Services not starting
```bash
# Check logs
tail -50 logs/fastapi.log
tail -50 logs/streamlit.log

# Check if Elasticsearch is running
curl http://localhost:9200

# Check if .env exists
cat .env
```

### Watchdog not running
```bash
# Check if script exists and is executable
ls -la watchdog.sh
# Should show: -rwxr-xr-x

# Start manually
./watchdog.sh &

# Or restart everything
./stop_demo.sh && ./start_demo.sh
```

### Too many restarts (5/hour limit reached)
```bash
# Check what's causing crashes
tail -100 logs/watchdog.log
tail -100 logs/fastapi.log

# Fix the root cause (e.g., Elasticsearch down, memory issue)
# Then restart manually
./stop_demo.sh && ./start_demo.sh
```

### Port already in use
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9

# Then restart
./start_demo.sh
```

## ✅ Success Indicators

After deployment, you should see:

1. **GitHub Actions**: ✅ Green checkmark on workflow
2. **Health Check**: `curl http://localhost:8000/health` returns 200
3. **Streamlit**: `curl http://localhost:8501` returns 200
4. **Watchdog**: `ps aux | grep watchdog.sh` shows running process
5. **Logs**: `tail -f logs/watchdog.log` shows "All services running normally"

## 🎉 Summary

| What | How | When |
|------|-----|------|
| **Deploy** | `git push origin main` | GitHub Actions auto-deploys |
| **Watchdog Starts** | Automatically | During deployment |
| **Auto-Restart** | Automatic | Within 30-60s of crash |
| **Monitor** | `tail -f logs/watchdog.log` | Anytime |
| **Stop** | `./stop_demo.sh` | When needed |
| **Start** | `./start_demo.sh` | When needed |

**Bây giờ bạn chỉ cần push code, watchdog sẽ tự động lo phần còn lại!** 🚀
