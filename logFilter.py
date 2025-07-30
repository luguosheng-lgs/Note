# python 删除指定文件的指定行后的数据

import os

def remove_after_line(file_path, line_number):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    with open(file_path, 'w') as f:
        for i, line in enumerate(lines):
            if i >= line_number:
                break
            f.write(line)
# 函数，判断文件中的行是否包含某些字符串，包含则输出到新文件中
def filter_file(file_path, keywords):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    with open(file_path + '.filter', 'w') as f:
        for line in lines:
            if any(keyword in line for keyword in keywords):
                f.write(line)
# 函数，判断文件中的行是否包含某些字符串，包含则删除该行
def filter_file_delete(file_path, keywords):
    #with open(file_path, 'r') as f:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    with open(file_path + '.filter', 'w') as f:
        for line in lines:
            if not any(keyword in line for keyword in keywords):
                f.write(line)
# 函数，遍历文件中的行，如果当前行与下一行含有指定字符串，则删除下一行
def filter_file_delete_next_line(file_path, keywords):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    with open(file_path, 'w') as f:
        for i, line in enumerate(lines):
            if i >= len(lines) - 1:
                break
            if not any(keyword in line for keyword in keywords):
                f.write(line)
            if any(keyword in lines[i+1] for keyword in keywords):
                f.write(line)

# 函数，遍历文件中的行，对连续行均包含关键字的行只保留第一行
def filter_file_delete_duplicate(file_path, keyword, output_path=None):
    """
    过滤文件中连续包含关键字的行（只保留第一行），并将结果保存到文件
    
    :param file_path: 输入文件路径
    :param keyword: 需要检测的关键字
    :param output_path: 输出文件路径（默认覆盖原文件）
    """
    result_lines = []
    last_has_keyword = False
    
    # 读取并过滤文件
    with open(file_path, 'r') as file:
    #with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 检查是否包含任意关键字
            current_has_keyword = any(k in line for k in keywords)
            
            if current_has_keyword and last_has_keyword:
                continue
            print(line)
            result_lines.append(line)
            last_has_keyword = current_has_keyword
    
    # 确定输出路径（默认覆盖原文件）
    save_path = output_path if output_path else file_path
    
    # 将结果写回文件
    with open(save_path, 'w', encoding='utf-8') as out_file:
        out_file.writelines(result_lines)

def calculate_pause_resume_times(file_path):
    """
    计算日志文件中每个恢复信号与上一个暂停信号之间的时间差，并计算总耗时
    
    :param file_path: 日志文件路径
    :return: (总耗时(秒), 时间差列表)
    """
    # 时间格式转换函数
    def parse_log_time(time_str):
        """将日志时间字符串转换为datetime对象"""
        # 示例字符串: "23/06 14:37:58.140"
        day_month, time_part = time_str.split()
        hour, minute, second_ms = time_part.split(':')
        second, ms = second_ms.split('.')
        return datetime(2025, 6, int(day_month.split('/')[0]), 
                        int(hour), int(minute), int(second), int(ms)*1000)

    # 初始化变量
    total_duration = 0.0
    pause_times = []  # 存储暂停时间
    time_diffs = []   # 存储每个时间差
    last_pause_time = None
    
    # 正则表达式匹配时间戳
    time_pattern = re.compile(r'\[(\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\]')
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 提取时间戳
            time_match = time_pattern.search(line)
            if not time_match:
                continue
                
            timestamp = time_match.group(1)
            current_time = parse_log_time(timestamp)
            
            # 检测暂停信号
            if 'detect PLC Pause siganl' in line:
                last_pause_time = current_time
                pause_times.append(current_time)
            
            # 检测恢复信号
            elif 'detect PLC resume siganl' in line and last_pause_time:
                time_diff = (current_time - last_pause_time).total_seconds()
                time_diffs.append(time_diff)
                total_duration += time_diff
                last_pause_time = None  # 重置暂停时间
    
    return total_duration, time_diffs

if __name__ == "__main__":
    # 指定要删除的文件路径
    file_path = 'E:/Desktop/联调日志/2号机/07-22-测试日志.txt.filter'
    # 指定要删除的行数
    line_number = 35226
    # remove_after_line(file_path, line_number)

    #调用filter_file函数，将包含指定字符串的行输出到新文件中
    keywords = ['失败']
    #filter_file(file_path, keywords)

    #filter_file_delete(file_path, keywords)

    filter_file_delete_duplicate(file_path, keywords)