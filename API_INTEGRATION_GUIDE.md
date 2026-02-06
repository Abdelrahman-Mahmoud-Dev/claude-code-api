# Claude Code API - Integration Guide

> كل ما يحتاجه مشروعك الخارجي للتواصل مع الـ API بدقة 100%

---

## Base URL

```
http://localhost:8000/v1
```

---

## Authentication

### API Key (اختياري)

لو الـ API Key مفعّل في `.env`:

```
Authorization: Bearer YOUR_API_KEY
```

لو مش مفعّل، ابعت أي قيمة أو اتركه فاضي.

### Error (401)

```json
{
  "error": {
    "message": "Missing API key",
    "type": "api_error",
    "code": "401"
  }
}
```

---

## Endpoints

### 1. Chat Completions (الأساسي)

```
POST /v1/chat/completions
```

#### Request

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Hello!"
    }
  ],
  "stream": false,
  "temperature": 1.0,
  "top_p": 1.0,
  "max_tokens": 4096,
  "session_id": "my-session-123",
  "enable_tools": false,
  "stream_options": {
    "include_usage": false
  }
}
```

#### Request Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `model` | string | YES | `claude-sonnet-4-5-20250929` | اسم الموديل |
| `messages` | array | YES | - | قائمة الرسائل |
| `messages[].role` | string | YES | - | `"system"` \| `"user"` \| `"assistant"` |
| `messages[].content` | string \| array | YES | - | نص الرسالة أو array من `{type, text}` |
| `messages[].name` | string | no | null | اسم المرسل (اختياري) |
| `stream` | boolean | no | `false` | تفعيل الـ streaming |
| `temperature` | float | no | `1.0` | 0 - 2 (best-effort, مش مدعوم بالكامل) |
| `top_p` | float | no | `1.0` | 0 - 1 (best-effort, مش مدعوم بالكامل) |
| `max_tokens` | integer | no | null | عدد التوكنز الأقصى |
| `max_completion_tokens` | integer | no | null | نفس `max_tokens` |
| `n` | integer | no | `1` | لازم يكون 1 |
| `session_id` | string | no | null | لاستمرار المحادثة |
| `enable_tools` | boolean | no | `false` | تفعيل أدوات Claude Code |
| `user` | string | no | null | معرّف المستخدم (للتتبع) |
| `stream_options` | object | no | null | إعدادات الـ streaming |
| `stream_options.include_usage` | boolean | no | `false` | إضافة usage في آخر chunk |
| `stop` | string \| array | no | null | **غير مدعوم** - يتم تجاهله |
| `presence_penalty` | float | no | `0` | **غير مدعوم** - يتم تجاهله |
| `frequency_penalty` | float | no | `0` | **غير مدعوم** - يتم تجاهله |
| `logit_bias` | object | no | null | **غير مدعوم** - يتم تجاهله |

#### Response (Non-Streaming)

```json
{
  "id": "chatcmpl-a1b2c3d4",
  "object": "chat.completion",
  "created": 1706745600,
  "model": "claude-sonnet-4-5-20250929",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150
  },
  "system_fingerprint": null
}
```

#### Response (Streaming - SSE)

Content-Type: `text/event-stream`

```
data: {"id":"chatcmpl-xyz","object":"chat.completion.chunk","created":1706745600,"model":"claude-sonnet-4-5-20250929","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}

data: {"id":"chatcmpl-xyz","object":"chat.completion.chunk","created":1706745600,"model":"claude-sonnet-4-5-20250929","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-xyz","object":"chat.completion.chunk","created":1706745600,"model":"claude-sonnet-4-5-20250929","choices":[{"index":0,"delta":{"content":" world!"},"finish_reason":null}]}

data: {"id":"chatcmpl-xyz","object":"chat.completion.chunk","created":1706745600,"model":"claude-sonnet-4-5-20250929","choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":10,"completion_tokens":5,"total_tokens":15}}

data: [DONE]
```

> ملاحظة: `usage` بيظهر في آخر chunk بس لو `stream_options.include_usage = true`

---

### 2. Anthropic Messages API

```
POST /v1/messages
```

#### Request

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 1024,
  "system": "You are a helpful assistant.",
  "messages": [
    {
      "role": "user",
      "content": "Hello!"
    }
  ],
  "temperature": 1.0,
  "stream": false
}
```

