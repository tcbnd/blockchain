from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import re
import uuid
from dotenv import load_dotenv
from ocr_to_blockchain import OCRBlockchainBridge

load_dotenv()

app = Flask(__name__)
CORS(app)

# 配置
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'json'}

# 初始化区块链桥接
print('🚀 正在初始化区块链桥接...')
try:
    bridge = OCRBlockchainBridge()
    print('✅ 区块链桥接初始化完成！')
except Exception as e:
    print(f'❌ 区块链桥接初始化失败: {e}')
    bridge = None

# 初始化OCR引擎 (统一版本 - 支持Windows和其他平台)
print('🚀 正在初始化OCR引擎...')
ocr_engine = None

# 检查并尝试不同的OCR选项 (按优先级和兼容性排序)
ocr_options = [
    ('paddleocr', 'PaddleOCR (最强推荐)'),
    ('easyocr', 'EasyOCR (推荐)'), 
    ('tesseract', 'Tesseract OCR'),
    ('mock', '模拟OCR模式 (演示用途)')
]

for engine_name, description in ocr_options:
    try:
        if engine_name == 'paddleocr':
            # 尝试PaddleOCR (延迟初始化)
            import paddleocr
            ocr_engine = 'paddleocr_lazy'
            print(f'✅ {description} - 已安装 (延迟初始化)')
            break
            
        elif engine_name == 'easyocr':
            # 尝试EasyOCR (延迟初始化)
            import easyocr
            ocr_engine = 'easyocr_lazy'
            print(f'✅ {description} - 已安装 (延迟初始化)')
            break
            
        elif engine_name == 'tesseract':
            # 尝试Tesseract (如果可用)
            import pytesseract
            from PIL import Image
            # 简单测试
            version = pytesseract.get_tesseract_version()
            ocr_engine = 'tesseract'
            print(f'✅ {description} - 版本: {version}')
            break
            
        elif engine_name == 'mock':
            # 模拟模式总是可用
            ocr_engine = 'mock'
            print(f'✅ {description} - 已启用')
            break
            
    except ImportError as e:
        print(f'⚠️ {description} - 不可用: {str(e)[:50]}...')
        continue
    except Exception as e:
        print(f'❌ {description} - 初始化失败: {str(e)[:50]}...')
        continue

if ocr_engine is None:
    ocr_engine = 'mock'
    print('🔄 回退到模拟OCR模式')

print(f'🎯 当前OCR引擎: {ocr_engine}')

