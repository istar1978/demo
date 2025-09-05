import os
import sys
import base64

def get_image_mime_type(file_path):
    """获取图片文件的MIME类型"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.png']:
        return 'image/png'
    elif ext in ['.jpg', '.jpeg']:
        return 'image/jpeg'
    else:
        raise ValueError(f"不支持的图片格式: {ext}，仅支持PNG和JPG")

def image_to_base64(file_path):
    """将图片文件转换为Base64编码字符串"""
    try:
        with open(file_path, 'rb') as image_file:
            # 读取图片内容并转换为Base64
            base64_str = base64.b64encode(image_file.read()).decode('utf-8')
            # 获取MIME类型
            mime_type = get_image_mime_type(file_path)
            # 返回完整的data URI
            return f"data:{mime_type};base64,{base64_str}"
    except Exception as e:
        raise IOError(f"读取图片文件失败: {str(e)}")

def generate_html_with_image(image_paths, output_path=None, title="图片展示"):
    """
    生成包含Base64嵌入图片的HTML文件
    
    参数:
        image_paths: 图片文件路径列表，可以是单个路径或多个路径
        output_path: 输出HTML文件路径，默认为当前目录下的images.html
        title: HTML页面标题
    """
    # 确保image_paths是列表
    if isinstance(image_paths, str):
        image_paths = [image_paths]
    
    # 验证所有文件是否存在
    for path in image_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"图片文件不存在: {path}")
    
    # 生成图片标签
    image_tags = []
    for path in image_paths:
        base64_data = image_to_base64(path)
        # 获取文件名作为alt文本
        alt_text = os.path.basename(path)
        # 添加图片标签，设置响应式样式
        image_tags.append(f'<img src="{base64_data}" alt="{alt_text}" style="max-width: 100%; height: auto; margin: 10px 0;">')
    
    # HTML模板
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="images-container">
            {''.join(image_tags)}
        </div>
    </div>
</body>
</html>"""
    
    # 确定输出路径
    if output_path is None:
        output_path = "images.html"
    else:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    # 写入HTML文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    return output_path

def main():
    if len(sys.argv) < 2:
        print("用法: python image_to_html.py <图片路径1> [图片路径2] ... [输出HTML路径]")
        print("示例: python image_to_html.py image1.png image2.jpg output.html")
        sys.exit(1)
    
    # 分离输入图片路径和输出路径
    # 如果最后一个参数以.html结尾，则视为输出路径
    if sys.argv[-1].lower().endswith('.html'):
        image_paths = sys.argv[1:-1]
        output_path = sys.argv[-1]
    else:
        image_paths = sys.argv[1:]
        output_path = None
    
    if not image_paths:
        print("请至少提供一个图片文件路径")
        sys.exit(1)
    
    try:
        output_file = generate_html_with_image(image_paths, output_path)
        print(f"成功生成HTML文件: {os.path.abspath(output_file)}")
    except Exception as e:
        print(f"处理失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
