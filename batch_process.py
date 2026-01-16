"""
批量处理OCR结果并上传到区块链
"""

import os
import sys
from ocr_to_blockchain import OCRBlockchainBridge
from datetime import datetime

def batch_process_ocr_results(output_folder='outputs', upload_folder='uploads'):
    """
    批量处理outputs文件夹中的所有OCR结果
    """
    bridge = OCRBlockchainBridge()
    
    # 获取所有OCR结果文件
    result_files = []
    for filename in os.listdir(output_folder):
        if filename.endswith('_result.json') and not filename.endswith('_blockchain.json'):
            result_files.append(filename)
    
    if not result_files:
        print("❌ 没有找到待处理的OCR结果文件")
        return
    
    result_files.sort()
    print(f"找到 {len(result_files)} 个OCR结果文件\n")
    
    # 统计信息
    success_count = 0
    failed_count = 0
    results = []
    
    for i, result_file in enumerate(result_files, 1):
        print(f"\n{'='*80}")
        print(f"处理进度: {i}/{len(result_files)}")
        print(f"{'='*80}")
        
        result_path = os.path.join(output_folder, result_file)
        
        # 尝试找到对应的原始图片
        image_name = result_file.replace('_result.json', '.png')
        if not os.path.exists(os.path.join(upload_folder, image_name)):
            image_name = result_file.replace('_result.json', '.jpg')
        if not os.path.exists(os.path.join(upload_folder, image_name)):
            image_name = result_file.replace('_result.json', '.jpeg')
        
        image_path = os.path.join(upload_folder, image_name)
        if not os.path.exists(image_path):
            print(f"⚠️ 未找到对应的图片文件，将只上传数据")
            image_path = None
        
        try:
            result = bridge.process_ocr_result(result_path, image_path)
            success_count += 1
            results.append({
                'file': result_file,
                'success': True,
                'ipfs_hash': result['ipfs']['dataHash'],
                'bill_number': result['billData']['billNumber']
            })
        except Exception as e:
            failed_count += 1
            print(f"❌ 处理失败: {e}")
            results.append({
                'file': result_file,
                'success': False,
                'error': str(e)
            })
        
        # 添加延迟以避免API限流
        if i < len(result_files):
            import time
            time.sleep(2)
    
    # 打印总结
    print(f"\n{'='*80}")
    print(f"批量处理完成")
    print(f"{'='*80}")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {failed_count}")
    print(f"📊 总计: {len(result_files)}")
    
    # 保存处理日志
    log_file = f"batch_process_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    import json
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total': len(result_files),
            'success': success_count,
            'failed': failed_count,
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📝 详细日志已保存到: {log_file}")


def process_single_file(result_file, image_file=None):
    """
    处理单个OCR结果文件
    """
    bridge = OCRBlockchainBridge()
    
    if not os.path.exists(result_file):
        print(f"❌ 文件不存在: {result_file}")
        return
    
    image_path = None
    if image_file and os.path.exists(image_file):
        image_path = image_file
    
    result = bridge.process_ocr_result(result_file, image_path)
    
    if result['success']:
        print("\n🎉 处理成功！")
        print(f"IPFS数据: {result['ipfs']['dataUrl']}")
        if result['ipfs']['imageUrl']:
            print(f"IPFS图片: {result['ipfs']['imageUrl']}")


def main():
    """
    命令行入口
    """
    if len(sys.argv) < 2:
        print("批量处理OCR结果并上传到区块链")
        print("\n用法:")
        print("  1. 批量处理所有文件:")
        print("     python batch_process.py batch")
        print("\n  2. 处理单个文件:")
        print("     python batch_process.py single <result.json> [image.png]")
        print("\n示例:")
        print("     python batch_process.py batch")
        print("     python batch_process.py single outputs/20260108_142146_result.json uploads/20260108_142146_bill.png")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == 'batch':
        batch_process_ocr_results()
    elif mode == 'single':
        if len(sys.argv) < 3:
            print("❌ 缺少结果文件路径")
            sys.exit(1)
        
        result_file = sys.argv[2]
        image_file = sys.argv[3] if len(sys.argv) > 3 else None
        
        process_single_file(result_file, image_file)
    else:
        print(f"❌ 未知模式: {mode}")
        print("支持的模式: batch, single")
        sys.exit(1)


if __name__ == "__main__":
    main()