# 创建必要的目录
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def perform_ocr(image_path):
    """执行OCR处理 - 统一版本支持所有平台"""
    global ocr_engine
    
    try:
        if ocr_engine is None:
            return None, "OCR引擎未初始化"
        
        # PaddleOCR (延迟初始化) - 最强推荐
        if ocr_engine == 'paddleocr_lazy':
            try:
                import paddleocr
                reader = paddleocr.PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
                results = reader.ocr(image_path, cls=True)
                
                extracted_texts = []
                total_confidence = 0
                
                for line in results[0] or []:
                    if line:
                        bbox, (text, confidence) = line
                        if confidence > 0.1:
                            extracted_texts.append({
                                'text': text.strip(),
                                'confidence': confidence,
                                'bbox': bbox
                            })
                            total_confidence += confidence
                
                avg_confidence = total_confidence / len(extracted_texts) if extracted_texts else 0
                return extracted_texts, avg_confidence
                
            except Exception as e:
                print(f"PaddleOCR错误，切换到备选方案: {e}")
                ocr_engine = 'easyocr_lazy' if 'easyocr' in str(e).lower() else 'mock'
                return perform_ocr(image_path)
        
        # EasyOCR (延迟初始化) - 推荐
        elif ocr_engine == 'easyocr_lazy':
            try:
                import easyocr
                reader = easyocr.Reader(['en'], gpu=False, verbose=False)
                results = reader.readtext(image_path)
                
                extracted_texts = []
                total_confidence = 0
                
                for (bbox, text, confidence) in results:
                    if confidence > 0.1:
                        extracted_texts.append({
                            'text': text.strip(),
                            'confidence': confidence,
                            'bbox': bbox
                        })
                        total_confidence += confidence
                
                avg_confidence = total_confidence / len(extracted_texts) if extracted_texts else 0
                return extracted_texts, avg_confidence
                
            except Exception as e:
                print(f"EasyOCR错误，切换到备选方案: {e}")
                ocr_engine = 'tesseract' if 'tesseract' in str(e).lower() else 'mock'
                return perform_ocr(image_path)
        
        # Tesseract OCR - 备选
        elif ocr_engine == 'tesseract':
            try:
                from PIL import Image
                import pytesseract
                
                image = Image.open(image_path)
                text = pytesseract.image_to_string(image)
                
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                extracted_texts = [{'text': line, 'confidence': 0.8, 'bbox': None} for line in lines]
                
                return extracted_texts, 0.8
            except Exception as e:
                print(f"Tesseract错误，切换到模拟模式: {e}")
                ocr_engine = 'mock'
                return perform_ocr(image_path)
        
        # 模拟OCR模式 (总是可用) - 演示用途
        elif ocr_engine == 'mock':
            mock_texts = [
                "BILL OF LADING",
                f"B/L No: BL{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "Vessel: MAERSK CONTAINER SHIP",
                "Port of Loading: Shanghai, China",
                "Port of Discharge: Los Angeles, USA", 
                "Shipper: Global Export Company Ltd",
                "Consignee: International Import Corp",
                "Description of Goods: Electronics & Components",
                "Gross Weight: 2500 KGS",
                "Container No: MSKU1234567",
                "Seal No: 987654321",
                f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "Freight: Prepaid",
                "Terms: CIF Los Angeles"
            ]
            
            extracted_texts = []
            for text in mock_texts:
                extracted_texts.append({
                    'text': text,
                    'confidence': 0.95,
                    'bbox': None
                })
            
            return extracted_texts, 0.95
        
        # 如果OCR引擎已经存在且是reader对象 (向后兼容)
        elif hasattr(ocr_engine, 'readtext'):  # EasyOCR reader对象
            results = ocr_engine.readtext(image_path)
            extracted_texts = []
            total_confidence = 0
            
            for (bbox, text, confidence) in results:
                if confidence > 0.1:
                    extracted_texts.append({
                        'text': text.strip(),
                        'confidence': confidence,
                        'bbox': bbox
                    })
                    total_confidence += confidence
            
            avg_confidence = total_confidence / len(extracted_texts) if extracted_texts else 0
            return extracted_texts, avg_confidence
        
        elif hasattr(ocr_engine, 'ocr'):  # PaddleOCR reader对象
            results = ocr_engine.ocr(image_path, cls=True)
            extracted_texts = []
            total_confidence = 0
            
            for line in results[0] or []:
                if line:
                    bbox, (text, confidence) = line
                    if confidence > 0.1:
                        extracted_texts.append({
                            'text': text.strip(),
                            'confidence': confidence,
                            'bbox': bbox
                        })
                        total_confidence += confidence
            
            avg_confidence = total_confidence / len(extracted_texts) if extracted_texts else 0
            return extracted_texts, avg_confidence
        
        # 默认回退到模拟模式
        else:
            print(f"未知OCR引擎类型: {ocr_engine}, 切换到模拟模式")
            ocr_engine = 'mock'
            return perform_ocr(image_path)
            
    except Exception as e:
        print(f"OCR处理异常: {e}, 切换到模拟模式")
        ocr_engine = 'mock'
        return perform_ocr(image_path)

