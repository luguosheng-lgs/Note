import sys
import os
import ctypes
from pynput.keyboard import Controller, Key
from time import sleep
import tkinter as tk
import threading
# 检查是否以管理员权限运行
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    

if is_admin():
    # 创建键盘控制器
    keyboard = Controller()

    # 模拟输入文本
    text_to_type = "Hello, World!"
    isRunning = False

    def keyboardInput(text):
        print("正在模拟输入文本: " + text)
        for char in text:
            keyboard.press(char)
            keyboard.release(char)
        # 模拟按下回车键
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

    def on_start_click():
        # 启动一个新的线程来执行模拟输入
        global isRunning
        if isRunning:
            isRunning = False
            startButton.config(text="开始")
        else:
            isRunning = True
            startButton.config(text="停止")
            sleepAfterStart = input_box1.get()
            sleepAfterStart = int(sleepAfterStart)
            sleep(sleepAfterStart)
            threading.Thread(target=perform_keyboard_actions).start()
        
    def on_stop_click():
        # 停止模拟输入
        global isRunning
        print("停止模拟输入")

    def perform_keyboard_actions():
        # 读取input_box1中的内容
        global isRunning
        sleepInterval = input_box2.get()
        sleepInterval = int(sleepInterval)
        for row in entries:
            if not isRunning:
                break
            # 获取 Entry 组件和 checkbox_var 组件
            entry, checkbox_var = row
            if entry.get() and checkbox_var.get(): 
                keyboardInput(entry.get())
                sleep(sleepInterval)
        
        if not isRunning:
            return
        # 循环读取多行输入框text_input的一行一行文本
        if text_input_checkbox_var.get():
            text_input_context = text_input.get('1.0', 'end-1c')  # 获取整个文本内容
            for row in text_input_context.split('\n'):
                if not isRunning:
                    break
                if row.strip(): 
                    keyboardInput(row)
                    sleep(sleepInterval)

        # 修改startButton的文本为"开始"
        isRunning = False
        startButton.config(text="开始")

    def create_single_column_table(root, startRow, rows):
        # 创建一个框架来容纳表格
        frame = tk.Frame(root)
        frame.grid(row=startRow, column=1, padx=3, pady=3)

        # 创建一个二维数组来保存所有的 Entry 组件和Checkbutton组件
        entries = []

        # 创建表格的每一行
        for i in range(startRow, startRow + rows):
            entry = tk.Entry(frame, width=30)
            entry.grid(row=i, column=1, padx=3, pady=3)

            # 创建 IntVar 变量来存储 Checkbutton 的状态
            checkbox_var = tk.IntVar()
            #创建一个勾选框
            checkbox = tk.Checkbutton(frame, text="", variable=checkbox_var)
            checkbox.grid(row=i, column=2, padx=3, pady=3)
            #将 Entry 和 Checkbutton 组件保存在一个子列表中
            row_components = [entry, checkbox_var]
            entries.append(row_components)

        return entries

    if __name__ == "__main__":
        
        root = tk.Tk()
        rowIndex = 0
        # 设置窗口标题
        root.title("键盘模拟工具V1.1 - by:luguosheng")
        # 创建一个文本显示标签
        label1 = tk.Label(root, text="开始后延迟时间(s)")
        label1.grid(row=rowIndex, column=0, padx=3, pady=3)
        # 创建一个输入框,默认值为3
        entry_text = tk.StringVar(value="3")
        input_box1 = tk.Entry(root, textvariable=entry_text)
        input_box1.grid(row=rowIndex, column=1, padx=3, pady=3)
        
        rowIndex += 1
        label2 = tk.Label(root, text="每段文本输出间隔时间(s)")
        label2.grid(row=rowIndex, column=0, padx=3, pady=3)
        # 创建一个输入框
        entry_text = tk.StringVar(value="1")
        input_box2 = tk.Entry(root, textvariable=entry_text)
        input_box2.grid(row=rowIndex, column=1, padx=3, pady=3)

        rowIndex += 1
        label2 = tk.Label(root, text="模拟键盘输出文本：")
        label2.grid(row=rowIndex, column=0, padx=3, pady=3)
        # 创建一个列表输入框
        entries = create_single_column_table(root, 3, 6)

        rowIndex += 6
        # 创建一个多行文本输入框
        label2 = tk.Label(root, text="批量模拟键盘输出文本：")
        label2.grid(row=rowIndex, column=0, padx=3, pady=3)
        
        rowIndex += 1
        text_input = tk.Text(root, height=12, width=35)
        text_input.grid(row=rowIndex, column=1, padx=3, pady=3)

        
        #创建一个勾选框
        text_input_checkbox_var = tk.IntVar()
        text_input_checkbox = tk.Checkbutton(root, text="", variable=text_input_checkbox_var)
        text_input_checkbox.grid(row=rowIndex, column=3, padx=3, pady=3)

        rowIndex += 1
        # 创建一个框架来容纳表格
        # ButtonFrame = tk.Frame(root)
        # ButtonFrame.grid(row=rowIndex, column=1, padx=3, pady=3)
        startButton = tk.Button(root, text="开始", width=15)
        startButton.grid(row=rowIndex, column=1, padx=3, pady=3)
        startButton.config(command=on_start_click)
        # stopButton = tk.Button(ButtonFrame, text="停止", width=15)
        # stopButton.grid(row=rowIndex, column=1, padx=3, pady=3)
        # stopButton.config(command=on_stop_click)

        rowIndex += 1
        label2 = tk.Label(root, text="切换到英文小写输入，点击开始后，鼠标点击目标输入位置")
        label2.grid(row=rowIndex, column=1, padx=3, pady=3)
        

        # 设置窗口大小
        root.geometry("520x560")
        root.mainloop()
else:
    # 重新以管理员权限运行
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)