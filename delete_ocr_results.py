#!/usr/bin/env python3
"""
OCR结果管理工具 - 删除和清理OCR文档结果
"""

import os
import json
import shutil
from datetime import datetime

def list_ocr_results():
    """列出所有OCR结果文件"""
    output_dir = "outputs"
    
    if not os.path.exists(output_dir):
        print("❌ outputs目录不存在")
        return []
    
    # 获取所有OCR结果文件
    ocr_files = []
    blockchain_files = []
    
    for filename in os.listdir(output_dir):
        if filename.endswith('_result.json'):
            ocr_files.append(filename)
        elif filename.endswith('_blockchain.json'):
            blockchain_files.append(filename)
    
    # 分析文件状态
    results = []
    for ocr_file in sorted(ocr_files, reverse=True):
        try:
            file_path = os.path.join(output_dir, ocr_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查是否有对应的区块链文件
            blockchain_file = ocr_file.replace('_result.json', '_blockchain.json')
            has_blockchain = blockchain_file in blockchain_files
            
            # 检查是否有对应的纯文本文件
            txt_file = ocr_file.replace('_result.json', '_ocr.txt')
            has_txt = os.path.exists(os.path.join(output_dir, txt_file))
            
            results.append({
                'ocr_file': ocr_file,
                'blockchain_file': blockchain_file if has_blockchain else None,
                'txt_file': txt_file if has_txt else None,
                'has_blockchain': has_blockchain,
                'timestamp': data.get('timestamp', 'Unknown'),
                'original_filename': data.get('original_filename', 'Unknown'),
                'confidence': data.get('average_confidence', 0),
                'text_lines': len(data.get('extracted_texts', [])),
                'file_size': os.path.getsize(file_path)
            })
            
        except Exception as e:
            print(f"⚠️ 读取文件 {ocr_file} 时出错: {e}")
    
    return results

def display_results(results):
    """显示OCR结果列表"""
    print(f"\n📁 找到 {len(results)} 个OCR结果文件:")
    print("=" * 100)
    print(f"{'序号':<4} {'文件名':<40} {'原始文件':<25} {'置信度':<8} {'行数':<6} {'区块链':<8} {'大小':<10}")
    print("=" * 100)
    
    for i, result in enumerate(results, 1):
        blockchain_status = "✅" if result['has_blockchain'] else "❌"
        confidence = f"{result['confidence']:.1%}" if result['confidence'] else "N/A"
        file_size = f"{result['file_size']/1024:.1f}KB"
        
        print(f"{i:<4} {result['ocr_file'][:39]:<40} {result['original_filename'][:24]:<25} "
              f"{confidence:<8} {result['text_lines']:<6} {blockchain_status:<8} {file_size:<10}")

def delete_ocr_result(results, indices, backup=True):
    """删除指定的OCR结果文件"""
    if backup:
        # 创建备份目录
        backup_dir = f"backup_deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        print(f"📦 创建备份目录: {backup_dir}")
    
    deleted_count = 0
    output_dir = "outputs"
    
    for index in indices:
        if 1 <= index <= len(results):
            result = results[index - 1]
            
            try:
                files_to_delete = [result['ocr_file']]
                
                # 添加相关文件
                if result['blockchain_file']:
                    files_to_delete.append(result['blockchain_file'])
                if result['txt_file']:
                    files_to_delete.append(result['txt_file'])
                
                print(f"\n🗑️ 删除文件组 {index}: {result['ocr_file']}")
                
                for file_to_delete in files_to_delete:
                    file_path = os.path.join(output_dir, file_to_delete)
                    if os.path.exists(file_path):
                        if backup:
                            # 备份文件
                            backup_path = os.path.join(backup_dir, file_to_delete)
                            shutil.copy2(file_path, backup_path)
                            print(f"   📦 备份: {file_to_delete}")
                        
                        # 删除文件
                        os.remove(file_path)
                        print(f"   ❌ 删除: {file_to_delete}")
                
                deleted_count += 1
                
            except Exception as e:
                print(f"❌ 删除文件组 {index} 时出错: {e}")
        else:
            print(f"❌ 无效的序号: {index}")
    
    print(f"\n✅ 成功删除 {deleted_count} 个文件组")
    if backup and deleted_count > 0:
        print(f"📦 备份位置: {backup_dir}")

def delete_by_criteria(results):
    """根据条件批量删除"""
    print("\n🎯 批量删除选项:")
    print("1. 删除所有未处理到区块链的文件")
    print("2. 删除所有置信度低于指定值的文件")
    print("3. 删除指定时间范围的文件")
    print("4. 删除空的或错误的文件")
    print("5. 返回主菜单")
    
    choice = input("\n请选择 (1-5): ").strip()
    
    if choice == "1":
        # 删除未处理到区块链的文件
        to_delete = [i for i, result in enumerate(results, 1) if not result['has_blockchain']]
        if to_delete:
            print(f"\n找到 {len(to_delete)} 个未处理到区块链的文件")
            confirm = input("确认删除? (y/N): ").strip().lower()
            if confirm == 'y':
                delete_ocr_result(results, to_delete)
        else:
            print("✅ 没有找到未处理到区块链的文件")
    
    elif choice == "2":
        # 删除低置信度文件
        try:
            threshold = float(input("请输入置信度阈值 (0.0-1.0): "))
            to_delete = [i for i, result in enumerate(results, 1) 
                        if result['confidence'] and result['confidence'] < threshold]
            if to_delete:
                print(f"\n找到 {len(to_delete)} 个置信度低于 {threshold:.1%} 的文件")
                confirm = input("确认删除? (y/N): ").strip().lower()
                if confirm == 'y':
                    delete_ocr_result(results, to_delete)
            else:
                print(f"✅ 没有找到置信度低于 {threshold:.1%} 的文件")
        except ValueError:
            print("❌ 无效的置信度值")
    
    elif choice == "3":
        # 删除指定日期的文件
        date_str = input("请输入日期 (格式: YYYYMMDD, 如: 20260106): ").strip()
        if len(date_str) == 8 and date_str.isdigit():
            to_delete = [i for i, result in enumerate(results, 1) 
                        if result['ocr_file'].startswith(date_str)]
            if to_delete:
                print(f"\n找到 {len(to_delete)} 个日期为 {date_str} 的文件")
                confirm = input("确认删除? (y/N): ").strip().lower()
                if confirm == 'y':
                    delete_ocr_result(results, to_delete)
            else:
                print(f"✅ 没有找到日期为 {date_str} 的文件")
        else:
            print("❌ 无效的日期格式")
    
    elif choice == "4":
        # 删除空文件或错误文件
        to_delete = [i for i, result in enumerate(results, 1) 
                    if result['text_lines'] == 0 or result['file_size'] < 100]
        if to_delete:
            print(f"\n找到 {len(to_delete)} 个空文件或错误文件")
            confirm = input("确认删除? (y/N): ").strip().lower()
            if confirm == 'y':
                delete_ocr_result(results, to_delete)
        else:
            print("✅ 没有找到空文件或错误文件")

def interactive_delete():
    """交互式删除界面"""
    while True:
        print("\n" + "=" * 60)
        print("🗑️ OCR结果删除工具")
        print("=" * 60)
        
        # 获取最新文件列表
        results = list_ocr_results()
        if not results:
            print("❌ 没有找到OCR结果文件")
            return
        
        display_results(results)
        
        print(f"\n🛠️ 操作选项:")
        print("1. 按序号删除 (例如: 1,3,5 或 1-10)")
        print("2. 批量删除")
        print("3. 刷新列表")
        print("4. 退出")
        
        choice = input("\n请选择操作 (1-4): ").strip()
        
        if choice == "1":
            # 按序号删除
            indices_input = input("请输入要删除的序号 (例如: 1,3,5 或 1-10): ").strip()
            try:
                indices = []
                for part in indices_input.split(','):
                    part = part.strip()
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        indices.extend(range(start, end + 1))
                    else:
                        indices.append(int(part))
                
                if indices:
                    print(f"\n将删除序号: {indices}")
                    confirm = input("确认删除? (y/N): ").strip().lower()
                    if confirm == 'y':
                        delete_ocr_result(results, indices)
                
            except ValueError:
                print("❌ 无效的序号格式")
        
        elif choice == "2":
            # 批量删除
            delete_by_criteria(results)
        
        elif choice == "3":
            # 刷新列表
            continue
        
        elif choice == "4":
            # 退出
            print("👋 退出删除工具")
            break
        
        else:
            print("❌ 无效的选择")

if __name__ == '__main__':
    print("🗑️ OCR结果删除工具")
    print("⚠️ 警告: 此工具将永久删除文件，请谨慎操作！")
    print("📦 所有删除的文件都会自动备份")
    
    confirm = input("\n继续使用删除工具? (y/N): ").strip().lower()
    if confirm == 'y':
        interactive_delete()
    else:
        print("👋 取消操作")