def save_ocr_result(extracted_texts, avg_confidence, original_filename):
    """保存OCR结果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 生成结果文件名
    base_name = os.path.splitext(original_filename)[0]
    
    # 检查是否已经包含时间戳 (格式: YYYYMMDD_HHMMSS_)
    import re
    has_timestamp = re.match(r'^\d{8}_\d{6}_', base_name)
    
    if has_timestamp:
        # 如果已经有时间戳，直接使用base_name
        safe_name = re.sub(r'[^\w\-_.]', '_', base_name)
        result_filename = f"{safe_name}_result.json"
        ocr_filename = f"{safe_name}_ocr.txt"
    else:
        # 如果没有时间戳，添加时间戳
        safe_name = re.sub(r'[^\w\-_.]', '_', base_name)
        result_filename = f"{timestamp}_{safe_name}_result.json"
        ocr_filename = f"{timestamp}_{safe_name}_ocr.txt"
    
    # 保存详细结果 - 使用统一格式
    result_data = {
        "filename": original_filename,
        "timestamp": timestamp,
        "texts": extracted_texts,  # 使用 'texts' 作为主键，与OCR结果一致
        "extracted_texts": extracted_texts,  # 保留兼容性
        "average_confidence": avg_confidence,
        "total_lines": len(extracted_texts),
        "processing_info": {
            "engine": str(ocr_engine),
            "processed_at": datetime.now().isoformat()
        }
    }
    
    result_path = os.path.join(app.config['OUTPUT_FOLDER'], result_filename)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    # 保存纯文本
    ocr_path = os.path.join(app.config['OUTPUT_FOLDER'], ocr_filename)
    with open(ocr_path, 'w', encoding='utf-8') as f:
        for item in extracted_texts:
            f.write(f"{item['text']}\n")
    
    return result_filename, result_data

@app.route('/')
def index():
    """统一主页 - 处理现有OCR结果和新上传"""
    return render_template('index_visual.html')

@app.route('/api/ocr-files')
def list_ocr_files():
    """获取所有可用的OCR结果文件"""
    try:
        ocr_files = []
        output_dir = app.config['OUTPUT_FOLDER']
        
        for filename in os.listdir(output_dir):
            if filename.endswith('_result.json'):
                file_path = os.path.join(output_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 检查是否已经处理过
                    blockchain_file = filename.replace('_result.json', '_blockchain.json')
                    blockchain_path = os.path.join(output_dir, blockchain_file)
                    
                    # Initialize status variables
                    processed = False
                    pending_mint = False
                    
                    if os.path.exists(blockchain_path):
                        # 读取blockchain文件检查状态
                        try:
                            with open(blockchain_path, 'r', encoding='utf-8') as bf:
                                blockchain_data = json.load(bf)
                                # 只有当tokenId存在时才视为已处理
                                if blockchain_data.get('blockchain', {}).get('tokenId'):
                                    processed = True
                                else:
                                    # IPFS已上传但还未NFT铸造
                                    pending_mint = True
                        except Exception as be:
                            print(f'Error reading blockchain file {blockchain_file}: {be}')
                    
                    ocr_files.append({
                        'filename': filename,
                        'processed': processed,
                        'pending_mint': pending_mint,
                        'confidence': data.get('average_confidence', 0),
                        'text_lines': len(data.get('extracted_texts', [])),
                        'original_filename': data.get('original_filename', filename)
                    })
                except Exception as e:
                    print(f'Error reading {filename}: {e}')
        
        # 按文件名排序（最新的在前）
        ocr_files.sort(key=lambda x: x['filename'], reverse=True)
        
        return jsonify({
            'success': True,
            'files': ocr_files,
            'total': len(ocr_files)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取文件列表失败: {str(e)}'
        }), 500

@app.route('/api/process-ocr', methods=['POST'])
def process_ocr_file():

    """处理指定的OCR结果文件 - 只上传到IPFS，不铸造NFT"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({
                'success': False,
                'error': '未指定文件名'
            }), 400
        
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': f'文件不存在: {filename}'
            }), 404
        
        if not bridge:
            return jsonify({
                'success': False,
                'error': '区块链桥接未初始化'
            }), 500
        
        # 只上传到IPFS，不铸造NFT
        result = bridge.upload_to_ipfs_only(file_path)
        
        # 保存中间結果（只有IPFS數據，blockchain部分為pending）
        blockchain_filename = filename.replace('_result.json', '_blockchain.json')
        blockchain_path = os.path.join(app.config['OUTPUT_FOLDER'], blockchain_filename)
        
        with open(blockchain_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Check if NFT already exists
        blockchain_status = result.get('blockchain', {}).get('status')
        token_id = result.get('blockchain', {}).get('tokenId')
        
        if blockchain_status == 'minted' and token_id:
            # NFT already exists
            return jsonify({
                'success': True,
                'result': result,
                'message': f'✅ 已上傳到IPFS\n⚠️ 此提單已鑄造為NFT (Token ID: {token_id})',
                'ipfs_ready': True,
                'nft_minted': True,
                'already_exists': True
            })
        else:
            # NFT needs to be minted
            return jsonify({
                'success': True,
                'result': result,
                'message': f'已上傳到IPFS，等待鑄造NFT',
                'ipfs_ready': True,
                'nft_minted': False
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'處理失敗: {str(e)}'
        }), 500

@app.route('/api/mint-nft', methods=['POST'])
def mint_nft():
    """鑄造NFT - 基於已上傳到IPFS的數據"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({
                'success': False,
                'error': '未指定文件名'
            }), 400
        
        # 讀取中間結果
        blockchain_filename = filename.replace('_result.json', '_blockchain.json')
        blockchain_path = os.path.join(app.config['OUTPUT_FOLDER'], blockchain_filename)
        
        if not os.path.exists(blockchain_path):
            return jsonify({
                'success': False,
                'error': '請先上傳到IPFS'
            }), 404
        
        with open(blockchain_path, 'r', encoding='utf-8') as f:
            ipfs_result = json.load(f)
        
        if not bridge:
            return jsonify({
                'success': False,
                'error': '区块链桥接未初始化'
            }), 500
        
        # 檢查是否已經鑄造過
        if ipfs_result.get('blockchain', {}).get('tokenId'):
            return jsonify({
                'success': True,
                'result': ipfs_result,
                'message': 'NFT已經鑄造過了',
                'already_minted': True
            })
        
        # 鑄造NFT
        nft_result = bridge.mint_nft_from_ipfs(ipfs_result)
        
        # Check if bill already exists
        if not nft_result.get('success') and nft_result.get('already_exists'):
            # If we have existing token ID, update the blockchain file and return success
            if nft_result.get('existing_token_id'):
                # Update blockchain file with existing token ID
                ipfs_result['blockchain']['tokenId'] = nft_result['existing_token_id']
                ipfs_result['blockchain']['status'] = 'minted'
                ipfs_result['blockchain']['note'] = '此提單已於先前鑄造'
                if nft_result.get('existing_data'):
                    ipfs_result['blockchain']['existingOwner'] = nft_result['existing_data'].get('owner')
                
                with open(blockchain_path, 'w', encoding='utf-8') as f:
                    json.dump(ipfs_result, f, ensure_ascii=False, indent=2)
                
                return jsonify({
                    'success': True,
                    'result': ipfs_result,
                    'already_minted': True,
                    'message': f'⚠️ 此提單已鑄造過NFT\n\nToken ID: {nft_result["existing_token_id"]}\n\n{nft_result.get("solution", "")}'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': nft_result.get('message', '提單已存在'),
                    'already_exists': True,
                    'message': nft_result.get('message'),
                    'solution': nft_result.get('solution')
                }), 409  # 409 Conflict
        
        if not nft_result.get('success'):
            return jsonify({
                'success': False,
                'error': nft_result.get('error', 'NFT鑄造失敗'),
                'details': nft_result.get('last_error'),
                'solution': nft_result.get('solution')
            }), 500
        
        # 更新結果文件
        with open(blockchain_path, 'w', encoding='utf-8') as f:
            json.dump(nft_result, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'result': nft_result,
            'message': f'NFT鑄造成功！Token ID: {nft_result["blockchain"]["tokenId"]}',
            'nft_minted': True
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'鑄造NFT失敗: {str(e)}'
        }), 500

@app.route('/api/batch-process', methods=['POST'])
def batch_process():
    """批量处理所有OCR文件"""
    try:
        if not bridge:
            return jsonify({
                'success': False,
                'error': '区块链桥接未初始化'
            }), 500
        
        output_dir = app.config['OUTPUT_FOLDER']
        ocr_files = [f for f in os.listdir(output_dir) if f.endswith('_result.json')]
        
        results = []
        for filename in ocr_files:
            # 检查是否已经处理过
            blockchain_file = filename.replace('_result.json', '_blockchain.json')
            if os.path.exists(os.path.join(output_dir, blockchain_file)):
                results.append({
                    'filename': filename,
                    'status': 'skipped',
                    'message': '已经处理过'
                })
                continue
            
            try:
                file_path = os.path.join(output_dir, filename)
                result = bridge.process_ocr_result(file_path)
                results.append({
                    'filename': filename,
                    'status': 'success',
                    'result': result
                })
            except Exception as e:
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'total': len(ocr_files),
            'processed': len([r for r in results if r['status'] == 'success'])
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'批量处理失败: {str(e)}'
        }), 500

@app.route('/api/results/<filename>')
def get_result(filename):
    """获取处理结果"""
    try:
        result_file = filename.replace('_result.json', '_blockchain.json')
        result_path = os.path.join(app.config['OUTPUT_FOLDER'], result_file)
        
        if not os.path.exists(result_path):
            return jsonify({
                'success': False,
                'error': '结果文件不存在'
            }), 404
        
        with open(result_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取结果失败: {str(e)}'
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传新图片进行OCR处理"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '未选择文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '未选择文件'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': '不支持的文件格式'
            }), 400
        
        # 保存上传文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(file_path)
        
        return jsonify({
            'success': True,
            'filename': safe_filename,
            'message': '文件上传成功',
            'ocr_available': ocr_engine is not None
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'上传失败: {str(e)}'
        }), 500

@app.route('/api/ocr-process', methods=['POST'])
def process_uploaded_file():
    """处理上传的图片进行OCR"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({
                'success': False,
                'error': '未指定文件名'
            }), 400
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': f'文件不存在: {filename}'
            }), 404
        
        if ocr_engine is None:
            return jsonify({
                'success': False,
                'error': 'OCR引擎未初始化',
                'install_hint': 'py -m pip install paddleocr 或 py -m pip install easyocr'
            }), 500
        
        # 执行OCR
        extracted_texts, avg_confidence = perform_ocr(file_path)
        if extracted_texts is None:
            return jsonify({
                'success': False,
                'error': f'OCR处理失败: {avg_confidence}'
            }), 500
        
        # 保存OCR结果
        result_filename, result_data = save_ocr_result(extracted_texts, avg_confidence, filename)
        
        return jsonify({
            'success': True,
            'result_filename': result_filename,
            'ocr_result': result_data,
            'message': f'OCR处理完成，提取到 {len(extracted_texts)} 行文本',
            'engine_used': str(ocr_engine)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }), 500

