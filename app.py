from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from paddleocr import PaddleOCR
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
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf'}

# 初始化OCR引擎
print('正在初始化OCR引擎...')
ocr = PaddleOCR(use_textline_orientation=True, lang='en')
print('✅ OCR引擎初始化完成！')

# 加载验证数据
check_data = {}
try:
    with open('check_normalized.json', 'r', encoding='utf-8') as f:
        check_json = json.load(f)
        for bill in check_json.get('bills_of_lading', []):
            filename = bill.get('file_name', '')
            if filename:
                check_data[filename] = bill
    print(f'✅ 加载了 {len(check_data)} 条验证数据')
except Exception as e:
    print(f'⚠️ 加载check_normalized.json失败: {e}')
    check_data = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def calculate_accuracy(extracted_data, ground_truth):
    """计算提取数据的准确率"""
    if not ground_truth or not extracted_data:
        return {
            'overall': 0.0,
            'details': {},
            'message': '无验证数据'
        }
    
    # 从ground_truth中提取documents[0]的数据
    gt_doc = ground_truth.get('detail', {}).get('documents', [{}])[0]
    
    # ✅ 智能字段映射（支持多种可能的字段名）
    def get_field(doc, *field_names):
        """尝试从多个可能的字段名中获取值"""
        for name in field_names:
            value = doc.get(name, '')
            if value:
                return value
        return ''
    
    field_comparisons = [
        # 基本信息字段
        ('bl_number', ['bill_info', 'B/L NO'], get_field(gt_doc, 'bill_of_lading__number', 'bl_number')),
        ('vessel', ['bill_info', 'VESSEL'], get_field(gt_doc, 'vessel_name', 'vessel')),
        ('voyage', ['bill_info', 'VOYAGE'], get_field(gt_doc, 'vessel_address', 'voyage')),
        ('port_of_loading', ['bill_info', 'PORT OF LOADING'], get_field(gt_doc, 'place_of_loading', 'port_of_loading')),
        ('port_of_discharge', ['bill_info', 'PORT OF DISCHARGE'], get_field(gt_doc, 'place_of_delivery', 'place_of_discharge', 'port_of_discharge')),
        ('place_of_delivery', ['bill_info', 'PLACE OF DELIVERY'], get_field(gt_doc, 'place_of_delivery')),
        ('gross_weight', ['bill_info', 'GROSS WEIGHT'], get_field(gt_doc, 'total_gross_weight_value', 'gross_weight')),
        ('measurement', ['bill_info', 'MEASUREMENT'], get_field(gt_doc, 'measurement')),
        # 发货人信息
        ('shipper_name', ['shipper', 'name'], get_field(gt_doc, 'shipper_company_name', 'shipper_name')),
        ('shipper_address', ['shipper', 'address'], get_field(gt_doc, 'shipper_address')),
        # 收货人信息
        ('consignee_name', ['consignee', 'name'], get_field(gt_doc, 'consignee_company_name', 'consignee_name')),
        ('consignee_address', ['consignee', 'address'], get_field(gt_doc, 'consignee_address')),
    ]
    
    correct = 0
    total = 0
    details = {}
    
    def normalize_text(text):
        """标准化文本用于比较"""
        if isinstance(text, list):
            text = ' '.join(str(t) for t in text)
        text = str(text).strip().upper()
        # 移除多余空格和特殊字符
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[,.:;\-_()]', '', text)  # ✅ 添加括号
        return text
    
    def get_nested_value(data, keys):
        """从嵌套字典中获取值"""
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, '')
            else:
                return ''
        return value
    
    for field_name, extracted_keys, gt_value in field_comparisons:
        total += 1
        
        # 获取提取的值
        extracted_value = get_nested_value(extracted_data, extracted_keys)
        
        # 标准化
        extracted_norm = normalize_text(extracted_value)
        gt_norm = normalize_text(gt_value)
        
        # 比较
        if extracted_norm and gt_norm:
            # 计算相似度
            if extracted_norm == gt_norm:
                is_correct = True
                similarity = 1.0
            elif extracted_norm in gt_norm or gt_norm in extracted_norm:
                is_correct = True
                similarity = 0.8
            else:
                # 计算Jaccard相似度
                set1 = set(extracted_norm.split())
                set2 = set(gt_norm.split())
                if set1 and set2:
                    intersection = len(set1 & set2)
                    union = len(set1 | set2)
                    similarity = intersection / union if union > 0 else 0
                    is_correct = similarity >= 0.6
                else:
                    is_correct = False
                    similarity = 0
            
            if is_correct:
                correct += 1
            
            details[field_name] = {
                'extracted': str(extracted_value)[:100],
                'ground_truth': str(gt_value)[:100],
                'correct': is_correct,
                'similarity': round(similarity, 2)
            }
        elif not extracted_norm and not gt_norm:
            # 都为空也算正确
            correct += 1
            details[field_name] = {
                'extracted': '',
                'ground_truth': '',
                'correct': True,
                'similarity': 1.0
            }
        else:
            # 一个为空一个不为空
            details[field_name] = {
                'extracted': str(extracted_value)[:100],
                'ground_truth': str(gt_value)[:100],
                'correct': False,
                'similarity': 0
            }
    
    overall_accuracy = (correct / total * 100) if total > 0 else 0
    
    return {
        'overall': round(overall_accuracy, 2),
        'correct_fields': correct,
        'total_fields': total,
        'details': details
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件上传'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件格式'}), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 执行OCR识别
        print(f'正在识别: {filepath}')
        print(f'文件大小: {os.path.getsize(filepath)} bytes')
        
        result = ocr.ocr(filepath)
        
        print(f'OCR原始结果类型: {type(result)}')
        
        # ✅ 处理新版本 PaddleOCR 返回的字典格式
        texts = []
        scores = []
        
        if result and isinstance(result, list) and len(result) > 0:
            first_result = result[0]
            
            # 新版本返回字典格式
            if isinstance(first_result, dict):
                print('检测到新版本 PaddleOCR 字典格式')
                
                rec_texts = first_result.get('rec_texts', [])
                rec_scores = first_result.get('rec_scores', [])
                
                print(f'识别到 {len(rec_texts)} 个文本块')
                
                for text, score in zip(rec_texts, rec_scores):
                    text = str(text).strip()
                    if text:
                        texts.append(text)
                        scores.append(float(score))
            
            # 旧版本返回列表格式
            elif isinstance(first_result, list):
                print('检测到旧版本 PaddleOCR 列表格式')
                
                for line in first_result:
                    try:
                        if line and len(line) >= 2:
                            if isinstance(line[1], tuple) and len(line[1]) >= 2:
                                text = str(line[1][0]).strip()
                                score = float(line[1][1])
                                
                                if text:
                                    texts.append(text)
                                    scores.append(score)
                    except Exception as e:
                        print(f'处理单行时出错: {e}')
                        continue
        
        print(f'✅ 最终识别到 {len(texts)} 行文字')
        
        if len(texts) == 0:
            return jsonify({
                'error': '未识别到文字内容',
                'detail': '图片可能质量不佳或不包含文字'
            }), 400
        
        # 打印前几行识别结果
        print('\n识别结果预览:')
        for i, (text, score) in enumerate(list(zip(texts, scores))[:10]):
            print(f'  {i+1}. {text[:60]:<60} (置信度: {score*100:.1f}%)')
        
        # 提取关键字段
        extracted_data = extract_bill_info(texts)
        
        # 计算准确率（如果存在验证数据）
        accuracy = None
        original_filename = secure_filename(file.filename)  # 原始文件名（不带时间戳）
        if original_filename in check_data:
            print(f'📊 找到验证数据，正在计算准确率...')
            ground_truth = check_data[original_filename]
            accuracy = calculate_accuracy(extracted_data, ground_truth)
            print(f'✅ 准确率: {accuracy["overall"]}% ({accuracy["correct_fields"]}/{accuracy["total_fields"]} 字段正确)')
        else:
            print(f'⚠️ 未找到验证数据: {original_filename}')
        
        # 构建返回结果
        ocr_data = {
            'filename': filename,
            'total_lines': len(texts),
            'average_confidence': sum(scores) / len(scores) if scores else 0,
            'texts': [
                {
                    'text': text,
                    'confidence': float(score)
                }
                for text, score in zip(texts, scores)
            ],
            'extracted': extracted_data,
            'accuracy': accuracy
        }
        
        # 保存结果
        result_filename = f"{timestamp}_result.json"
        result_path = os.path.join(app.config['OUTPUT_FOLDER'], result_filename)
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(ocr_data, f, ensure_ascii=False, indent=2)
        
        # 保存纯文本结果
        txt_filename = f"{timestamp}_ocr.txt"
        txt_path = os.path.join(app.config['OUTPUT_FOLDER'], txt_filename)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"识别文件: {filename}\n")
            f.write(f"识别时间: {timestamp}\n")
            f.write(f"总行数: {len(texts)}\n")
            f.write(f"平均置信度: {ocr_data['average_confidence']*100:.2f}%\n")
            f.write("="*80 + "\n\n")
            for i, (text, score) in enumerate(zip(texts, scores), 1):
                f.write(f"{i:3d}. {text:<80} (置信度: {score*100:.1f}%)\n")
        
        print(f'\n✅ 识别完成！保存到: {result_filename}')
        print(f'   文本文件: {txt_filename}')
        
        return jsonify({
            'success': True,
            'data': ocr_data,
            'result_file': result_filename,
            'uploaded_file': filename
        })
            
    except Exception as e:
        print(f'\n❌ 错误: {str(e)}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

def extract_bill_info(texts):
    """使用 HKBU GenAI (Gemini 2.5 Pro) 提取提单关键信息 - 增強版"""
    import requests
    import json
    import os
    from dotenv import load_dotenv
    
    # 加载环境变量
    load_dotenv()
    
    API_URL = os.getenv('API_URL', 'https://genai.hkbu.edu.hk/api/v0/rest/deployments/gemini-2.5-pro/chat/completions?api-version=v1')
    API_KEY = os.getenv('API_KEY', '1cd1c0a0-6d63-4c4b-9aba-ab0f07f86d71')
    
    # 合并所有OCR文本，保留行號方便定位
    full_text = "\n".join([f"[{i+1}] {str(t)}" for i, t in enumerate(texts) if t])
    
    # 改進版提示詞 - 更詳細的指引
    prompt = f"""你是一個專業的海運提單數據提取專家。請從以下OCR識別的文本中準確提取關鍵信息。

OCR文本（帶行號）：
{full_text}

**提取規則**：
1. 提單號 (B/L NO): 通常在文件頂部，格式如 217077365、OH-123456、MAEU123456789
2. 船名 (VESSEL): 船舶名稱，通常全大寫，如 COSCO SHIPPING、MAERSK LINE
3. 航次 (VOYAGE): 航次號碼，通常在船名附近
4. 發貨人 (SHIPPER): 標註 "SHIPPER" 的公司名稱和地址
5. 收貨人 (CONSIGNEE): 標註 "CONSIGNEE" 的公司名稱和地址
6. 裝貨港 (PORT OF LOADING): 出發港口，如 Shanghai, China
7. 卸貨港 (PORT OF DISCHARGE): 目的港口，如 Los Angeles, USA
8. 貨物描述: 標註 "DESCRIPTION" 或 "CARGO" 的內容
9. 毛重 (GROSS WEIGHT): 包含單位，如 2000 KG
10. 體積 (MEASUREMENT): 包含單位，如 50 CBM

請以JSON格式返回：
{{
    "bill_info": {{
        "B/L NO": "提單號",
        "VESSEL": "船名",
        "VOYAGE": "航次",
        "PORT OF LOADING": "裝貨港",
        "PORT OF DISCHARGE": "卸貨港",
        "PLACE OF DELIVERY": "交貨地點",
        "GROSS WEIGHT": "毛重（含單位）",
        "MEASUREMENT": "體積（含單位）",
        "cargo_description": "貨物描述"
    }},
    "shipper": {{
        "name": "發貨人公司全名",
        "address": ["地址行1", "地址行2", "地址行3"]
    }},
    "consignee": {{
        "name": "收貨人公司全名",
        "address": ["地址行1", "地址行2", "地址行3"]
    }},
    "cargo": ["貨物項目1", "貨物項目2"]
}}

**重要**：
- 只返回純JSON，不要markdown標記
- 找不到的字段返回空字符串或空數組
- 保留原始格式和大小寫
- 地址和貨物描述分行處理"""

    try:
        # 构建请求
        headers = {
            'Content-Type': 'application/json',
            'api-key': API_KEY
        }
        
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "你是一個專業的海運提單數據提取專家，擁有超過10年的經驗。你非常熟悉各種提單格式（MAERSK、COSCO、MSC等）。你只返回純JSON格式，不包含任何markdown標記、代碼塊符號或額外說明。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,  # 降低隨機性，提高準確性
            "max_tokens": 3000,  # 增加token數量
            "top_p": 0.95
        }
        
        print('📡 正在调用 HKBU GenAI API...')
        
        # 发送请求
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30  # 30秒超时
        )
        
        # 检查响应状态
        if response.status_code != 200:
            print(f'❌ API 请求失败: {response.status_code}')
            print(f'错误信息: {response.text}')
            raise Exception(f'API返回错误: {response.status_code}')
        
        # 解析响应
        response_data = response.json()
        print('✅ API 调用成功')
        
        # 提取LLM返回的内容
        result_text = response_data['choices'][0]['message']['content'].strip()
        
        print(f'📝 LLM 原始返回:\n{result_text}\n')
        
        # 清理返回内容（移除可能的markdown代码块标记）
        if result_text.startswith('```'):
            # 移除markdown代码块
            lines = result_text.split('\n')
            result_text = '\n'.join(lines[1:-1])  # 去掉第一行和最后一行
            if result_text.startswith('json'):
                result_text = result_text[4:].strip()
        
        # 解析JSON
        result = json.loads(result_text)
        
        print('✅ JSON 解析成功')
        print(f'📊 提取到的数据:\n{json.dumps(result, ensure_ascii=False, indent=2)}\n')
        
        # 转换为系统需要的格式
        info = {
            'shipper': {
                'name': result.get('shipper_name', ''),
                'address': [line.strip() for line in result.get('shipper_address', '').split('\n') if line.strip()]
            },
            'consignee': {
                'name': result.get('consignee_name', ''),
                'address': [line.strip() for line in result.get('consignee_address', '').split('\n') if line.strip()]
            },
            'bill_info': {
                'B/L NO': result.get('bl_number', ''),
                'VESSEL': result.get('vessel', ''),
                'VOYAGE': result.get('voyage', ''),
                'PORT OF LOADING': result.get('port_of_loading', ''),
                'PORT OF DISCHARGE': result.get('port_of_discharge', ''),
                'PLACE OF DELIVERY': result.get('place_of_delivery', ''),
                'GROSS WEIGHT': result.get('gross_weight', ''),
                'MEASUREMENT': result.get('measurement', ''),
            },
            'cargo': [line.strip() for line in result.get('cargo_description', '').split('\n') if line.strip()] if result.get('cargo_description') else [],
            'container_info': result.get('container_info', '')
        }
        
        return info
        
    except requests.exceptions.Timeout:
        print('❌ API 请求超时')
        return {
            'shipper': {'name': '', 'address': []},
            'consignee': {'name': '', 'address': []},
            'bill_info': {},
            'cargo': [],
            'error': 'API请求超时'
        }
        
    except requests.exceptions.RequestException as e:
        print(f'❌ 网络请求失败: {str(e)}')
        return {
            'shipper': {'name': '', 'address': []},
            'consignee': {'name': '', 'address': []},
            'bill_info': {},
            'cargo': [],
            'error': f'网络请求失败: {str(e)}'
        }
        
    except json.JSONDecodeError as e:
        print(f'❌ JSON 解析失败: {str(e)}')
        print(f'原始返回内容: {result_text}')
        return {
            'shipper': {'name': '', 'address': []},
            'consignee': {'name': '', 'address': []},
            'bill_info': {},
            'cargo': [],
            'error': f'JSON解析失败: {str(e)}'
        }
        
    except Exception as e:
        print(f'❌ LLM 提取失败: {str(e)}')
        import traceback
        traceback.print_exc()
        
        return {
            'shipper': {'name': '', 'address': []},
            'consignee': {'name': '', 'address': []},
            'bill_info': {},
            'cargo': [],
            'error': f'LLM提取失败: {str(e)}'
        }

