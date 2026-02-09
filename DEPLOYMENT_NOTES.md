# Deployment Notes - Claude Code API

ملخص سريع لأهم نقاط الـ deployment، خصوصاً الـ Authentication.

---

## Authentication - نوعين مختلفين

| النوع | الغرض | متى تحتاجه |
|-------|-------|-------------|
| **`API_KEY`** (في `.env`) | حماية الـ API endpoint بتاعك من أي حد يستخدمه | **اختياري** - لو مش عايز حماية، متحطوش خالص |
| **Claude CLI Auth** (`claude auth login`) | تسجيل دخول مع Claude/Anthropic | **مطلوب** - عشان السيرفر يتكلم مع Claude |

### الفرق بالتفصيل

- **`API_KEY`**: ده زي password لسيرفرك إنت. لو حاطه، كل request لازم يبعت `Authorization: Bearer <API_KEY>`. لو مش حاطه، أي حد يقدر يبعت requests.
- **Claude CLI Auth**: ده اللي بيخلي السيرفر يتكلم مع Claude API. بتعمل `claude auth login` مرة واحدة والـ credentials بتتحفظ في `~/.claude/`.

---

## خطوات الـ Deploy على VPS مع CLI Auth

### 1. تثبيت Node.js و Claude CLI (على الـ Host - مش جوا Docker)

```bash
# تثبيت Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# تثبيت Claude CLI
sudo npm install -g @anthropic-ai/claude-code

# تسجيل الدخول
claude auth login
# الـ credentials بتتحفظ في ~/.claude/
```

### 2. إعداد Docker Compose

في `docker-compose.prod.yml`:

```yaml
volumes:
  - ~/.claude:/root/.claude    # ده بيوصل credentials الـ CLI للـ container
```

> الـ Docker Container مش محتاج Node.js - الـ Python SDK (`claude-agent-sdk`) بيقرأ الـ credentials من `/root/.claude/` اللي متعملها mount.

### 3. إعداد `.env`

```env
CLAUDE_AUTH_METHOD=cli          # استخدم CLI auth
# API_KEY=                      # اختياري - لو عايز حماية للـ endpoint حطه، لو لا سيبه معلق
```

### 4. بناء وتشغيل

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

---

## أوامر التحقق

### التأكد إن Claude CLI مسجل دخول

```bash
# على الـ Host
claude auth status

# أو شوف الـ credentials
ls -la ~/.claude/
```

### التأكد إن الـ Container شايف الـ Credentials

```bash
docker exec claude-code-api ls -la /root/.claude/
```

### اختبار الـ API

```bash
# Health check
curl http://127.0.0.1:9514/health

# عبر الدومين
curl https://your-domain.com/health

# قائمة الموديلز
curl https://your-domain.com/v1/models
```

### تجديد مصادقة Claude

```bash
claude auth login                   # إعادة تسجيل الدخول
docker restart claude-code-api      # إعادة تشغيل لتحميل الـ credentials الجديدة
```

---

## ملاحظات مهمة

1. **بدون `API_KEY`**: أي حد يعرف الـ URL يقدر يستخدم الـ API ويستهلك credits. الحماية الوحيدة هي إن الـ Docker port مربوط بـ `127.0.0.1` (الوصول بس من Nginx/Reverse Proxy).

2. **الـ `prompt_for_api_protection()`**: الـ function دي بتشتغل بس لما تشغل السيرفر بـ `python main.py` مباشرة. في Docker (اللي بيستخدم `uvicorn` مباشرة)، مش بتشتغل.

3. **لو الـ CLI credentials انتهت صلاحيتها**: اعمل `claude auth login` تاني على الـ Host ثم `docker restart claude-code-api`.

4. **مشكلة صلاحيات `~/.claude/` (Permission denied)**: لو `claude auth status` أو `claude auth login` بيدي `EACCES: permission denied`، السبب إن المجلد مملوك لـ `root` مش للمستخدم الحالي. الحل:
   ```bash
   sudo chown -R $(whoami):$(whoami) ~/.claude/
   claude auth login
   docker restart claude-code-api
   ```
   > ده بيحصل لما الـ CLI يتثبت أو يشتغل بـ `sudo` أول مرة.
