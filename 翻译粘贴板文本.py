# 通过快捷键`ctrl + t`,将剪贴板中的文本翻译为英文并复制到剪贴板中
import pyperclip
import keyboard
from googletrans import Translator
from pynput import keyboard

def translate_clipboard():
    try:
        # 获取剪贴板内容
        text = pyperclip.paste()
        
        # 翻译逻辑
        translator = Translator()
        translated = translator.translate(text, dest='en').text
        
        # 回写剪贴板
        pyperclip.copy(translated)
        print("翻译成功！")
    except Exception as e:
        print(f"翻译失败: {str(e)}")


def on_activate():
    translate_clipboard()

hotkey = keyboard.HotKey(
    keyboard.HotKey.parse('<ctrl>+t'),
    on_activate
)

with keyboard.Listener(on_press=hotkey.press) as listener:
    listener.join()