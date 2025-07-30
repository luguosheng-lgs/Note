from PIL import Image
import os
from pdf2image import convert_from_path
import os

def pdf_to_images(pdf_path: str, output_dir: str, dpi=200, fmt='png'):
    """
    将PDF文件转换为多张图片
    :param pdf_path: PDF文件路径
    :param output_dir: 图片输出目录
    :param dpi: 输出分辨率（默认200 DPI）
    :param fmt: 图片格式（默认png，可选 jpeg）
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 转换PDF为图片列表
    images = convert_from_path(
        pdf_path=pdf_path,
        dpi=dpi,
        output_folder=output_dir,
        fmt=fmt,
        output_file="page"  # 输出文件名前缀
    )
    
    # 获取实际保存的文件路径
    output_files = [os.path.join(output_dir, f"page_{i+1}.{fmt}") 
                   for i in range(len(images))]
    
    print(f"转换完成! 共生成 {len(images)} 张图片:")
    for file in output_files:
        print(f"  - {file}")
    
    return output_files
def convert_pngs_to_pdf(input_paths: list, output_path: str):
    """
    将多张PNG图片合并输出到一个PDF文件
    :param input_paths: PNG图片路径列表
    :param output_path: 输出的PDF文件路径

    该功能依赖:https://github.com/oschwartz10612/poppler-windows/releases/tag/v24.08.0-0
    """
    images = []
    
    # 打开所有图片并转换为RGB模式
    for path in input_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"图片不存在: {path}")
            
        img = Image.open(path)
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        images.append(img)
    
    # 将第一张图片保存为PDF，并附加其余图片
    images[0].save(
        output_path, "PDF", resolution=400.0,
        save_all=True, append_images=images[1:]
    )

# 使用示例 - 将8张图片合并为单个PDF
if __name__ == "__main__":
    # 替换为你的8张图片路径
    png_files = [
        "E:/Desktop/陆国生-住房补助申请资料/page0001-1.png",
        "E:/Desktop/陆国生-住房补助申请资料/page0001-2.png",
        "E:/Desktop/陆国生-住房补助申请资料/page0001-3.png",
        "E:/Desktop/陆国生-住房补助申请资料/page0001-4.png",
        "E:/Desktop/陆国生-住房补助申请资料/page0001-5.png",
        "E:/Desktop/陆国生-住房补助申请资料/page0001-6.png",
        "E:/Desktop/陆国生-住房补助申请资料/page0001-7.png",
        "E:/Desktop/陆国生-住房补助申请资料/page0001-8.png"
    ]
    
    output_pdf = "combined_output.pdf"  # 输出PDF路径
    
    convert_pngs_to_pdf(png_files, output_pdf)
    print(f"转换完成! 8张图片已合并保存至: {output_pdf}")
    # 输入PDF路径
    # input_pdf = "E:/Desktop/陆国生-住房补助申请资料/a.pdf"  # 替换为你的PDF文件
    
    # # 输出目录
    # output_directory = "E:/Desktop/陆国生-住房补助申请资料/output"  # 图片保存目录
    
    # # 执行转换（可调整参数）
    # pdf_to_images(
    #     pdf_path=input_pdf,
    #     output_dir=output_directory,
    #     dpi=300,  # 提高分辨率
    #     fmt='png'  # 输出格式
    # )