import sys
import os
import ctypes
from pynput.keyboard import Controller, Key
from time import sleep
import tkinter as tk
import threading

import pyautogui
from pyzbar.pyzbar import decode
from PIL import Image
from pynput import mouse
from mss import mss
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

    def capture_and_decode_qr():  # noqa: E302
        try:
             # 获取所有显示器信息
            user32 = ctypes.windll.user32
            screens = []
            
            # 回调函数枚举显示器
            def _callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
                rect = lprcMonitor.contents
                screens.append({
                    "left": rect.left,
                    "top": rect.top,
                    "width": rect.right - rect.left,
                    "height": rect.bottom - rect.top
                })
                return 1
            
            MONITORENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, 
                                                ctypes.c_ulong, ctypes.POINTER(ctypes.wintypes.RECT), 
                                                ctypes.c_ulong)
            user32.EnumDisplayMonitors(0, 0, MONITORENUMPROC(_callback), 0)
            
            points = []
            
            def on_click(x, y, button, pressed):
                if pressed and button == mouse.Button.left:
                    points.append((x, y))
                    print(f"已选择第{len(points)}个点: ({x}, {y})")
                    if len(points) == 2:
                        return False

            print("请依次点击区域的左上角和右下角")
            with mouse.Listener(on_click=on_click) as listener:
                listener.join()

            if len(points) < 2:
                print("需要选择两个坐标点")
                return

            # 确定两个点所在的显示器
            target_screen = None
            for screen in screens:
                s_left = screen["left"]
                s_top = screen["top"]
                s_right = s_left + screen["width"]
                s_bottom = s_top + screen["height"]
                
                if all(s_left <= p[0] <= s_right and s_top <= p[1] <= s_bottom for p in points):
                    target_screen = screen
                    break
                    
            # === 新增区域计算代码 ===
            x1, y1 = points[0]
            x2, y2 = points[1]
            region = (
                min(x1, x2) - target_screen["left"],  # 相对X坐标
                min(y1, y2) - target_screen["top"],   # 相对Y坐标
                abs(x2 - x1),                         # 宽度
                abs(y2 - y1)                          # 高度
            )

            # 截图参数调整为：
            from mss import mss
            with mss() as sct:
                # 计算绝对截图区域
                capture_area = {
                    "left": target_screen["left"] + region[0],
                    "top": target_screen["top"] + region[1],
                    "width": region[2],
                    "height": region[3]
                }
                
                # 截取指定区域
                screenshot = sct.grab(capture_area)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # 解析二维码
                decoded_objects = decode(img)
            if decoded_objects:
                for obj in decoded_objects:
                    #print(f"解析到的二维码内容: {obj.data.decode('utf-8')}")
                    text_input.insert(tk.END, obj.data.decode('utf-8') + "\n")
            else:
                #print("未检测到二维码")
                text_input.insert(tk.END, "未检测到二维码" + "\n")
        except Exception as e:
            #print(f"解析二维码时出错: {e}")
            text_input.insert(tk.END, f"解析二维码时出错: {e}" + "\n")

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
        
        # 新增截图和解析二维码按钮
        rowIndex += 1
        qr_button = tk.Button(root, text="截图解析二维码", width=15, command=capture_and_decode_qr)
        qr_button.grid(row=rowIndex, column=1, padx=3, pady=3)

        # 设置窗口大小
        root.geometry("520x600")
        root.mainloop()
else:
    # 重新以管理员权限运行
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)