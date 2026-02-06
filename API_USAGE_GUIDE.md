# دليل استخدام Claude Code API - الدليل الشامل

كيفية استخدام Claude Code API في مشاريعك - دليل شامل يغطي جميع المميزات والنقاط والإعدادات.

**رابط الـ API:** `https://ai.beingmomen.com`

**الإصدار:** `2.2.0`

---

## جدول المحتويات

- [المصادقة](#المصادقة-authentication)
- [البداية السريعة](#البداية-السريعة)
- [الموديلات المتاحة](#الموديلات-المتاحة)
- [التوثيق التفاعلي (Docs & ReDoc)](#التوثيق-التفاعلي-docs--redoc)
- [المميزات](#المميزات)
  - [رسائل النظام](#1-رسائل-النظام-system-messages)
  - [محادثة متعددة الأدوار](#2-محادثة-متعددة-الأدوار-multi-turn)
  - [البث المباشر](#3-البث-المباشر-streaming)
  - [استمرارية الجلسة](#4-استمرارية-الجلسة-session-continuity)
  - [تفعيل الأدوات](#5-تفعيل-الأدوات-tools)
  - [Headers مخصصة لـ Claude](#6-headers-مخصصة-لـ-claude)
  - [دعم MCP](#7-دعم-mcp-model-context-protocol)
- [مرجع نقاط الوصول الكامل](#مرجع-نقاط-الوصول-الكامل-api-endpoints)
- [أمثلة كاملة](#أمثلة-كاملة)
- [متغيرات البيئة](#متغيرات-البيئة-environment-variables)
- [حدود الاستخدام](#حدود-الاستخدام-rate-limits)
- [أكواد الأخطاء](#أكواد-الأخطاء-error-codes)
- [التعامل مع الأخطاء](#التعامل-مع-الأخطاء)
- [النشر والتشغيل](#النشر-والتشغيل-deployment)

---

## المصادقة (Authentication)

جميع الطلبات تحتاج header المصادقة:

```
Authorization: Bearer your-api-key
```

### طرق المصادقة الخلفية (Backend Authentication)

الخادم يدعم عدة طرق للمصادقة مع Claude:

| الطريقة | المتغير | الوصف |
|---------|---------|-------|
| `cli` (افتراضي) | `CLAUDE_AUTH_METHOD=cli` | مصادقة Claude Code CLI (`claude auth login`) |
| `api_key` | `ANTHROPIC_API_KEY=sk-ant-*` | مفتاح Anthropic API مباشر |
| `bedrock` | `CLAUDE_CODE_USE_BEDROCK=1` | AWS Bedrock مع بيانات AWS |
| `vertex` | `CLAUDE_CODE_USE_VERTEX=1` | Google Vertex AI مع بيانات GCP |

### فحص حالة المصادقة

```bash
curl https://ai.beingmomen.com/v1/auth/status \
  -H "Authorization: Bearer your-api-key"
```

**الرد:**
```json
{
  "claude_code_auth": {
    "method": "claude_cli",
    "status": {
      "valid": true,
      "details": "Claude CLI authentication active"
    }
  },
  "server_info": {
    "api_key_required": true,
    "api_key_source": "environment",
    "version": "1.0.0"
  }
}
```

---

## البداية السريعة

### Python (مكتبة OpenAI)

```bash
pip install openai
```

```python
from openai import OpenAI

# إنشاء العميل
client = OpenAI(
    base_url="https://ai.beingmomen.com/v1",
    api_key="your-api-key"
)

# إرسال رسالة
response = client.chat.completions.create(
    model="claude-sonnet-4-5-20250929",
    messages=[
        {"role": "user", "content": "مرحبا!"}
    ]
)

# طباعة الرد
print(response.choices[0].message.content)
```

### JavaScript / Node.js

```bash
npm install openai
```

```javascript
import OpenAI from "openai";

// إنشاء العميل
const client = new OpenAI({
  baseURL: "https://ai.beingmomen.com/v1",
  apiKey: "your-api-key",
});

// إرسال رسالة
const response = await client.chat.completions.create({
  model: "claude-sonnet-4-5-20250929",
  messages: [{ role: "user", content: "مرحبا!" }],
});

// طباعة الرد
console.log(response.choices[0].message.content);
```

### cURL

```bash
curl -X POST https://ai.beingmomen.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "messages": [{"role": "user", "content": "مرحبا!"}]
  }'
```

### Python (مكتبة Anthropic الأصلية)

```bash
pip install anthropic
```

```python
import anthropic

client = anthropic.Anthropic(
    base_url="https://ai.beingmomen.com",
    api_key="your-api-key"
)

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    messages=[
        {"role": "user", "content": "مرحبا!"}
    ]
)

print(response.content[0].text)
```

---

## الموديلات المتاحة

### عائلة Claude 4.5 (الأحدث - موصى بها)

| الموديل | الوصف | الأفضل لـ |
|---------|-------|-----------|
| `claude-opus-4-5-20250929` | الأقوى والأذكى | التحليل المعقد والتفكير العميق |
| `claude-sonnet-4-5-20250929` | **موصى به** | البرمجة والاستخدام العام |
| `claude-haiku-4-5-20251001` | سريع ورخيص | الردود السريعة والمهام البسيطة |

### عائلة Claude 4.1 و 4.0

| الموديل | الوصف |
|---------|-------|
| `claude-opus-4-1-20250805` | Claude 4.1 Opus |
| `claude-opus-4-20250514` | Claude 4 Opus |
| `claude-sonnet-4-20250514` | Claude 4 Sonnet |

> **ملاحظة:** موديلات Claude 3.x غير مدعومة من Claude Agent SDK.

### عرض جميع الموديلات

```bash
curl https://ai.beingmomen.com/v1/models \
  -H "Authorization: Bearer your-api-key"
```

**الرد:**
```json
{
  "object": "list",
  "data": [
    {"id": "claude-opus-4-5-20250929", "object": "model", "owned_by": "anthropic"},
    {"id": "claude-sonnet-4-5-20250929", "object": "model", "owned_by": "anthropic"},
    {"id": "claude-haiku-4-5-20251001", "object": "model", "owned_by": "anthropic"},
    {"id": "claude-opus-4-1-20250805", "object": "model", "owned_by": "anthropic"},
    {"id": "claude-opus-4-20250514", "object": "model", "owned_by": "anthropic"},
    {"id": "claude-sonnet-4-20250514", "object": "model", "owned_by": "anthropic"}
  ]
}
```

---

## التوثيق التفاعلي (Docs & ReDoc)

الـ API يوفر واجهتين تفاعليتين لاستكشاف واختبار جميع نقاط الوصول مباشرة من المتصفح:

### Swagger UI (Docs)

```
https://ai.beingmomen.com/docs
```

واجهة **Swagger UI** التفاعلية توفر:
- قائمة بجميع نقاط الوصول (Endpoints) مع وصف تفصيلي لكل منها
- إمكانية **تجربة الطلبات مباشرة** من المتصفح (Try it out)
- عرض **شكل الطلب والرد** (Request/Response Schema) لكل نقطة
- عرض **المعاملات المطلوبة والاختيارية** لكل نقطة وصول
- دعم المصادقة - أدخل الـ API Key من زر **Authorize** في الأعلى
- تصنيف النقاط حسب المجموعات (Chat, Sessions, Tools, MCP, Health)

#### كيفية الاستخدام:

1. افتح `https://ai.beingmomen.com/docs` في المتصفح
2. اضغط على زر **Authorize** في أعلى الصفحة
3. أدخل الـ API Key في خانة Bearer Token
4. اختر أي نقطة وصول واضغط **Try it out**
5. عدّل المعاملات حسب الحاجة واضغط **Execute**
6. شاهد الطلب والرد مباشرة

### ReDoc

```
https://ai.beingmomen.com/redoc
```

واجهة **ReDoc** توفر:
- توثيق **أنيق وسهل القراءة** بتصميم ثلاثي الأعمدة
- شرح تفصيلي لكل نقطة وصول مع أمثلة الطلب والرد
- عرض **هيكل البيانات** (Data Models) بشكل شجري
- **جدول محتويات** جانبي للتنقل السريع
- مناسبة للطباعة والمشاركة كمرجع

### الصفحة الرئيسية التفاعلية

```
https://ai.beingmomen.com/
```

الصفحة الرئيسية توفر:
- عرض **حالة الخادم والمصادقة** مباشرة
- **Quick Start** مع أمر cURL جاهز للنسخ
- استعراض نقاط الوصول مع إمكانية **فتح الردود الحية** (Live Response)
- وضع داكن/فاتح قابل للتبديل
- روابط مباشرة لـ Docs و ReDoc

---

## المميزات

### 1. رسائل النظام (System Messages)

تحدد شخصية وسلوك Claude:

```python
response = client.chat.completions.create(
    model="claude-sonnet-4-5-20250929",
    messages=[
        # رسالة النظام - تحدد الدور
        {"role": "system", "content": "أنت مدرس بايثون متخصص. أجب بالعربية."},
        # رسالة المستخدم
        {"role": "user", "content": "اشرح لي الـ decorators"}
    ]
)
```

### 2. محادثة متعددة الأدوار (Multi-turn)

أرسل تاريخ المحادثة كاملاً:

```python
response = client.chat.completions.create(
    model="claude-sonnet-4-5-20250929",
    messages=[
        {"role": "user", "content": "ما هي Python؟"},
        {"role": "assistant", "content": "Python هي لغة برمجة..."},
        # الرسالة الجديدة - Claude يفهم السياق السابق
        {"role": "user", "content": "أعطني مثال hello world"}
    ]
)
```

### 3. البث المباشر (Streaming)

الرد يظهر كلمة كلمة بدلاً من الانتظار:

#### Python

```python
stream = client.chat.completions.create(
    model="claude-sonnet-4-5-20250929",
    messages=[{"role": "user", "content": "اكتب قصيدة"}],
    stream=True  # تفعيل البث
)

# طباعة كل جزء فور وصوله
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

#### مع معلومات الاستخدام (Usage) في البث

```python
stream = client.chat.completions.create(
    model="claude-sonnet-4-5-20250929",
    messages=[{"role": "user", "content": "اكتب قصيدة"}],
    stream=True,
    stream_options={"include_usage": True}  # إضافة معلومات الاستخدام
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    # معلومات الاستخدام تأتي في آخر chunk
    if chunk.usage:
        print(f"\nTokens: {chunk.usage.total_tokens}")
```

#### JavaScript

```javascript
const stream = await client.chat.completions.create({
  model: "claude-sonnet-4-5-20250929",
  messages: [{ role: "user", content: "اكتب قصيدة" }],
  stream: true,
});

for await (const chunk of stream) {
  if (chunk.choices[0].delta.content) {
    process.stdout.write(chunk.choices[0].delta.content);
  }
}
```

#### cURL

```bash
curl -X POST https://ai.beingmomen.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "messages": [{"role": "user", "content": "اكتب قصيدة"}],
    "stream": true
  }'
```

### 4. استمرارية الجلسة (Session Continuity)

Claude يتذكر المحادثة بين الطلبات المختلفة:

```python
# الرسالة الأولى - عرّف نفسك
response1 = client.chat.completions.create(
    model="claude-sonnet-4-5-20250929",
    messages=[
        {"role": "user", "content": "اسمي أحمد وأنا أبني تطبيق FastAPI"}
    ],
    extra_body={"session_id": "project-123"}  # معرف الجلسة
)

# الرسالة الثانية - Claude يتذكر السياق!
response2 = client.chat.completions.create(
    model="claude-sonnet-4-5-20250929",
    messages=[
        {"role": "user", "content": "ما اسمي وماذا أبني؟"}
    ],
    extra_body={"session_id": "project-123"}  # نفس معرف الجلسة
)
# Claude سيرد: "اسمك أحمد وأنت تبني تطبيق FastAPI"
```

#### إدارة الجلسات

```bash
# عرض الجلسات النشطة
curl https://ai.beingmomen.com/v1/sessions \
  -H "Authorization: Bearer your-api-key"

# معلومات جلسة محددة
curl https://ai.beingmomen.com/v1/sessions/project-123 \
  -H "Authorization: Bearer your-api-key"

# إحصائيات الجلسات
curl https://ai.beingmomen.com/v1/sessions/stats \
  -H "Authorization: Bearer your-api-key"

# حذف جلسة
curl -X DELETE https://ai.beingmomen.com/v1/sessions/project-123 \
  -H "Authorization: Bearer your-api-key"
```

**رد معلومات الجلسة:**
```json
{
  "session_id": "project-123",
  "created_at": "2025-01-15T10:30:00Z",
  "last_accessed": "2025-01-15T11:15:00Z",
  "message_count": 8,
  "expires_at": "2025-01-15T12:15:00Z"
}
```

**رد إحصائيات الجلسات:**
```json
{
  "session_stats": {
    "active_sessions": 5,
    "expired_sessions": 0,
    "total_messages": 45
  },
  "cleanup_interval_minutes": 5,
  "default_ttl_hours": 1
}
```

> الجلسات تنتهي تلقائياً بعد **ساعة** من عدم النشاط. يتم تمديد المدة مع كل طلب جديد.

### 5. تفعيل الأدوات (Tools)

الأدوات معطلة افتراضياً للسرعة (أسرع 5-10 مرات). فعّلها عند الحاجة:

```python
response = client.chat.completions.create(
    model="claude-sonnet-4-5-20250929",
    messages=[
        {"role": "user", "content": "اقرأ ملف main.py واشرحه لي"}
    ],
    extra_body={"enable_tools": True}  # تفعيل الأدوات
)
```

#### الأدوات المتاحة (14 أداة)

| الأداة | الوصف | الفئة |
|--------|-------|-------|
| `Read` | قراءة الملفات | ملفات |
| `Write` | كتابة/إنشاء الملفات | ملفات |
| `Edit` | تعديل أجزاء من الملفات | ملفات |
| `Glob` | بحث عن ملفات بالنمط (مثل `*.py`) | ملفات |
| `Grep` | بحث في محتوى الملفات بالـ regex | ملفات |
| `NotebookEdit` | تعديل خلايا Jupyter Notebook | ملفات |
| `Bash` | تنفيذ أوامر shell | نظام |
| `BashOutput` | جلب مخرجات الأوامر الخلفية | نظام |
| `KillShell` | إيقاف أوامر shell الخلفية | نظام |
| `WebFetch` | جلب محتوى من الويب | إنترنت |
| `WebSearch` | البحث في الويب | إنترنت |
| `TodoWrite` | إدارة قائمة المهام | إنتاجية |
| `Skill` | تنفيذ مهارات متخصصة | متقدم |
| `Task` | إطلاق وكلاء فرعيين | متقدم |

#### الأدوات المفعلة افتراضياً (عند `enable_tools: true`)

`Read`, `Glob`, `Grep`, `Bash`, `Write`, `Edit`

#### إدارة إعدادات الأدوات

```bash
# عرض جميع الأدوات مع التفاصيل
curl https://ai.beingmomen.com/v1/tools \
  -H "Authorization: Bearer your-api-key"

# عرض إعدادات الأدوات الحالية
curl https://ai.beingmomen.com/v1/tools/config \
  -H "Authorization: Bearer your-api-key"

# تحديث إعدادات الأدوات (عام)
curl -X POST https://ai.beingmomen.com/v1/tools/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "allowed_tools": ["Read", "Glob", "Grep", "Bash"],
    "disallowed_tools": ["Task", "WebFetch"]
  }'

# تحديث إعدادات الأدوات (لجلسة محددة)
curl -X POST https://ai.beingmomen.com/v1/tools/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "session_id": "project-123",
    "allowed_tools": ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
  }'

# إحصائيات الأدوات
curl https://ai.beingmomen.com/v1/tools/stats \
  -H "Authorization: Bearer your-api-key"
```

### 6. Headers مخصصة لـ Claude

تحكم بخيارات Claude Agent SDK عبر HTTP Headers:

```bash
curl -X POST https://ai.beingmomen.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -H "X-Claude-Max-Turns: 5" \
  -H "X-Claude-Allowed-Tools: Read,Glob,Grep,Bash" \
  -H "X-Claude-Permission-Mode: bypassPermissions" \
  -H "X-Claude-Max-Thinking-Tokens: 10000" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "messages": [{"role": "user", "content": "حلل هذا الكود"}],
    "enable_tools": true
  }'
```

| الـ Header | الوصف | القيم |
|------------|-------|-------|
| `X-Claude-Max-Turns` | عدد الدورات القصوى | رقم (مثل `5`, `10`) |
| `X-Claude-Allowed-Tools` | الأدوات المسموحة | أسماء مفصولة بفواصل |
| `X-Claude-Disallowed-Tools` | الأدوات المحظورة | أسماء مفصولة بفواصل |
| `X-Claude-Permission-Mode` | وضع الصلاحيات | `default`, `acceptEdits`, `bypassPermissions`, `plan` |
| `X-Claude-Max-Thinking-Tokens` | حد التفكير | رقم (مثل `10000`) |

### 7. دعم MCP (Model Context Protocol)

ربط خوادم MCP خارجية لتوسيع قدرات Claude:

```bash
# عرض خوادم MCP المسجلة
curl https://ai.beingmomen.com/v1/mcp/servers \
  -H "Authorization: Bearer your-api-key"

# تسجيل خادم MCP جديد
curl -X POST https://ai.beingmomen.com/v1/mcp/servers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "name": "my-mcp-server",
    "command": "/path/to/mcp-server",
    "args": ["--port", "3001"],
    "env": {"API_KEY": "value"},
    "description": "خادم MCP مخصص",
    "enabled": true
  }'

# الاتصال بخادم MCP
curl -X POST https://ai.beingmomen.com/v1/mcp/connect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{"server_name": "my-mcp-server"}'

# قطع الاتصال
curl -X POST https://ai.beingmomen.com/v1/mcp/disconnect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{"server_name": "my-mcp-server"}'

# إحصائيات MCP
curl https://ai.beingmomen.com/v1/mcp/stats \
  -H "Authorization: Bearer your-api-key"
```

**رد الاتصال:**
```json
{
  "message": "Connected to MCP server 'my-mcp-server'",
  "tools": 5,
  "resources": 3,
  "prompts": 2
}
```

---

## مرجع نقاط الوصول الكامل (API Endpoints)

### المحادثة - صيغة OpenAI

```
POST /v1/chat/completions
```

**جميع المعاملات:**
```json
{
  "model": "claude-sonnet-4-5-20250929",
  "messages": [
    {"role": "system", "content": "رسالة النظام (اختياري)"},
    {"role": "user", "content": "رسالتك هنا"}
  ],
  "temperature": 1.0,
  "top_p": 1.0,
  "max_tokens": null,
  "max_completion_tokens": null,
  "stream": false,
  "session_id": "معرف-الجلسة-اختياري",
  "enable_tools": false,
  "user": "معرف-المستخدم-اختياري",
  "stream_options": {
    "include_usage": false
  }
}
```

| المعامل | النوع | الافتراضي | الوصف |
|---------|-------|-----------|-------|
| `model` | string | **مطلوب** | معرف الموديل |
| `messages` | array | **مطلوب** | مصفوفة الرسائل |
| `temperature` | float (0-2) | `1.0` | درجة العشوائية (عبر system prompt) |
| `top_p` | float (0-1) | `1.0` | تنوع الردود (عبر system prompt) |
| `max_tokens` | int | `null` | حد الـ tokens |
| `max_completion_tokens` | int | `null` | بديل لـ max_tokens |
| `stream` | bool | `false` | تفعيل البث المباشر |
| `session_id` | string | `null` | معرف الجلسة للاستمرارية |
| `enable_tools` | bool | `false` | تفعيل أدوات Claude |
| `user` | string | `null` | معرف المستخدم للتتبع |
| `stream_options` | object | `null` | خيارات البث |

> **ملاحظة:** المعاملات `presence_penalty`, `frequency_penalty`, `stop`, `logit_bias`, `n > 1` غير مدعومة ويتم تجاهلها مع تحذير.

**الرد (غير متدفق):**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1704067200,
  "model": "claude-sonnet-4-5-20250929",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "نص الرد"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

**الرد (متدفق - Streaming):**
```
data: {"id":"chatcmpl-abc","object":"chat.completion.chunk","model":"claude-sonnet-4-5-20250929","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}

data: {"id":"chatcmpl-abc","object":"chat.completion.chunk","model":"claude-sonnet-4-5-20250929","choices":[{"index":0,"delta":{"content":"مرحبا"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc","object":"chat.completion.chunk","model":"claude-sonnet-4-5-20250929","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

### المحادثة - صيغة Anthropic

```
POST /v1/messages
```

**الطلب:**
```json
{
  "model": "claude-sonnet-4-5-20250929",
  "messages": [
    {"role": "user", "content": "رسالتك هنا"}
  ],
  "max_tokens": 4096,
  "system": "رسالة النظام (اختياري)",
  "temperature": 1.0,
  "top_p": null,
  "top_k": null,
  "stop_sequences": null,
  "stream": false,
  "metadata": {}
}
```

**الرد:**
```json
{
  "id": "msg_abc123",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "نص الرد"
    }
  ],
  "model": "claude-sonnet-4-5-20250929",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 20
  }
}
```

> **ملاحظة:** نقطة `/v1/messages` تفعّل الأدوات تلقائياً لأنها مصممة لعملاء Anthropic SDK الذين يستخدمونها غالباً لسيناريوهات الوكلاء (Agentic Workflows).

### فحص التوافق

```
POST /v1/compatibility
```

يفحص مدى توافق طلبك مع معاملات OpenAI API:

```bash
curl -X POST https://ai.beingmomen.com/v1/compatibility \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "messages": [{"role": "user", "content": "test"}],
    "temperature": 0.7,
    "presence_penalty": 0.5
  }'
```

### تصحيح الأخطاء (Debug)

```
POST /v1/debug/request
```

يعرض كيف يتم تحليل طلبك - مفيد لتصحيح الأخطاء:

```bash
curl -X POST https://ai.beingmomen.com/v1/debug/request \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "messages": [{"role": "user", "content": "test"}]
  }'
```

### جدول نقاط الوصول الكامل

| النقطة | الطريقة | الوصف | حد الاستخدام |
|--------|---------|-------|--------------|
| `/` | GET | الصفحة الرئيسية التفاعلية | - |
| `/docs` | GET | **توثيق Swagger UI التفاعلي** | - |
| `/redoc` | GET | **توثيق ReDoc** | - |
| `/health` | GET | فحص صحة الخادم | 30/دقيقة |
| `/version` | GET | إصدار الـ API | 30/دقيقة |
| `/v1/models` | GET | عرض الموديلات المتاحة | - |
| `/v1/chat/completions` | POST | المحادثة (صيغة OpenAI) | 10/دقيقة |
| `/v1/messages` | POST | المحادثة (صيغة Anthropic) | 10/دقيقة |
| `/v1/compatibility` | POST | فحص توافق الطلب | - |
| `/v1/auth/status` | GET | حالة المصادقة | 10/دقيقة |
| `/v1/debug/request` | POST | تصحيح أخطاء الطلبات | 2/دقيقة |
| `/v1/sessions` | GET | عرض الجلسات النشطة | 15/دقيقة |
| `/v1/sessions/stats` | GET | إحصائيات الجلسات | 15/دقيقة |
| `/v1/sessions/{id}` | GET | تفاصيل جلسة محددة | 15/دقيقة |
| `/v1/sessions/{id}` | DELETE | حذف جلسة | 15/دقيقة |
| `/v1/tools` | GET | عرض جميع الأدوات | 30/دقيقة |
| `/v1/tools/config` | GET | عرض إعدادات الأدوات | 30/دقيقة |
| `/v1/tools/config` | POST | تحديث إعدادات الأدوات | 30/دقيقة |
| `/v1/tools/stats` | GET | إحصائيات الأدوات | 30/دقيقة |
| `/v1/mcp/servers` | GET | عرض خوادم MCP | 30/دقيقة |
| `/v1/mcp/servers` | POST | تسجيل خادم MCP | 30/دقيقة |
| `/v1/mcp/connect` | POST | الاتصال بخادم MCP | 30/دقيقة |
| `/v1/mcp/disconnect` | POST | قطع الاتصال بخادم MCP | 30/دقيقة |
| `/v1/mcp/stats` | GET | إحصائيات MCP | 30/دقيقة |

---

## أمثلة كاملة

### Python: شات بوت مع جلسة

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://ai.beingmomen.com/v1",
    api_key="your-api-key"
)

session_id = "chatbot-001"

while True:
    user_input = input("أنت: ")
    if user_input.lower() in ["exit", "quit", "خروج"]:
        break

    response = client.chat.completions.create(
        model="claude-sonnet-4-5-20250929",
        messages=[{"role": "user", "content": user_input}],
        extra_body={"session_id": session_id}
    )

    print(f"Claude: {response.choices[0].message.content}\n")
```

### Python: شات بوت مع بث مباشر

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://ai.beingmomen.com/v1",
    api_key="your-api-key"
)

while True:
    user_input = input("\nأنت: ")
    if user_input.lower() in ["exit", "quit", "خروج"]:
        break

    print("Claude: ", end="", flush=True)

    stream = client.chat.completions.create(
        model="claude-sonnet-4-5-20250929",
        messages=[{"role": "user", "content": user_input}],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

    print()
```

### Python: مساعد برمجي مع أدوات

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://ai.beingmomen.com/v1",
    api_key="your-api-key"
)

# Claude يمكنه قراءة الملفات وتنفيذ الأوامر
response = client.chat.completions.create(
    model="claude-sonnet-4-5-20250929",
    messages=[
        {"role": "system", "content": "أنت مساعد برمجي. حلل الكود واقترح تحسينات."},
        {"role": "user", "content": "اقرأ ملفات المشروع واعطني ملخص عن البنية"}
    ],
    extra_body={
        "enable_tools": True,
        "session_id": "code-review-001"
    }
)

print(response.choices[0].message.content)
```

### JavaScript: تكامل مع Express.js

```javascript
import express from "express";
import OpenAI from "openai";

const app = express();
app.use(express.json());

const client = new OpenAI({
  baseURL: "https://ai.beingmomen.com/v1",
  apiKey: "your-api-key",
});

// نقطة وصول المحادثة
app.post("/chat", async (req, res) => {
  const { message, sessionId } = req.body;

  const response = await client.chat.completions.create({
    model: "claude-sonnet-4-5-20250929",
    messages: [{ role: "user", content: message }],
    extra_body: { session_id: sessionId },
  });

  res.json({
    reply: response.choices[0].message.content,
  });
});

// نقطة وصول البث المباشر
app.post("/chat/stream", async (req, res) => {
  const { message } = req.body;

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  const stream = await client.chat.completions.create({
    model: "claude-sonnet-4-5-20250929",
    messages: [{ role: "user", content: message }],
    stream: true,
  });

  for await (const chunk of stream) {
    if (chunk.choices[0].delta.content) {
      res.write(`data: ${JSON.stringify({ content: chunk.choices[0].delta.content })}\n\n`);
    }
  }

  res.write("data: [DONE]\n\n");
  res.end();
});

app.listen(3000, () => console.log("الخادم يعمل على المنفذ 3000"));
```

### JavaScript: تكامل مع Next.js

```javascript
// app/api/chat/route.js
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://ai.beingmomen.com/v1",
  apiKey: process.env.CLAUDE_API_KEY,
});

export async function POST(request) {
  const { message, sessionId } = await request.json();

  const response = await client.chat.completions.create({
    model: "claude-sonnet-4-5-20250929",
    messages: [{ role: "user", content: message }],
    ...(sessionId && { extra_body: { session_id: sessionId } }),
  });

  return Response.json({
    reply: response.choices[0].message.content,
  });
}
```

### Python: تكامل مع FastAPI

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from openai import OpenAI, APIError, RateLimitError
from pydantic import BaseModel

app = FastAPI()

client = OpenAI(
    base_url="https://ai.beingmomen.com/v1",
    api_key="your-api-key"
)

class ChatRequest(BaseModel):
    message: str
    session_id: str = None
    stream: bool = False

@app.post("/chat")
async def chat(req: ChatRequest):
    extra = {}
    if req.session_id:
        extra["session_id"] = req.session_id

    try:
        if req.stream:
            # بث مباشر
            def generate():
                stream = client.chat.completions.create(
                    model="claude-sonnet-4-5-20250929",
                    messages=[{"role": "user", "content": req.message}],
                    stream=True,
                    extra_body=extra
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

            return StreamingResponse(generate(), media_type="text/plain")
        else:
            response = client.chat.completions.create(
                model="claude-sonnet-4-5-20250929",
                messages=[{"role": "user", "content": req.message}],
                extra_body=extra
            )
            return {"reply": response.choices[0].message.content}

    except RateLimitError:
        raise HTTPException(status_code=429, detail="تجاوزت حد الطلبات")
    except APIError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Python: تكامل مع Flask

```python
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    base_url="https://ai.beingmomen.com/v1",
    api_key="your-api-key"
)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message")

    response = client.chat.completions.create(
        model="claude-sonnet-4-5-20250929",
        messages=[{"role": "user", "content": message}]
    )

    return jsonify({
        "reply": response.choices[0].message.content
    })

if __name__ == "__main__":
    app.run(port=5000)
```

---

## متغيرات البيئة (Environment Variables)

### المصادقة

| المتغير | الوصف | مثال |
|---------|-------|------|
| `CLAUDE_AUTH_METHOD` | طريقة المصادقة | `cli`, `api_key`, `bedrock`, `vertex` |
| `ANTHROPIC_API_KEY` | مفتاح Anthropic API | `sk-ant-api03-...` |
| `CLAUDE_CODE_USE_BEDROCK` | تفعيل AWS Bedrock | `1` |
| `AWS_ACCESS_KEY_ID` | مفتاح AWS | - |
| `AWS_SECRET_ACCESS_KEY` | سر AWS | - |
| `AWS_REGION` | منطقة AWS | `us-east-1` |
| `CLAUDE_CODE_USE_VERTEX` | تفعيل Vertex AI | `1` |
| `ANTHROPIC_VERTEX_PROJECT_ID` | مشروع GCP | - |
| `CLOUD_ML_REGION` | منطقة GCP | `us-central1` |
| `GOOGLE_APPLICATION_CREDENTIALS` | ملف مصادقة GCP | `/path/to/key.json` |

### الخادم

| المتغير | الوصف | الافتراضي |
|---------|-------|-----------|
| `PORT` | منفذ الخادم | `8000` |
| `CLAUDE_WRAPPER_HOST` | عنوان الربط | `0.0.0.0` |
| `API_KEY` | مفتاح حماية الـ API | - (بدون حماية) |
| `CLAUDE_CWD` | مجلد العمل لـ Claude | مجلد مؤقت معزول |
| `MAX_TIMEOUT` | مهلة الطلب (مللي ثانية) | `600000` (10 دقائق) |
| `MAX_REQUEST_SIZE` | حجم الطلب الأقصى (بايت) | `10485760` (10MB) |
| `CORS_ORIGINS` | أصول CORS المسموحة | `["*"]` |
| `DEFAULT_MODEL` | الموديل الافتراضي | `claude-sonnet-4-5-20250929` |

### التصحيح

| المتغير | الوصف | الافتراضي |
|---------|-------|-----------|
| `DEBUG_MODE` | وضع التصحيح الكامل | `false` |
| `VERBOSE` | التسجيل المفصل | `false` |

### حدود الاستخدام

| المتغير | الوصف | الافتراضي |
|---------|-------|-----------|
| `RATE_LIMIT_ENABLED` | تفعيل حدود الاستخدام | `true` |
| `RATE_LIMIT_PER_MINUTE` | الحد العام | `30` |
| `RATE_LIMIT_CHAT_PER_MINUTE` | حد المحادثة | `10` |
| `RATE_LIMIT_DEBUG_PER_MINUTE` | حد التصحيح | `2` |
| `RATE_LIMIT_AUTH_PER_MINUTE` | حد المصادقة | `10` |
| `RATE_LIMIT_SESSION_PER_MINUTE` | حد الجلسات | `15` |
| `RATE_LIMIT_HEALTH_PER_MINUTE` | حد فحص الصحة | `30` |

---

## حدود الاستخدام (Rate Limits)

| النقطة | الحد | قابل للتعديل |
|--------|------|-------------|
| `/v1/chat/completions` | 10 طلبات/دقيقة | `RATE_LIMIT_CHAT_PER_MINUTE` |
| `/v1/messages` | 10 طلبات/دقيقة | `RATE_LIMIT_CHAT_PER_MINUTE` |
| `/v1/auth/status` | 10 طلبات/دقيقة | `RATE_LIMIT_AUTH_PER_MINUTE` |
| `/v1/sessions/*` | 15 طلب/دقيقة | `RATE_LIMIT_SESSION_PER_MINUTE` |
| `/v1/debug/request` | 2 طلب/دقيقة | `RATE_LIMIT_DEBUG_PER_MINUTE` |
| `/health`, `/version` | 30 طلب/دقيقة | `RATE_LIMIT_HEALTH_PER_MINUTE` |
| الباقي | 30 طلب/دقيقة | `RATE_LIMIT_PER_MINUTE` |

عند تجاوز الحد، ستحصل على خطأ HTTP 429:

```json
{
  "error": {
    "message": "Rate limit exceeded. Try again in 60 seconds.",
    "type": "rate_limit_exceeded",
    "code": "too_many_requests",
    "retry_after": 60
  }
}
```

---

## أكواد الأخطاء (Error Codes)

| الكود | المعنى | السبب المحتمل |
|-------|--------|---------------|
| `200` | نجاح | الطلب تم بنجاح |
| `400` | طلب خاطئ | معاملات غير صالحة أو أسماء أدوات خاطئة |
| `401` | غير مصرح | مفتاح API مفقود أو غير صالح |
| `404` | غير موجود | الجلسة أو المورد غير موجود |
| `413` | الحمولة كبيرة | حجم الطلب تجاوز `MAX_REQUEST_SIZE` |
| `422` | خطأ تحقق | صيغة الطلب غير صحيحة |
| `429` | تجاوز الحد | طلبات كثيرة في فترة قصيرة |
| `500` | خطأ خادم | خطأ في Claude SDK أو خطأ داخلي |
| `503` | الخدمة غير متاحة | فشل المصادقة مع Claude أو MCP غير متوفر |

### صيغة الخطأ

```json
{
  "error": {
    "message": "وصف الخطأ",
    "type": "نوع الخطأ",
    "code": "كود الخطأ"
  }
}
```

### أنواع الأخطاء

| النوع | الوصف |
|-------|-------|
| `validation_error` | فشل التحقق من المعاملات |
| `authentication_error` | بيانات المصادقة غير صالحة |
| `streaming_error` | خطأ أثناء البث المباشر |
| `api_error` | خطأ عام في الـ API |
| `rate_limit_exceeded` | تجاوز حد الاستخدام |
| `request_too_large` | حجم الطلب كبير جداً |

### خطأ التحقق التفصيلي (422)

عند إرسال طلب بصيغة خاطئة، تحصل على تفاصيل مفيدة:

```json
{
  "error": {
    "message": "Request validation failed - the request body doesn't match the expected format",
    "type": "validation_error",
    "code": "invalid_request_error",
    "details": [
      {
        "field": "body -> messages",
        "message": "field required",
        "type": "missing"
      }
    ],
    "help": {
      "common_issues": [
        "Missing required fields (model, messages)",
        "Invalid field types (e.g. messages should be an array)",
        "Invalid role values (must be 'system', 'user', or 'assistant')",
        "Invalid parameter ranges (e.g. temperature must be 0-2)"
      ],
      "debug_tip": "Set DEBUG_MODE=true for more detailed logging"
    }
  }
}
```

---

## التعامل مع الأخطاء

### Python

```python
from openai import OpenAI, APIError, RateLimitError, AuthenticationError, APIConnectionError
import time

client = OpenAI(
    base_url="https://ai.beingmomen.com/v1",
    api_key="your-api-key"
)

def chat_with_retry(message, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="claude-sonnet-4-5-20250929",
                messages=[{"role": "user", "content": message}]
            )
            return response.choices[0].message.content

        except RateLimitError:
            # تجاوزت حد الطلبات - انتظر وأعد المحاولة
            wait_time = 60 * (attempt + 1)
            print(f"تجاوزت حد الطلبات. الانتظار {wait_time} ثانية...")
            time.sleep(wait_time)

        except AuthenticationError:
            # مفتاح API غير صالح
            print("مفتاح الـ API غير صالح. تحقق من المفتاح.")
            break

        except APIConnectionError:
            # لا يمكن الاتصال بالخادم
            print("لا يمكن الاتصال بالخادم. تحقق من الرابط.")
            break

        except APIError as e:
            # خطأ عام في الـ API
            print(f"خطأ في الـ API ({e.status_code}): {e.message}")
            if e.status_code >= 500:
                time.sleep(5)  # انتظر قبل المحاولة مرة أخرى
            else:
                break

    return None

# الاستخدام
result = chat_with_retry("مرحبا، كيف حالك؟")
if result:
    print(result)
```

### JavaScript

```javascript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "https://ai.beingmomen.com/v1",
  apiKey: "your-api-key",
});

async function chatWithRetry(message, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await client.chat.completions.create({
        model: "claude-sonnet-4-5-20250929",
        messages: [{ role: "user", content: message }],
      });
      return response.choices[0].message.content;
    } catch (error) {
      if (error.status === 429) {
        // تجاوز حد الاستخدام
        const waitTime = 60 * (attempt + 1) * 1000;
        console.log(`تجاوزت حد الطلبات. الانتظار ${waitTime / 1000} ثانية...`);
        await new Promise((resolve) => setTimeout(resolve, waitTime));
      } else if (error.status === 401) {
        console.error("مفتاح الـ API غير صالح");
        break;
      } else {
        console.error(`خطأ: ${error.message}`);
        if (error.status >= 500) {
          await new Promise((resolve) => setTimeout(resolve, 5000));
        } else {
          break;
        }
      }
    }
  }
  return null;
}
```

---

## النشر والتشغيل (Deployment)

### التشغيل المحلي

```bash
# تثبيت التبعيات
poetry install

# تشغيل الخادم
poetry run python -m src.main

# أو عبر نقطة الدخول
poetry run claude-wrapper

# تشغيل على منفذ مختلف
PORT=9000 poetry run python -m src.main

# تشغيل مع تفعيل التصحيح
DEBUG_MODE=true poetry run python -m src.main
```

### Docker

```bash
# بناء الصورة
docker build -t claude-wrapper .

# تشغيل الحاوية
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -e API_KEY=your-api-key \
  claude-wrapper
```

### Docker Compose

```bash
# تشغيل للتطوير
docker-compose up

# تشغيل للإنتاج
docker-compose -f docker-compose.prod.yml up -d
```

**ملف `docker-compose.yml`:**
```yaml
version: '3'
services:
  claude-wrapper:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ~/.claude:/root/.claude
    environment:
      - PORT=8000
```

### التحقق من التشغيل

```bash
# فحص الصحة
curl http://localhost:8000/health

# فحص الإصدار
curl http://localhost:8000/version

# فحص المصادقة
curl http://localhost:8000/v1/auth/status

# فتح التوثيق التفاعلي
open http://localhost:8000/docs
```

---

## ملخص سريع

| ماذا تريد؟ | كيف؟ |
|------------|------|
| إرسال رسالة | `POST /v1/chat/completions` |
| بث مباشر | أضف `"stream": true` |
| جلسة مستمرة | أضف `"session_id": "my-session"` في `extra_body` |
| تفعيل الأدوات | أضف `"enable_tools": true` في `extra_body` |
| استخدام Anthropic SDK | `POST /v1/messages` |
| استعراض التوثيق | افتح `/docs` أو `/redoc` |
| فحص الصحة | `GET /health` |
| عرض الموديلات | `GET /v1/models` |
| إدارة الجلسات | `GET/DELETE /v1/sessions/{id}` |
| إعداد الأدوات | `GET/POST /v1/tools/config` |
| ربط MCP | `POST /v1/mcp/servers` ثم `POST /v1/mcp/connect` |
| تصحيح الأخطاء | `POST /v1/debug/request` أو فعّل `DEBUG_MODE=true` |
