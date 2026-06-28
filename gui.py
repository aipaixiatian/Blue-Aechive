import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import tasks
from tasks import (
    find_and_click_with_timeout,
    is_image_present,
    find_and_press,
    press_until_gone
)

class AutoScriptGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("桃信")
        self.root.geometry("600x500")

        self.running = False
        self.thread = None

        self.task_sequence = [
            (find_and_click_with_timeout, 'Momotalk.png', None, '打开Momotalk'),
            (find_and_click_with_timeout, 'News.png', None, '打开新闻'),
            (find_and_click_with_timeout, 'xingxi.png', None, '打开学生讯息'),
            (press_until_gone, 'hf.png', '1', '回复消息'),
            (find_and_press, 'jb.png', 'space', '羁绊任务'),
            (find_and_press, 'jb2.png', 'space', '羁绊任务2'),
            (find_and_click_with_timeout, 'tg1.png', None, '跳过1'),
            (find_and_click_with_timeout, 'tg2.png', None, '跳过2'),
            (find_and_click_with_timeout, 'tap.png', None, '跳过3'),
            (press_until_gone, 'hf.png', '1', '回复消息'),
            (find_and_click_with_timeout, 'tc.png', None, '退出'),
        ]

        self.create_widgets()

    def create_widgets(self):
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(
            btn_frame, text="启动脚本", command=self.start_script,
            width=15, height=2, bg="lightgreen"
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = tk.Button(
            btn_frame, text="停止脚本", command=self.stop_script,
            width=15, height=2, bg="lightcoral", state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(self.root, text="就绪", font=("Arial", 12))
        self.status_label.pack(pady=5)

        self.log_area = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, width=70, height=20,
            font=("Consolas", 10)
        )
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        clear_btn = tk.Button(self.root, text="清空日志", command=self.clear_log)
        clear_btn.pack(pady=5)

    def log(self, message):
        self.root.after(0, lambda: self.log_area.insert(tk.END, message + "\n"))
        self.root.after(0, lambda: self.log_area.see(tk.END))

    def clear_log(self):
        self.log_area.delete(1.0, tk.END)

    def set_status(self, text):
        self.root.after(0, lambda: self.status_label.config(text=text))

    def start_script(self):
        if self.running:
            return

        tasks.stop_flag = False

        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.log("=== 脚本启动 ===")
        self.set_status("运行中...")

        self.thread = threading.Thread(target=self.run_tasks, daemon=True)
        self.thread.start()

    def stop_script(self):
        if not self.running:
            return

        self.log("⏹ 正在停止脚本（立即中断当前任务）...")
        self.set_status("正在停止...")

        tasks.stop_flag = True

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.set_status("已停止")
        self.log("=== 脚本已停止 ===")

    def run_tasks(self):
        try:
            while self.running:
                for func, image, extra, desc in self.task_sequence:
                    # 检查停止标志
                    if not self.running or tasks.stop_flag:
                        return

                    # 检查是否完成（适配新返回值）
                    present, check_msg = is_image_present('my.png', confidence=0.9)
                    if present:
                        self.log(f"✅ 已完成（检测到 my.png）{check_msg}")
                        self.set_status("已完成")
                        self._finish_ui()
                        return

                    self.log(f"▶ 执行: {desc}")
                    self.set_status(f"执行中: {desc}")

                    try:
                        # ---------- 这里是关键改动 ----------
                        if extra is not None:
                            success, detail_msg = func(image, extra)
                        else:
                            success, detail_msg = func(image)
                        # ------------------------------------

                        # 根据返回值打印详细日志
                        if success:
                            self.log(f"   ✅ {detail_msg}")
                        else:
                            self.log(f"   ❌ {detail_msg}")
                            self.set_status(f"步骤失败: {desc}")
                            # 关键步骤失败，建议停止脚本，避免卡死
                            self.log("⚠️ 因步骤失败，脚本已自动停止")
                            return
                    except Exception as e:
                        self.log(f"❌ 任务执行异常: {e}")
                        self.set_status("出错")
                        return

                    time.sleep(1)

                if self.running and not tasks.stop_flag:
                    self.log("--- 完成一轮，继续循环 ---")
        except Exception as e:
            self.log(f"❌ 脚本异常: {e}")
            self.set_status("异常")
        finally:
            # 确保停止时恢复 UI 状态
            if not self.running or tasks.stop_flag:
                self.root.after(0, self._finish_ui)

    def _finish_ui(self):
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        if self.running:
            self.running = False
            self.set_status("已完成")
        else:
            self.set_status("已停止")
        self.log("=== 脚本结束 ===")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoScriptGUI(root)
    root.mainloop()