#### Request Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `model` | string | YES | - | اسم الموديل |
| `messages` | array | YES | - | قائمة الرسائل (`user` \| `assistant` فقط) |
| `max_tokens` | integer | YES | `4096` | عدد التوكنز الأقصى |
| `system` | string | no | null | system prompt |
| `temperature` | float | no | `1.0` | 0 - 1 |
| `top_p` | float | no | null | 0 - 1 |
| `top_k` | integer | no | null | - |
| `stop_sequences` | array | no | null | - |
| `stream` | boolean | no | `false` | - |
| `metadata` | object | no | null | - |

#### Response

```json
{
  "id": "msg_01a2b3c4d5e6f7g8h9i0",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Hello! How can I help you?"
    }
  ],
  "model": "claude-sonnet-4-5-20250929",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 100,
    "output_tokens": 50
  }
}
```

---

### 3. List Models

```
GET /v1/models
```

#### Response

```json
{
  "object": "list",
  "data": [
    { "id": "claude-opus-4-5-20250929", "object": "model", "owned_by": "anthropic" },
    { "id": "claude-sonnet-4-5-20250929", "object": "model", "owned_by": "anthropic" },
    { "id": "claude-haiku-4-5-20251001", "object": "model", "owned_by": "anthropic" },
    { "id": "claude-opus-4-1-20250805", "object": "model", "owned_by": "anthropic" },
    { "id": "claude-opus-4-20250514", "object": "model", "owned_by": "anthropic" },
    { "id": "claude-sonnet-4-20250514", "object": "model", "owned_by": "anthropic" }
  ]
}
```

---

### 4. Health Check

```
GET /health
```

```json
{ "status": "healthy", "service": "claude-code-openai-wrapper" }
```

---

### 5. Version

```
GET /version
```

```json
{ "version": "2.2.0", "service": "claude-code-openai-wrapper", "api_version": "v1" }
```

---

### 6. Auth Status

```
GET /v1/auth/status
```

```json
{
  "claude_code_auth": {
    "method": "claude_cli",
    "status": { "valid": true, "errors": [] }
  },
  "server_info": {
    "api_key_required": false,
    "version": "1.0.0"
  }
}
```

---

### 7. Sessions

```
GET    /v1/sessions              → قائمة الجلسات
GET    /v1/sessions/stats        → إحصائيات الجلسات
GET    /v1/sessions/{session_id} → تفاصيل جلسة معينة
DELETE /v1/sessions/{session_id} → حذف جلسة
```

---

### 8. Tools

```
GET  /v1/tools        → قائمة الأدوات المتاحة
GET  /v1/tools/config → إعدادات الأدوات الحالية
POST /v1/tools/config → تعديل إعدادات الأدوات
GET  /v1/tools/stats  → إحصائيات الأدوات
```

---

### 9. MCP Servers

```
GET  /v1/mcp/servers     → قائمة السيرفرات
POST /v1/mcp/servers     → تسجيل سيرفر جديد
POST /v1/mcp/connect     → اتصال بسيرفر
POST /v1/mcp/disconnect  → قطع اتصال
GET  /v1/mcp/stats       → إحصائيات
```

---

### 10. Debug & Compatibility

```
POST /v1/debug/request    → فحص وتحليل الـ request
POST /v1/compatibility    → فحص التوافق مع الـ API
```

---

## Custom Headers

| Header | Type | Description |
|--------|------|-------------|
| `X-Claude-Max-Turns` | integer (1-100) | عدد الخطوات الاستقلالية |
| `X-Claude-Allowed-Tools` | string (comma-separated) | الأدوات المسموحة |
| `X-Claude-Disallowed-Tools` | string (comma-separated) | الأدوات الممنوعة |
| `X-Claude-Permission-Mode` | string | `default` \| `acceptEdits` \| `bypassPermissions` \| `plan` |
| `X-Claude-Max-Thinking-Tokens` | integer (0-50000) | توكنز التفكير |
| `X-Request-ID` | string | معرّف مخصص للطلب |

---

## Available Models

| Model | Description |
|-------|-------------|
| `claude-opus-4-5-20250929` | الأقوى |
| `claude-sonnet-4-5-20250929` | **الموصى به** - أفضل موديل للكود |
| `claude-haiku-4-5-20251001` | سريع ورخيص |
| `claude-opus-4-1-20250805` | Opus 4 محدّث |
| `claude-opus-4-20250514` | Opus 4 الأصلي |
| `claude-sonnet-4-20250514` | Sonnet 4 الأصلي |

---

## Error Responses

### Format

```json
{
  "error": {
    "message": "Error description",
    "type": "error_type",
    "code": "error_code",
    "param": "field_name",
    "details": []
  }
}
```

### Error Codes

