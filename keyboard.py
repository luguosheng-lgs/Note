from pynput.keyboard import Controller, Key
from time import sleep

# 创建键盘控制器
keyboard = Controller()

# 模拟输入文本
text_to_type = "Hello, World!"

def keyboardInput(text):
    for char in text:
        keyboard.press(char)
        keyboard.release(char)
    # 模拟按下回车键
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

if __name__ == "__main__":
    sleep(3)
    # 创建一个字符串数组
    text_list = ["860567072281477;P1Y24GN0K027548"]

    for text in text_list:
        keyboardInput(text)
        sleep(1)