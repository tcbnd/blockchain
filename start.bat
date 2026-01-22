@echo off
echo 🚀 启动统一版 OCR-to-Blockchain 系统
echo =======================================

echo 🔍 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python未安装或不在PATH中
    echo 请确保Python已正确安装
    pause
    exit /b 1
)

echo ✅ Python环境正常

echo 🔍 检查OCR引擎 (按优先级)...
python -c "import paddleocr; print('✅ PaddleOCR可用 - 最强推荐')" 2>nul || (
    python -c "import easyocr; print('✅ EasyOCR可用 - 推荐')" 2>nul || (
        python -c "import pytesseract; print('✅ Tesseract可用 - 备选')" 2>nul || (
            echo ⚠️ 未找到专业OCR引擎，将使用模拟模式
            echo 💡 建议安装: python -m pip install paddleocr
            echo 💡 或安装: python -m pip install easyocr
        )
    )
)

echo 🔍 检查区块链环境...
if exist .env (
    echo ✅ .env配置文件存在
) else (
    echo ❌ .env配置文件不存在
    echo 请确保配置了PINATA_API_KEY等环境变量
)

if exist node_modules\.bin\hardhat.cmd (
    echo ✅ Hardhat环境可用
) else (
    echo ❌ Hardhat未安装
    echo 请运行: npm install
)

echo.
echo 🌐 启动统一版Web服务器...
echo 📊 功能包括: OCR处理 + 区块链集成 + 可视化界面
echo 🔗 访问地址: http://localhost:5000
echo.
python app_unified.py
