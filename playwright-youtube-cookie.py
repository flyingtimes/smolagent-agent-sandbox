from playwright.sync_api import Playwright, sync_playwright, expect
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

def save_cookies(cookies, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(cookies, f, indent=2)

def load_cookies(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Cookie文件 {file_path} 不存在")
        return None
    except json.JSONDecodeError:
        print(f"Cookie文件 {file_path} 格式错误")
        return None

def is_within_24hours(upload_time_text):
    """检查视频是否在24小时内发布"""
    if '小时前' in upload_time_text:
        hours = int(upload_time_text.split('小时前')[0])
        return hours <= 24
    return False

def run(playwright: Playwright) -> None:
    try:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        browser = playwright.chromium.launch(
            headless=True,
            proxy={"server": "http://127.0.0.1:1087"},
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )
        context = browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            java_script_enabled=True,
            ignore_https_errors=True,
            permissions=['geolocation', 'notifications'],
            extra_http_headers={
                'Accept-Language': 'zh-CN,zh;q=0.9',
            }
        )
        
        # 修改webdriver标记
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });
        """)
        
        # 加载cookie
        cookies = load_cookies('youtube_cookies.json')
        if cookies:
            context.add_cookies(cookies)
        else:
            print("无法加载cookie，将以未登录状态访问YouTube")
            
        page = context.new_page()
        
        # 访问YouTube频道
        page.goto("https://www.youtube.com/@stone_ji/videos")
        
        # 等待页面加载完成
        page.wait_for_load_state('networkidle')
        print("正在获取24小时内发布的视频...")
        # 等待视频列表加载
        videos = page.locator("ytd-rich-grid-media")
        print(videos)
        # 获取所有视频信息
        for i in range(videos.count()):
            video = videos.nth(i)
            # 获取视频标题
            title = video.locator("#video-title").inner_text()
            print(title)
            # 获取视频链接
            link = video.locator("#video-title-link").get_attribute("href")
            if link:
                link = "https://www.youtube.com" + link
            upload_time = video.locator("#inline-metadata-item").first.inner_text()
            print(f"\n标题: {title}")
            print(f"链接: {link}")
            print(f"发布时间: {upload_time}")
        
        # 等待一段时间以便查看结果
        print("\n数据获取完成，等待10秒后关闭...")
        time.sleep(10)
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        if 'page' in locals():
            page.close()
        if 'context' in locals():
            context.close()
        if 'browser' in locals():
            browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)