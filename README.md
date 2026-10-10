# 🚀 Quick Start Guide - OCR to Blockchain

## Step-by-Step Setup

### 1. Check Your Environment (2 minutes)

Run the test script to verify everything is configured:

```bash
python test_integration.py
```

This will check:
- ✅ Environment variables
- ✅ Python packages
- ✅ Pinata connection
- ✅ OCR files
- ✅ Blockchain setup

### 2. Process Your First Bill of Lading (5 minutes)

#### Option A: Use Existing OCR Result

```bash
# Find an existing OCR result
ls outputs/*_result.json

# Process it
python ocr_to_blockchain.py outputs/20260108_142146_result.json
```

#### Option B: OCR + Blockchain in One Step

Start the web server:
```bash
python app.py
```

Then upload a bill image via browser:
```
http://localhost:5000
```

Or use curl:
```bash
curl -X POST http://localhost:5000/ocr-and-mint \
  -F "file=@test_images/your_bill.png"
```

### 3. Verify the Results

After processing, you'll get:

**Console Output:**
```
✅ 数据已上传到IPFS: QmXxXxXxXxXxXxXx...
✅ 文件已上传到IPFS: QmYyYyYyYyYyYyYy...
✅ NFT铸造成功
```

**Blockchain Result File:**
`outputs/TIMESTAMP_blockchain.json` contains:
- Bill data extracted from OCR
- IPFS hashes and URLs
- Transaction hash and Token ID

**View on IPFS:**
```
https://gateway.pinata.cloud/ipfs/YOUR_IPFS_HASH
```

**View on Blockchain:**
```
https://amoy.polygonscan.com/tx/YOUR_TX_HASH
```

## 📊 Usage Examples

### Example 1: Process Latest OCR Result

```bash
# Get latest result file
LATEST=$(ls -t outputs/*_result.json | head -1)

# Process it
python ocr_to_blockchain.py $LATEST
```

### Example 2: Batch Process All Files

```bash
# Process all OCR results in outputs folder
python batch_process.py batch

# Check the log
cat batch_process_log_*.json
```

### Example 3: Web API Integration

```python
import requests

# Upload and process in one call
files = {'file': open('bill_of_lading.png', 'rb')}
response = requests.post('http://localhost:5000/ocr-and-mint', files=files)

result = response.json()
print(f"IPFS URL: {result['blockchain']['ipfs']['dataUrl']}")
print(f"Token ID: {result['blockchain']['blockchain']['tokenId']}")
```

### Example 4: Python Script Integration

```python
from ocr_to_blockchain import OCRBlockchainBridge

# Initialize bridge
bridge = OCRBlockchainBridge()

# Process OCR result
result = bridge.process_ocr_result(
    ocr_result_path='outputs/20260108_142146_result.json',
    image_path='uploads/20260108_142146_bill.png'
)

# Access results
print(f"Bill Number: {result['billData']['billNumber']}")
print(f"IPFS Hash: {result['ipfs']['dataHash']}")
print(f"View: {result['ipfs']['dataUrl']}")
```

## 🔧 Troubleshooting

### "PINATA_API_KEY not found"

**Solution:**
1. Make sure `.env` file exists
2. Copy from example: `cp env.example .env`
3. Edit `.env` and add your Pinata keys

```bash
PINATA_API_KEY=your_actual_key_here
PINATA_SECRET_KEY=your_actual_secret_here
```

### "No OCR result files found"

**Solution:**
First run OCR to generate results:

```bash
python app.py  # Then upload images via web interface
```

Or use existing test images:
```bash
ls test_images/
```

### "Contract deployment failed"

**Solution:**
1. Check you have testnet ETH
2. Get from faucet: https://www.alchemy.com/faucets/ethereum-sepolia
3. Verify network: `npx hardhat run scripts/deploy.js --network sepolia`

### "Module not found"

**Solution:**
Install Python dependencies:
```bash
pip install -r requirements.txt
```

Install Node.js dependencies:
```bash
npm install
```

## 📈 Performance Tips

1. **Batch Processing**: Process multiple files at once
   ```bash
   python batch_process.py batch
   ```

2. **Use Background Jobs**: For production, use Celery or similar
   ```python
   # app.py can be integrated with task queue
   ```

3. **Cache OCR Results**: Don't re-process same images
   ```bash
   # Check if result exists before OCR
   ls outputs/${timestamp}_result.json
   ```

## 🎯 Next Steps

1. **Integrate with Frontend**: Update [frontend/app.js](frontend/app.js) to call new endpoints

2. **Add More Features**:
   - Email notifications
   - Webhook callbacks
   - QR code generation

3. **Deploy to Production**:
   - Use proper web server (gunicorn, nginx)
   - Set up SSL certificates
   - Configure proper logging

## 📚 Additional Resources

- Full documentation: [OCR_BLOCKCHAIN_INTEGRATION.md](OCR_BLOCKCHAIN_INTEGRATION.md)
- Smart contract: [contracts/BillOfLadingNFT.sol](contracts/BillOfLadingNFT.sol)
- API reference: See Flask routes in [app.py](app.py)

## 💡 Pro Tips

1. **Save API Costs**: Test with small batches first
2. **Monitor Gas**: Check gas prices before minting many NFTs
3. **Backup Data**: Keep local copies of important results
4. **Version Control**: Don't commit `.env` file!

## ✨ Success Checklist

- [ ] Environment variables configured
- [ ] Pinata connection successful
- [ ] OCR results generated
- [ ] First file processed successfully
- [ ] IPFS links accessible
- [ ] NFT minted and visible on blockchain

---

**Need Help?** Open an issue or check the troubleshooting section in the main documentation.
