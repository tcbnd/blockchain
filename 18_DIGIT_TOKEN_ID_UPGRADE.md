# 🔢 升級到18位Token ID

## 問題說明

當前合約的Token ID從0開始遞增（1, 2, 3...），需要升級為18位數字的Token ID（例如：100000000000000001）。

---

## 解決方案

### 方案1：部署新合約 ⭐ 推薦

部署新版本的智能合約，Token ID從 `100000000000000000` 開始（18位數字）。

#### 步驟1：編譯新合約

```powershell
npx hardhat compile
```

#### 步驟2：部署新合約到Sepolia測試網

```powershell
npx hardhat run scripts/deploy_v2.js --network sepolia
```

#### 步驟3：更新環境變量

複製輸出的新合約地址，更新 `.env` 文件：

```env
# 舊地址（保留作為備份）
# OLD_CONTRACT_ADDRESS=0x89e89036f3f4dCdFE8DdA8C78E54FfA2D09095ED

# 新地址（18位Token ID）
CONTRACT_ADDRESS=<新合約地址>
```

#### 步驟4：重啟應用

```powershell
py .\app_unified.py
```

#### 步驟5：更新前端合約地址

編輯 `static/wallet.js`，更新合約地址：

```javascript
const contractAddress = '<新合約地址>';
```

---

### Token ID 格式對比

#### 舊合約
```
Token ID: 1
Token ID: 2
Token ID: 3
...
```

#### 新合約 (v2)
```
Token ID: 100000000000000000 (18位)
Token ID: 100000000000000001 (18位)
Token ID: 100000000000000002 (18位)
...
```

---

## 重要說明

### 數據遷移

- ⚠️ 部署新合約後，舊NFT數據**不會自動遷移**
- 舊合約的NFT仍然存在於區塊鏈上
- 如需保留舊數據，需要手動記錄或導出

### 建議做法

1. **測試環境**：先在測試網部署新合約
2. **驗證功能**：確保所有功能正常工作
3. **更新文檔**：記錄新舊合約地址
4. **用戶通知**：如果有其他用戶，需要通知合約地址變更

---

## 完整部署流程

### 1. 備份當前數據

```powershell
# 導出當前OCR結果
Copy-Item -Path "outputs" -Destination "outputs_backup_$(Get-Date -Format 'yyyyMMdd')" -Recurse
```

### 2. 編譯合約

```powershell
npx hardhat compile
```

預期輸出：
```
Compiled 1 Solidity file successfully
```

### 3. 部署新合約

```powershell
npx hardhat run scripts/deploy_v2.js --network sepolia
```

預期輸出：
```
正在部署 BillOfLadingNFT v2 (18位Token ID)...

部署账户: 0x28A69686CE21d33d7b792E807Cdc3e07E8fB8555
账户余额: 123456789000000000 wei

✅ 合约部署成功!
合约地址: 0xNEW_CONTRACT_ADDRESS_HERE

正在测试铸造NFT以验证Token ID...
✅ 测试NFT已铸造!
Token ID: 100000000000000000
Token ID长度: 18 位数字
✅ Token ID格式正确 (18位)
```

### 4. 更新配置

編輯 `.env` 文件：
```env
CONTRACT_ADDRESS=0xNEW_CONTRACT_ADDRESS_HERE
```

編輯 `static/wallet.js` (第6行)：
```javascript
const contractAddress = '0xNEW_CONTRACT_ADDRESS_HERE';
```

### 5. 測試新合約

```powershell
# 重啟應用
py .\app_unified.py

# 在瀏覽器訪問
# http://localhost:5000
```

測試流程：
1. ✅ 上傳新圖片
2. ✅ 執行完整流程
3. ✅ 檢查Token ID是否為18位
4. ✅ 驗證所有功能正常

---

## 驗證Token ID

### 方法1：在應用中查看

1. 鑄造NFT後，查看區塊鏈標籤
2. Token ID應顯示18位數字

### 方法2：在Etherscan查看

1. 訪問：`https://sepolia.etherscan.io/address/<新合約地址>`
2. 點擊 "Contract" → "Read Contract"
3. 查看任何NFT的Token ID

### 方法3：使用Hardhat Console

```powershell
npx hardhat console --network sepolia
```

```javascript
const contract = await ethers.getContractAt("BillOfLadingNFT", "<新合約地址>");
const billNumber = "YOUR_BILL_NUMBER";
const tokenId = await contract.billNumberToTokenId(billNumber);
console.log("Token ID:", tokenId.toString());
console.log("Length:", tokenId.toString().length);
```

---

## 故障排除

### 問題1：部署失敗

**錯誤**: `insufficient funds for gas`

**解決**: 
```powershell
# 檢查賬戶餘額
npx hardhat console --network sepolia
```

```javascript
const [signer] = await ethers.getSigners();
console.log("Address:", signer.address);
console.log("Balance:", ethers.formatEther(await ethers.provider.getBalance(signer.address)), "ETH");
```

如果餘額不足，從 [Sepolia Faucet](https://sepoliafaucet.com) 獲取測試ETH。

### 問題2：Token ID仍然是短數字

**原因**: 可能還在使用舊合約地址

**檢查**:
1. `.env` 文件中的 `CONTRACT_ADDRESS`
2. `static/wallet.js` 中的 `contractAddress`
3. 重啟應用後測試

### 問題3：舊NFT無法訪問

**說明**: 這是正常的，新舊合約是獨立的

**解決**: 如需訪問舊NFT，臨時切換回舊合約地址

---

## Gas費用估算

- **部署合約**: ~0.005 ETH
- **鑄造NFT**: ~0.001 ETH per NFT
- **總計**: 約 0.006 ETH（測試網免費）

---

## 合約對比

| 特性 | 舊合約 | 新合約 (v2) |
|-----|--------|------------|
| Token ID起始 | 0 | 100000000000000000 |
| Token ID位數 | 1-N位 | 固定18位 |
| 功能 | 完整 | 完整 |
| 部署狀態 | 已部署 | 待部署 |
| 地址 | 0x89e8...95ED | 待生成 |

---

## 下一步

1. ✅ 部署新合約
2. ✅ 更新配置文件
3. ✅ 測試Token ID格式
4. ✅ 驗證所有功能
5. ✅ 更新文檔記錄

---

## 參考文檔

- **新合約代碼**: `contracts/BillOfLadingNFT_v2.sol`
- **部署腳本**: `scripts/deploy_v2.js`
- **原合約文檔**: `CONTRACT_DOCUMENTATION.md`
- **Etherscan**: `https://sepolia.etherscan.io`

---

**準備好部署新合約了嗎？運行部署命令開始吧！🚀**
