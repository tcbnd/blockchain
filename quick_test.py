#!/usr/bin/env python3
"""
快速测试OCR引擎
"""

def test_ocr_engines():
    print("🔍 测试OCR引擎优先级...")
    
    # 测试PaddleOCR
    try:
        print("🔄 测试PaddleOCR...")
        import paddleocr
        ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        print("✅ PaddleOCR可用！")
        return "paddleocr"
    except ImportError as e:
        print(f"❌ PaddleOCR不可用: {e}")
    
    # 测试EasyOCR
    try:
        print("🔄 测试EasyOCR...")
        import easyocr
        reader = easyocr.Reader(['en'])
        print("✅ EasyOCR可用！")
        return "easyocr"
    except ImportError as e:
        print(f"❌ EasyOCR不可用: {e}")
    
    # 测试Tesseract
    try:
        print("🔄 测试Tesseract...")
        import pytesseract
        from PIL import Image
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract可用！版本: {version}")
        return "tesseract"
    except ImportError as e:
        print(f"❌ Tesseract不可用: {e}")
    except Exception as e:
        print(f"❌ Tesseract配置错误: {e}")
    
    print("⚠️ 将使用模拟模式")
    return "mock"

def test_hardhat():
    print("\n🔧 测试Hardhat命令...")
    import subprocess
    import os
    
    # 检查文件存在性
    commands_to_test = [
        ('node_modules\\.bin\\hardhat.cmd', 'Windows批处理文件'),
        ('node_modules\\.bin\\hardhat', 'Unix可执行文件'),
        ('npx hardhat', 'NPX命令')
    ]
    
    for cmd_str, description in commands_to_test:
        if cmd_str.startswith('node_modules'):
            file_path = cmd_str
            if os.path.exists(file_path):
                print(f"✅ {description}: {file_path} 存在")
            else:
                print(f"❌ {description}: {file_path} 不存在")
        else:
            try:
                result = subprocess.run(
                    cmd_str.split() + ['--version'], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if result.returncode == 0:
                    print(f"✅ {description}: 可用")
                    print(f"   版本: {result.stdout.strip()}")
                else:
                    print(f"❌ {description}: 错误 - {result.stderr.strip()}")
            except FileNotFoundError:
                print(f"❌ {description}: 命令未找到")
            except subprocess.TimeoutExpired:
                print(f"⏰ {description}: 命令超时")

if __name__ == '__main__':
    print("🚀 快速系统检查...")
    print("=" * 40)
    
    # 测试OCR
    ocr_engine = test_ocr_engines()
    print(f"\n🎯 最佳可用OCR引擎: {ocr_engine}")
    
    # 测试Hardhat
    test_hardhat()
    
    print("\n" + "=" * 40)
    print("✅ 检查完成！")