| HTTP Status | Type | Description |
|-------------|------|-------------|
| 401 | `api_error` | API key مفقود أو غلط |
| 413 | `request_too_large` | حجم الطلب أكبر من 10MB |
| 422 | `validation_error` | بيانات الطلب غلط |
| 429 | `rate_limit_exceeded` | تجاوز حد الطلبات |
| 500 | `api_error` | خطأ في السيرفر |
| 503 | `api_error` | سيرفر MCP مش متاح |

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/v1/chat/completions` | 10 req/min |
| `/v1/messages` | 10 req/min |
| `/v1/debug/*` | 2 req/min |
| `/v1/auth/*` | 10 req/min |
| `/v1/sessions/*` | 15 req/min |
| `/health`, `/version` | 30 req/min |
| باقي الـ endpoints | 30 req/min |

عند تجاوز الحد:

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

Header: `Retry-After: 60`

---

## Session Management

- ابعت `session_id` في الـ request لاستمرار المحادثة
- الجلسة بتنتهي بعد **ساعة** من آخر استخدام
- التنظيف التلقائي كل **5 دقائق**

---

## Code Examples

### Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="your-api-key"  # أو أي قيمة لو مش مفعّل
)

# محادثة عادية
response = client.chat.completions.create(
    model="claude-sonnet-4-5-20250929",
    messages=[
        {"role": "system", "content": "أنت مساعد مفيد"},
        {"role": "user", "content": "مرحبا!"}
    ]
)
print(response.choices[0].message.content)

# Streaming
stream = client.chat.completions.create(
    model="claude-sonnet-4-5-20250929",
    messages=[{"role": "user", "content": "اكتب قصة قصيرة"}],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### JavaScript (OpenAI SDK)

```javascript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "http://localhost:8000/v1",
  apiKey: "your-api-key",
});

// محادثة عادية
const response = await client.chat.completions.create({
  model: "claude-sonnet-4-5-20250929",
  messages: [
    { role: "system", content: "أنت مساعد مفيد" },
    { role: "user", content: "مرحبا!" },
  ],
});
console.log(response.choices[0].message.content);

// Streaming
const stream = await client.chat.completions.create({
  model: "claude-sonnet-4-5-20250929",
  messages: [{ role: "user", content: "اكتب قصة قصيرة" }],
  stream: true,
});
for await (const chunk of stream) {
  process.stdout.write(chunk.choices[0]?.delta?.content || "");
}
```

### cURL

```bash
# محادثة عادية
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# مع session
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "messages": [{"role": "user", "content": "اسمي أحمد"}],
    "session_id": "session-123"
  }'

# مع tools
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Claude-Allowed-Tools: Read,Write,Bash" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "messages": [{"role": "user", "content": "اقرأ الملف /etc/hostname"}],
    "enable_tools": true
  }'

# Streaming
curl -N -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-5-20250929",
    "messages": [{"role": "user", "content": "عد من 1 لـ 10"}],
    "stream": true
  }'
```

### PHP (Laravel/Guzzle)

```php
use GuzzleHttp\Client;

$client = new Client(['base_uri' => 'http://localhost:8000']);

$response = $client->post('/v1/chat/completions', [
    'headers' => [
        'Content-Type' => 'application/json',
        'Authorization' => 'Bearer your-api-key',
    ],
    'json' => [
        'model' => 'claude-sonnet-4-5-20250929',
        'messages' => [
            ['role' => 'user', 'content' => 'Hello!']
        ],
    ],
]);

$data = json_decode($response->getBody(), true);
echo $data['choices'][0]['message']['content'];
```

### C# (.NET)

```csharp
using var httpClient = new HttpClient();
httpClient.BaseAddress = new Uri("http://localhost:8000");
httpClient.DefaultRequestHeaders.Add("Authorization", "Bearer your-api-key");

var request = new {
    model = "claude-sonnet-4-5-20250929",
    messages = new[] {
        new { role = "user", content = "Hello!" }
    }
};

var response = await httpClient.PostAsJsonAsync("/v1/chat/completions", request);
var result = await response.Content.ReadFromJsonAsync<JsonElement>();
Console.WriteLine(result.GetProperty("choices")[0]
    .GetProperty("message")
    .GetProperty("content")
    .GetString());
```

---

## Quick Checklist

- [ ] Base URL: `http://localhost:8000/v1`
- [ ] Content-Type: `application/json`
- [ ] Model: `claude-sonnet-4-5-20250929` (الموصى به)
- [ ] `messages` array مع `role` و `content`
- [ ] `Authorization: Bearer KEY` (لو مفعّل)
- [ ] `stream: true` لو عايز streaming
- [ ] `session_id` لو عايز استمرار محادثة
- [ ] `enable_tools: true` لو عايز أدوات Claude Code