@app.route('/history')
def history():
    """查看历史记录"""
    results = []
    if os.path.exists(app.config['OUTPUT_FOLDER']):
        for filename in sorted(os.listdir(app.config['OUTPUT_FOLDER']), reverse=True):
            if filename.endswith('.json'):
                filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        results.append({
                            'filename': filename,
                            'timestamp': filename.split('_')[0] + '_' + filename.split('_')[1] if '_' in filename else filename,  # ✅ 添加安全检查
                            'data': data
                        })
                except Exception as e:
                    print(f'读取历史记录失败: {filename}, 错误: {e}')
    return jsonify({'success': True, 'results': results})

@app.route('/download/<filename>')
def download_file(filename):
    """下载结果文件"""
    try:
        return send_file(
            os.path.join(app.config['OUTPUT_FOLDER'], filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/upload-to-blockchain', methods=['POST'])
def upload_to_blockchain():
    """
    将OCR结果上传到IPFS并铸造NFT
    接受参数：
    - ocr_result_file: OCR结果JSON文件名（在outputs目录中）
    - image_file: 可选，原始图片文件名（在uploads目录中）
    """
    try:
        data = request.json
        ocr_result_file = data.get('ocr_result_file')
        image_file = data.get('image_file')
        
        if not ocr_result_file:
            return jsonify({
                'success': False,
                'error': '缺少ocr_result_file参数'
            }), 400
        
        # 构建完整路径
        ocr_result_path = os.path.join(app.config['OUTPUT_FOLDER'], ocr_result_file)
        
        if not os.path.exists(ocr_result_path):
            return jsonify({
                'success': False,
                'error': f'OCR结果文件不存在: {ocr_result_file}'
            }), 404
        
        # 如果提供了图片文件，构建路径
        image_path = None
        if image_file:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file)
            if not os.path.exists(image_path):
                print(f'⚠️ 图片文件不存在: {image_file}，将只上传数据')
                image_path = None
        
        # 初始化区块链桥接器
        bridge = OCRBlockchainBridge()
        
        # 处理OCR结果并上传到区块链
        result = bridge.process_ocr_result(ocr_result_path, image_path)
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        print(f'❌ 上传到区块链失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'上传失败: {str(e)}'
        }), 500

