import asyncio
import json
import os
import sys
import argparse
from pathlib import Path
import urllib.parse
from patchright.async_api import async_playwright, Page, BrowserContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

SENSITIVE_DATA = {}

# 添加命令行参数解析
def parse_arguments():
    parser = argparse.ArgumentParser(description='下载Z-Library图书')
    parser.add_argument('-n', '--name', type=str, help='要查找下载的图书名称')
    return parser.parse_args()

# --- Helper Functions (from playwright_script_helpers.py) ---
from patchright.async_api import Page


# --- Helper Function for Replacing Sensitive Data ---
def replace_sensitive_data(text: str, sensitive_map: dict) -> str:
	"""Replaces sensitive data placeholders in text."""
	if not isinstance(text, str):
		return text
	for placeholder, value in sensitive_map.items():
		replacement_value = str(value) if value is not None else ''
		text = text.replace(f'<secret>{placeholder}</secret>', replacement_value)
	return text


# --- Helper Function for Robust Action Execution ---
class PlaywrightActionError(Exception):
	"""Custom exception for errors during Playwright script action execution."""

	pass


async def _try_locate_and_act(page: Page, selector: str, action_type: str, text: str | None = None, step_info: str = '') -> None:
	"""
	Attempts an action (click/fill) with XPath fallback by trimming prefixes.
	Raises PlaywrightActionError if the action fails after all fallbacks.
	"""
	print(f'Attempting {action_type} ({step_info}) using selector: {repr(selector)}')
	original_selector = selector
	MAX_FALLBACKS = 50  # Increased fallbacks
	# Increased timeouts for potentially slow pages
	INITIAL_TIMEOUT = 10000  # Milliseconds for the first attempt (10 seconds)
	FALLBACK_TIMEOUT = 1000  # Shorter timeout for fallback attempts (1 second)

	try:
		locator = page.locator(selector).first
		if action_type == 'click':
			await locator.click(timeout=INITIAL_TIMEOUT)
			print('clicked...')
		elif action_type == 'fill' and text is not None:
			await locator.fill(text, timeout=INITIAL_TIMEOUT)
		else:
			# This case should ideally not happen if called correctly
			raise PlaywrightActionError(f"Invalid action_type '{action_type}' or missing text for fill. ({step_info})")
		print(f"  Action '{action_type}' successful with original selector.")
		await page.wait_for_timeout(500)  # Wait after successful action
		return  # Successful exit
	except Exception as e:
		print(f"  Warning: Action '{action_type}' failed with original selector ({repr(selector)}): {e}. Starting fallback...")

		# Fallback only works for XPath selectors
		if not selector.startswith('xpath='):
			# Raise error immediately if not XPath, as fallback won't work
			raise PlaywrightActionError(
				f"Action '{action_type}' failed. Fallback not possible for non-XPath selector: {repr(selector)}. ({step_info})"
			)

		xpath_parts = selector.split('=', 1)
		if len(xpath_parts) < 2:
			raise PlaywrightActionError(
				f"Action '{action_type}' failed. Could not extract XPath string from selector: {repr(selector)}. ({step_info})"
			)
		xpath = xpath_parts[1]  # Correctly get the XPath string

		segments = [seg for seg in xpath.split('/') if seg]

		for i in range(1, min(MAX_FALLBACKS + 1, len(segments))):
			trimmed_xpath_raw = '/'.join(segments[i:])
			fallback_xpath = f'xpath=//{trimmed_xpath_raw}'

			print(f'    Fallback attempt {i}/{MAX_FALLBACKS}: Trying selector: {repr(fallback_xpath)}')
			try:
				locator = page.locator(fallback_xpath).first
				if action_type == 'click':
					await locator.click(timeout=FALLBACK_TIMEOUT)
				elif action_type == 'fill' and text is not None:
					try:
						await locator.clear(timeout=FALLBACK_TIMEOUT)
						await page.wait_for_timeout(100)
					except Exception as clear_error:
						print(f'    Warning: Failed to clear field during fallback ({step_info}): {clear_error}')
					await locator.fill(text, timeout=FALLBACK_TIMEOUT)

				print(f"    Action '{action_type}' successful with fallback selector: {repr(fallback_xpath)}")
				await page.wait_for_timeout(500)
				return  # Successful exit after fallback
			except Exception as fallback_e:
				print(f'    Fallback attempt {i} failed: {fallback_e}')
				if i == MAX_FALLBACKS:
					# Raise exception after exhausting fallbacks
					raise PlaywrightActionError(
						f"Action '{action_type}' failed after {MAX_FALLBACKS} fallback attempts. Original selector: {repr(original_selector)}. ({step_info})"
					)

	# This part should not be reachable if logic is correct, but added as safeguard
	raise PlaywrightActionError(f"Action '{action_type}' failed unexpectedly for {repr(original_selector)}. ({step_info})")

