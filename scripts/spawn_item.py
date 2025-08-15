import subprocess
import pyautogui
import time
import pygetwindow as gw
import pyperclip
import sys
from utils.logger import logger

def send_command(command: str):
    try:
        scum_window = next((w for w in gw.getAllTitles() if "SCUM" in w), None)
        if not scum_window:
            logger.error("SCUM window not found.")
            return False
        pyautogui.press('t')
        time.sleep(0.8)
        pyperclip.copy(command)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')
        return True
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.error("Usage: python spawn_item.py <item> <steam_id>")
        sys.exit(1)
    item, steam_id = sys.argv[1], sys.argv[2]
    success = send_command(f'#spawnItem {item} {steam_id}')
    sys.exit(0 if success else 1)
