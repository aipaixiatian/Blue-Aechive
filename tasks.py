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

def find_and_click(image_name, confidence=0.8):
    # 1. 检查图片文件是否存在
    target = cv2.imread(get_path(image_name))
    if target is None:
        return False, f"图片文件不存在: {image_name}"

    # 2. 检查截图是否成功
    screen = get_screenshot()
    if screen is None:
        return False, "屏幕截图失败"

    # 3. 模板匹配
    res = cv2.matchTemplate(screen, target, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    # 4. 判断匹配度并执行点击
    if max_val >= confidence:
        h, w = target.shape[:2]
        center_x = max_loc[0] + w // 2 + random.randint(-2, 2)
        center_y = max_loc[1] + h // 2 + random.randint(-2, 2)
        pyautogui.click(center_x, center_y)
        return True, f"点击成功 (匹配度 {max_val:.2f})"
    else:
        return False, f"未找到 (最大匹配度 {max_val:.2f}，要求 ≥{confidence})"

def find_and_click_with_timeout(image_name, timeout=30, confidence=0.8):
    start_time = time.time()
    attempt = 0
    while time.time() - start_time < timeout:
        attempt += 1
        success, msg = find_and_click(image_name, confidence)
        if success:
            return True, f"{msg} (耗时 {attempt} 秒)"
        time.sleep(1)
    return False, f"等待 {timeout}s 超时，未能找到并点击 {image_name}"

def is_image_present(image_name, confidence=0.7):
    target = cv2.imread(get_path(image_name))
    if target is None:
        return False, f"图片文件不存在: {image_name}"
    
    screen = get_screenshot()
    if screen is None:
        return False, "屏幕截图失败"
    
    res = cv2.matchTemplate(screen, target, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    
    found = max_val >= confidence
    if found:
        return True, f"检测到 (匹配度 {max_val:.2f})"
    else:
        return False, f"未检测到 (最大匹配度 {max_val:.2f}，要求 ≥{confidence})"

def click_until_gone(image_name, max_attempts=10, confidence=0.8):
    for i in range(max_attempts):
        success, msg = find_and_click(image_name, confidence)
        if success:
            time.sleep(1)
        else:
            # 检查是否真的消失了
            present, _ = is_image_present(image_name, confidence)
            if not present:
                return True, f"{image_name} 已消失 (第 {i+1} 次尝试)"
            else:
                time.sleep(1)
    return False, f"尝试 {max_attempts} 次后 {image_name} 仍未消失"

def find_and_press(image_name, key, confidence=0.8):
    target = cv2.imread(get_path(image_name))
    if target is None:
        return False, f"图片文件不存在: {image_name}"
    
    screen = get_screenshot()
    if screen is None:
        return False, "屏幕截图失败"
    
    res = cv2.matchTemplate(screen, target, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    
    if max_val >= confidence:
        pyautogui.press(key)
        return True, f"检测到 {image_name}，已按下 '{key}' (匹配度 {max_val:.2f})"
    else:
        return False, f"未检测到 {image_name} (最大匹配度 {max_val:.2f}，要求 ≥{confidence})，未按下按键"

def press_until_gone(image_name, key, max_attempts=10, confidence=0.8):
    for i in range(max_attempts):
        # 注意：is_image_present 现在返回 (bool, str)
        present, msg = is_image_present(image_name, confidence)
        
        if present:
            pyautogui.press(key)
            # 这里把识别详情打印出来（可选，但为了日志我们保留）
            print(f"   {msg}，按下 '{key}' (第 {i+1}/{max_attempts} 次)")
            time.sleep(1)
        else:
            # 图片已消失，返回成功，附带消失信息
            return True, f"{image_name} 已消失 (第 {i+1} 次检测时 {msg})"
    
    # 尝试次数用完仍未消失
    return False, f"尝试 {max_attempts} 次后 {image_name} 仍未消失"
