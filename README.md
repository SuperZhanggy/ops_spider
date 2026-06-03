# ops-screenshot

基于 Playwright 的 Grafana 看板截图服务，通过 HTTP API 获取完整看板截图。

## 技术栈

- Python 3.11+
- FastAPI + uvicorn
- Playwright (Chromium)
- [uv](https://github.com/astral-sh/uv) 依赖管理

## 快速开始

### 安装依赖

```bash
uv sync
uv run playwright install chromium
```

### 启动服务

```bash
uv run python main.py
```

服务默认监听 `0.0.0.0:8031`。

## API

### GET /screenshot

截取指定 Grafana 看板的完整截图（PNG）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| url  | string | 是 | Grafana 看板 URL，会自动追加 `&kiosk` 隐藏导航栏 |

**示例：**

```bash
curl "http://localhost:8031/screenshot?url=https://grafana.example.com/d/abc123/my-dashboard" \
  -o dashboard.png
```

### GET /health

健康检查。

```bash
curl http://localhost:8031/health
# {"status":"ok"}
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
