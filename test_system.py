#!/usr/bin/env python3
"""
测试增强版OCR-to-Blockchain系统
"""

import sys
import os
import json

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_blockchain_bridge():
    """测试区块链桥接功能"""
    print("🧪 测试区块链桥接...")
    
    try:
        from ocr_to_blockchain import OCRBlockchainBridge
        bridge = OCRBlockchainBridge()
        print("✅ 区块链桥接初始化成功")
        
        # 测试IPFS上传
        test_data = {
            "bill_number": "TEST123",
            "vessel": "TEST SHIP",
            "test": True
        }
        
        print("🔄 测试IPFS上传...")
        result = bridge.upload_json_to_pinata(test_data, "test-bill")
        
        if result and 'IpfsHash' in result:
            print(f"✅ IPFS上传成功: {result['IpfsHash']}")
            print(f"🌐 IPFS链接: https://gateway.pinata.cloud/ipfs/{result['IpfsHash']}")
            
            # 测试NFT铸造（会失败但能测试脚本调用）
            print("🔄 测试NFT铸造调用...")
            nft_result = bridge.mint_nft_via_hardhat(
                "TEST123", 
                result['IpfsHash'], 
                "test_hash"
            )
            
            print(f"NFT铸造结果: {nft_result}")
        else:
            print(f"❌ IPFS上传失败: {result}")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_ocr_files():
    """检查现有OCR文件"""
    print("\n📁 检查现有OCR文件...")
    
    output_dir = "outputs"
    if not os.path.exists(output_dir):
        print("❌ outputs目录不存在")
        return
    
    ocr_files = [f for f in os.listdir(output_dir) if f.endswith('_result.json')]
    blockchain_files = [f for f in os.listdir(output_dir) if f.endswith('_blockchain.json')]
    
    print(f"📄 OCR结果文件: {len(ocr_files)}")
    print(f"🔗 区块链处理文件: {len(blockchain_files)}")
    print(f"⏳ 待处理文件: {len(ocr_files) - len(blockchain_files)}")

def check_environment():
    """检查环境配置"""
    print("\n🔧 检查环境配置...")
    
    # 检查.env文件
    if os.path.exists('.env'):
        print("✅ .env文件存在")
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ['PINATA_API_KEY', 'PINATA_SECRET_KEY', 'CONTRACT_ADDRESS']
        for var in required_vars:
            value = os.getenv(var)
            if value:
                print(f"✅ {var}: {value[:10]}..." if len(value) > 10 else f"✅ {var}: {value}")
            else:
                print(f"❌ {var}: 未设置")
    else:
        print("❌ .env文件不存在")
    
    # 检查Node.js环境
    print("\n🔧 检查Node.js环境...")
    if os.path.exists('package.json'):
        print("✅ package.json存在")
    else:
        print("❌ package.json不存在")
    
    if os.path.exists('node_modules'):
        print("✅ node_modules存在")
    else:
        print("❌ node_modules不存在，请运行: npm install")

if __name__ == '__main__':
    print("🚀 开始系统测试...")
    print("=" * 50)
    
    check_environment()
    test_ocr_files()
    test_blockchain_bridge()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！")
    print("\n🌐 启动Web服务器:")
    print("   py app_enhanced.py")
    print("\n📖 访问地址:")
    print("   http://localhost:5000")
