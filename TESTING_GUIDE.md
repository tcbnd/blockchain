# 🧪 Contract Functions Testing Guide

## ✅ What Has Been Implemented

### 1. **Wallet Integration** 👛
- Web3.js integrated into the UI
- MetaMask connection/disconnection
- Automatic network detection (Sepolia)
- Display current wallet address and network
- Auto-reconnect on page reload

### 2. **Smart Contract Functions** 🔧

All 6 contract functions are now available in the UI:

#### **Read-Only Functions** (No wallet needed)
1. **Get Bill Data** (`getBillData`) - Query all bill information by Token ID
2. **Check Transferability** (`isTransferable`) - Check if bill can be transferred
3. **Get Token URI** (`tokenURI`) - Get NFT metadata URI

#### **Transaction Functions** (Requires wallet)
4. **Pledge for Financing** (`pledgeForFinancing`) - Lock bill for financing
5. **Release Ownership** (`releaseOwnership`) - Unlock bill after financing
6. **Mint Bill NFT** (`mintBill`) - Automatically handled by system

### 3. **Python Test Suite** 🐍
Complete automated testing script: `test_contract_functions.py`

---

## 🚀 How to Test

### **Step 1: Setup MetaMask**

1. Install MetaMask extension: https://metamask.io
2. Import your account using the private key from `.env`:
   ```
   PRIVATE_KEY=0x6f12f57e80ca5811b236690e75c62ede172cc70b05d336d200fa7af2e5388a0c
   ```
3. Switch to **Sepolia Test Network**
4. Get test ETH from faucet: https://sepoliafaucet.com

### **Step 2: Test in Web UI**

1. **Start the application:**
   ```powershell
   .\start.bat
   ```

2. **Open browser**: http://localhost:5000

3. **Go to Blockchain Tab** (⛓️ 區塊鏈)

4. **Connect Wallet:**
   - Click "🔗 連接 MetaMask"
   - Approve in MetaMask popup
   - Your address will show in the UI

5. **Test Read Functions** (No gas needed):
   
   a. **Query Bill Data:**
   - Click "📊 查詢提單數據"
   - Enter Token ID (e.g., `1`)
   - View all bill information

   b. **Check Transferability:**
   - Click "🔄 檢查轉讓性"
   - Enter Token ID
   - See if bill can be transferred

   c. **Get Token URI:**
   - Click "🔗 獲取元數據"
   - Enter Token ID
   - Opens IPFS metadata in new tab

6. **Test Transaction Functions** (Requires gas):

   a. **Pledge for Financing:**
   - Click "💰 質押融資"
   - Enter Token ID
   - Enter financier address (or use your own for testing)
   - Enter amount in ETH (e.g., `1`)
   - Confirm MetaMask transaction
   - Wait for confirmation

   b. **Release Ownership:**
   - Click "🔓 釋放所有權"
   - Enter Token ID
   - Confirm MetaMask transaction
   - ⚠️ Note: Must be called by the financier address

### **Step 3: Test with Python Script**

1. **Run automated test suite:**
   ```powershell
   python test_contract_functions.py
   ```

2. **Follow prompts:**
   - Enter Token ID to test
   - Enter financier address (optional for transaction tests)
   - Confirm transaction tests

3. **Review results:**
   - All function calls are tested automatically
   - Transaction hashes displayed
   - Etherscan links provided

---

## 📊 Test Scenarios

### **Scenario 1: Complete Bill Lifecycle**

1. **Upload and Process Bill**
   - Go to "📤 新增與比較" tab
   - Upload bill image
   - Click "⛓️ 完整處理"
   - Wait for IPFS upload

2. **Mint NFT**
   - Go to "⛓️ 區塊鏈" tab
   - Click "🎨 鑄造 NFT"
   - Note the Token ID

3. **Query Bill Data**
   - Click "📊 查詢提單數據"
   - Enter Token ID
   - Verify all data is correct

4. **Check Initial Transferability**
   - Should return: ✅ Can Transfer

