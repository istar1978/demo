import os
import sys
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes

def generate_key(key_size=16):
    """生成指定长度的随机密钥"""
    return get_random_bytes(key_size)

def encrypt_content(content, key):
    """使用AES-CBC模式加密内容"""
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(content.encode('utf-8'), AES.block_size))
    
    # 返回IV和加密内容的Base64编码
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    
    return iv, ct

def encrypt_html_file(input_path, output_path=None, key=None):
    """
    加密HTML文件
    
    参数:
        input_path: 输入HTML文件路径
        output_path: 输出加密文件路径，默认为输入路径加".encrypted.html"
        key: 加密密钥，如不提供则自动生成
    """
    # 生成或使用提供的密钥
    if key is None:
        key = generate_key()
    elif len(key) not in [16, 24, 32]:
        raise ValueError("密钥长度必须为16、24或32字节")
    
    # 读取HTML内容
    with open(input_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 加密内容
    iv, encrypted_content = encrypt_content(html_content, key)
    
    # 生成解密所需的JavaScript代码
    decrypt_js = f"""<script>
    // 解密脚本 - 会在页面加载时自动执行
    (function() {{
        // 加密参数
        const key = atob("{base64.b64encode(key).decode('utf-8')}");
        const iv = atob("{iv}");
        const encryptedData = atob("{encrypted_content}");
        
        // AES-CBC解密实现
        async function decrypt() {{
            // 将密钥和IV转换为CryptoJS所需格式
            const keyBytes = Uint8Array.from([...key].map(c => c.charCodeAt(0)));
            const ivBytes = Uint8Array.from([...iv].map(c => c.charCodeAt(0)));
            const dataBytes = Uint8Array.from([...encryptedData].map(c => c.charCodeAt(0)));
            
            // 导入密钥
            const cryptoKey = await crypto.subtle.importKey(
                "raw",
                keyBytes,
                {{ name: "AES-CBC" }},
                false,
                ["decrypt"]
            );
            
            // 解密
            const decrypted = await crypto.subtle.decrypt(
                {{ name: "AES-CBC", iv: ivBytes }},
                cryptoKey,
                dataBytes
            );
            
            // 将解密结果转换为字符串
            return new TextDecoder().decode(decrypted);
        }}
        
        // 执行解密并替换页面内容
        decrypt().then(html => {{
            // 替换整个文档
            document.open();
            document.write(html);
            document.close();
        }}).catch(error => {{
            document.body.innerHTML = "<h1>解密失败</h1><p>无法解密页面内容: " + error.message + "</p>";
            console.error("解密错误:", error);
        }});
    }})();
    </script>"""
    
    # 确定输出路径
    if output_path is None:
        file_name, file_ext = os.path.splitext(input_path)
        output_path = f"{file_name}.encrypted{file_ext}"
    
    # 写入加密后的文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(decrypt_js)
    
    # 返回密钥（如果是自动生成的）
    return key if key is not None else None

def main():
    if len(sys.argv) < 2:
        print("用法: python html_encryptor.py <input_html_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        key = encrypt_html_file(input_file, output_file)
        print(f"文件已成功加密并保存至: {output_file or input_file.replace('.html', '.encrypted.html')}")
        print(f"加密密钥 (请妥善保存，如需再次加密相同内容时使用): {base64.b64encode(key).decode('utf-8')}")
    except Exception as e:
        print(f"加密失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