@app.route('/api/full-process', methods=['POST'])
def full_process():
    """完整流程：上传 -> OCR -> 区块链"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '未选择文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': '无效的文件'
            }), 400
        
        if ocr_engine is None or not bridge:
            missing = []
            if ocr_engine is None:
                missing.append('OCR引擎')
            if not bridge:
                missing.append('区块链桥接')
            
            return jsonify({
                'success': False,
                'error': f'系统未完全初始化，缺少: {", ".join(missing)}',
                'install_hint': 'py -m pip install paddleocr' if ocr_engine is None else None
            }), 500
        
        # 1. 保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(file_path)
        
        # 2. OCR处理
        extracted_texts, avg_confidence = perform_ocr(file_path)
        if extracted_texts is None:
            return jsonify({
                'success': False,
                'error': f'OCR处理失败: {avg_confidence}'
            }), 500
        
        # 3. 保存OCR结果
        result_filename, result_data = save_ocr_result(extracted_texts, avg_confidence, safe_filename)
        
        # 4. 只上傳到IPFS（不自動鑄造NFT）
        result_path = os.path.join(app.config['OUTPUT_FOLDER'], result_filename)
        blockchain_result = bridge.upload_to_ipfs_only(result_path, file_path)
        
        # 5. 保存中間結果
        blockchain_filename = result_filename.replace('_result.json', '_blockchain.json')
        blockchain_path = os.path.join(app.config['OUTPUT_FOLDER'], blockchain_filename)
        
        with open(blockchain_path, 'w', encoding='utf-8') as f:
            json.dump(blockchain_result, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'ocr_result': result_data,
            'blockchain_result': blockchain_result,
            'result_filename': result_filename,
            'message': '已完成OCR和IPFS上傳，請點擊「鑄造NFT」按鈕完成',
            'engine_used': str(ocr_engine),
            'ipfs_ready': True,
            'nft_minted': False
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'完整流程处理失败: {str(e)}'
        }), 500

@app.route('/api/stats')
def get_stats():
    """获取系统统计信息"""
    try:
        output_dir = app.config['OUTPUT_FOLDER']
        upload_dir = app.config['UPLOAD_FOLDER']
        
        # OCR结果文件统计
        ocr_files = [f for f in os.listdir(output_dir) if f.endswith('_result.json')]
        blockchain_files = [f for f in os.listdir(output_dir) if f.endswith('_blockchain.json')]
        
        # 上传文件统计
        uploaded_files = []
        if os.path.exists(upload_dir):
            uploaded_files = [f for f in os.listdir(upload_dir) 
                            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'))]
        
        # 计算置信度统计
        confidence_stats = []
        for filename in ocr_files:
            try:
                with open(os.path.join(output_dir, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    confidence_stats.append(data.get('average_confidence', 0))
            except:
                continue
        
        avg_confidence = sum(confidence_stats) / len(confidence_stats) if confidence_stats else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_ocr_files': len(ocr_files),
                'processed_to_blockchain': len(blockchain_files),
                'pending_blockchain': len(ocr_files) - len(blockchain_files),
                'uploaded_images': len(uploaded_files),
                'average_confidence': round(avg_confidence * 100, 2),
                'system_status': {
                    'ocr_engine': ocr_engine is not None,
                    'ocr_engine_type': str(ocr_engine),
                    'blockchain_bridge': bridge is not None
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取统计信息失败: {str(e)}'
        }), 500

@app.route('/api/blockchain/latest-nft')
def get_latest_nft():
    """获取最新的NFT信息"""
    try:
        output_dir = app.config['OUTPUT_FOLDER']
        blockchain_files = [f for f in os.listdir(output_dir) if f.endswith('_blockchain.json')]
        
        if not blockchain_files:
            return jsonify({
                'success': True,
                'nft': None,
                'message': '暂无NFT数据'
            })
        
        # 按时间排序，获取最新的
        blockchain_files.sort(reverse=True)
        latest_file = blockchain_files[0]
        
        with open(os.path.join(output_dir, latest_file), 'r', encoding='utf-8') as f:
            nft_data = json.load(f)
        
        return jsonify({
            'success': True,
            'nft': nft_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blockchain/contract-info')
def get_contract_info():
    """获取智能合约信息"""
    try:
        contract_address = os.getenv('CONTRACT_ADDRESS')
        
        return jsonify({
            'success': True,
            'contract': {
                'address': contract_address,
                'network': 'Sepolia Testnet',
                'explorer_url': f"https://sepolia.etherscan.io/address/{contract_address}" if contract_address else None,
                'functions': [
                    {
                        'name': 'mintBill',
                        'description': '创建新的提单NFT',
                        'type': 'write'
                    },
                    {
                        'name': 'pledgeForFinancing',
                        'description': '将提单质押用于融资',
                        'type': 'write'
                    },
                    {
                        'name': 'releaseOwnership',
                        'description': '释放提单所有权',
                        'type': 'write'
                    },
                    {
                        'name': 'getBillData',
                        'description': '获取提单数据',
                        'type': 'read'
                    },
                    {
                        'name': 'isTransferable',
                        'description': '检查是否可转让',
                        'type': 'read'
                    },
                    {
                        'name': 'tokenURI',
                        'description': '获取NFT元数据URI',
                        'type': 'read'
                    }
                ]
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blockchain/nft-history')
def get_nft_history():
    """获取所有NFT历史记录"""
    try:
        output_dir = app.config['OUTPUT_FOLDER']
        blockchain_files = [f for f in os.listdir(output_dir) if f.endswith('_blockchain.json')]
        
        nft_history = []
        for filename in sorted(blockchain_files, reverse=True):
            try:
                with open(os.path.join(output_dir, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    nft_history.append({
                        'filename': filename,
                        'timestamp': data.get('processing_info', {}).get('timestamp', 'Unknown'),
                        'bill_number': data.get('bill_data', {}).get('bill_number', 'Unknown'),
                        'transaction_hash': data.get('nft_result', {}).get('transaction_hash'),
                        'explorer_url': data.get('nft_result', {}).get('explorer_url'),
                        'ipfs_url': data.get('nft_result', {}).get('ipfs_url'),
                        'success': data.get('nft_result', {}).get('success', False)
                    })
            except Exception as e:
                print(f"Error reading {filename}: {e}")
        
        return jsonify({
            'success': True,
            'history': nft_history,
            'total': len(nft_history)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/compare-result/<filename>')
def compare_result(filename):
    """获取OCR结果进行比较"""
    try:
        # 查找对应的OCR结果文件
        result_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(result_path):
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404
        
        with open(result_path, 'r', encoding='utf-8') as f:
            ocr_data = json.load(f)
        
        # 查找对应的区块链结果
        blockchain_filename = filename.replace('_result.json', '_blockchain.json')
        blockchain_path = os.path.join(app.config['OUTPUT_FOLDER'], blockchain_filename)
        blockchain_data = None
        
        if os.path.exists(blockchain_path):
            with open(blockchain_path, 'r', encoding='utf-8') as f:
                blockchain_data = json.load(f)
        
        return jsonify({
            'success': True,
            'ocr_result': ocr_data,
            'blockchain_result': blockchain_data,
            'original_filename': ocr_data.get('original_filename')
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    """提供上传的图片文件"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'文件不存在: {str(e)}'
        }), 404

