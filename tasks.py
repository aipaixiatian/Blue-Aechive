import pyautogui
import time
import os
import sys
import subprocess
import cv2
import numpy as np
import platform
import pyautogui
import random

stop_flag = False

def get_screenshot():##根据操作系统获取屏幕截图
    system = platform.system()

    if system == "Windows":
        screenshot = pyautogui.screenshot()
        return cv2 .cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    elif system == "Linux":
        try:
            process = subprocess.run(['grim', '-'], stdout=subprocess.PIPE, check=True)
            img_array = np.frombuffer(process.stdout, dtype=np.uint8)
            return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        except Exception as e:##处理截图错误
            print(f"Error taking screenshot: {e}")
            return None

def get_path(filename):##获取文件路径，适应打包后的环境
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, filename)

def find_and_click(image_name, confidence=0.8):##查找并点击图像
    target = cv2.imread(get_path(image_name))
    if target is None:
        print(f"未找到图片 {image_name}")
        return False
    
    screen = get_screenshot()
    if screen is None: return False
    res = cv2.matchTemplate(screen, target, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    if max_val >= confidence:
        h, w = target.shape[:2]
        center_x = max_loc[0] + w // 2 + random.randint(-2, 2)
        center_y = max_loc[1] + h // 2 + random.randint(-2, 2)
        pyautogui.click(center_x, center_y)
        return True
    return False

def find_and_click_with_timeout(image_name, timeout=30):##带超时的查找和点击
    start_time = time.time()
    while time.time() - start_time < timeout:
       if find_and_click(image_name):
           print(f"点击成功 {image_name}")
           return True
       time.sleep(1)
    return False

def is_image_present(image_name, confidence=0.7):##计算匹配度 只观察不点击
    target = cv2.imread(get_path(image_name))
    if target is None: return False
    
    screen = get_screenshot()
    if screen is None: return False
    
    res = cv2.matchTemplate(screen, target, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    
    return max_val >= confidence

def click_until_gone(image_name, max_attempts=10):###点击直到图像消失
    for i in range(max_attempts):
        if find_and_click(image_name):
            time.sleep(1)
        else:
            if not is_image_present(image_name):
                print(f"{image_name} 已消失.")
                return True
            else:
                time.sleep(1)
    return False

def find_and_press(image_name, key, confidence=0.8):###查找图像并按下指定键
    target = cv2.imread(get_path(image_name))
    if target is None: return False

    screen = get_screenshot()
    if screen is None: return False

    fes = cv2.matchTemplate(screen, target, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(fes)
    if max_val >= confidence:
        print(f"检测到 {image_name}, 正在按下 {key}.")
        pyautogui.press(key)
        return True
    return False

def press_until_gone(image_name, key ,max_attempts=10, confidence=0.8):
    for i in range(max_attempts):
        if is_image_present(image_name, confidence):
            print(f"检测到{image_name},按下{key}(第{i+1}/{max_attempts}次)")
            pyautogui.press(key)
            time.sleep(1)
        else:
            print(f"{image_name}已消失")
            return True
    print(f"尝试{max_attempts}次后{image_name}仍未消失")
    return False
