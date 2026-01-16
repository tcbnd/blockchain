"""
OCR to Blockchain Integration
将OCR提取的提单数据上传到IPFS并铸造NFT
"""

import os
import json
import requests
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import hashlib

load_dotenv()

class OCRBlockchainBridge:
    def __init__(self):
        self.pinata_api_key = os.getenv('PINATA_API_KEY')
        self.pinata_secret_key = os.getenv('PINATA_SECRET_KEY')
        self.contract_address = os.getenv('CONTRACT_ADDRESS')
        self.pinata_base_url = 'https://api.pinata.cloud'
        
        if not self.pinata_api_key or not self.pinata_secret_key:
            raise ValueError("❌ 请在.env文件中配置PINATA_API_KEY和PINATA_SECRET_KEY")
    
    def upload_json_to_pinata(self, json_data, metadata_name):
        """
        上传JSON数据到Pinata IPFS
        """
        url = f"{self.pinata_base_url}/pinning/pinJSONToIPFS"
        
        headers = {
            'Content-Type': 'application/json',
            'pinata_api_key': self.pinata_api_key,
            'pinata_secret_api_key': self.pinata_secret_key
        }
        
        payload = {
            "pinataContent": json_data,
            "pinataMetadata": {
                "name": metadata_name,
                "keyvalues": {
                    "type": "bill_of_lading",
                    "timestamp": datetime.now().isoformat()
                }
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            print(f"✅ 数据已上传到IPFS: {result['IpfsHash']}")
            return result
        except Exception as e:
            print(f"❌ 上传到Pinata失败: {e}")
            raise
    
    def upload_file_to_pinata(self, file_path, metadata_name):
        """
        上传文件（如图片）到Pinata IPFS
        """
        url = f"{self.pinata_base_url}/pinning/pinFileToIPFS"
        
        headers = {
            'pinata_api_key': self.pinata_api_key,
            'pinata_secret_api_key': self.pinata_secret_key
        }
        
        with open(file_path, 'rb') as file:
            files = {'file': file}
            
            metadata = {
                "name": metadata_name,
                "keyvalues": {
                    "type": "bill_of_lading_image",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            data = {
                'pinataMetadata': json.dumps(metadata)
            }
            
            try:
                response = requests.post(url, files=files, data=data, headers=headers)
                response.raise_for_status()
                result = response.json()
                print(f"✅ 文件已上传到IPFS: {result['IpfsHash']}")
                return result
            except Exception as e:
                print(f"❌ 上传文件到Pinata失败: {e}")
                raise
    
    def calculate_data_hash(self, data):
        """
        计算数据的SHA256哈希
        """
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def transform_ocr_to_bill_data(self, ocr_result):
        """
        将OCR结果转换为提单标准格式
        """
        # 支持新舊兩種OCR結果格式
        extracted = ocr_result.get('extracted', {}) or ocr_result.get('extracted_data', {})
        bill_info = extracted.get('bill_info', {})
        shipper = extracted.get('shipper', {})
        consignee = extracted.get('consignee', {})
        
        # 處理地址 - 可能是字串或列表
        shipper_address = shipper.get('address', '')
        if isinstance(shipper_address, list):
            shipper_address = '\n'.join(shipper_address)
        
        consignee_address = consignee.get('address', '')
        if isinstance(consignee_address, list):
            consignee_address = '\n'.join(consignee_address)
        
        # 處理貨物描述 - 可能是字串或列表
        cargo = extracted.get('cargo', [])
        cargo_desc = bill_info.get('cargo_description', '') or bill_info.get('DESCRIPTION OF GOODS', '')
        if not cargo_desc and isinstance(cargo, list):
            cargo_desc = '\n'.join(cargo)
        
        # 构建标准化的提单数据
        bill_data = {
            "billNumber": bill_info.get('B/L NO', '') or bill_info.get('bl_number', ''),
            "vessel": bill_info.get('VESSEL', '') or bill_info.get('vessel', ''),
            "voyage": bill_info.get('VOYAGE', '') or bill_info.get('voyage', ''),
            "portOfLoading": bill_info.get('PORT OF LOADING', '') or bill_info.get('port_of_loading', ''),
            "portOfDischarge": bill_info.get('PORT OF DISCHARGE', '') or bill_info.get('port_of_discharge', ''),
            "placeOfDelivery": bill_info.get('PLACE OF DELIVERY', '') or bill_info.get('place_of_delivery', ''),
            "shipper": {
                "name": shipper.get('name', ''),
                "address": shipper_address
            },
            "consignee": {
                "name": consignee.get('name', ''),
                "address": consignee_address
            },
            "cargoDescription": cargo_desc,
            "containerInfo": extracted.get('container_info', ''),
            "grossWeight": bill_info.get('GROSS WEIGHT', '') or bill_info.get('gross_weight', ''),
            "measurement": bill_info.get('MEASUREMENT', '') or bill_info.get('measurement', ''),
            "issueDate": datetime.now().isoformat().split('T')[0],
            "extractedAt": datetime.now().isoformat(),
            "accuracy": ocr_result.get('accuracy', {}).get('overall', 0),
            "originalFilename": ocr_result.get('filename', ''),
            "ocrConfidence": ocr_result.get('average_confidence', 0)
        }
        
        return bill_data
    
    def mint_nft_via_hardhat(self, bill_number, ipfs_hash, data_hash, shipper_address=None):
        """
        通过Hardhat脚本铸造NFT
        """
        if not self.contract_address:
            print("⚠️ 未设置CONTRACT_ADDRESS，跳过NFT铸造")
            return None
        
        try:
            # 准备环境变量
            env = os.environ.copy()
            env['BILL_NUMBER'] = bill_number
            env['IPFS_HASH'] = ipfs_hash
            env['DATA_HASH'] = data_hash
            
            if shipper_address:
                env['SHIPPER_ADDRESS'] = shipper_address
            
            # 调用Node.js脚本铸造NFT
            result = subprocess.run(
                ['npx', 'hardhat', 'run', 'scripts/mintFromOCR.js', '--network', 'sepolia'],
                env=env,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            if result.returncode == 0:
                print("✅ NFT铸造成功")
                print(result.stdout)
                return result.stdout
            else:
                print(f"❌ NFT铸造失败: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ 调用铸造脚本失败: {e}")
            return None
    
    def process_ocr_result(self, ocr_result_path, image_path=None):
        """
        处理OCR结果的完整流程：
        1. 读取OCR结果
        2. 转换为标准格式
        3. 上传到IPFS
        4. 铸造NFT（可选）
        """
        print(f"\n{'='*60}")
        print(f"开始处理OCR结果: {ocr_result_path}")
        print(f"{'='*60}\n")
        
        # 1. 读取OCR结果
        with open(ocr_result_path, 'r', encoding='utf-8') as f:
            ocr_result = json.load(f)
        
        print(f"📄 文件名: {ocr_result.get('filename', 'Unknown')}")
        print(f"📊 平均置信度: {ocr_result.get('average_confidence', 0):.2%}")
        print(f"📝 提取文本行数: {ocr_result.get('total_lines', 0)}")
        
        # 2. 转换为标准提单格式
        print("\n步骤 1/4: 转换数据格式...")
        bill_data = self.transform_ocr_to_bill_data(ocr_result)
        print(f"✅ 提单编号: {bill_data['billNumber']}")
        print(f"✅ 船舶名称: {bill_data['vessel']}")
        print(f"✅ 装货港: {bill_data['portOfLoading']}")
        print(f"✅ 卸货港: {bill_data['portOfDischarge']}")
        
        # 3. 上传原始图片到IPFS（如果提供）
        image_ipfs_hash = None
        if image_path and os.path.exists(image_path):
            print(f"\n步骤 2/4: 上传原始图片到IPFS...")
            image_result = self.upload_file_to_pinata(
                image_path,
                f"bill_image_{bill_data['billNumber']}"
            )
            image_ipfs_hash = image_result['IpfsHash']
            bill_data['imageIPFS'] = image_ipfs_hash
            print(f"✅ 图片IPFS: ipfs://{image_ipfs_hash}")
        
        # 4. 上传提单数据到IPFS
        print(f"\n步骤 3/4: 上传提单数据到IPFS...")
        data_result = self.upload_json_to_pinata(
            bill_data,
            f"bill_data_{bill_data['billNumber']}"
        )
        data_ipfs_hash = data_result['IpfsHash']
        print(f"✅ 数据IPFS: ipfs://{data_ipfs_hash}")
        
        # 5. 计算数据哈希
        data_hash = self.calculate_data_hash(bill_data)
        print(f"✅ 数据哈希: 0x{data_hash}")
        
        # 6. 铸造NFT（可选）
        print(f"\n步骤 4/4: 铸造NFT...")
        mint_result = self.mint_nft_via_hardhat(
            bill_data['billNumber'],
            data_ipfs_hash,
            data_hash
        )
        
        # 7. 返回完整结果
        result = {
            "success": True,
            "billData": bill_data,
            "ipfs": {
                "dataHash": data_ipfs_hash,
                "dataUrl": f"https://gateway.pinata.cloud/ipfs/{data_ipfs_hash}",
                "imageHash": image_ipfs_hash,
                "imageUrl": f"https://gateway.pinata.cloud/ipfs/{image_ipfs_hash}" if image_ipfs_hash else None
            },
            "blockchain": {
                "dataHash": f"0x{data_hash}",
                "contractAddress": self.contract_address,
                "mintResult": mint_result
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存结果
        result_file = ocr_result_path.replace('_result.json', '_blockchain.json')
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"✅ 处理完成！结果已保存到: {result_file}")
        print(f"{'='*60}\n")
        print(f"📊 查看数据: {result['ipfs']['dataUrl']}")
        if result['ipfs']['imageUrl']:
            print(f"🖼️  查看图片: {result['ipfs']['imageUrl']}")
        
        return result


def main():
    """
    命令行入口：处理指定的OCR结果文件
    """
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python ocr_to_blockchain.py <ocr_result.json> [image_path]")
        print("示例: python ocr_to_blockchain.py outputs/20260108_142146_result.json test_images/bill.png")
        sys.exit(1)
    
    ocr_result_path = sys.argv[1]
    image_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(ocr_result_path):
        print(f"❌ 文件不存在: {ocr_result_path}")
        sys.exit(1)
    
    bridge = OCRBlockchainBridge()
    result = bridge.process_ocr_result(ocr_result_path, image_path)
    
    if result['success']:
        print("\n🎉 成功将OCR数据上链！")
    else:
        print("\n❌ 处理失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