# --- End Helper Functions ---
async def run_generated_script(book_name=None):
    global SENSITIVE_DATA
    async with async_playwright() as p:
        browser = None
        context = None
        page = None
        exit_code = 0 # Default success exit code
        try:
            print('Launching chromium browser...')
            # browser = await p.chromium.launch_persistent_context(
            #     headless=False, 
            #     user_data_dir="./browser_data",
            #     channel="chrome",
            #     accept_downloads=True,
            #     proxy={'server': 'http://127.0.0.1:1087', 'bypass': None, 'username': None, 'password': None}
            #     )
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
                
            # Create context with downloads enabled
            #context = await browser.new_context(
            #    no_viewport=True,
            #    accept_downloads=True
            #)
            print('Browser context created with downloads enabled.')
            
            
            # Set up download handler
            default_context = browser.contexts[0]
            page = default_context.pages[0]
            #page = await browser.new_page()
            await page.wait_for_timeout(20000)
            # Set up download handler to save files to Downloads folder
            download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
            
            # 使用异步函数处理下载
            async def handle_download(download):
                print(f"正在下载: {download.suggested_filename}")
                await download.save_as(os.path.join(download_path, download.suggested_filename))
                print(f"下载完成: {download.suggested_filename}")
            
            page.on("download", handle_download)
            
            print(f'下载路径设置为: {download_path}')
            # Initial page handling
            if default_context.pages:
                page = default_context.pages[0]
                print('Using initial page provided by context.')
            else:
                page = await default_context.new_page()
                print('Created a new page as none existed.')
            print('\n--- 开始执行脚本 ---')

            # --- Step 1 ---
            # Action 1
            print(f"导航到: https://101ml.fi (Step 1, Action 1)")
            await page.goto("https://101ml.fi", timeout=50000)
            await page.wait_for_load_state('load', timeout=50000)
            print('页面已加载')
            
            # --- Step 2 ---
            # Action 2
            search_term = book_name if book_name else "\u5c04\u96d5\u82f1\u96c4\u4f20"
            print(f"搜索图书: {search_term}")
            await _try_locate_and_act(page, "xpath=//html/body/div[2]/div/div/div[1]/form/div[1]/div/div[1]/input", "fill", text=replace_sensitive_data(search_term, SENSITIVE_DATA), step_info="Step 2, 输入搜索关键词")
            # Action 3
            await _try_locate_and_act(page, "xpath=//html/body/div[2]/div/div/div[1]/form/div[1]/div/div[2]/div/button", "click", step_info="Step 2, 点击搜索")
            await page.wait_for_timeout(5000)
            selector = "xpath=//*[@id=\"searchResultBox\"]//div[contains(@class,\"book-item\")][1]//z-bookcard"
            locator = await page.locator(selector).first.get_attribute('href')
            print("找到图书链接: https://101ml.fi"+locator)
            await page.goto("https://101ml.fi"+locator, timeout=50000)
            await page.wait_for_load_state('load', timeout=50000)
            
            # --- Step 3 ---
            # Action 4
            await _try_locate_and_act(page, "xpath=//a[@class=\"btn btn-default addDownloadedBook\"]", "click", step_info="Step 3, 下载")
            print("等待下载完成...")
            # 等待下载完成
            await page.wait_for_timeout(30000)  # 30秒应该足够大多数下载
            print("下载等待时间结束")
            
        except PlaywrightActionError as pae:
            print(f'\n--- Playwright 操作错误: {pae} ---', file=sys.stderr)
            exit_code = 1
        except Exception as e:
            print(f'\n--- 发生意外错误: {e} ---', file=sys.stderr)
            import traceback
            traceback.print_exc()
            exit_code = 1
        finally:
            print('\n--- 脚本执行完成 ---')
            print('正在关闭浏览器/上下文...')
            if context:
                 try: await context.close()
                 except Exception as ctx_close_err: print(f'  警告: 无法关闭上下文: {ctx_close_err}', file=sys.stderr)
            if browser:
                 try: await browser.close()
                 except Exception as browser_close_err: print(f'  警告: 无法关闭浏览器: {browser_close_err}', file=sys.stderr)
            print('浏览器/上下文已关闭.')
            # 使用确定的退出代码退出
            if exit_code != 0:
                print(f'脚本执行出错 (退出代码 {exit_code}).', file=sys.stderr)
                sys.exit(exit_code)

# --- Script Entry Point ---
if __name__ == '__main__':
    args = parse_arguments()
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(run_generated_script(args.name))