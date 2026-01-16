"""
测试OCR到区块链集成
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_environment():
    """测试环境配置"""
    print("="*60)
    print("测试环境配置")
    print("="*60)
    
    required_vars = {
        'PINATA_API_KEY': '必需 - Pinata API密钥',
        'PINATA_SECRET_KEY': '必需 - Pinata密钥',
        'CONTRACT_ADDRESS': '可选 - 智能合约地址（用于铸造NFT）',
        'PRIVATE_KEY': '可选 - 钱包私钥（用于铸造NFT）'
    }
    
    missing = []
    optional_missing = []
    
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            masked = value[:8] + '...' if len(value) > 8 else '***'
            print(f"✅ {var}: {masked}")
        else:
            if '必需' in desc:
                missing.append(var)
                print(f"❌ {var}: 未设置 - {desc}")
            else:
                optional_missing.append(var)
                print(f"⚠️  {var}: 未设置 - {desc}")
    
    print()
    
    if missing:
        print(f"❌ 缺少必需的环境变量: {', '.join(missing)}")
        print("请在.env文件中配置这些变量")
        return False
    
    if optional_missing:
        print(f"⚠️  未配置可选变量: {', '.join(optional_missing)}")
        print("如果需要铸造NFT，请配置这些变量")
    
    print("✅ 环境配置检查通过！")
    return True


def test_pinata_connection():
    """测试Pinata连接"""
    print("\n" + "="*60)
    print("测试Pinata连接")
    print("="*60)
    
    try:
        import requests
        
        api_key = os.getenv('PINATA_API_KEY')
        secret_key = os.getenv('PINATA_SECRET_KEY')
        
        if not api_key or not secret_key:
            print("❌ Pinata密钥未配置")
            return False
        
        url = 'https://api.pinata.cloud/data/testAuthentication'
        headers = {
            'pinata_api_key': api_key,
            'pinata_secret_api_key': secret_key
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Pinata连接成功！")
            print(f"响应: {response.json()}")
            return True
        else:
            print(f"❌ Pinata认证失败: {response.status_code}")
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试Pinata连接时出错: {e}")
        return False


def test_ocr_files():
    """检查OCR文件"""
    print("\n" + "="*60)
    print("检查OCR结果文件")
    print("="*60)
    
    outputs_dir = 'outputs'
    
    if not os.path.exists(outputs_dir):
        print(f"❌ 输出目录不存在: {outputs_dir}")
        return False
    
    result_files = [f for f in os.listdir(outputs_dir) if f.endswith('_result.json')]
    
    if not result_files:
        print(f"⚠️  未找到OCR结果文件（*_result.json）")
        print("请先运行OCR识别生成结果文件")
        return False
    
    print(f"✅ 找到 {len(result_files)} 个OCR结果文件")
    print(f"最新的文件: {sorted(result_files)[-1]}")
    
    return True


def test_blockchain_setup():
    """测试区块链设置"""
    print("\n" + "="*60)
    print("测试区块链设置")
    print("="*60)
    
    contract_address = os.getenv('CONTRACT_ADDRESS')
    private_key = os.getenv('PRIVATE_KEY')
    
    if not contract_address:
        print("⚠️  CONTRACT_ADDRESS未设置")
        print("如果不铸造NFT，可以跳过此步骤")
        return False
    
    if not private_key:
        print("⚠️  PRIVATE_KEY未设置")
        print("需要私钥才能铸造NFT")
        return False
    
    print(f"✅ 合约地址: {contract_address}")
    print(f"✅ 私钥已配置")
    
    # 检查Hardhat配置
    if os.path.exists('hardhat.config.js'):
        print("✅ Hardhat配置文件存在")
    else:
        print("⚠️  Hardhat配置文件不存在")
    
    # 检查部署脚本
    if os.path.exists('scripts/mintFromOCR.js'):
        print("✅ 铸造脚本存在")
    else:
        print("❌ 铸造脚本不存在")
        return False
    
    return True


def test_import_modules():
    """测试Python模块导入"""
    print("\n" + "="*60)
    print("测试Python模块")
    print("="*60)
    
    modules = {
        'paddleocr': 'PaddleOCR',
        'flask': 'Flask',
        'requests': 'Requests',
        'dotenv': 'python-dotenv',
        'cv2': 'OpenCV'
    }
    
    missing = []
    
    for module, name in modules.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - 未安装")
            missing.append(name)
    
    if missing:
        print(f"\n❌ 缺少模块: {', '.join(missing)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("\n✅ 所有Python模块已安装！")
    return True


def run_integration_test():
    """运行集成测试"""
    print("\n" + "="*60)
    print("运行集成测试")
    print("="*60)
    
    try:
        from ocr_to_blockchain import OCRBlockchainBridge
        
        print("✅ OCRBlockchainBridge模块导入成功")
        
        bridge = OCRBlockchainBridge()
        print("✅ OCRBlockchainBridge实例化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("OCR到区块链集成 - 系统测试")
    print("="*80 + "\n")
    
    tests = [
        ("环境配置", test_environment),
        ("Python模块", test_import_modules),
        ("Pinata连接", test_pinata_connection),
        ("OCR文件", test_ocr_files),
        ("区块链设置", test_blockchain_setup),
        ("集成测试", run_integration_test)
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ {name}测试异常: {e}")
            results[name] = False
    
    # 总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统已准备就绪。")
        print("\n下一步:")
        print("1. 运行 'python app.py' 启动Web服务")
        print("2. 或运行 'python ocr_to_blockchain.py <result.json>' 处理单个文件")
        print("3. 或运行 'python batch_process.py batch' 批量处理")
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息")
        print("参考 OCR_BLOCKCHAIN_INTEGRATION.md 获取帮助")
        sys.exit(1)


if __name__ == "__main__":
    main()