5. **Pledge for Financing**
   - Click "💰 質押融資"
   - Enter Token ID and financier address
   - Enter financing amount
   - Confirm transaction

6. **Check Transferability Again**
   - Should now return: ❌ Cannot Transfer

7. **Release Ownership**
   - Switch to financier wallet (or use test account)
   - Click "🔓 釋放所有權"
   - Confirm transaction

8. **Final Transferability Check**
   - Should return: ✅ Can Transfer

### **Scenario 2: Multi-Wallet Testing**

1. **Wallet A (Owner):**
   - Mint NFT
   - Pledge for financing to Wallet B

2. **Wallet B (Financier):**
   - Try to transfer (should fail - not owner)
   - Release ownership
   
3. **Wallet A (Owner):**
   - Verify can now transfer
   - Transfer to Wallet C

### **Scenario 3: Error Handling**

1. **Test invalid Token ID:**
   - Should show proper error message

2. **Test unauthorized release:**
   - Non-financier tries to release
   - Should fail with proper error

3. **Test double financing:**
   - Try to pledge already-financed bill
   - Should fail

---

## 🔍 Verification Links

After each transaction, verify on Sepolia Etherscan:

- **Contract**: https://sepolia.etherscan.io/address/0x89e89036f3f4dCdFE8DdA8C78E54FfA2D09095ED
- **Your Transactions**: https://sepolia.etherscan.io/address/YOUR_ADDRESS
- **Specific Transaction**: https://sepolia.etherscan.io/tx/TX_HASH
- **NFT Token**: https://sepolia.etherscan.io/token/0x89e89036f3f4dCdFE8DdA8C78E54FfA2D09095ED?a=TOKEN_ID

---

## ⚠️ Important Notes

1. **Gas Costs**: All transactions require Sepolia ETH for gas
2. **Network**: Must be on Sepolia testnet
3. **Wallet Security**: Never share private keys
4. **Transaction Time**: Sepolia blocks take ~12 seconds
5. **Default Wallet**: Uses wallet from `.env` for backend minting
6. **UI Wallet**: Users can connect any MetaMask wallet for testing

---

## 🐛 Troubleshooting

**Problem**: MetaMask not detected
- **Solution**: Install MetaMask extension and refresh page

**Problem**: Wrong network
- **Solution**: Switch to Sepolia in MetaMask

**Problem**: Transaction fails
- **Solution**: Check you have enough Sepolia ETH for gas

**Problem**: "Not owner" error
- **Solution**: Ensure connected wallet owns the Token ID

**Problem**: Cannot release ownership
- **Solution**: Must be called by financier address

**Problem**: Functions not working
- **Solution**: Check browser console (F12) for errors

---

## ✅ Success Criteria

All tests pass when:
- ✅ Wallet connects successfully
- ✅ All read functions return data
- ✅ Transactions confirm on blockchain
- ✅ Etherscan shows transaction details
- ✅ Bill state changes correctly
- ✅ Transferability updates properly

---

## 📝 Test Results Log

Document your test results:

```
Date: _______________
Tester: _______________

✅ Wallet Connection: PASS / FAIL
✅ Get Bill Data: PASS / FAIL
✅ Check Transferability: PASS / FAIL
✅ Get Token URI: PASS / FAIL
✅ Pledge for Financing: PASS / FAIL
✅ Release Ownership: PASS / FAIL
✅ Python Test Suite: PASS / FAIL

Notes:
_________________________________
_________________________________
```

---

## 🎯 Next Steps

After successful testing:
1. Document any issues found
2. Test with multiple wallets
3. Test edge cases
4. Verify all Etherscan links work
5. Confirm IPFS data accessibility
6. Test full OCR → NFT → Financing workflow

---

## 📞 Support

If you encounter issues:
1. Check browser console (F12)
2. Check Flask terminal output
3. Verify Sepolia network status
4. Ensure sufficient test ETH
5. Review transaction on Etherscan

**Happy Testing! 🚀**
