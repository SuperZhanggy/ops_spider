from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from playwright.async_api import async_playwright, TimeoutError
from io import BytesIO

router = APIRouter()

@router.get("/grafana")
async def grafana_dashboard(url: str = Query(..., description="Grafana 看板 URL")):
    try:
        # kiosk模式会隐藏：顶部导航 左侧菜单 用户菜单
        if not url.endswith("&kiosk"):
            url += "&kiosk"
        with async_playwright() as p:
            browser = p.chromium.launch(headless=True)

            page = browser.new_page(
                viewport={"width": 1920, "height": 4000}
            )

            page.goto(url)

            # 4️⃣ 等网络空闲
            page.wait_for_load_state("networkidle")

            # ✅ 1. 获取 react-grid-layout 的实际高度并滚动触发懒加载
            grid_height = page.evaluate("""
                    () => {
                        const grid = document.querySelector('.react-grid-layout');
                        return grid ? grid.scrollHeight : document.body.scrollHeight;
                    }
                """)

            page.evaluate("""
                    async (height) => {
                        return new Promise(resolve => {
                            let step = 600;
                            let current = 0;
                            function scroll() {
                                window.scrollTo(0, current);
                                current += step;
                                if (current < height) {
                                    setTimeout(scroll, 100);
                                } else {
                                    window.scrollTo(0, 0);
                                    resolve();
                                }
                            }
                            scroll();
                        });
                    }
                """, grid_height)

            # 5️⃣ 额外等待
            # 等待 grafana panel 渲染
            page.wait_for_timeout(1000)

            # ✅ 2. 以 react-grid-layout 的高度作为截图高度
            page.set_viewport_size({"width": 1920, "height": grid_height})

            # 6️⃣ 截图到内存
            image_bytes = page.screenshot(full_page=True)

            browser.close()

        return StreamingResponse(
            BytesIO(image_bytes),
            media_type="image/png",
            headers={
                "Content-Disposition": "inline; filename=grafana_screenshot.png"
            }
        )

    except TimeoutError as e:
        raise HTTPException(
            status_code=504,
            detail=f"页面加载超时: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
