# سجل عملية النشر (Deployment Log)

توثيق تفصيلي لعملية نشر Claude Code API على Hostinger VPS مع CloudPanel، يشمل جميع الخطوات والمشاكل التي واجهتنا وحلولها.

---

## بيانات البيئة

| البند | القيمة |
|-------|--------|
| **VPS Provider** | Hostinger |
| **لوحة التحكم** | CloudPanel |
| **نظام التشغيل** | Ubuntu 24.04 |
| **المستخدم** | `beingmomen-ai` (Site User أنشأه CloudPanel) |
| **الدومين** | `ai.beingmomen.com` |
| **المنفذ** | `9514` |
| **مسار المشروع** | `/home/beingmomen-ai/htdocs/ai.beingmomen.com` |
| **الـ Repo** | `https://github.com/Abdelrahman-Mahmoud-Dev/claude-code-api` (public) |
| **المصادقة** | Claude CLI Auth (`claude auth login`) |
| **الـ Container** | `claude-code-api` |
| **الـ Docker Image** | `aibeingmomencom-claude-wrapper` |

---

## الخطوات بالترتيب الزمني

### 1. إنشاء Reverse Proxy في CloudPanel

**الخطوات:**
1. فتح CloudPanel على `https://VPS_IP:8443`
2. Sites → Add Site → **Create a Reverse Proxy**
3. الإعدادات:
   - Domain Name: `ai.beingmomen.com`
   - Reverse Proxy Url: `http://127.0.0.1:9514`
   - Site User: `beingmomen-ai` (أُنشئ تلقائياً)

**النتيجة:**
- تم إنشاء المستخدم `beingmomen-ai`
- تم إنشاء المسار `/home/beingmomen-ai/htdocs/ai.beingmomen.com`
- CloudPanel يدير Nginx ويوجه الطلبات من الدومين إلى `127.0.0.1:9514`

> **ملاحظة:** في البداية كان المنفذ `8000` في الإعدادات، تم تغييره إلى `9514` قبل الضغط على Create.

---

### 2. الاتصال بالـ VPS

```bash
ssh beingmomen-ai@VPS_IP
```

> **ملاحظة:** الاتصال تم كـ `beingmomen-ai` مباشرة (Site User)، وليس `root`. هذا يعني أن بعض الأوامر تحتاج `sudo`.

---

### 3. تثبيت Docker

**المشكلة:** Docker غير مثبت.

```bash
beingmomen-ai@srv635353:~$ docker --version
Command 'docker' not found
```

**الحل:**

```bash
sudo apt update && sudo apt install docker.io -y
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

ثم **خروج ودخول مرة أخرى** لتفعيل صلاحيات docker group:

```bash
exit
ssh beingmomen-ai@VPS_IP
```

**التحقق:**

```bash
docker --version
# Docker version 28.2.2
```

---

### 4. تثبيت Docker Compose V2

**المشكلة:** `docker compose` غير موجود.

```bash
beingmomen-ai@srv635353:~$ docker compose -f docker-compose.prod.yml build
unknown shorthand flag: 'f' in -f
```

و `docker-compose` (V1) أيضاً غير موجود:

```bash
beingmomen-ai@srv635353:~$ docker-compose --version
Command 'docker-compose' not found
```

**الحل:**

```bash
sudo apt update && sudo apt install docker-compose-v2 -y
```

**التحقق:**

```bash
docker compose version
# Docker Compose version 2.37.1
```

---

### 5. Clone المشروع

```bash
cd /home/beingmomen-ai/htdocs
git clone https://github.com/Abdelrahman-Mahmoud-Dev/claude-code-api.git ai.beingmomen.com
cd ai.beingmomen.com
```

> **ملاحظة:** الـ repo عام (public)، لذلك لا يحتاج token للـ clone.

---

### 6. إنشاء ملف .env

```bash
nano /home/beingmomen-ai/htdocs/ai.beingmomen.com/.env
```

**المحتوى:**

```env
CLAUDE_AUTH_METHOD=cli
API_KEY=your-secure-api-key-here
PORT=9514
CLAUDE_WRAPPER_HOST=0.0.0.0
MAX_TIMEOUT=600000
CORS_ORIGINS=["https://ai.beingmomen.com"]
DEFAULT_MODEL=claude-sonnet-4-5-20250929
RATE_LIMIT_ENABLED=true
RATE_LIMIT_CHAT_PER_MINUTE=10
```

> **ملاحظة:** لم نستخدم `ANTHROPIC_API_KEY` لأننا نستخدم CLI auth بدلاً من API key مباشر.

---

### 7. تثبيت Node.js و Claude CLI

**المشكلة:** Claude CLI غير موجود داخل Docker container.

حاولنا أولاً تشغيل `claude auth login` داخل Docker:

```bash
docker run -it --rm -v ~/.claude:/root/.claude aibeingmomencom-claude-wrapper claude auth login
# Error: "claude": executable file not found in $PATH
```

ثم جربنا عبر Poetry:

```bash
docker run -it --rm -v ~/.claude:/root/.claude aibeingmomencom-claude-wrapper poetry run claude auth login
# Command not found: claude
```

**السبب:** `claude-agent-sdk` هو Python SDK فقط، الـ `claude` CLI الفعلي يحتاج Node.js.

**الحل:** تثبيت Node.js و Claude CLI على الخادم مباشرة (خارج Docker):

```bash
# تثبيت Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# تثبيت Claude CLI
sudo npm install -g @anthropic-ai/claude-code
```

ثم تسجيل الدخول:

```bash
claude auth login
```

> الـ credentials تُحفظ في `~/.claude/` على الخادم، والـ Docker container يقرأها عبر volume mount: `~/.claude:/root/.claude`

---

### 8. بناء Docker Image

**المشكلة الأولى:** ملف `docker-compose.prod.yml` غير موجود على الخادم.

```bash
docker compose -f docker-compose.prod.yml build
# open docker-compose.prod.yml: no such file or directory
```

**السبب:** الملفات الجديدة (docker-compose.prod.yml, .dockerignore, deploy.yml, Dockerfile المعدل) كانت على الجهاز المحلي فقط ولم تُرفع إلى GitHub.

**الحل:** عمل push من الجهاز المحلي ثم pull على الخادم:

```bash
# من الجهاز المحلي
git add . && git commit -m "add deployment files" && git push

