# ops-screenshot

基于 Playwright 的 Grafana 看板截图服务，通过 HTTP API 获取完整看板截图。支持 LDAP 登录认证与 Token 鉴权。

## 技术栈

- Python 3.11+
- FastAPI + uvicorn
- Playwright (Chromium async)
- LDAP3 — 域控认证
- PyJWT — Token 签发/验证
- loguru — 结构化日志
- [uv](https://github.com/astral-sh/uv) 依赖管理

## 快速开始

### 安装依赖

```bash
uv sync
uv run playwright install chromium
```

### 配置文件

复制 `config.yml` 并根据环境修改：

```yaml
# LDAP 配置
LDAP_SERVER_POOL: ["ldap://your-ldap:389"]
ADMIN_DN: "CN=xxx,OU=xxx,DC=example,DC=com"
ADMIN_PASSWORD: "xxx"
SEARCH_BASE: "DC=example,DC=com"

# JWT 秘钥
SECRET_KEY: "your-secret-key"
TOKEN_EXPIRE_DAYS: 7
```

### 启动服务

```bash
uv run python main.py
```

服务默认监听 `0.0.0.0:8031`。

## API

### POST /api/auth/login

LDAP 登录，返回 JWT Token。

**Body:**

```json
{
  "username": "xxxxxxxxxx",
  "password": "xxxxxxxxxx"
}
```

**Response:**

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### GET /api/screenshot/grafana

截取指定 Grafana 看板的完整截图（PNG）。需携带有效 Token。

| Header | 值 | 必填 |
|--------|-----|------|
| Authorization | `Bearer <token>` | 是 |

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url  | string | 是 | Grafana 看板 URL，会自动追加 `&kiosk` |

**示例：**

```bash
curl "http://localhost:8031/api/screenshot/grafana?url=https://grafana.example.com/d/abc123" \
  -H "Authorization: Bearer eyJ..." \
  -o dashboard.png
```

### GET /health

健康检查（无需 Token）。

```bash
curl http://localhost:8031/health
# {"status":"ok"}
```

## 项目结构

```
├── api/
│   ├── routes/
│   │   ├── authentication.py   # 登录接口
│   │   └── screenshot.py       # 截图接口
│   └── deps.py                 # 认证依赖（login_required）
├── core/
│   ├── ldap.py                 # LDAP 工具类
│   └── sign.py                 # JWT 签发/验证
├── config/
│   ├── conf.py                 # 配置加载
│   └── logging.py              # loguru 日志配置
├── config.yml                  # 应用配置
├── main.py                     # 入口
└── logs/                       # 日志目录
```

## 工作原理

1. 追加 `&kiosk` 参数进入看板模式，隐藏顶部导航、侧栏菜单
2. 等待页面网络空闲 (`networkidle`)
3. 获取 `.react-grid-layout` 实际高度，逐段滚动触发懒加载
4. 回滚至顶部后，以实际高度为 viewport 截取全页截图
5. 返回 PNG 图片流

## 注意事项

- 首次运行需执行 `playwright install chromium` 安装浏览器
- 截图为 headless 模式，需确保 Grafana 可匿名访问或已配置免认证
- 日志输出至 `logs/ops_spider.log` 和 `logs/ops_spider.err.log`
