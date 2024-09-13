import os
import json
import subprocess
import requests

def send_telegram_message(token, chat_id, message):
    telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
    telegram_payload = {
        "chat_id": chat_id,
        "text": message,
        "reply_markup": '{"inline_keyboard":[[{"text":"Feedback question?","url":"https://t.me/yxjsjl"}]]}'
    }

    response = requests.post(telegram_url, json=telegram_payload)
    print(f"Telegram status code request：{response.status_code}")
    print(f"Telegram request return content：{response.text}")

    if response.status_code != 200:
        print("Failed to send Telegram message")
    else:
        print("Send Telegram message successfully")

# Get key from environment variable
telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')


# Initialize the message
summary_message = "serv00-vless Restore operation results：\n"

# By default, restore the command
restore_command = "cd ~/domains/$USER.serv00.net/vless && ./check_vless.sh"
try:
    output = subprocess.check_output(restore_command, shell=True, stderr=subprocess.STDOUT)
    summary_message += f"\nsuccessful recovery command for user: {USER} output：\n{output.decode('utf-8')}"
except subprocess.CalledProcessError as e:
    summary_message += f"\ncannot be restored for user: {USER} output：\n{e.output.decode('utf-8')}"

# Send summary messages to Telegram
send_telegram_message(telegram_token, telegram_chat_id, summary_message)
