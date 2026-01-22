#!/usr/bin/env python3
"""
测试区块链NFT铸造
"""

import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_nft_minting():
    """测试NFT铸造功能"""
    print("🔄 测试NFT铸造功能...")
    
    try:
        from ocr_to_blockchain import OCRBlockchainBridge
        bridge = OCRBlockchainBridge()
        
        # 测试IPFS上传
        test_data = {
            "bill_number": f"TEST_{int(datetime.now().timestamp())}",
            "vessel": "TEST VESSEL",
            "port_loading": "Test Port",
            "timestamp": datetime.now().isoformat(),
            "test_mode": True
        }
        
        print("🔄 步骤 1/4: 上传到IPFS...")
        ipfs_result = bridge.upload_json_to_pinata(test_data, f"test-bill-{int(datetime.now().timestamp())}")
        
        if ipfs_result and 'IpfsHash' in ipfs_result:
            ipfs_hash = ipfs_result['IpfsHash']
            print(f"✅ IPFS上传成功: {ipfs_hash}")
            print(f"🌐 IPFS链接: https://gateway.pinata.cloud/ipfs/{ipfs_hash}")
            
            # 测试NFT铸造
            print("🔄 步骤 2/4: 铸造NFT...")
            nft_result = bridge.mint_nft_via_hardhat(
                test_data["bill_number"],
                ipfs_hash,
                "test_data_hash"
            )
            
            print(f"\n🔄 NFT铸造结果:")
            print(json.dumps(nft_result, indent=2, ensure_ascii=False))
            
            if nft_result and nft_result.get('success'):
                print("✅ NFT铸造成功！")
                if nft_result.get('explorer_url'):
                    print(f"🌐 交易链接: {nft_result['explorer_url']}")
                if nft_result.get('contract_url'):
                    print(f"📄 合约链接: {nft_result['contract_url']}")
            else:
                print("❌ NFT铸造失败")
                if 'solution' in nft_result:
                    print(f"💡 解决方案: {nft_result['solution']}")
                
        else:
            print(f"❌ IPFS上传失败: {ipfs_result}")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def list_pending_files():
    """列出待处理的OCR文件"""
    print("\n📁 检查待处理文件...")
    
    output_dir = "outputs"
    if not os.path.exists(output_dir):
        print("❌ outputs目录不存在")
        return []
    
    ocr_files = [f for f in os.listdir(output_dir) if f.endswith('_result.json')]
    blockchain_files = [f for f in os.listdir(output_dir) if f.endswith('_blockchain.json')]
    
    pending_files = []
    for ocr_file in ocr_files:
        blockchain_file = ocr_file.replace('_result.json', '_blockchain.json')
        if blockchain_file not in blockchain_files:
            pending_files.append(ocr_file)
    
    print(f"⏳ 发现 {len(pending_files)} 个待处理文件:")
    for i, file in enumerate(pending_files[:5]):  # 显示前5个
        print(f"  {i+1}. {file}")
    
    if len(pending_files) > 5:
        print(f"  ... 还有 {len(pending_files)-5} 个文件")
    
    return pending_files

if __name__ == '__main__':
    print("🚀 测试区块链NFT铸造功能...")
    print("=" * 50)
    
    # 列出待处理文件
    pending_files = list_pending_files()
    
    # 测试NFT铸造
    test_nft_minting()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！")
    
    if pending_files:
        print(f"\n💡 您有 {len(pending_files)} 个OCR文件可以处理到区块链")
        print("   启动Web界面: py app_enhanced.py")
        print("   访问: http://localhost:5000")
