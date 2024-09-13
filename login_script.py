import json
import asyncio
from pyppeteer import launch
from datetime import datetime, timedelta, timezone
import aiofiles
import random
import requests
import os

# 从环境变量中获取 Telegram Bot Token 和 Chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def format_to_iso(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')

async def delay_time(ms):
    await asyncio.sleep(ms / 1000)

# Global browser instance
browser = None

# telegram information
message = 'serv00&ct8 اجرای خودکار اسکریپت\n'

async def login(username, password, panel):
    global browser

    page = None  # Make sure page is defined in all cases
    serviceName = 'ct8' if 'ct8' in panel else 'serv00'
    try:
        if not browser:
            browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])

        page = await browser.newPage()
        url = f'https://{panel}/login/?next=/'
        await page.goto(url)

        username_input = await page.querySelector('#id_username')
        if username_input:
            await page.evaluate('''(input) => input.value = ""''', username_input)

        await page.type('#id_username', username)
        await page.type('#id_password', password)

        login_button = await page.querySelector('#submit')
        if login_button:
            await login_button.click()
        else:
            raise Exception('دکمه ورود پیدا نشد')

        await page.waitForNavigation()

        is_logged_in = await page.evaluate('''() => {
            const logoutButton = document.querySelector('a[href="/logout/"]');
            return logoutButton !== null;
        }''')

        return is_logged_in

    except Exception as e:
        print(f'{serviceName}کاربری {username} خطا به هنگام ورود: {e}')
        return False

    finally:
        if page:
            await page.close()

async def main():
    global message
    message = 'اجرای خودکار اسکریپت serv00&ct8\n'

    try:
        async with aiofiles.open('accounts.json', mode='r', encoding='utf-8') as f:
            accounts_json = await f.read()
        # accounts_json = os.getenv('ACCOUNTS_JSON')
        # print(f'تست: {TELEGRAM_CHAT_ID}')
        accounts = json.loads(accounts_json)
    except Exception as e:
        print(f'به هنگام خواندن accounts.json این خطا رخ داد: {e}')
        return

    for account in accounts:
        username = account['username']
        password = account['password']
        panel = account['panel']

        serviceName = 'ct8' if 'ct8' in panel else 'serv00'
        is_logged_in = await login(username, password, panel)

        if is_logged_in:
            now_utc = format_to_iso(datetime.now(timezone.utc))
            now_tehran = format_to_iso(datetime.now(timezone.utc) + timedelta(hours=3, minutes=30))
            success_message = f'نوع سرور {serviceName} با کاربری {username} به وقت تهران {now_tehran}（UTC {now_utc}）با موفقیت وارد شد！'
            message += success_message + '\n'
            print(success_message)
        else:
            message += f'نوع سرور {serviceName} کاربری {username} ورود ناموفق بود، لطفا بررسی کنید آیا کاربری و رمز عبور صحیح است؟ \n'
            print(message)

        delay = random.randint(1000, 8000)
        await delay_time(delay)
        
    message += f'تمامی {serviceName} ورود به حساب تکمیل شد！'
    await send_telegram_message(message)
    print(message)

async def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': {
            'inline_keyboard': [
                [
                    {
                        'text': 'بازخورد مشکلات',
                        'url': 'https://t.me/yxjsjl'
                    }
                ]
            ]
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"ارسال پیام به تلگرام انجام نشد: {response.text}")
    except Exception as e:
        print(f"ارسال پیام به تلگرام انجام نشد: {e}")

if __name__ == '__main__':
    asyncio.run(main())
