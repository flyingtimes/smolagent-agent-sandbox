from playwright.sync_api import Playwright, sync_playwright, expect
import json
import time
from pathlib import Path

def save_cookies(cookies, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(cookies, f, indent=2)

def run(playwright: Playwright) -> None:
    try:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        browser = playwright.chromium.launch(
            headless=False,
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
        
        page = context.new_page()
        
        # 访问YouTube
        page.goto("https://youtube.com/")
        
        # 等待并点击登录按钮 - 使用更具体的选择器
        page.wait_for_load_state('networkidle')
        login_button = page.locator("#buttons >> text=登录").first
        login_button.wait_for(state='visible')
        login_button.click()
        time.sleep(3)
        # 输入邮箱
        email_input = page.get_by_label('电子邮件地址')
        email_input.wait_for(state='visible')
        email_input.fill("chetingtianxia@gmail.com")
        time.sleep(1)
        # 点击下一步
        next_button = page.get_by_role("button", name="下一步")
        next_button.wait_for(state='visible')
        next_button.click()
        # 等待密码输入框出现
        password_input = page.get_by_label("输入您的密码")
        password_input.wait_for(state='visible')
        time.sleep(1)
        # 输入密码
        password_input.fill("AV7gzE0whExRRZK5giKKZVheVsUuT7")
        time.sleep(1)
        
        # 点击下一步按钮完成登录
        next_button = page.get_by_role("button", name="下一步")
        next_button.wait_for(state='visible')
        next_button.click()
        # 等待用户手动完成登录（输入密码等步骤）
        print("请在60秒内完成手动登录...")
        time.sleep(60)
        
        # 获取并保存cookies
        cookies = context.cookies()
        cookies_file = Path('youtube_cookies.json')
        save_cookies(cookies, cookies_file)
        print(f"Cookies已保存到: {cookies_file.absolute()}")
        
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