# من الخادم
cd /home/beingmomen-ai/htdocs/ai.beingmomen.com
git pull
```

**البناء الناجح:**

```bash
docker compose -f docker-compose.prod.yml build
# [+] Building 34.4s (12/12) FINISHED
# ✔ claude-wrapper Built
```

> **ملاحظة:** البناء الأول أخذ ~34 ثانية. الصورة اسمها `aibeingmomencom-claude-wrapper` (Docker Compose يسمي الصور بناءً على اسم المجلد).

---

### 9. تشغيل الـ Container

```bash
docker compose -f docker-compose.prod.yml up -d
```

**الناتج:**

```
✔ Network aibeingmomencom_default  Created
✔ Container claude-code-api        Started
```

**التحقق:**

```bash
docker ps
# CONTAINER ID   IMAGE                            STATUS                  PORTS
# 3d160416e1dd   aibeingmomencom-claude-wrapper   Up (health: starting)   127.0.0.1:9514->9514/tcp

curl http://127.0.0.1:9514/health
# {"status":"healthy","service":"claude-code-openai-wrapper"}
```

> **تحذير ظهر:** `the attribute 'version' is obsolete` - هذا تحذير غير مؤثر بسبب `version: '3.8'` في docker-compose.prod.yml. يمكن حذف السطر.

---

### 10. تفعيل SSL

من CloudPanel:
1. Sites → ai.beingmomen.com → SSL/TLS
2. Let's Encrypt → Create Certificate

**التحقق:**

```bash
curl https://ai.beingmomen.com/health
# {"status":"healthy","service":"claude-code-openai-wrapper"}
```

---

### 11. إعداد GitHub Actions

#### 11.1 إنشاء SSH Key

من الجهاز المحلي:

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/deploy_ai_beingmomen
# بدون passphrase
```

نسخ المفتاح العام إلى الخادم:

```bash
ssh-copy-id -i ~/.ssh/deploy_ai_beingmomen.pub beingmomen-ai@VPS_IP
```

#### 11.2 إضافة GitHub Secrets

في الـ repo → Settings → Secrets and variables → Actions:

| Secret | القيمة |
|--------|--------|
| `VPS_HOST` | عنوان IP الخادم |
| `VPS_USERNAME` | `beingmomen-ai` |
| `VPS_SSH_PORT` | `22` |
| `VPS_SSH_KEY` | محتوى `~/.ssh/deploy_ai_beingmomen` (المفتاح الخاص) |

#### 11.3 ملف deploy.yml

