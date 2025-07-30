import os
import psutil
import time


# 打印各个CPU的占用率
while True:
    # 获取CPU核心数·
    cpu_count = os.cpu_count()

    # 获取CPU占用率列表
    cpu_percentages = psutil.cpu_percent(interval=1, percpu=True)
    for i, cpu_percentage in enumerate(cpu_percentages):
        print(f"CPU {i}: {cpu_percentage}%")
    
    print(" ")
    print(" ")
    
    print("================================")
    # 休眠1秒
    time.sleep(1)
