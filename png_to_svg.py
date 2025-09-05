import os
import sys
from PIL import Image
import potrace

def png_to_svg(input_path, output_path=None, threshold=128):
    """
    将PNG图片转换为SVG矢量图
    
    参数:
        input_path: 输入PNG文件路径
        output_path: 输出SVG文件路径，默认为输入路径替换为.svg
        threshold: 二值化阈值，范围0-255，默认为128
    """
    # 验证输入文件
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")
    
    if not input_path.lower().endswith('.png'):
        raise ValueError("输入文件必须是PNG格式")
    
    # 确定输出路径
    if output_path is None:
        file_name = os.path.splitext(input_path)[0]
        output_path = f"{file_name}.svg"
    
    try:
        # 打开图片并转换为灰度图
        with Image.open(input_path) as img:
            # 转换为灰度图像
            img_gray = img.convert('L')
            
            # 二值化处理（将图像转为黑白）
            img_binary = img_gray.point(lambda x: 0 if x < threshold else 255, '1')
            
            # 获取图像数据
            width, height = img_binary.size
            data = img_binary.tobytes()
            
            # 创建Potrace位图对象
            bitmap = potrace.Bitmap(width, height, data)
            
            # 进行矢量跟踪
            path = bitmap.trace()
            
            # 生成SVG内容
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n')
                
                # 遍历所有曲线并写入SVG路径
                for curve in path:
                    f.write('  <path d="')
                    first = True
                    for segment in curve:
                        if segment.is_corner:
                            # 角点
                            x0, y0 = segment.c0
                            x1, y1 = segment.c1
                            x2, y2 = segment.end_point
                            if first:
                                f.write(f'M {x0} {y0} L {x1} {y1} L {x2} {y2}')
                                first = False
                            else:
                                f.write(f' L {x1} {y1} L {x2} {y2}')
                        else:
                            # 曲线段
                            x0, y0 = segment.c0
                            x1, y1 = segment.c1
                            x2, y2 = segment.c2
                            x3, y3 = segment.end_point
                            if first:
                                f.write(f'M {x0} {y0} C {x1} {y1}, {x2} {y2}, {x3} {y3}')
                                first = False
                            else:
                                f.write(f' C {x1} {y1}, {x2} {y2}, {x3} {y3}')
                    f.write('" fill="black"/>\n')
                
                f.write('</svg>')
        
        return output_path
    
    except Exception as e:
        raise RuntimeError(f"转换失败: {str(e)}")

def main():
    if len(sys.argv) < 2:
        print("用法: python png_to_svg.py <input_png_file> [output_svg_file] [threshold]")
        print("示例: python png_to_svg.py image.png output.svg 128")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 128
    
    try:
        output_path = png_to_svg(input_file, output_file, threshold)
        print(f"成功转换为SVG文件: {os.path.abspath(output_path)}")
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    