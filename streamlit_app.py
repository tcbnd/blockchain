"""
提單OCR識別系統 - Streamlit版本
支援OCR識別 + IPFS上傳 + NFT鑄造
"""

import streamlit as st
import os
import json
from datetime import datetime
from PIL import Image
import io
from paddleocr import PaddleOCR
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 初始化PaddleOCR (使用session_state避免重複初始化)
@st.cache_resource
def init_ocr():
    """初始化OCR引擎"""
    return PaddleOCR(use_textline_orientation=True, lang='en')

# 設置頁面配置
st.set_page_config(
    page_title="提單OCR識別系統",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義CSS樣式
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #667eea;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .success-box {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 標題
st.markdown('<h1 class="main-header">📦 提單OCR識別系統</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Bill of Lading OCR Recognition System - Powered by PaddleOCR & Blockchain</p>', unsafe_allow_html=True)

# 側邊欄
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=OCR+System", use_column_width=True)
    st.markdown("### ⚙️ 系統配置")
    
    # 檢查Pinata配置
    pinata_configured = bool(os.getenv('PINATA_API_KEY') and os.getenv('PINATA_SECRET_KEY'))
    if pinata_configured:
        st.success("✅ Pinata IPFS 已配置")
    else:
        st.warning("⚠️ Pinata 未配置")
    
    # 檢查合約配置
    contract_configured = bool(os.getenv('CONTRACT_ADDRESS'))
    if contract_configured:
        st.success("✅ 智能合約已配置")
        st.code(os.getenv('CONTRACT_ADDRESS')[:10] + "...", language=None)
    else:
        st.info("ℹ️ 未配置智能合約")
    
    st.markdown("---")
    st.markdown("### 📊 系統狀態")
    st.metric("OCR引擎", "已就緒", "PaddleOCR")
    st.metric("網絡", "Sepolia", "測試網")
    
    st.markdown("---")
    st.markdown("### 📚 文檔連結")
    st.markdown("[📘 使用指南](OCR_BLOCKCHAIN_INTEGRATION.md)")
    st.markdown("[🚀 快速開始](QUICKSTART.md)")
    st.markdown("[🇭🇰 粵語指南](粵語快速指南.md)")

# 主要內容
tab1, tab2, tab3, tab4 = st.tabs(["📤 上傳識別", "⛓️ 區塊鏈上傳", "📜 歷史記錄", "ℹ️ 關於"])

with tab1:
    st.markdown("### 📤 上傳提單圖片")
    
    # 文件上傳
    uploaded_file = st.file_uploader(
        "選擇提單圖片 (支援 PNG, JPG, JPEG)",
        type=['png', 'jpg', 'jpeg'],
        help="拖放文件或點擊選擇"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 📷 原始圖片")
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True, caption=f"檔案名: {uploaded_file.name}")
            
            # 圖片信息
            st.info(f"""
            **圖片信息**
            - 尺寸: {image.size[0]} x {image.size[1]}
            - 格式: {image.format}
            - 大小: {uploaded_file.size / 1024:.2f} KB
            """)
        
        with col2:
            st.markdown("#### 🔍 OCR識別")
            
            if st.button("🚀 開始識別", type="primary", use_container_width=True):
                with st.spinner("正在識別中，請稍候..."):
                    try:
                        # 保存臨時文件
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        temp_filename = f"{timestamp}_{uploaded_file.name}"
                        temp_path = os.path.join("uploads", temp_filename)
                        os.makedirs("uploads", exist_ok=True)
                        
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # 執行OCR
                        ocr = init_ocr()
                        result = ocr.ocr(temp_path)
                        
                        # 提取文本
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
                                        continue
                        
                        if len(texts) == 0:
                            st.error("❌ 未識別到文字內容")
                        else:
                            # 保存到session_state
                            st.session_state['ocr_result'] = {
                                'texts': texts,
                                'scores': scores,
                                'filename': temp_filename,
                                'temp_path': temp_path,
                                'timestamp': timestamp
                            }
                            
                            st.success(f"✅ 識別完成！共識別到 {len(texts)} 行文字")
                    
                    except Exception as e:
                        st.error(f"❌ 識別失敗: {str(e)}")
        
        # 顯示識別結果
        if 'ocr_result' in st.session_state:
            st.markdown("---")
            st.markdown("### 📊 識別結果")
            
            result = st.session_state['ocr_result']
            texts = result['texts']
            scores = result['scores']
            avg_confidence = sum(scores) / len(scores) * 100 if scores else 0
            
            # 統計卡片
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">識別行數</div>
                    <div class="stat-value">{len(texts)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">平均置信度</div>
                    <div class="stat-value">{avg_confidence:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                high_conf = sum(1 for s in scores if s > 0.9)
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">高置信度</div>
                    <div class="stat-value">{high_conf}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                low_conf = sum(1 for s in scores if s < 0.7)
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">低置信度</div>
                    <div class="stat-value">{low_conf}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 完整識別結果
            with st.expander("📝 查看完整識別文本", expanded=False):
                for i, (text, score) in enumerate(zip(texts, scores), 1):
                    confidence_color = "🟢" if score > 0.9 else "🟡" if score > 0.7 else "🔴"
                    st.text(f"{i:3d}. {confidence_color} {text} ({score*100:.1f}%)")
            
            # 添加準確率對比功能（如果有驗證數據）
            if 'extracted_data' in st.session_state and st.session_state.get('extracted_data'):
                st.markdown("---")
                st.markdown("### 🎯 準確率對比")
                
                extracted = st.session_state['extracted_data']
                
                # 載入驗證數據
                import json
                try:
                    with open('bills_labeled_data.json', 'r', encoding='utf-8') as f:
                        ground_truth_data = json.load(f)
                    
                    # 查找匹配的驗證數據
                    filename_base = result['filename'].rsplit('.', 1)[0]
                    matching_gt = None
                    
                    for item in ground_truth_data:
                        if 'detail' in item and 'file_data' in item['detail']:
                            gt_filename = item['detail']['file_data'].get('file_name', '')
                            gt_base = gt_filename.rsplit('.', 1)[0] if gt_filename else ''
                            if gt_base and filename_base.endswith(gt_base):
                                matching_gt = item
                                break
                    
                    if matching_gt:
                        gt_doc = matching_gt.get('detail', {}).get('documents', [{}])[0]
                        
                        # 對比表格
                        st.markdown("#### 📋 字段對比結果")
                        
                        comparison_data = []
                        
                        # 定義字段對比
                        def get_gt_field(doc, *field_names):
                            for name in field_names:
                                value = doc.get(name, '')
                                if value:
                                    return value
                            return ''
                        
                        def normalize_text(text):
                            if isinstance(text, list):
                                text = ' '.join(str(t) for t in text)
                            import re
                            text = str(text).strip().upper()
                            text = re.sub(r'\s+', ' ', text)
                            text = re.sub(r'[,.:;\-_()]', '', text)
                            return text
                        
                        fields_to_compare = [
                            ('提單號 (B/L NO)', ['bill_info', 'B/L NO'], get_gt_field(gt_doc, 'bill_of_lading__number', 'bl_number')),
                            ('船名 (VESSEL)', ['bill_info', 'VESSEL'], get_gt_field(gt_doc, 'vessel_name', 'vessel')),
                            ('航次 (VOYAGE)', ['bill_info', 'VOYAGE'], get_gt_field(gt_doc, 'vessel_address', 'voyage')),
                            ('裝貨港', ['bill_info', 'PORT OF LOADING'], get_gt_field(gt_doc, 'place_of_loading', 'port_of_loading')),
                            ('卸貨港', ['bill_info', 'PORT OF DISCHARGE'], get_gt_field(gt_doc, 'place_of_delivery', 'port_of_discharge')),
                            ('托運人名稱', ['shipper', 'name'], get_gt_field(gt_doc, 'shipper_company_name', 'shipper_name')),
                            ('收貨人名稱', ['consignee', 'name'], get_gt_field(gt_doc, 'consignee_company_name', 'consignee_name')),
                            ('毛重', ['bill_info', 'GROSS WEIGHT'], get_gt_field(gt_doc, 'total_gross_weight_value', 'gross_weight')),
                        ]
                        
                        correct_count = 0
                        total_count = 0
                        
                        for field_name, extract_keys, gt_value in fields_to_compare:
                            # 獲取提取值
                            extracted_value = extracted
                            for key in extract_keys:
                                if isinstance(extracted_value, dict):
                                    extracted_value = extracted_value.get(key, '')
                                else:
                                    extracted_value = ''
                                    break
                            
                            # 標準化比較
                            extracted_norm = normalize_text(extracted_value)
                            gt_norm = normalize_text(gt_value)
                            
                            is_correct = False
                            if extracted_norm and gt_norm:
                                total_count += 1
                                if extracted_norm == gt_norm or extracted_norm in gt_norm or gt_norm in extracted_norm:
                                    is_correct = True
                                    correct_count += 1
                            
                            # 顯示結果
                            status = "✅" if is_correct else "❌"
                            comparison_data.append({
                                "字段": field_name,
                                "識別結果": str(extracted_value)[:50] + "..." if len(str(extracted_value)) > 50 else str(extracted_value),
                                "正確答案": str(gt_value)[:50] + "..." if len(str(gt_value)) > 50 else str(gt_value),
                                "狀態": status
                            })
                        
                        # 顯示對比表格
                        import pandas as pd
                        df = pd.DataFrame(comparison_data)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        # 顯示準確率
                        if total_count > 0:
                            accuracy = (correct_count / total_count) * 100
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("總字段數", total_count)
                            with col2:
                                st.metric("正確字段數", correct_count)
                            with col3:
                                st.metric("準確率", f"{accuracy:.1f}%", delta=f"{correct_count}/{total_count}")
                        
                        if accuracy >= 80:
                            st.success(f"🎉 準確率優秀！達到 {accuracy:.1f}%")
                        elif accuracy >= 60:
                            st.info(f"👍 準確率良好：{accuracy:.1f}%")
                        else:
                            st.warning(f"⚠️ 準確率有待提高：{accuracy:.1f}%")
                    
                    else:
                        st.info("ℹ️ 未找到對應的驗證數據")
                
                except FileNotFoundError:
                    st.warning("⚠️ 未找到驗證數據文件 (bills_labeled_data.json)")
                except Exception as e:
                    st.error(f"❌ 載入驗證數據失敗: {str(e)}")

with tab2:
    st.markdown("### ⛓️ 上傳到區塊鏈")
    
    if 'ocr_result' not in st.session_state:
        st.info("ℹ️ 請先在「上傳識別」標籤頁進行OCR識別")
    else:
        st.markdown("""
        <div class="info-box">
            <strong>🔗 區塊鏈上傳流程</strong><br>
            1️⃣ 上傳圖片到 Pinata IPFS<br>
            2️⃣ 上傳數據到 Pinata IPFS<br>
            3️⃣ 在 Sepolia 區塊鏈鑄造 NFT
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔗 開始上傳到IPFS並鑄造NFT", type="primary", use_container_width=True):
            if not pinata_configured:
                st.error("❌ 請先配置 Pinata API 密鑰")
            else:
                with st.spinner("正在處理中..."):
                    try:
                        from ocr_to_blockchain import OCRBlockchainBridge
                        import requests
                        
                        # 保存OCR結果到JSON
                        result = st.session_state['ocr_result']
                        timestamp = result['timestamp']
                        texts = result['texts']
                        scores = result['scores']
                        
                        # 步驟1: 使用AI提取提單資料
                        st.info("📡 正在使用 AI 提取提單資料...")
                        
                        # 加入行號幫助定位
                        full_text = "\n".join([f"[{i+1}] {str(t)}" for i, t in enumerate(texts) if t])
                        
                        # 調用 HKBU GenAI API
                        api_url = "https://api.hkbu.edu.hk/genai/v1/chat/completion"
                        api_key = os.getenv('HKBU_GENAI_API_KEY')
                        
                        if not api_key:
                            st.error("❌ 缺少 HKBU GenAI API Key")
                            st.stop()
                        
                        prompt = f"""請從以下OCR識別出的提單(Bill of Lading)文字中，準確提取關鍵信息。每行前有 [行號] 標記。

提取規則：
1. B/L NO (提單號): 通常在右上角，格式如 XXXX123456、OH-23040018、M205607737
2. VESSEL (船名): 在 VESSEL 或 Vessel Name 欄位，如 ONE SWAN、CMA CGM
3. VOYAGE (航次): 在 VOYAGE 或 Voy. 欄位，通常是數字+字母，如 023W、042E
4. PORT OF LOADING (裝貨港): 城市+國家，如 OAKLAND, CA (UNITED STATES)
5. PORT OF DISCHARGE (卸貨港): 城市+國家，如 HO CHI MINH CITY (VIETNAM)
6. PLACE OF DELIVERY (交貨地): 最終目的地
7. SHIPPER (托運人): 公司名稱+地址
8. CONSIGNEE (收貨人): 公司名稱+地址
9. GROSS WEIGHT (毛重): 數字+單位 KGS
10. CONTAINER INFO (貨櫃資訊): 櫃號+類型，如 FFAU3699949 (40HC)

OCR文字:
{full_text}

請以JSON格式返回，字段包含：shipper_name, shipper_address, consignee_name, consignee_address, bl_number, vessel, voyage, port_of_loading, port_of_discharge, place_of_delivery, cargo_description, container_info, gross_weight, measurement"""
                        
                        payload = {
                            "model": "gemini-2.0-flash-exp",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "你係一位有10年經驗的海運提單專家，精通提單格式同各種欄位。請準確提取資料，唔確定嘅欄位留空。"
                                },
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            "temperature": 0.1,
                            "max_tokens": 3000
                        }
                        
                        headers = {
                            "x-api-key": api_key,
                            "Content-Type": "application/json"
                        }
                        
                        response = requests.post(api_url, json=payload, headers=headers)
                        response.raise_for_status()
                        ai_result = response.json()
                        
                        # 解析AI返回的JSON
                        content = ai_result['choices'][0]['message']['content']
                        
                        # 提取JSON (可能被包在```json```裡)
                        import re
                        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                        if json_match:
                            extracted_json = json_match.group(1)
                        else:
                            extracted_json = content
                        
                        extracted_data = json.loads(extracted_json)
                        
                        # 構建完整的OCR結果
                        ocr_data = {
                            'filename': result['filename'],
                            'total_lines': len(texts),
                            'average_confidence': sum(scores) / len(scores),
                            'texts': [
                                {'text': text, 'confidence': float(score)}
                                for text, score in zip(texts, scores)
                            ],
                            'extracted': {
                                'shipper': {
                                    'name': extracted_data.get('shipper_name', ''),
                                    'address': extracted_data.get('shipper_address', '')
                                },
                                'consignee': {
                                    'name': extracted_data.get('consignee_name', ''),
                                    'address': extracted_data.get('consignee_address', '')
                                },
                                'bill_info': {
                                    'B/L NO': extracted_data.get('bl_number', ''),
                                    'VESSEL': extracted_data.get('vessel', ''),
                                    'VOYAGE': extracted_data.get('voyage', ''),
                                    'PORT OF LOADING': extracted_data.get('port_of_loading', ''),
                                    'PORT OF DISCHARGE': extracted_data.get('port_of_discharge', ''),
                                    'PLACE OF DELIVERY': extracted_data.get('place_of_delivery', ''),
                                    'GROSS WEIGHT': extracted_data.get('gross_weight', ''),
                                    'MEASUREMENT': extracted_data.get('measurement', '')
                                },
                                'cargo': extracted_data.get('cargo_description', ''),
                                'container_info': extracted_data.get('container_info', '')
                            }
                        }
                        
                        st.success(f"✅ AI 提取成功！提單號: {extracted_data.get('bl_number', 'N/A')}")
                        
                        # 保存結果
                        os.makedirs("outputs", exist_ok=True)
                        result_filename = f"{timestamp}_result.json"
                        result_path = os.path.join("outputs", result_filename)
                        
                        with open(result_path, 'w', encoding='utf-8') as f:
                            json.dump(ocr_data, f, ensure_ascii=False, indent=2)
                        
                        # 步驟2: 上傳到區塊鏈
                        st.info("🔗 正在上傳到 IPFS 並鑄造 NFT...")
                        bridge = OCRBlockchainBridge()
                        blockchain_result = bridge.process_ocr_result(
                            result_path,
                            result.get('temp_path')
                        )
                        
                        # 保存區塊鏈結果
                        st.session_state['blockchain_result'] = blockchain_result
                        
                        st.success("✅ 完整流程成功！")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ 處理失敗: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
        
        # 顯示區塊鏈結果
        if 'blockchain_result' in st.session_state:
            result = st.session_state['blockchain_result']
            
            # 顯示提取的提單資料
            st.markdown("---")
            st.markdown("### 📋 提取的提單資料")
            
            if result.get('bill_data'):
                bill = result['bill_data']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📄 基本資料")
                    st.text_input("提單編號 (B/L NO)", bill.get('billNumber', 'N/A'), disabled=True)
                    st.text_input("船名 (VESSEL)", bill.get('vessel', 'N/A'), disabled=True)
                    st.text_input("航次 (VOYAGE)", bill.get('voyage', 'N/A'), disabled=True)
                    
                    st.markdown("#### 📍 港口資料")
                    st.text_input("裝貨港", bill.get('portOfLoading', 'N/A'), disabled=True)
                    st.text_input("卸貨港", bill.get('portOfDischarge', 'N/A'), disabled=True)
                    st.text_input("交貨地", bill.get('placeOfDelivery', 'N/A'), disabled=True)
                
                with col2:
                    st.markdown("#### 🏢 托運人")
                    shipper = bill.get('shipper', {})
                    st.text_input("公司名稱", shipper.get('name', 'N/A'), disabled=True)
                    st.text_area("地址", shipper.get('address', 'N/A'), disabled=True, height=80)
                    
                    st.markdown("#### 🏢 收貨人")
                    consignee = bill.get('consignee', {})
                    st.text_input("公司名稱", consignee.get('name', 'N/A'), disabled=True, key="consignee_name")
                    st.text_area("地址", consignee.get('address', 'N/A'), disabled=True, height=80)
                
                st.markdown("#### 📦 貨物資料")
                col3, col4 = st.columns(2)
                with col3:
                    st.text_input("毛重", bill.get('grossWeight', 'N/A'), disabled=True)
                    st.text_input("貨櫃資訊", bill.get('containerInfo', 'N/A'), disabled=True)
                with col4:
                    st.text_input("尺寸", bill.get('measurement', 'N/A'), disabled=True)
                    st.text_input("準確率", f"{bill.get('accuracy', 0):.1f}%", disabled=True)
                
                if bill.get('cargoDescription'):
                    st.text_area("貨物描述", bill.get('cargoDescription', 'N/A'), disabled=True, height=100)
            
            st.markdown("---")
            st.markdown("### 📡 IPFS 信息")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📄 數據")
                if result.get('ipfs', {}).get('dataHash'):
                    st.code(result['ipfs']['dataHash'], language=None)
                    st.link_button(
                        "🔗 查看數據",
                        result['ipfs']['dataUrl'],
                        use_container_width=True
                    )
            
            with col2:
                st.markdown("#### 🖼️ 圖片")
                if result.get('ipfs', {}).get('imageHash'):
                    st.code(result['ipfs']['imageHash'], language=None)
                    st.link_button(
                        "🔗 查看圖片",
                        result['ipfs']['imageUrl'],
                        use_container_width=True
                    )
            
            if result.get('blockchain', {}).get('contractAddress'):
                st.markdown("---")
                st.markdown("### 🔐 區塊鏈信息")
                
                st.text_input("合約地址", result['blockchain']['contractAddress'], disabled=True)
                st.text_input("數據哈希", result['blockchain']['dataHash'], disabled=True)
                
                if contract_configured and result['blockchain'].get('mintResult'):
                    st.success("✅ NFT 鑄造成功！")
                    
                    try:
                        mint_data = json.loads(result['blockchain']['mintResult']) if isinstance(result['blockchain']['mintResult'], str) else result['blockchain']['mintResult']
                        
                        if mint_data.get('success'):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Token ID", mint_data.get('tokenId', 'N/A'))
                                st.metric("Gas 使用量", mint_data.get('gasUsed', 'N/A'))
                            
                            with col2:
                                if mint_data.get('transactionHash'):
                                    st.link_button(
                                        "🔍 查看交易",
                                        f"https://sepolia.etherscan.io/tx/{mint_data['transactionHash']}",
                                        use_container_width=True
                                    )
                    except:
                        pass

with tab3:
    st.markdown("### 📜 歷史記錄")
    
    # 讀取輸出文件夾
    if os.path.exists("outputs"):
        result_files = [f for f in os.listdir("outputs") if f.endswith('_result.json')]
        result_files.sort(reverse=True)
        
        if result_files:
            st.info(f"找到 {len(result_files)} 條歷史記錄")
            
            for filename in result_files[:10]:  # 只顯示最近10條
                filepath = os.path.join("outputs", filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    with st.expander(f"📄 {filename}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("識別行數", data.get('total_lines', 0))
                        
                        with col2:
                            avg_conf = data.get('average_confidence', 0) * 100
                            st.metric("平均置信度", f"{avg_conf:.1f}%")
                        
                        with col3:
                            st.text(f"檔案: {data.get('filename', 'N/A')}")
                except:
                    pass
        else:
            st.warning("暫無歷史記錄")
    else:
        st.warning("輸出文件夾不存在")

with tab4:
    st.markdown("### ℹ️ 關於系統")
    
    st.markdown("""
    ## 📦 提單OCR識別系統
    
    這是一個基於 **PaddleOCR** 的提單識別系統，結合了 **IPFS** 分布式儲存和 **區塊鏈** NFT 技術。
    
    ### 🌟 主要功能
    
    - ✅ **OCR 識別**: 使用 PaddleOCR 進行高精度文字識別
    - ✅ **智能提取**: AI 自動提取提單關鍵信息
    - ✅ **IPFS 儲存**: 通過 Pinata 上傳到 IPFS
    - ✅ **NFT 鑄造**: 在 Sepolia 區塊鏈鑄造 NFT
    - ✅ **歷史記錄**: 完整的處理歷史追蹤
    
    ### 🔧 技術棧
    
    - **前端**: Streamlit
    - **OCR**: PaddleOCR
    - **IPFS**: Pinata
    - **區塊鏈**: Ethereum Sepolia
    - **智能合約**: Solidity + Hardhat
    
    ### 📚 文檔
    
    - [完整文檔](OCR_BLOCKCHAIN_INTEGRATION.md)
    - [快速開始](QUICKSTART.md)
    - [粵語指南](粵語快速指南.md)
    
    ### 👨‍💻 開發者
    
    版本: 2.0 (Streamlit)  
    更新日期: 2026-01-16
    """)

# 頁腳
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #999;">Powered by PaddleOCR, Streamlit & Blockchain Technology</p>',
    unsafe_allow_html=True
)