@app.route('/api/delete-ocr', methods=['DELETE'])
def delete_ocr_result():
    """删除指定的OCR结果文件"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        create_backup = data.get('backup', True)
        
        if not filename:
            return jsonify({
                'success': False,
                'error': '未指定文件名'
            }), 400
        
        output_dir = app.config['OUTPUT_FOLDER']
        
        # 检查OCR结果文件是否存在
        ocr_file_path = os.path.join(output_dir, filename)
        if not os.path.exists(ocr_file_path):
            return jsonify({
                'success': False,
                'error': f'OCR文件不存在: {filename}'
            }), 404
        
        # 确定相关文件
        base_name = filename.replace('_result.json', '')
        related_files = []
        
        # 添加所有相关文件
        for ext in ['_result.json', '_blockchain.json', '_ocr.txt']:
            file_path = os.path.join(output_dir, base_name + ext)
            if os.path.exists(file_path):
                related_files.append({
                    'name': base_name + ext,
                    'path': file_path
                })
        
        deleted_files = []
        backup_dir = None
        
        # 创建备份目录 (如果需要)
        if create_backup:
            backup_dir = f"backup_deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
        
        # 删除文件
        for file_info in related_files:
            try:
                # 备份文件
                if create_backup:
                    import shutil
                    backup_path = os.path.join(backup_dir, file_info['name'])
                    shutil.copy2(file_info['path'], backup_path)
                
                # 删除文件
                os.remove(file_info['path'])
                deleted_files.append(file_info['name'])
                
            except Exception as e:
                print(f"删除文件 {file_info['name']} 时出错: {e}")
        
        return jsonify({
            'success': True,
            'deleted_files': deleted_files,
            'backup_location': backup_dir if create_backup else None,
            'message': f'成功删除 {len(deleted_files)} 个相关文件'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'删除失败: {str(e)}'
        }), 500

@app.route('/api/delete-batch', methods=['DELETE'])
def delete_batch_ocr():
    """批量删除OCR结果文件"""
    try:
        data = request.get_json()
        filenames = data.get('filenames', [])
        criteria = data.get('criteria', {})
        create_backup = data.get('backup', True)
        
        output_dir = app.config['OUTPUT_FOLDER']
        
        # 如果提供了文件名列表，直接删除
        if filenames:
            files_to_delete = filenames
        else:
            # 根据条件筛选文件
            files_to_delete = []
            all_ocr_files = [f for f in os.listdir(output_dir) if f.endswith('_result.json')]
            
            for filename in all_ocr_files:
                should_delete = False
                
                try:
                    file_path = os.path.join(output_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data_content = json.load(f)
                    
                    # 检查各种删除条件
                    if criteria.get('unprocessed'):
                        # 删除未处理到区块链的文件
                        blockchain_file = filename.replace('_result.json', '_blockchain.json')
                        if not os.path.exists(os.path.join(output_dir, blockchain_file)):
                            should_delete = True
                    
                    elif criteria.get('low_confidence'):
                        # 删除低置信度文件
                        threshold = criteria.get('confidence_threshold', 0.5)
                        confidence = data_content.get('average_confidence', 0)
                        if confidence < threshold:
                            should_delete = True
                    
                    elif criteria.get('date_range'):
                        # 删除指定日期的文件
                        target_date = criteria.get('date')
                        if target_date and filename.startswith(target_date):
                            should_delete = True
                    
                    elif criteria.get('empty_files'):
                        # 删除空文件或错误文件
                        text_lines = len(data_content.get('extracted_texts', []))
                        file_size = os.path.getsize(file_path)
                        if text_lines == 0 or file_size < 100:
                            should_delete = True
                    
                    if should_delete:
                        files_to_delete.append(filename)
                
                except Exception as e:
                    print(f"处理文件 {filename} 时出错: {e}")
        
        if not files_to_delete:
            return jsonify({
                'success': True,
                'deleted_count': 0,
                'message': '没有找到符合条件的文件'
            })
        
        # 创建备份目录
        backup_dir = None
        if create_backup:
            backup_dir = f"backup_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
        
        deleted_files = []
        
        # 批量删除文件
        for filename in files_to_delete:
            try:
                base_name = filename.replace('_result.json', '')
                related_files = []
                
                # 查找相关文件
                for ext in ['_result.json', '_blockchain.json', '_ocr.txt']:
                    file_path = os.path.join(output_dir, base_name + ext)
                    if os.path.exists(file_path):
                        related_files.append({
                            'name': base_name + ext,
                            'path': file_path
                        })
                
                # 删除相关文件
                for file_info in related_files:
                    try:
                        # 备份文件
                        if create_backup:
                            import shutil
                            backup_path = os.path.join(backup_dir, file_info['name'])
                            shutil.copy2(file_info['path'], backup_path)
                        
                        # 删除文件
                        os.remove(file_info['path'])
                        deleted_files.append(file_info['name'])
                        
                    except Exception as e:
                        print(f"删除文件 {file_info['name']} 时出错: {e}")
            
            except Exception as e:
                print(f"处理文件组 {filename} 时出错: {e}")
        
        return jsonify({
            'success': True,
            'deleted_count': len(files_to_delete),
            'deleted_files': deleted_files,
            'backup_location': backup_dir if create_backup else None,
            'message': f'成功删除 {len(files_to_delete)} 个文件组'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'批量删除失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    print('🚀 OCR-到-区块链 Web服务器')
    print('📁 支持现有OCR文件处理和新图片上传')
    print('🔍 OCR引擎支持: PaddleOCR → EasyOCR → Tesseract → Mock')
    print('🔗 包含完整区块链可视化和智能合约交互')
    print(f'🎯 当前OCR引擎: {ocr_engine}')
    print('🌐 访问: http://localhost:5000')
    print('=' * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
