import cx_Freeze

executables = [cx_Freeze.Executable("D:/WorkCode/python/keyboardUI.py")]

cx_Freeze.setup(
    name="键盘模拟输入 — designed by luguosheng",
    version="1.0",
    description="My Python script",
    executables=executables
)
