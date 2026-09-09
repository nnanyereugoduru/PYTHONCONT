import pyautogui
import time

print("Starting in:")
for i in range(5, 0, -1):
    print(i)
    time.sleep(1)

screen_width, screen_height = pyautogui.size()
y = screen_height // 2

active = True
while active:
    try:
        pyautogui.moveTo(0, y, duration=1)
        time.sleep(0.3)
        pyautogui.moveTo(screen_width, y, duration=1)
        time.sleep(0.3)
    except KeyboardInterrupt:
        active = False