@app.route('/ocr-and-mint', methods=['POST'])
def ocr_and_mint():
    """
    一站式服务：OCR识别 + 上传IPFS + 铸造NFT
    直接上传图片，完成全流程
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # 1. 保存上传的文件
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            print(f'\n{"="*60}')
            print(f'开始OCR识别并上链流程')
            print(f'{"="*60}\n')
            
            # 2. 执行OCR识别
            print(f'步骤 1/3: OCR识别...')
            result = ocr.ocr(filepath)
            
            texts = []
            scores = []
            
            if result and isinstance(result, list) and len(result) > 0:
                first_result = result[0]
                
                if isinstance(first_result, dict):
                    rec_texts = first_result.get('rec_texts', [])
                    rec_scores = first_result.get('rec_scores', [])
                    
                    for text, score in zip(rec_texts, rec_scores):
                        text = str(text).strip()
                        if text:
                            texts.append(text)
                            scores.append(float(score))
                
                elif isinstance(first_result, list):
                    for line in first_result:
                        try:
                            if line and len(line) >= 2:
                                if isinstance(line[1], tuple) and len(line[1]) >= 2:
                                    text = str(line[1][0]).strip()
                                    score = float(line[1][1])
                                    
                                    if text:
                                        texts.append(text)
                                        scores.append(score)
                        except Exception as e:
                            print(f'处理单行时出错: {e}')
                            continue
            
            print(f'✅ 识别到 {len(texts)} 行文字')
            
            # 3. 智能提取结构化数据
            print(f'步骤 2/3: 提取结构化数据...')
            extracted_data = smart_extract(texts)
            
            # 4. 保存OCR结果
            avg_confidence = sum(scores) / len(scores) if scores else 0
            ocr_result = {
                'filename': unique_filename,
                'total_lines': len(texts),
                'average_confidence': avg_confidence,
                'texts': [{'text': t, 'confidence': s} for t, s in zip(texts, scores)],
                'extracted_data': extracted_data
            }
            
            result_filename = f"{timestamp}_result.json"
            result_filepath = os.path.join(app.config['OUTPUT_FOLDER'], result_filename)
            
            with open(result_filepath, 'w', encoding='utf-8') as f:
                json.dump(ocr_result, f, indent=2, ensure_ascii=False)
            
            print(f'✅ OCR结果已保存: {result_filename}')
            
            # 5. 上传到区块链
            print(f'步骤 3/3: 上传到IPFS并铸造NFT...')
            bridge = OCRBlockchainBridge()
            blockchain_result = bridge.process_ocr_result(result_filepath, filepath)
            
            # 6. 合并结果
            final_result = {
                'success': True,
                'ocr': {
                    'filename': unique_filename,
                    'total_lines': len(texts),
                    'average_confidence': avg_confidence,
                    'result_file': result_filename
                },
                'blockchain': blockchain_result
            }
            
            print(f'\n{"="*60}')
            print(f'✅ 全流程完成！')
            print(f'{"="*60}\n')
            
            return jsonify(final_result)
            
        except Exception as e:
            print(f'❌ 处理失败: {e}')
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    # 确保文件夹存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    print('='*80)
    print('🚀 提单OCR识别系统启动中...')
    print('='*80)
    print('📍 访问地址: http://127.0.0.1:5000')
    print('📍 或者访问: http://localhost:5000')
    print('='*80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)