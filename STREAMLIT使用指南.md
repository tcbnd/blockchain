# 🚀 Streamlit 使用指南

## 📦 安裝 Streamlit

```bash
# 安裝 Streamlit
pip3 install streamlit

# 或者更新 requirements.txt
echo "streamlit>=1.30.0" >> requirements.txt
pip3 install -r requirements.txt
```

## 🎯 啟動應用

### 方法1：直接運行
```bash
streamlit run streamlit_app.py
```

### 方法2：指定端口
```bash
streamlit run streamlit_app.py --server.port 8501
```

### 方法3：允許外部訪問
```bash
streamlit run streamlit_app.py --server.address 0.0.0.0
```

### 方法4：背景運行
```bash
nohup streamlit run streamlit_app.py &
```

## 🌐 訪問地址

啟動後會看到：
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

- **本地訪問**: http://localhost:8501
- **網絡訪問**: http://你的IP:8501

## ✨ Streamlit 功能特點

### 對比 Flask Web

| 功能 | Flask | Streamlit |
|-----|-------|-----------|
| 開發速度 | 需要寫HTML/CSS | 純Python，超快 |
| 互動性 | 需要JavaScript | 內建互動組件 |
| 部署難度 | 中等 | 簡單 |
| 實時更新 | 需要配置 | 自動熱重載 |
| 數據展示 | 需要圖表庫 | 內建圖表 |
| 適合場景 | 生產環境 | 原型/內部工具 |

### Streamlit 優勢

1. **零前端代碼** - 只用Python
2. **即時預覽** - 修改代碼立即看到效果
3. **豐富組件** - 按鈕、滑塊、圖表等開箱即用
4. **狀態管理** - `st.session_state` 輕鬆管理狀態
5. **快速原型** - 10分鐘搭建原型

## 🎨 界面功能

### 標籤頁1：📤 上傳識別
- 拖放或選擇圖片
- 預覽圖片
- OCR識別
- 顯示統計卡片
- 查看完整文本

### 標籤頁2：⛓️ 區塊鏈上傳
- 一鍵上傳到IPFS
- 鑄造NFT
- 顯示IPFS連結
- 顯示區塊鏈信息
- Etherscan連結

### 標籤頁3：📜 歷史記錄
- 查看所有處理過的文件
- 顯示統計信息
- 快速預覽結果

### 標籤頁4：ℹ️ 關於
- 系統介紹
- 技術棧
- 文檔連結

## 🔧 配置要求

### 必需配置（.env）
```bash
# Pinata IPFS
PINATA_API_KEY=your_api_key
PINATA_SECRET_KEY=your_secret_key

# 可選：NFT鑄造
CONTRACT_ADDRESS=0x你的合約地址
PRIVATE_KEY=0x你的私鑰

# 可選：AI提取
API_URL=https://genai.hkbu.edu.hk/...
API_KEY=your_api_key
```

### 文件夾結構
```
blockchain/
├── streamlit_app.py      # Streamlit主程序
├── ocr_to_blockchain.py  # 區塊鏈橋接
├── uploads/              # 上傳的圖片
├── outputs/              # OCR結果
└── .env                  # 環境配置
```

## 💡 使用流程

### 完整流程
1. 啟動: `streamlit run streamlit_app.py`
2. 打開瀏覽器: http://localhost:8501
3. 切換到「📤 上傳識別」
4. 上傳提單圖片
5. 點擊「🚀 開始識別」
6. 查看識別結果
7. 切換到「⛓️ 區塊鏈上傳」
8. 點擊「🔗 開始上傳」
9. 等待處理完成
10. 查看IPFS連結和NFT信息

### 快速測試
```bash
# 1. 安裝依賴
pip3 install streamlit

# 2. 啟動應用
streamlit run streamlit_app.py

# 3. 瀏覽器會自動打開
```

## 🎯 提高提取準確率的方法

### 1. 改進的Prompt（已完成）
- ✅ 添加行號方便AI定位
- ✅ 詳細的字段提取規則
- ✅ 更專業的system角色
- ✅ 提高temperature精度

### 2. 圖片預處理
```python
# 在OCR前預處理圖片
from PIL import Image, ImageEnhance

def enhance_image(image):
    # 提高對比度
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)
    
    # 提高銳化
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)
    
    return image
```

### 3. 多次識別取最佳
```python
# 多次OCR取置信度最高的結果
results = []
for _ in range(3):
    result = ocr.ocr(image)
    results.append(result)

# 選擇平均置信度最高的
best_result = max(results, key=lambda x: avg_confidence(x))
```

### 4. 字段驗證
```python
# 驗證提取的字段格式
def validate_bl_number(bl_no):
    # 提單號格式驗證
    patterns = [
        r'^\d{9}$',           # 9位數字
        r'^[A-Z]{4}\d+$',     # 4字母+數字
        r'^[A-Z]+-\d+$'       # 字母-數字
    ]
    return any(re.match(p, bl_no) for p in patterns)
```

### 5. 使用OCR專用模型
```python
# 切換到更精確的模型
ocr = PaddleOCR(
    use_textline_orientation=True,
    lang='en',
    det_model_dir='path/to/better_det_model',
    rec_model_dir='path/to/better_rec_model',
    use_angle_cls=True,  # 啟用角度分類
    use_gpu=True         # 使用GPU加速
)
```

## 📊 性能優化

### Streamlit緩存
```python
@st.cache_resource
def init_ocr():
    return PaddleOCR(...)

@st.cache_data
def process_image(image_bytes):
    # 處理圖片
    pass
```

### 異步處理
```python
import asyncio

async def upload_to_ipfs_async(data):
    # 異步上傳
    pass
```

## 🚀 部署到生產環境

### 使用Streamlit Cloud（免費）
1. Push代碼到GitHub
2. 訪問 https://streamlit.io/cloud
3. 連接GitHub倉庫
4. 添加secrets（環境變量）
5. 點擊部署

### 使用Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py"]
```

### 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 🎨 自定義樣式

### 修改主題
創建 `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### 添加Logo
```python
st.sidebar.image("logo.png", use_column_width=True)
```

## 📱 移動端優化

Streamlit自動響應式，但可以：
```python
# 檢測移動端
if st.session_state.get('is_mobile'):
    # 移動端佈局
    st.columns(1)
else:
    # 桌面端佈局
    st.columns([1, 2])
```

## 🔍 調試技巧

```python
# 顯示變量
st.write("調試信息:", variable)

# 顯示完整對象
st.json(data)

# 顯示代碼
with st.echo():
    result = process_data()

# 進度條
progress_bar = st.progress(0)
for i in range(100):
    progress_bar.progress(i + 1)
```

## 📚 更多資源

- [Streamlit文檔](https://docs.streamlit.io)
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Streamlit論壇](https://discuss.streamlit.io)
- [組件庫](https://streamlit.io/components)

## 🎉 總結

你依家有：
- ✅ Flask版本（生產環境用）
- ✅ Streamlit版本（快速原型/內部工具）
- ✅ 改進的提取邏輯
- ✅ 完整的文檔

**推薦使用場景**：
- 🏢 內部使用 → Streamlit（簡單快速）
- 🌐 對外服務 → Flask（更靈活）
- 🧪 原型測試 → Streamlit（超快開發）

試下啦！🚀
