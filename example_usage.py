"""
示例：使用OCR到区块链集成
演示如何将提单OCR结果上传到IPFS并铸造NFT
"""

from ocr_to_blockchain import OCRBlockchainBridge
import os
import json

def example_process_latest_result():
    """
    示例1：处理最新的OCR结果
    """
    print("\n" + "="*60)
    print("示例1：处理最新的OCR结果")
    print("="*60 + "\n")
    
    # 找到最新的结果文件
    output_folder = 'outputs'
    result_files = [f for f in os.listdir(output_folder) 
                   if f.endswith('_result.json') and not f.endswith('_blockchain.json')]
    
    if not result_files:
        print("❌ 未找到OCR结果文件")
        return
    
    # 按时间排序，获取最新的
    result_files.sort(reverse=True)
    latest_file = result_files[0]
    
    print(f"找到最新文件: {latest_file}")
    
    # 构建完整路径
    result_path = os.path.join(output_folder, latest_file)
    
    # 初始化桥接器
    bridge = OCRBlockchainBridge()
    
    # 处理文件
    result = bridge.process_ocr_result(result_path)
    
    # 显示结果
    print("\n" + "="*60)
    print("处理结果")
    print("="*60)
    print(f"✅ 提单编号: {result['billData']['billNumber']}")
    print(f"✅ 船舶: {result['billData']['vessel']}")
    print(f"✅ IPFS数据: {result['ipfs']['dataUrl']}")
    if result['ipfs']['imageUrl']:
        print(f"✅ IPFS图片: {result['ipfs']['imageUrl']}")


def example_upload_specific_file():
    """
    示例2：上传指定的OCR结果
    """
    print("\n" + "="*60)
    print("示例2：上传指定的OCR结果")
    print("="*60 + "\n")
    
    # 指定文件
    ocr_result_path = 'outputs/20260108_142146_result.json'
    image_path = 'uploads/20260108_142146_Maersk-No._217077365.png'
    
    if not os.path.exists(ocr_result_path):
        print(f"❌ 文件不存在: {ocr_result_path}")
        return
    
    # 初始化桥接器
    bridge = OCRBlockchainBridge()
    
    # 处理（包含图片）
    if os.path.exists(image_path):
        result = bridge.process_ocr_result(ocr_result_path, image_path)
    else:
        print("⚠️ 图片文件不存在，只上传数据")
        result = bridge.process_ocr_result(ocr_result_path)
    
    print(f"\n✅ 处理完成！")
    print(f"查看数据: {result['ipfs']['dataUrl']}")


def example_read_and_display_result():
    """
    示例3：读取并显示已处理的区块链结果
    """
    print("\n" + "="*60)
    print("示例3：读取已处理的区块链结果")
    print("="*60 + "\n")
    
    # 找到区块链结果文件
    output_folder = 'outputs'
    blockchain_files = [f for f in os.listdir(output_folder) 
                       if f.endswith('_blockchain.json')]
    
    if not blockchain_files:
        print("❌ 未找到已处理的区块链结果")
        print("请先运行示例1或示例2")
        return
    
    # 读取最新的
    blockchain_files.sort(reverse=True)
    latest_file = blockchain_files[0]
    
    filepath = os.path.join(output_folder, latest_file)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    print(f"文件: {latest_file}\n")
    print("提单信息:")
    print(f"  编号: {result['billData']['billNumber']}")
    print(f"  船舶: {result['billData']['vessel']}")
    print(f"  装货港: {result['billData']['portOfLoading']}")
    print(f"  卸货港: {result['billData']['portOfDischarge']}")
    
    print("\nIPFS信息:")
    print(f"  数据哈希: {result['ipfs']['dataHash']}")
    print(f"  数据URL: {result['ipfs']['dataUrl']}")
    if result['ipfs'].get('imageHash'):
        print(f"  图片哈希: {result['ipfs']['imageHash']}")
        print(f"  图片URL: {result['ipfs']['imageUrl']}")
    
    print("\n区块链信息:")
    print(f"  数据哈希: {result['blockchain']['dataHash']}")
    print(f"  合约地址: {result['blockchain']['contractAddress']}")
    
    if result['blockchain'].get('mintResult'):
        print(f"  铸造结果: ✅ 成功")


def example_json_only_upload():
    """
    示例4：只上传JSON数据到IPFS（不铸造NFT）
    """
    print("\n" + "="*60)
    print("示例4：只上传JSON数据到IPFS")
    print("="*60 + "\n")
    
    # 初始化桥接器
    bridge = OCRBlockchainBridge()
    
    # 准备数据
    test_data = {
        "billNumber": "TEST-" + str(int(os.times().elapsed * 1000)),
        "vessel": "TEST VESSEL",
        "shipper": "Test Shipper Co.",
        "consignee": "Test Consignee Inc.",
        "portOfLoading": "Test Port A",
        "portOfDischarge": "Test Port B"
    }
    
    print("上传测试数据...")
    
    # 只上传JSON
    result = bridge.upload_json_to_pinata(
        test_data,
        f"test_bill_{test_data['billNumber']}"
    )
    
    ipfs_hash = result['IpfsHash']
    
    print(f"\n✅ 上传成功！")
    print(f"IPFS哈希: {ipfs_hash}")
    print(f"查看数据: https://gateway.pinata.cloud/ipfs/{ipfs_hash}")


def main():
    """
    主函数：运行所有示例
    """
    print("\n" + "="*80)
    print("OCR到区块链集成 - 使用示例")
    print("="*80)
    
    examples = {
        '1': ('处理最新的OCR结果', example_process_latest_result),
        '2': ('上传指定的OCR结果', example_upload_specific_file),
        '3': ('读取已处理的结果', example_read_and_display_result),
        '4': ('只上传JSON到IPFS', example_json_only_upload)
    }
    
    print("\n可用的示例:")
    for key, (desc, _) in examples.items():
        print(f"  {key}. {desc}")
    print("  0. 运行所有示例")
    print("  q. 退出")
    
    choice = input("\n请选择 (0-4, q): ").strip()
    
    if choice == 'q':
        print("退出")
        return
    
    if choice == '0':
        # 运行所有示例
        for desc, func in examples.values():
            try:
                func()
                print("\n" + "-"*80)
            except Exception as e:
                print(f"\n❌ 示例执行失败: {e}")
                import traceback
                traceback.print_exc()
    elif choice in examples:
        desc, func = examples[choice]
        try:
            func()
        except Exception as e:
            print(f"\n❌ 示例执行失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ 无效的选择")


if __name__ == "__main__":
    main()
