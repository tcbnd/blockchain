# OCR to Blockchain Integration

This system connects the OCR (Optical Character Recognition) system with blockchain technology through Pinata IPFS, enabling automatic extraction of Bill of Lading data and minting as NFTs.

## 🌟 Features

- **OCR Recognition**: Extract text and structured data from Bill of Lading images
- **IPFS Storage**: Upload both images and data to IPFS via Pinata
- **NFT Minting**: Automatically mint NFTs on Ethereum Sepolia testnet
- **Data Integrity**: Calculate and store data hashes on-chain
- **Batch Processing**: Process multiple OCR results at once
- **REST API**: Web interface and API endpoints for easy integration

## 📋 Prerequisites

1. **Python 3.8+** with required packages
2. **Node.js 16+** with Hardhat
3. **Pinata Account** with API keys
4. **Polygon Wallet** with MATIC tokens
5. **Deployed Smart Contract** (BillOfLadingNFT)

## 🚀 Quick Start

### 1. Configure Environment

Copy and edit the environment file:

```bash
cp env.example .env
```

Update these critical values in `.env`:

```env
# Pinata IPFS Configuration
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key

# Blockchain Configuration
PRIVATE_KEY=your_wallet_private_key
CONTRACT_ADDRESS=your_deployed_contract_address

# Network RPC
SEPOLIA_RPC_URL=https://ethereum-sepolia-rpc.publicnode.com
```

### 2. Install Dependencies

**Python packages:**
```bash
pip install -r requirements.txt
```

**Node.js packages:**
```bash
npm install
```

### 3. Deploy Smart Contract (if not already deployed)

```bash
npx hardhat run scripts/deploy.js --network sepolia
```

Save the contract address to your `.env` file.

## 💡 Usage

### Method 1: Process Existing OCR Results

If you already have OCR results in the `outputs/` folder:

```bash
# Process a single file
python ocr_to_blockchain.py outputs/20260108_142146_result.json uploads/bill_image.png

# Batch process all files
python batch_process.py batch

# Process specific file with batch script
python batch_process.py single outputs/20260108_142146_result.json
```

### Method 2: OCR + Blockchain in One Step

Start the Flask web server:

```bash
python app.py
```

Then use the API endpoint:

```bash
# Complete flow: OCR + IPFS + NFT
curl -X POST http://localhost:5000/ocr-and-mint \
  -F "file=@/path/to/bill_of_lading.png"
```

Or via the web interface:
- Open http://localhost:5000
- Upload a Bill of Lading image
- Click "OCR and Mint NFT"

### Method 3: Upload Existing OCR Results via API

```bash
curl -X POST http://localhost:5000/upload-to-blockchain \
  -H "Content-Type: application/json" \
  -d '{
    "ocr_result_file": "20260108_142146_result.json",
    "image_file": "20260108_142146_bill.png"
  }'
```

## 📁 File Structure

```
blockchain/
├── ocr_to_blockchain.py      # Main integration bridge
├── batch_process.py           # Batch processing tool
├── app.py                     # Flask web server (updated)
├── scripts/
│   ├── mintFromOCR.js        # Hardhat script for minting
│   └── deploy.js             # Contract deployment
├── outputs/                   # OCR results
│   ├── *_result.json         # OCR extracted data
│   └── *_blockchain.json     # Blockchain processing results
├── uploads/                   # Original images
└── utils/
    └── pinataClient.js       # Pinata IPFS client
```

## 🔄 Workflow

```
1. Image Upload
   ↓
2. OCR Processing (PaddleOCR)
   ↓
3. Data Extraction (AI-powered)
   ↓
4. Upload Image to IPFS (Pinata)
   ↓
5. Upload Data to IPFS (Pinata)
   ↓
6. Calculate Data Hash
   ↓
7. Mint NFT on Polygon
   ↓
8. Return Results
```

## 📊 Output Format

After processing, you'll get a blockchain result JSON:

```json
{
  "success": true,
  "billData": {
    "billNumber": "BOL-217077365",
    "vessel": "MAERSK VESSEL",
    "shipper": {...},
    "consignee": {...},
    ...
  },
  "ipfs": {
    "dataHash": "QmXxXxXxXxXxXxXx...",
    "dataUrl": "https://gateway.pinata.cloud/ipfs/QmXxXx...",
    "imageHash": "QmYyYyYyYyYyYyYy...",
    "imageUrl": "https://gateway.pinata.cloud/ipfs/QmYyYy..."
  },
  "blockchain": {
    "dataHash": "0xabcdef123456...",
    "contractAddress": "0x1234567890abcdef...",
    "tokenId": "1",
    "transactionHash": "0x9876543210fedcba..."
  },
  "timestamp": "2026-01-16T10:30:00"
}
```

## 🔍 Verification

### Verify on IPFS

```bash
# View data on IPFS
curl https://gateway.pinata.cloud/ipfs/YOUR_DATA_HASH

# View image on IPFS
open https://gateway.pinata.cloud/ipfs/YOUR_IMAGE_HASH
```

### Verify on Blockchain

Visit Etherscan (Sepolia Testnet):
```
https://sepolia.etherscan.io/tx/YOUR_TRANSACTION_HASH
```

Or query the contract:
```bash
npx hardhat run scripts/getContractInfo.js --network sepolia
```

## 🛠️ API Endpoints

### POST /ocr-and-mint
Upload image → OCR → IPFS → Mint NFT (complete flow)

**Request:**
```bash
curl -X POST http://localhost:5000/ocr-and-mint \
  -F "file=@bill.png"
```

**Response:**
```json
{
  "success": true,
  "ocr": {...},
  "blockchain": {...}
}
```

### POST /upload-to-blockchain
Process existing OCR result → IPFS → Mint NFT

**Request:**
```bash
curl -X POST http://localhost:5000/upload-to-blockchain \
  -H "Content-Type: application/json" \
  -d '{
    "ocr_result_file": "20260108_142146_result.json",
    "image_file": "20260108_142146_bill.png"
  }'
```

### POST /ocr
OCR recognition only (existing endpoint)

### GET /history
Get all OCR processing history

## ⚙️ Configuration Options

### OCRBlockchainBridge Class

```python
from ocr_to_blockchain import OCRBlockchainBridge

bridge = OCRBlockchainBridge()

# Process OCR result with image
result = bridge.process_ocr_result(
    ocr_result_path='outputs/result.json',
    image_path='uploads/bill.png'
)

# Upload JSON to IPFS only
ipfs_result = bridge.upload_json_to_pinata(
    json_data={'key': 'value'},
    metadata_name='my-data'
)
```

## 🐛 Troubleshooting

### Error: "PINATA_API_KEY not found"
- Make sure `.env` file exists in the project root
- Check that the keys are correctly set in `.env`

### Error: "CONTRACT_ADDRESS not set"
- Deploy the smart contract first: `npm run deploy:amoy`
- Add the contract address to `.env`

### Error: "insufficient funds"
- Get testnet ETH from Sepolia faucet
- https://www.alchemy.com/faucets/ethereum-sepolia
- https://faucet.quicknode.com/ethereum/sepolia

### NFT not minting but IPFS upload succeeds
- Check if the contract address is correct
- Verify your wallet has enough MATIC
- Check network connectivity to Polygon RPC

## 📚 Additional Resources

- [Pinata Documentation](https://docs.pinata.cloud/)
- [Ethereum Sepolia Testnet](https://sepolia.dev/)
- [Hardhat Documentation](https://hardhat.org/docs)
- [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR)

## 🔐 Security Notes

- **Never commit `.env` file** to version control
- Keep your private keys secure
- Use testnet for development
- Rotate API keys periodically

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📧 Support

For issues and questions, please open an issue on GitHub.
