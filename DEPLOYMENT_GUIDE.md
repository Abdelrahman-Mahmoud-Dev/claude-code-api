# Deployment Guide - Hostinger VPS with CloudPanel

Complete step-by-step guide to deploy Claude Code API on a Hostinger VPS with CloudPanel and Docker.

## Prerequisites

- Hostinger VPS with CloudPanel installed
- SSH access to the VPS
- A domain/subdomain pointed to the VPS IP (e.g. `ai.beingmomen.com`)
- Claude account (Pro or Max subscription for CLI auth)

---

## Step 1: Create Reverse Proxy in CloudPanel

1. Open CloudPanel: `https://YOUR_VPS_IP:8443`
2. Go to **Sites** → **Add Site** → **Create a Reverse Proxy**
3. Fill in:
   - **Domain Name:** `ai.yourdomain.com`
   - **Reverse Proxy Url:** `http://127.0.0.1:9514`
4. Click **Create**

---

## Step 2: Connect to VPS via SSH

```bash
ssh root@YOUR_VPS_IP
```

Then switch to the site user:

```bash
su - beingmomen-ai
```

---

## Step 3: Install Docker & Docker Compose

```bash
# Install Docker
sudo apt update && sudo apt install docker.io -y

# Enable Docker on boot
sudo systemctl enable docker
sudo systemctl start docker

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose V2
sudo apt install docker-compose-v2 -y

# IMPORTANT: Logout and login again for group changes
exit
ssh beingmomen-ai@YOUR_VPS_IP

# Verify installation
docker --version
docker compose version
```

---

## Step 4: Install Node.js & Claude CLI

Required for `claude auth login`:

```bash
# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Claude CLI globally
sudo npm install -g @anthropic-ai/claude-code

# Verify
node --version
claude --version
```

---

## Step 5: Clone the Project

```bash
cd /home/beingmomen-ai/htdocs

# Clone the repo
git clone https://github.com/Abdelrahman-Mahmoud-Dev/claude-code-api.git ai.beingmomen.com

cd ai.beingmomen.com
```

---

## Step 6: Create .env File

```bash
nano /home/beingmomen-ai/htdocs/ai.beingmomen.com/.env
```

Paste:

```env
CLAUDE_AUTH_METHOD=cli
API_KEY=your-secure-api-key-here
PORT=9514
CLAUDE_WRAPPER_HOST=0.0.0.0
MAX_TIMEOUT=600000
CORS_ORIGINS=["https://ai.yourdomain.com"]
DEFAULT_MODEL=claude-sonnet-4-5-20250929
RATE_LIMIT_ENABLED=true
RATE_LIMIT_CHAT_PER_MINUTE=10
```

Save: **Ctrl+O** → **Enter** → **Ctrl+X**

> **Note:** If using API key auth instead of CLI, replace `CLAUDE_AUTH_METHOD=cli` with:
> ```env
> ANTHROPIC_API_KEY=sk-ant-your-key-here
> ```

---

## Step 7: Claude Auth Login

```bash
claude auth login
```

- A URL will appear → open it in your browser
- Login with your Claude account
- Copy the token → paste it in the terminal
- Credentials are saved to `~/.claude/`

---

## Step 8: Build Docker Image

```bash
cd /home/beingmomen-ai/htdocs/ai.beingmomen.com
docker compose -f docker-compose.prod.yml build
```

> First build takes ~2-3 minutes. Subsequent builds are faster due to caching.

---

## Step 9: Start the Container

```bash
docker compose -f docker-compose.prod.yml up -d
```

Verify:

```bash
# Check container is running
docker ps

# Check health
curl http://127.0.0.1:9514/health
# Expected: {"status":"healthy","service":"claude-code-openai-wrapper"}
```

---

## Step 10: Enable SSL

1. Open CloudPanel: `https://YOUR_VPS_IP:8443`
2. Go to **Sites** → **ai.yourdomain.com** → **SSL/TLS**
3. Select **Let's Encrypt** → **Create Certificate**

Verify:

```bash
curl https://ai.yourdomain.com/health
# Expected: {"status":"healthy","service":"claude-code-openai-wrapper"}
```

---

## Step 11: Setup GitHub Actions (Auto-Deploy)

### 11.1: Generate SSH Deploy Key

On your **local machine** (not the VPS):

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/deploy_key
# Press Enter twice (no passphrase)
```

### 11.2: Copy Public Key to VPS

```bash
ssh-copy-id -i ~/.ssh/deploy_key.pub beingmomen-ai@YOUR_VPS_IP
```

### 11.3: Add GitHub Secrets

Go to: `https://github.com/YOUR_ORG/YOUR_REPO/settings/secrets/actions`

Click **"New repository secret"** for each:

| Name | Value |
|------|-------|
| `VPS_HOST` | Your VPS IP address |
| `VPS_USERNAME` | `beingmomen-ai` |
| `VPS_SSH_PORT` | `22` |
| `VPS_SSH_KEY` | Content of `~/.ssh/deploy_key` (private key) |

To get the private key content:

```bash
cat ~/.ssh/deploy_key
```

Copy **everything** including `-----BEGIN` and `-----END` lines.

### 11.4: Done!

Now every push to `main` branch will automatically deploy to the VPS.

---

## Management Commands

```bash
# View logs
docker logs -f claude-code-api

# Restart container
docker restart claude-code-api

# Stop container
docker compose -f docker-compose.prod.yml down

# Start container
docker compose -f docker-compose.prod.yml up -d

# Rebuild and restart (after manual code changes)
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

# Check container status
docker ps

# Clean up old images
docker image prune -f
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/v1/models` | GET | List available models |
| `/v1/chat/completions` | POST | Chat completions (OpenAI format) |
| `/v1/messages` | POST | Messages (Anthropic format) |
| `/v1/auth/status` | GET | Authentication status |
| `/v1/sessions` | GET | List active sessions |
| `/` | GET | Interactive landing page |

---

## Test the API

```bash
# Health check
curl https://ai.yourdomain.com/health

# List models
curl https://ai.yourdomain.com/v1/models \
  -H "Authorization: Bearer your-api-key"

# Chat completion
curl -X POST https://ai.yourdomain.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# Streaming
curl -X POST https://ai.yourdomain.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

---

## Troubleshooting

### Container won't start

```bash
docker logs claude-code-api
```

### Port already in use

```bash
# Check what's using port 9514
sudo netstat -tlnp | grep 9514

# Kill the process or change PORT in .env
```

### docker compose: command not found

```bash
sudo apt install docker-compose-v2 -y
```

### "claude: command not found" inside Docker

This is expected. Claude CLI runs on the host, not inside Docker. The container uses `claude-agent-sdk` (Python SDK) which reads credentials from the mounted `~/.claude/` volume.

### 502 Bad Gateway

```bash
# Check container is running
docker ps

# If not running, check logs and restart
docker logs claude-code-api
docker compose -f docker-compose.prod.yml up -d
```

### SSL certificate failed

Make sure your domain DNS A record points to the VPS IP:

```bash
dig ai.yourdomain.com +short
# Should return your VPS IP
```

### Auth token expired

```bash
# Re-login on the host
claude auth login

# Restart container to pick up new credentials
docker restart claude-code-api
```
