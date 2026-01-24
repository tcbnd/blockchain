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
        支持多种OCR结果格式：
        1. 结构化格式 (extracted/extracted_data)
        2. 简单格式 (texts/extracted_texts列表)
        """
        # 檢查是否為簡單OCR格式（只有texts列表）
        if 'texts' in ocr_result or 'extracted_texts' in ocr_result:
            # 簡單格式：提取所有文本並嘗試找到關鍵信息
            texts_list = ocr_result.get('texts', []) or ocr_result.get('extracted_texts', [])
            
            # 將文本列表轉為可搜索的字符串
            all_text = '\n'.join([item.get('text', '') if isinstance(item, dict) else str(item) for item in texts_list])
            
            # 智能提取所有字段
            import re
            
            # 初始化所有字段
            bill_number = ''
            vessel = ''
            voyage = ''
            port_of_loading = ''
            port_of_discharge = ''
            place_of_delivery = ''
            shipper_name = ''
            consignee_name = ''
            cargo_desc = ''
            container_no = ''
            gross_weight = ''
            seal_no = ''
            
            # 遍歷所有文本行進行智能匹配
            for i, item in enumerate(texts_list):
                text = item.get('text', '') if isinstance(item, dict) else str(item)
                text_upper = text.upper()
                
                # B/L No 提取 - 優先級最高
                if 'B/L NO' in text_upper or 'BL NO' in text_upper:
                    # 同一行提取
                    bl_match = re.search(r'(?:B/L\s*NO|BL\s*NO)[:\s]*(BL\d+)', text, re.IGNORECASE)
                    if bl_match:
                        bill_number = bl_match.group(1).upper()
                    # 下一行提取
                    elif i + 1 < len(texts_list):
                        next_text = texts_list[i + 1].get('text', '') if isinstance(texts_list[i + 1], dict) else str(texts_list[i + 1])
                        bl_match = re.search(r'(BL\d+)', next_text, re.IGNORECASE)
                        if bl_match:
                            bill_number = bl_match.group(1).upper()
                
                # Vessel 提取
                if 'VESSEL' in text_upper and ':' in text:
                    vessel = re.sub(r'^.*VESSEL[:\s]*', '', text, flags=re.IGNORECASE).strip()
                
                # Voyage 提取
                if 'VOYAGE' in text_upper and ':' in text:
                    voyage = re.sub(r'^.*VOYAGE[:\s]*', '', text, flags=re.IGNORECASE).strip()
                
                # Port of Loading 提取
                if 'PORT OF LOADING' in text_upper:
                    port_of_loading = re.sub(r'^.*PORT OF LOADING[:\s]*', '', text, flags=re.IGNORECASE).strip()
                
                # Port of Discharge 提取
                if 'PORT OF DISCHARGE' in text_upper:
                    port_of_discharge = re.sub(r'^.*PORT OF DISCHARGE[:\s]*', '', text, flags=re.IGNORECASE).strip()
                
                # Place of Delivery 提取
                if 'PLACE OF DELIVERY' in text_upper:
                    place_of_delivery = re.sub(r'^.*PLACE OF DELIVERY[:\s]*', '', text, flags=re.IGNORECASE).strip()
                
                # Shipper 提取
                if 'SHIPPER' in text_upper and ':' in text:
                    shipper_name = re.sub(r'^.*SHIPPER[:\s]*', '', text, flags=re.IGNORECASE).strip()
                
                # Consignee 提取
                if 'CONSIGNEE' in text_upper and ':' in text:
                    consignee_name = re.sub(r'^.*CONSIGNEE[:\s]*', '', text, flags=re.IGNORECASE).strip()
                
                # Description of Goods 提取
                if 'DESCRIPTION OF GOODS' in text_upper or 'DESCRIPTION' in text_upper:
                    cargo_desc = re.sub(r'^.*DESCRIPTION[:\s]*(?:OF GOODS[:\s]*)?', '', text, flags=re.IGNORECASE).strip()
                
                # Container No 提取
                if 'CONTAINER NO' in text_upper or 'CONTAINER' in text_upper:
                    container_no = re.sub(r'^.*CONTAINER[:\s]*(?:NO[:\s]*)?', '', text, flags=re.IGNORECASE).strip()
                
                # Gross Weight 提取
                if 'GROSS WEIGHT' in text_upper:
                    gross_weight = re.sub(r'^.*GROSS WEIGHT[:\s]*', '', text, flags=re.IGNORECASE).strip()
                
                # Seal No 提取
                if 'SEAL NO' in text_upper:
                    seal_no = re.sub(r'^.*SEAL NO[:\s]*', '', text, flags=re.IGNORECASE).strip()
            
            # 如果沒找到Bill Number，嘗試從檔案名提取
            if not bill_number:
                filename = ocr_result.get('filename', '') or ocr_result.get('original_filename', '')
                bl_match = re.search(r'(BL\d{10,})', filename, re.IGNORECASE)
                if bl_match:
                    bill_number = bl_match.group(1).upper()
            
            # 構建完整的提單數據 - 匹配UI顯示的結構
            bill_data = {
                "billNumber": bill_number or f"BL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "vessel": vessel,
                "voyage": voyage,
                "portOfLoading": port_of_loading,
                "portOfDischarge": port_of_discharge,
                "placeOfDelivery": place_of_delivery,
                "shipper": {
                    "name": shipper_name,
                    "address": ""
                },
                "consignee": {
                    "name": consignee_name,
                    "address": ""
                },
                "cargoDescription": cargo_desc,
                "containerInfo": container_no,
                "sealNumber": seal_no,
                "grossWeight": gross_weight,
                "measurement": "",
                "issueDate": datetime.now().isoformat().split('T')[0],
                "extractedAt": datetime.now().isoformat(),
                "accuracy": 0,
                "originalFilename": ocr_result.get('filename', '') or ocr_result.get('original_filename', ''),
                "ocrConfidence": ocr_result.get('average_confidence', 0),
                "rawText": all_text  # 保存原始文本供參考
            }
            
            return bill_data
        
        # 結構化格式處理（原有邏輯）
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
    
    def upload_to_ipfs_only(self, ocr_result_path, image_path=None):
        """
        只上傳到IPFS，不鑄造NFT
        返回包含IPFS信息的結果，blockchain部分標記為pending
        """
        print(f"\n{'='*60}")
        print(f"📤 開始處理OCR結果（僅上傳IPFS）")
        print(f"{'='*60}\n")
        
        # 1. 加載OCR結果
        print(f"步驟 1/3: 加載OCR結果...")
        with open(ocr_result_path, 'r', encoding='utf-8') as f:
            ocr_result = json.load(f)
        
        # 2. 轉換為提單格式
        bill_data = self.transform_ocr_to_bill_data(ocr_result)
        print(f"✅ 提單號: {bill_data['billNumber']}")
        
        # 3. 上傳圖片到IPFS（如果提供）
        image_ipfs_hash = None
        if image_path and os.path.exists(image_path):
            print(f"\n步驟 2/3: 上傳原始圖片到IPFS...")
            image_result = self.upload_file_to_pinata(
                image_path,
                f"bill_image_{bill_data['billNumber']}"
            )
            image_ipfs_hash = image_result['IpfsHash']
            bill_data['imageIPFS'] = image_ipfs_hash
            print(f"✅ 圖片IPFS: ipfs://{image_ipfs_hash}")
        
        # 4. 上傳提單數據到IPFS
        print(f"\n步驟 3/3: 上傳提單數據到IPFS...")
        data_result = self.upload_json_to_pinata(
            bill_data,
            f"bill_data_{bill_data['billNumber']}"
        )
        data_ipfs_hash = data_result['IpfsHash']
        print(f"✅ 數據IPFS: ipfs://{data_ipfs_hash}")
        
        # 5. 計算數據哈希
        data_hash = self.calculate_data_hash(bill_data)
        print(f"✅ 數據哈希: 0x{data_hash}")
        
        # 6. 檢查提單是否已經存在於區塊鏈
        print(f"\n🔍 檢查提單是否已存在...")
        existing_data = self.get_existing_bill_data(bill_data['billNumber'])
        
        # 7. 返回結果
        if existing_data and existing_data.get('tokenId'):
            # 提單已存在
            print(f"✅ 發現已存在的NFT - Token ID: {existing_data['tokenId']}")
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
                    "status": "minted",
                    "tokenId": existing_data['tokenId'],
                    "transactionHash": None,
                    "explorerUrl": None,
                    "contractUrl": f"https://sepolia.etherscan.io/address/{self.contract_address}",
                    "tokenUrl": f"https://sepolia.etherscan.io/token/{self.contract_address}?a={existing_data['tokenId']}",
                    "note": "此提單已於先前鑄造",
                    "existingOwner": existing_data.get('owner')
                },
                "timestamp": datetime.now().isoformat()
            }
            print(f"⚠️  此提單已鑄造為NFT (Token ID: {existing_data['tokenId']})")
        else:
            # 提單不存在，等待鑄造
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
                    "status": "pending",
                    "tokenId": None,
                    "transactionHash": None,
                    "message": "等待鑄造NFT"
                },
                "timestamp": datetime.now().isoformat()
            }
        
        print(f"\n{'='*60}")
        print(f"✅ IPFS上傳完成！")
        print(f"{'='*60}\n")
        print(f"📊 查看數據: {result['ipfs']['dataUrl']}")
        if result['ipfs']['imageUrl']:
            print(f"🖼️  查看圖片: {result['ipfs']['imageUrl']}")
        
        if result['blockchain']['status'] == 'pending':
            print(f"\n⚠️  請點擊「鑄造NFT」按鈕完成NFT鑄造")
        else:
            print(f"\n✅ NFT已存在 (Token ID: {result['blockchain']['tokenId']})")
        
        return result
    
    def mint_nft_from_ipfs(self, ipfs_result):
        """
        基於已上傳到IPFS的數據鑄造NFT
        """
        print(f"\n{'='*60}")
        print(f"🎨 開始鑄造NFT")
        print(f"{'='*60}\n")
        
        bill_data = ipfs_result['billData']
        data_ipfs_hash = ipfs_result['ipfs']['dataHash']
        data_hash = ipfs_result['blockchain']['dataHash'].replace('0x', '')
        
        print(f"提單號: {bill_data['billNumber']}")
        print(f"IPFS哈希: {data_ipfs_hash}")
        
        # 鑄造NFT
        mint_result = self.mint_nft_via_hardhat(
            bill_data['billNumber'],
            data_ipfs_hash,
            data_hash
        )
        
        # 更新結果
        result = ipfs_result.copy()
        
        if mint_result['success']:
            # 從stdout中提取tokenId
            token_id = self.extract_token_id(mint_result.get('stdout', ''))
            tx_hash = mint_result.get('transaction_hash')
            
            result['blockchain'] = {
                "dataHash": f"0x{data_hash}",
                "contractAddress": self.contract_address,
                "status": "minted",
                "tokenId": token_id,
                "transactionHash": tx_hash,
                "explorerUrl": f"https://sepolia.etherscan.io/tx/{tx_hash}" if tx_hash else None,
                "contractUrl": f"https://sepolia.etherscan.io/address/{self.contract_address}"
            }
            print(f"\n✅ NFT鑄造成功！")
            print(f"Token ID: {token_id}")
            print(f"交易哈希: {tx_hash}")
        elif mint_result.get('already_exists') and mint_result.get('existing_token_id'):
            # Bill already exists, use existing token ID
            token_id = mint_result.get('existing_token_id')
            existing_data = mint_result.get('existing_data', {})
            
            result['blockchain'] = {
                "dataHash": f"0x{data_hash}",
                "contractAddress": self.contract_address,
                "status": "minted",
                "tokenId": token_id,
                "transactionHash": None,
                "explorerUrl": None,
                "contractUrl": f"https://sepolia.etherscan.io/address/{self.contract_address}",
                "tokenUrl": f"https://sepolia.etherscan.io/token/{self.contract_address}?a={token_id}",
                "note": "此提單已於先前鑄造",
                "existingOwner": existing_data.get('owner')
            }
            print(f"\n⚠️ 提單已存在")
            print(f"Token ID: {token_id}")
            print(f"Owner: {existing_data.get('owner')}")
        else:
            result['blockchain']['status'] = "failed"
            result['blockchain']['error'] = mint_result.get('error', 'Unknown error')
            print(f"\n❌ NFT鑄造失敗: {mint_result.get('error')}")
        
        print(f"\n{'='*60}")
        
        return result
    
    def extract_token_id(self, stdout):
        """
        從Hardhat輸出中提取token ID
        """
        import re
        match = re.search(r'Token ID:\s*(\d+)', stdout)
        if match:
            return match.group(1)
        match = re.search(r'tokenId.*?(\d+)', stdout, re.IGNORECASE)
        if match:
            return match.group(1)
        return "1"  # 默認值
    
    def get_existing_bill_data(self, bill_number):
        """
        查詢區塊鏈上是否已存在該提單號，並獲取Token ID
        """
        if not self.contract_address:
            return None
            
        try:
            project_dir = os.path.dirname(os.path.abspath(__file__))
            env = os.environ.copy()
            env['CONTRACT_ADDRESS'] = self.contract_address
            env['BILL_NUMBER'] = bill_number
            
            # Try to run the check script
            commands_to_try = [
                ['npx', 'hardhat', 'run', 'scripts/checkBillExists.js', '--network', 'sepolia'],
                ['node_modules\\.bin\\hardhat.cmd', 'run', 'scripts/checkBillExists.js', '--network', 'sepolia'],
                ['cmd', '/c', 'node_modules\\.bin\\hardhat.cmd', 'run', 'scripts/checkBillExists.js', '--network', 'sepolia']
            ]
            
            for cmd in commands_to_try:
                try:
                    result = subprocess.run(
                        cmd,
                        env=env,
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='ignore',
                        cwd=project_dir,
                        timeout=30
                    )
                    
                    if result.returncode == 0 and '=== EXISTING_BILL_DATA ===' in result.stdout:
                        # Parse the JSON data
                        import json
                        import re
                        match = re.search(r'=== EXISTING_BILL_DATA ===\n(.+?)\n=== END_DATA ===', 
                                        result.stdout, re.DOTALL)
                        if match:
                            data = json.loads(match.group(1))
                            return data
                    
                except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                    continue
                    
            return None
            
        except Exception as e:
            print(f"⚠️ 查詢現有提單失敗: {e}")
            return None
    
    def mint_nft_via_hardhat(self, bill_number, ipfs_hash, data_hash, shipper_address=None):
        """
        通过Hardhat脚本铸造NFT
        """
        if not self.contract_address:
            print("⚠️ 未设置CONTRACT_ADDRESS，跳过NFT铸造")
            return {
                'success': False,
                'error': 'CONTRACT_ADDRESS not set',
                'solution': '请在.env文件中配置CONTRACT_ADDRESS'
            }
        
        try:
            # 准备环境变量
            env = os.environ.copy()
            env['BILL_NUMBER'] = bill_number
            env['IPFS_HASH'] = ipfs_hash
            env['DATA_HASH'] = data_hash
            
            if shipper_address:
                env['SHIPPER_ADDRESS'] = shipper_address
            
            print(f"🔧 调用环境检查...")
            print(f"📁 工作目录: {os.path.dirname(os.path.abspath(__file__))}")
            
            # 检查 package.json 和 node_modules
            project_dir = os.path.dirname(os.path.abspath(__file__))
            package_json_path = os.path.join(project_dir, 'package.json')
            node_modules_path = os.path.join(project_dir, 'node_modules')
            
            if not os.path.exists(package_json_path):
                return {
                    'success': False,
                    'error': 'package.json not found',
                    'solution': '请在项目根目录运行: npm install'
                }
            
            if not os.path.exists(node_modules_path):
                return {
                    'success': False,
                    'error': 'node_modules not found',
                    'solution': '请在项目根目录运行: npm install'
                }
            
            # 尝试不同的命令方式
            commands_to_try = [
                ['node_modules\\.bin\\hardhat.cmd', 'run', 'scripts/mintFromOCR.js', '--network', 'sepolia'],
                ['npx', 'hardhat', 'run', 'scripts/mintFromOCR.js', '--network', 'sepolia'],
                ['node_modules\\.bin\\hardhat', 'run', 'scripts/mintFromOCR.js', '--network', 'sepolia'],
                ['cmd', '/c', 'node_modules\\.bin\\hardhat.cmd', 'run', 'scripts/mintFromOCR.js', '--network', 'sepolia']
            ]
            
            last_error = None
            for cmd in commands_to_try:
                print(f"🔄 尝试命令: {' '.join(cmd)}")
                try:
                    result = subprocess.run(
                        cmd,
                        env=env,
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='ignore',
                        cwd=project_dir,
                        timeout=60  # 60秒超时
                    )
                    
                    if result.returncode == 0:
                        print("✅ NFT铸造成功")
                        print(result.stdout)
                        
                        # 解析交易哈希
                        tx_hash = self.extract_transaction_hash(result.stdout)
                        return {
                            'success': True,
                            'stdout': result.stdout,
                            'transaction_hash': tx_hash,
                            'explorer_url': f"https://sepolia.etherscan.io/tx/{tx_hash}" if tx_hash else None,
                            'contract_url': f"https://sepolia.etherscan.io/address/{self.contract_address}",
                            'ipfs_url': f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
                        }
                    else:
                        error_output = result.stderr or result.stdout
                        print(f"❌ 命令失败: {error_output}")
                        
                        # Check if bill already exists
                        if "Bill already exists" in error_output or "execution reverted" in error_output:
                            print("ℹ️ 提示: 該提單號已經鑄造過NFT")
                            print("🔍 正在查詢現有Token ID...")
                            
                            # Try to get existing token ID from blockchain
                            existing_data = self.get_existing_bill_data(bill_number)
                            
                            if existing_data:
                                print(f"✅ 找到現有NFT - Token ID: {existing_data.get('tokenId')}")
                                return {
                                    'success': False,
                                    'error': 'Bill already minted',
                                    'message': f'提單號 {bill_number} 已經存在',
                                    'already_exists': True,
                                    'existing_token_id': existing_data.get('tokenId'),
                                    'existing_data': existing_data,
                                    'solution': f"此提單已鑄造為NFT (Token ID: {existing_data.get('tokenId')})"
                                }
                            else:
                                return {
                                    'success': False,
                                    'error': 'Bill already minted',
                                    'message': f'提單號 {bill_number} 已經存在，但無法獲取Token ID',
                                    'already_exists': True,
                                    'solution': '請手動檢查區塊鏈記錄或聯繫管理員'
                                }
                        
                        last_error = error_output
                        continue
                        
                except subprocess.TimeoutExpired:
                    print("⏰ 命令超时")
                    last_error = "Command timeout"
                    continue
                except FileNotFoundError:
                    print(f"❌ 找不到命令: {cmd[0]}")
                    last_error = f"Command not found: {cmd[0]}"
                    continue
            
            return {
                'success': False,
                'error': 'All minting attempts failed',
                'last_error': last_error,
                'solution': '请运行: npm install && npm install -g @nomiclabs/hardhat'
            }
                
        except Exception as e:
            print(f"❌ 调用铸造脚本失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'solution': '请检查环境配置和依赖安装'
            }

    def extract_transaction_hash(self, output):
        """从输出中提取交易哈希"""
        import re
        # 匹配以0x开头的64字符哈希
        hash_pattern = r'0x[a-fA-F0-9]{64}'
        matches = re.findall(hash_pattern, output)
        return matches[0] if matches else None
    
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
