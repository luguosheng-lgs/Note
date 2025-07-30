import ctypes
from ctypes.wintypes import DWORD, WORD
from pynput.keyboard import Controller, Key
from time import sleep
import tkinter as tk

# 定义必要的常量
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008
VK_RETURN = 0x0D  # 回车键
# 定义结构体
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", WORD),
        ("wScan", WORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", ctypes.POINTER(DWORD)),
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", DWORD),
        ("wParamL", WORD),
        ("wParamH", WORD),
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", DWORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", ctypes.POINTER(DWORD)),
    ]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [
            ("ki", KEYBDINPUT),
            ("mi", MOUSEINPUT),
            ("hi", HARDWAREINPUT),
        ]
    _anonymous_ = ("_input",)
    _fields_ = [
        ("type", DWORD),
        ("_input", _INPUT),
    ]

# 定义函数原型
SendInput = ctypes.windll.user32.SendInput
SendInput.argtypes = [DWORD, ctypes.POINTER(INPUT), ctypes.c_int]
SendInput.restype = DWORD

# 获取虚拟键码
MapVirtualKey = ctypes.windll.user32.MapVirtualKeyW
MapVirtualKey.argtypes = [WORD, DWORD]
MapVirtualKey.restype = WORD

# 获取当前的键盘布局
GetKeyboardLayout = ctypes.windll.user32.GetKeyboardLayout
GetKeyboardLayout.argtypes = [DWORD]
GetKeyboardLayout.restype = ctypes.c_ulong

def send_keyboard_input(key, scan_code=False):
    # 获取当前键盘布局
    layout_id = GetKeyboardLayout(0)

    if not scan_code:
        # 转换为虚拟键码
        vk_code = ctypes.windll.user32.VkKeyScanW(ord(key))
        if vk_code == -1:
            raise ValueError(f"无法找到键 '{key}' 的虚拟键码")
    else:
        # 使用扫描码
        vk_code = key

    # 创建输入结构体
    input_struct = INPUT(
        type=INPUT_KEYBOARD,
        _input=KEYBDINPUT(
            wVk=vk_code,
            wScan=MapVirtualKey(vk_code, 0),
            dwFlags=0,
            time=0,
            dwExtraInfo=None
        )
    )

    # 发送按下事件
    SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(input_struct))

    # 修改输入结构体标志位
    input_struct._input.dwFlags = KEYEVENTF_KEYUP

    # 发送释放事件
    SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(input_struct))

def send_unicode_input(unicode_char):
    # 创建输入结构体
    input_struct = INPUT(
        type=INPUT_KEYBOARD,
        _input=KEYBDINPUT(
            wVk=0,
            wScan=0,
            dwFlags=KEYEVENTF_UNICODE,
            time=0,
            dwExtraInfo=None
        )
    )

    # 设置 Unicode 字符
    input_struct._input.wScan = ord(unicode_char)

    # 发送 Unicode 输入
    SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(input_struct))

def keyboardInput(text):
    print("正在模拟输入文本: " + text)
    for char in text:
        send_unicode_input(char)
    # # 模拟按下回车键
    # send_keyboard_input(VK_RETURN)

def on_click():
    # 读取input_box1中的内容
    sleepAfterStart = input_box1.get()
    sleepInterval = input_box2.get()
    sleepAfterStart = int(sleepAfterStart)
    sleepInterval = int(sleepInterval)
    sleep(sleepAfterStart)
    for row in entries:
        # 获取 Entry 组件和 checkbox_var 组件
        entry, checkbox_var = row
        if entry.get() and checkbox_var.get(): 
            keyboardInput(entry.get())
            sleep(sleepInterval)

def create_single_column_table(root, startRow, rows):
    # 创建一个框架来容纳表格
    frame = tk.Frame(root)
    frame.grid(row=startRow, column=1, padx=5, pady=5)

    # 创建一个二维数组来保存所有的 Entry 组件和Checkbutton组件
    entries = []

    # 创建表格的每一行
    for i in range(startRow, startRow + rows):
        entry = tk.Entry(frame, width=30)
        entry.grid(row=i, column=1, padx=5, pady=5)

        # 创建 IntVar 变量来存储 Checkbutton 的状态
        checkbox_var = tk.IntVar()
        #创建一个勾选框
        checkbox = tk.Checkbutton(frame, text="", variable=checkbox_var)
        checkbox.grid(row=i, column=2, padx=5, pady=5)
        #将 Entry 和 Checkbutton 组件保存在一个子列表中
        row_components = [entry, checkbox_var]
        entries.append(row_components)

    return entries

if __name__ == "__main__":
    
    root = tk.Tk()
    # 设置窗口标题
    root.title("键盘模拟输入")
    # 创建一个文本显示标签
    label1 = tk.Label(root, text="开始后延迟时间(s)")
    label1.grid(row=0, column=0, padx=5, pady=5)
    # 创建一个输入框,默认值为3
    entry_text = tk.StringVar(value="3")
    input_box1 = tk.Entry(root, textvariable=entry_text)
    input_box1.grid(row=0, column=1, padx=5, pady=5)
    
    label2 = tk.Label(root, text="每段字符输入间隔时间(s)")
    label2.grid(row=1, column=0, padx=5, pady=5)
    # 创建一个输入框
    entry_text = tk.StringVar(value="1")
    input_box2 = tk.Entry(root, textvariable=entry_text)
    input_box2.grid(row=1, column=1, padx=5, pady=5)

    label2 = tk.Label(root, text="模拟键盘输入文本：")
    label2.grid(row=2, column=0, padx=5, pady=5)
    # 创建一个列表输入框
    entries = create_single_column_table(root, 3, 5)

    button = tk.Button(root, text="开始", width=15)
    button.grid(row=8, column=1, padx=5, pady=5)
    button.config(command=on_click)

    # 设置窗口大小
    root.geometry("450x400")
    root.mainloop()
