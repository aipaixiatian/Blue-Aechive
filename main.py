from tasks import find_and_click_with_timeout, is_image_present, find_and_press, press_until_gone
import time

def main():
    task_sequence = [
        (find_and_click_with_timeout, 'Momotalk.png', None, '打开Momotalk'),
        (find_and_click_with_timeout, 'News.png', None, '打开新闻'),
        (find_and_click_with_timeout, 'xingxi.png', None,'打开学生讯息'),
        (press_until_gone, 'hf.png', '1', '回复消息'),
        (find_and_press, 'jb.png', 'space', ' 羁绊任务'),
        (find_and_press, 'jb2.png', 'space', ' 羁绊任务2'),
        (find_and_click_with_timeout, 'tg1.png', None, '跳过1'),
        (find_and_click_with_timeout, 'tg2.png', None, '跳过2'),
        (find_and_click_with_timeout, 'tap.png', None, '跳过3'),
        (press_until_gone, 'hf.png', '1', '回复消息'),
        (find_and_click_with_timeout, 'tc.png', None, '退出'),

    ]
    while True:
        for func, image, extra, desc in task_sequence:
            if is_image_present('my.png'):
                print("已完成")
                return
            print(f"---任务中: {desc}---")
            if extra is not None:
                func(image, extra)
            else:
                func(image)
            time.sleep(1)
        
   

                           
if __name__ == "__main__":
    main()