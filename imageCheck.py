from ast import Or
import numpy as np
import os

class ChunkCheckInfo:
    def __init__(self):
        self.check_state = 0
        self.pos_x = 0
        self.pos_y = 0
        self.value_v = 0
        self.value_u = 0

def check_frame_data_crash_rowbar_columnbar_edgecolourcast(
    image_path: str, 
    image_width: int, 
    image_height: int, 
    rowSampleNum: int, 
    columnSampleNum: int
) -> int:
    """
    检测图像中的花屏、横竖条纹和边缘偏色问题
    参数:
        image_path: YV12格式的图像文件路径
        image_width: 图像宽度
        image_height: 图像高度
        rowSampleNum: 横条检测采样行数
        columnSampleNum: 竖条检测采样列数
    返回:
        错误码 (0=正常, 负值=异常)
    """
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"错误: 文件不存在 - {image_path}")
        return -100
    
    # 读取图像文件内容
    with open(image_path, 'rb') as f:
        pFrameBuf = f.read()
    
    # 将字节数据转换为numpy数组便于处理
    y_size = image_width * image_height
    uv_size = y_size // 4
    total_size = y_size + 2 * uv_size
    
    # 检查文件大小是否匹配
    if len(pFrameBuf) < total_size:
        print(f"错误: 文件大小不足，预期 {total_size} 字节，实际 {len(pFrameBuf)} 字节")
        return -101
    
    y_plane = np.frombuffer(pFrameBuf[:y_size], dtype=np.uint8).reshape((image_height, image_width))
    v_plane = np.frombuffer(pFrameBuf[y_size:y_size+uv_size], dtype=np.uint8).reshape((image_height//2, image_width//2))
    u_plane = np.frombuffer(pFrameBuf[y_size+uv_size:y_size+2*uv_size], dtype=np.uint8).reshape((image_height//2, image_width//2))

    # ------------------------ 横条检测 ------------------------
    row_total = rowSampleNum
    row_base = image_height // rowSampleNum
    column_total = image_width
    chunkCheckInfo = [[ChunkCheckInfo() for _ in range(column_total)] for _ in range(row_total)]
    
    iRet = 0
    row_check_fail_num = 0
    row_crash_check_fail_num = 0
    row_colourcast_check_fail_num = 0

    y_plane = np.frombuffer(pFrameBuf[:y_size], dtype=np.uint8).astype(np.int16).reshape((image_height, image_width))
    v_plane = np.frombuffer(pFrameBuf[y_size:y_size+uv_size], dtype=np.uint8).astype(np.int16).reshape((image_height//2, image_width//2))
    u_plane = np.frombuffer(pFrameBuf[y_size+uv_size:y_size+2*uv_size], dtype=np.uint8).astype(np.int16).reshape((image_height//2, image_width//2))

    for row in range(row_total):
        # 跳过第一行
        if row == 0:
            continue
        row_pixel_crash_fail = 0
        row_pixel_colourcast_fail = 0
        
        for col in range(column_total - 1):
            if col == 0:
                continue
            # 获取当前采样行的Y值
            y_row = row * row_base
            y_val = y_plane[y_row, col]
            y_val_next = y_plane[y_row, col + 1]
            
            # 花屏检测: 相邻像素Y值差异≥5
            if abs(y_val_next - y_val) >= 5:
                row_pixel_crash_fail += 1
                chunkCheckInfo[row][col].check_state = -1
                chunkCheckInfo[row][col + 1].check_state = -1
            
            # 获取UV值 (注意UV平面尺寸减半)
            uv_row = y_row // 2
            uv_col = col // 2
            v_val = v_plane[uv_row, uv_col]
            v_val_next = v_plane[uv_row, (col + 1) // 2]
            u_val = u_plane[uv_row, uv_col]
            u_val_next = u_plane[uv_row, (col + 1) // 2]
            
            # 偏色检测: 相邻像素UV值差异≥5
            if abs(v_val_next - v_val) >= 5 or abs(u_val_next - u_val) >= 5:
                row_pixel_colourcast_fail += 1
            
            # 记录UV值用于边缘检测
            chunkCheckInfo[row][col].value_v = v_val
            chunkCheckInfo[row][col].value_u = u_val
            chunkCheckInfo[row][col + 1].value_v = v_val_next
            chunkCheckInfo[row][col + 1].value_u = u_val_next
        
        # 行失败判断
        if row_pixel_crash_fail >= column_total // 5:
            row_crash_check_fail_num += 1
            row_check_fail_num += 1
            iRet = -1
        elif row_pixel_colourcast_fail >= column_total // 5:
            row_colourcast_check_fail_num += 1
            row_check_fail_num += 1
            iRet = -21

    # 横条检测结果分析
    if row_check_fail_num == 0:
        # 检查竖条纹
        for col in range(column_total):
            fail_count = sum(1 for row in range(row_total) 
                          if chunkCheckInfo[row][col].check_state == -1)
            if fail_count >= (row_total * 2) // 3:
                iRet = -2
                break
        
        # 检查边缘偏色
        if iRet == 0:
            left_fail = right_fail = 0
            for row in range(row_total):
                mid_col = column_total // 2
                left_v = chunkCheckInfo[row][1].value_v
                left_u = chunkCheckInfo[row][1].value_u
                mid_v = chunkCheckInfo[row][mid_col].value_v
                mid_u = chunkCheckInfo[row][mid_col].value_u
                right_v = chunkCheckInfo[row][-1].value_v
                right_u = chunkCheckInfo[row][-1].value_u
                
                if abs(left_v - mid_v) >= 40 or abs(left_u - mid_u) >= 40:
                    print("left fail", left_v , mid_v, left_u, mid_u)
                    left_fail += 1
                if abs(right_v - mid_v) >= 40 or abs(right_u - mid_u) >= 40:
                    right_fail += 1
            
            if left_fail >= row_total * 2 // 3:
                iRet = -11
            elif right_fail >= row_total * 2 // 3:
                iRet = -12
    else:
        if row_crash_check_fail_num >= rowSampleNum * 2 // 3:
            iRet = -3
        elif row_colourcast_check_fail_num >= rowSampleNum * 2 // 3:
            iRet = -23

    # ------------------------ 竖条检测 ------------------------
    row_total = image_height
    column_total = columnSampleNum
    column_base = image_width // columnSampleNum
    chunkCheckInfo = [[ChunkCheckInfo() for _ in range(column_total)] for _ in range(row_total)]
    
    col_check_fail_num = 0
    col_crash_check_fail_num = 0
    col_colourcast_check_fail_num = 0

    y_plane = y_plane.astype(np.int16)  # 确保后续使用int16
    v_plane = v_plane.astype(np.int16)
    u_plane = u_plane.astype(np.int16)

    for col in range(column_total):
        # 跳过第一列
        if col == 0:
            continue
        col_pixel_crash_fail = 0
        col_pixel_colourcast_fail = 0
        col_pos = col * column_base
        
        for row in range(row_total - 1):
            
            if row == 0:
                continue
            # 获取当前采样列的Y值
            y_val = y_plane[row, col_pos]
            y_val_next = y_plane[row + 1, col_pos]
            
            # 花屏检测
            if abs(y_val_next - y_val) >= 5:
                col_pixel_crash_fail += 1
                chunkCheckInfo[row][col].check_state = -1
                chunkCheckInfo[row + 1][col].check_state = -1
            
            # 获取UV值
            uv_row = row // 2
            uv_col = col_pos // 2
            v_val = v_plane[uv_row, uv_col]
            v_val_next = v_plane[(row + 1) // 2, uv_col]
            u_val = u_plane[uv_row, uv_col]
            u_val_next = u_plane[(row + 1) // 2, uv_col]
            
            # 偏色检测 (竖条检测阈值40)
            if abs(v_val_next - v_val) >= 40 or abs(u_val_next - u_val) >= 40:
                col_pixel_colourcast_fail += 1
            
            # 记录UV值
            chunkCheckInfo[row][col].value_v = v_val
            chunkCheckInfo[row][col].value_u = u_val
            chunkCheckInfo[row + 1][col].value_v = v_val_next
            chunkCheckInfo[row + 1][col].value_u = u_val_next
        
        # 列失败判断
        if col_pixel_crash_fail >= row_total // 5:
            col_crash_check_fail_num += 1
            col_check_fail_num += 1
            iRet = -4
        elif col_pixel_colourcast_fail >= row_total // 5:
            col_colourcast_check_fail_num += 1
            col_check_fail_num += 1
            iRet = -24

    # 竖条检测结果分析
    if col_check_fail_num == 0:
        # 检查横条纹
        for row in range(row_total):
            fail_count = sum(1 for col in range(column_total) 
                          if chunkCheckInfo[row][col].check_state == -1)
            if fail_count >= (column_total * 2) // 3:
                iRet = -5
                break
        
        # 检查边缘偏色
        if iRet == 0:
            up_fail = down_fail = 0
            for col in range(column_total):
                mid_row = row_total // 2
                up_v = chunkCheckInfo[1][col].value_v
                up_u = chunkCheckInfo[1][col].value_u
                mid_v = chunkCheckInfo[mid_row][col].value_v
                mid_u = chunkCheckInfo[mid_row][col].value_u
                down_v = chunkCheckInfo[-1][col].value_v
                down_u = chunkCheckInfo[-1][col].value_u
                
                if abs(up_v - mid_v) >= 40 or abs(up_u - mid_u) >= 40:
                    up_fail += 1
                if abs(down_v - mid_v) >= 40 or abs(down_u - mid_u) >= 40:
                    down_fail += 1
            
            if up_fail >= column_total * 2 // 3:
                iRet = -13
            elif down_fail >= column_total * 2 // 3:
                iRet = -14
    else:
        if col_crash_check_fail_num >= columnSampleNum * 2 // 3:
            iRet = -6
        elif col_colourcast_check_fail_num >= columnSampleNum * 2 // 3:
            iRet = -26
    return iRet

# 打印yv12图像指定行或列的Y值
def print_yv12_row_or_column(image_path, image_width, image_height, row_or_column, is_row=True):
    """
    打印指定行或列的Y值
    参数:
        image_path: YV12格式的图像文件路径
        image_width: 图像宽度
        image_height: 图像高度
        row_or_column: 要打印的行或列索引
        is_row: True表示打印行，False表示打印列
    """
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"错误: 文件不存在 - {image_path}")
        return -100
    
    # 读取图像文件内容
    with open(image_path, 'rb') as f:
        pFrameBuf = f.read()
    
    # 计算各平面大小
    y_size = image_width * image_height
    uv_size = y_size // 4
    total_size = y_size + 2 * uv_size
    
    # 检查文件大小是否匹配
    if len(pFrameBuf) < total_size:
        print(f"错误: 文件大小不足，预期 {total_size} 字节，实际 {len(pFrameBuf)} 字节")
        return -101
    
    # 提取Y平面数据
    y_plane = np.frombuffer(pFrameBuf[:y_size], dtype=np.uint8).astype(np.int16).reshape((image_height, image_width))
    
    if is_row:
        # 打印指定行的Y值
        if row_or_column >= image_height:
            print(f"错误: 行索引 {row_or_column} 超出范围 (0-{image_height-1})")
            return
        print(f"第 {row_or_column} 行的Y值:")
        print(y_plane[row_or_column])
        #遍历y_plane[row_or_column]，打印相邻像素的差值大于5的像素
        for i in range(image_width-1):
            if abs(y_plane[row_or_column][i] - y_plane[row_or_column][i+1]) >= 5:
                print(f"差值大于5的 {i} 的Y值: {y_plane[row_or_column][i]} {y_plane[row_or_column][i+1]}")
    else:
        # 打印指定列的Y值
        if row_or_column >= image_width:
            print(f"错误: 列索引 {row_or_column} 超出范围 (0-{image_width-1})")
            return
        print(f"第 {row_or_column} 列的Y值:")
        print(y_plane[:, row_or_column])
        #遍历y_plane[:, row_or_column]，打印相邻像素的差值大于5的像素
        for i in range(image_height-1):
            if abs(y_plane[i][row_or_column] - y_plane[i+1][row_or_column]) >= 5:
                print(f"差值大于5的 {i} 的Y值: {y_plane[i][row_or_column]} {y_plane[i+1][row_or_column]}")

    
    
if __name__ == "__main__":
    image_path = 'E:/Desktop/联调日志/1号机/image/[07-29_17.38.52]_[3]_[I2530Q003627TB53Q52]_Image_800x448.yv12'
    image_width = 800
    image_height = 448
    rowSampleNum = 6
    columnSampleNum = 6
    ret = check_frame_data_crash_rowbar_columnbar_edgecolourcast(image_path, image_width, image_height, rowSampleNum, columnSampleNum)
    print(f"图像检测结果：{ret}" )
    if ret == -1 or ret == -3 or ret == -4 or ret == -6:
        print("花屏异常")
    elif ret == -2:
        print("竖条纹异常")
    elif ret == -5:
        print("横条纹异常")
    elif ret == -11:
        print("左边缘偏色异常")
    elif ret == -12:
        print("右边缘偏色异常")
    elif ret == -13:
        print("上边缘偏色异常")
    elif ret == -14:
        print("下边缘偏色异常")
    elif ret == -21 or ret == -23 or ret == -24 or ret == -26:
        print("偏色异常")
    elif ret == 0:
        print("图像正常")
    else:
        print("未知错误")

    # 打印指定行的Y值
    print_yv12_row_or_column(image_path, image_width, image_height, 9, is_row=True)