الملف `.github/workflows/deploy.yml` يعمل:
1. عند push للـ `main` branch
2. يتصل بالخادم عبر SSH
3. يسحب آخر كود
4. يبني Docker image جديد
5. يوقف الـ container القديم ويشغل الجديد
6. يفحص الـ health endpoint
7. ينظف الصور القديمة

---

## الملفات التي تم إنشاؤها/تعديلها

### ملفات معدلة

| الملف | التعديل |
|-------|---------|
| `Dockerfile` | إضافة `ENV PORT=8000`، إزالة `--reload`، إضافة `--workers 2`، استخدام `--without dev` |

### ملفات جديدة

| الملف | الوصف |
|-------|-------|
| `docker-compose.prod.yml` | إعدادات Docker للإنتاج (port 9514, health check, restart policy, logging) |
| `.github/workflows/deploy.yml` | GitHub Actions workflow للنشر التلقائي |
| `.dockerignore` | استبعاد .git, tests, docs, .env من Docker build |
| `DEPLOYMENT_GUIDE.md` | دليل التثبيت النظيف خطوة بخطوة |
| `API_USAGE_GUIDE.md` | دليل استخدام الـ API بالعربية |

---

## ملخص المشاكل وحلولها

| # | المشكلة | السبب | الحل |
|---|---------|-------|------|
| 1 | `docker: command not found` | Docker غير مثبت | `sudo apt install docker.io -y` |
| 2 | `unknown shorthand flag: 'f'` | Docker Compose V2 غير مثبت | `sudo apt install docker-compose-v2 -y` |
| 3 | `docker-compose: command not found` | Docker Compose V1 أيضاً غير مثبت | نفس الحل أعلاه |
| 4 | `no such file: docker-compose.prod.yml` | الملفات الجديدة لم تُرفع للـ repo | عمل push من المحلي ثم pull على الخادم |
| 5 | `claude: executable not found in $PATH` (داخل Docker) | Claude CLI يحتاج Node.js وهو غير موجود في الصورة | تثبيت Node.js و Claude CLI على الخادم مباشرة |
| 6 | `Command not found: claude` (عبر Poetry) | `claude-agent-sdk` هو Python SDK فقط، ليس CLI | نفس الحل أعلاه |
| 7 | `version is obsolete` تحذير | `version: '3.8'` في docker-compose قديم | تحذير غير مؤثر، يمكن حذف السطر |

---

## البنية النهائية

```
CloudPanel (Nginx)
    ↓
    ai.beingmomen.com (HTTPS/SSL)
    ↓
    http://127.0.0.1:9514
    ↓
Docker Container (claude-code-api)
    ↓
    FastAPI + Uvicorn (2 workers)
    ↓
    Claude Agent SDK → Claude API
```

```
GitHub (push to main)
    ↓
GitHub Actions (deploy.yml)
    ↓
SSH → VPS (beingmomen-ai)
    ↓
git pull → docker build → docker up
    ↓
Health Check → Done!
```

---

## أوامر الإدارة اليومية

```bash
# === حالة الخادم ===
docker ps                                          # حالة الحاوية
curl http://127.0.0.1:9514/health                  # فحص الصحة
curl https://ai.beingmomen.com/health              # فحص عبر الدومين

# === السجلات ===
docker logs claude-code-api                        # آخر السجلات
docker logs -f claude-code-api                     # متابعة مباشرة
docker logs --tail=50 claude-code-api              # آخر 50 سطر

# === إعادة التشغيل ===
docker restart claude-code-api                     # إعادة تشغيل سريعة

# === إعادة البناء الكامل ===
cd /home/beingmomen-ai/htdocs/ai.beingmomen.com
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

# === أمر واحد مختصر لإعادة البناء والتشغيل ===
docker compose -f docker-compose.prod.yml up -d --build

# === تحديث الكود يدوياً ===
cd /home/beingmomen-ai/htdocs/ai.beingmomen.com
git pull
docker compose -f docker-compose.prod.yml up -d --build

# === تنظيف ===
docker image prune -f                              # حذف الصور القديمة
docker system prune -f                             # تنظيف شامل

# === تجديد مصادقة Claude ===
claude auth login                                  # إعادة تسجيل الدخول
docker restart claude-code-api                     # إعادة تشغيل لتحميل الـ credentials الجديدة
```

---

## التاريخ

| التاريخ | الحدث |
|---------|-------|
| 2026-02-09 | النشر الأول - إعداد كامل من الصفر |
