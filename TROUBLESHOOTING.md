# 🔧 Troubleshooting Guide

## Common Issues and Solutions

---

## 🦊 METAMASK ISSUES

### Problem: "MetaMask not detected" error
**Symptoms**: Alert saying "請安裝 MetaMask!"

**Solutions**:
1. Install MetaMask extension from https://metamask.io
2. Refresh the browser page after installation
3. Make sure MetaMask is enabled in your browser
4. Try opening MetaMask extension to activate it
5. Check browser console (F12) for detailed errors

**How to verify**: You should see the MetaMask fox icon in your browser toolbar

---

### Problem: Wallet won't connect
**Symptoms**: Nothing happens when clicking "連接 MetaMask"

**Solutions**:
1. Check if MetaMask is unlocked (enter password)
2. Look for MetaMask popup window (might be behind other windows)
3. Open MetaMask manually and check for pending requests
4. Clear browser cache and reload page
5. Try disconnecting all sites in MetaMask settings, then reconnect

**Browser Console Check**:
```javascript
// Open console (F12) and type:
typeof window.ethereum
// Should return: "object" (not "undefined")
```

---

### Problem: Wrong network error
**Symptoms**: Alert saying "請切換到 Sepolia 測試網!"

**Solutions**:
1. Open MetaMask extension
2. Click network dropdown at top
3. Enable "Show test networks" in settings if needed
4. Select "Sepolia test network"
5. If Sepolia not visible, add it manually:
   - Network Name: Sepolia
   - RPC URL: https://ethereum-sepolia-rpc.publicnode.com
   - Chain ID: 11155111
   - Currency Symbol: ETH
   - Block Explorer: https://sepolia.etherscan.io

**Auto-switch**: The app will try to switch networks automatically. Approve the prompt.

---

### Problem: No test ETH for gas
**Symptoms**: Transaction fails with "insufficient funds"

**Solutions**:
1. Get test ETH from faucet: https://sepoliafaucet.com
2. Alternative faucets:
   - https://sepolia-faucet.pk910.de/
   - https://www.alchemy.com/faucets/ethereum-sepolia
3. You'll need at least 0.01 ETH for testing
4. Wait 24 hours between faucet requests (most faucets)

**Check Balance**: Open MetaMask → should show ETH amount

---

## ⛓️ BLOCKCHAIN FUNCTION ISSUES

### Problem: "Token does not exist" error
**Symptoms**: Error when querying bill data

**Solutions**:
1. Verify the Token ID exists:
   - Go to "檔案管理" tab
   - Check "NFT已鑄造" status
   - Note the Token ID
2. Token IDs start from 1 (not 0)
3. Check contract on Etherscan:
   https://sepolia.etherscan.io/address/0x89e89036f3f4dCdFE8DdA8C78E54FfA2D09095ED

**Verify Token**:
```
Contract → Read Contract → tokenURI(tokenId)
If it works, token exists
```

---

### Problem: "Not owner" error
**Symptoms**: Can't pledge financing or perform owner actions

**Solutions**:
1. Check who owns the token:
   - Call `getBillData(tokenId)`
   - Compare owner address with your connected wallet
2. Ensure you're connected with the correct wallet
3. For testing, use the default backend wallet:
   - Address: 0x28A69686CE21d33d7b792E807Cdc3e07E8fB8555
   - Import private key from `.env` to MetaMask

**Check Ownership**:
```
在 UI 中: 查詢提單數據 → 查看 Owner 欄位
Should match your wallet address
```

---

### Problem: "Not financier" error when releasing
**Symptoms**: releaseOwnership() fails

**Solutions**:
1. Only the financier can release ownership
2. Check who is the financier:
   - Call `getBillData(tokenId)`
   - Note the financier address
3. Switch to financier wallet in MetaMask:
   - Click MetaMask icon
   - Select correct account
   - Or import financier's private key
4. If testing alone, use your own address as both owner and financier

---

### Problem: Transaction pending forever
**Symptoms**: MetaMask shows transaction as pending for long time

**Solutions**:
1. Check Sepolia network status: https://sepolia.etherscan.io
2. Increase gas price in MetaMask (click "Edit" on transaction)
3. Cancel stuck transaction:
   - Click on pending transaction in MetaMask
   - Click "Cancel" or "Speed Up"
4. Wait ~30 seconds for Sepolia block confirmation
5. Check transaction on Etherscan using tx hash

**Normal Wait Time**: 12-30 seconds per transaction on Sepolia

---

### Problem: Transaction reverted/failed
**Symptoms**: Transaction shows "Failed" on Etherscan

**Solutions**:
1. Check error message on Etherscan (click transaction → view error)
2. Common causes:
   - Insufficient gas limit (increase in MetaMask)
   - Contract requirement not met (e.g., already financed)
   - Wrong wallet (not owner/financier)
   - Bill already in that state
3. Try transaction again with higher gas limit
4. Verify contract state before retrying

**Debug on Etherscan**:
```
Transaction → Logs → Look for error message
Common errors: "Not owner", "Already financed", "Not financier"
```

---

## 🖥️ APPLICATION ISSUES

### Problem: Application won't start
**Symptoms**: `.\start.bat` fails or shows errors

**Solutions**:
1. Check Python is installed: `python --version`
2. Check Node.js is installed: `node --version`
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   npm install
   ```
4. Check `.env` file exists and has required keys
5. Try running directly: `python app_unified.py`
6. Check port 5000 is not already in use

**Port Conflict**:
```powershell
# Find process using port 5000
netstat -ano | findstr :5000
# Kill process (replace PID)
taskkill /PID <PID> /F
```

---

### Problem: OCR not working
**Symptoms**: Upload successful but no text extracted

**Solutions**:
1. Check PaddleOCR is installed: `pip install paddleocr`
2. Check PaddlePaddle is installed: `pip install paddlepaddle`
3. Try different image format (JPG, PNG)
4. Ensure image is clear and readable
5. Check image file size (< 10MB recommended)
6. Look for errors in Flask terminal output

---

### Problem: IPFS upload fails
**Symptoms**: "IPFS upload failed" error

**Solutions**:
1. Check Pinata API keys in `.env`:
   ```
   PINATA_API_KEY=eb58c2f80178be2103ac
   PINATA_SECRET_API_KEY=<your_secret>
   ```
2. Verify API keys are valid at https://pinata.cloud
3. Check internet connection
4. Try uploading smaller file
5. Check Pinata account limits (free tier: 1GB)

**Test Pinata Connection**:
```powershell
python -c "import requests; print(requests.get('https://api.pinata.cloud/data/testAuthentication', headers={'pinata_api_key': 'YOUR_KEY', 'pinata_secret_api_key': 'YOUR_SECRET'}).json())"
```

---

### Problem: NFT minting fails
**Symptoms**: "Mint failed" error in UI

**Solutions**:
1. Check backend wallet has Sepolia ETH
2. Verify contract address in code:
   `0x89e89036f3f4dCdFE8DdA8C78E54FfA2D09095ED`
3. Check Hardhat scripts are in `scripts/` folder
4. Verify Node.js dependencies: `npm install`
5. Look for detailed error in Flask terminal
6. Check IPFS hashes were generated correctly

**Manual Test**:
```powershell
node scripts/mint-nft.js "BL123" "QmHash123" "dataHash" "tokenURI"
```

---

## 🌐 BROWSER/NETWORK ISSUES

### Problem: Functions not responding
**Symptoms**: Clicking buttons does nothing

**Solutions**:
1. Open browser console (F12)
2. Look for JavaScript errors
3. Check if wallet.js loaded: `Ctrl+U` → search for "wallet.js"
4. Hard refresh page: `Ctrl+Shift+R`
5. Clear browser cache
6. Try different browser (Chrome, Firefox, Brave)
7. Disable ad blockers temporarily

**Console Check**:
```javascript
// In browser console (F12):
typeof Web3
// Should return: "function"

typeof connectWallet
// Should return: "function"
```

---

### Problem: IPFS links not loading
**Symptoms**: Clicking IPFS hash shows nothing

**Solutions**:
1. Try different IPFS gateway:
   - `https://gateway.pinata.cloud/ipfs/[hash]`
   - `https://ipfs.io/ipfs/[hash]`
   - `https://cloudflare-ipfs.com/ipfs/[hash]`
2. Wait a few seconds (IPFS can be slow)
3. Check IPFS hash is valid (starts with "Qm" or "bafy")
4. Verify file was uploaded to Pinata dashboard
5. Some networks/firewalls block IPFS

---

### Problem: RPC errors
**Symptoms**: "Failed to fetch" or RPC timeout errors

**Solutions**:
1. Try alternative Sepolia RPC:
   - `https://rpc.sepolia.org`
   - `https://eth-sepolia.g.alchemy.com/v2/demo`
   - `https://sepolia.infura.io/v3/demo`
2. Check internet connection
3. Update RPC in wallet.js if needed
4. Verify Sepolia testnet is operational

---

## 🐍 PYTHON TEST SUITE ISSUES

### Problem: test_contract_functions.py errors
**Symptoms**: Script crashes or shows import errors

**Solutions**:
1. Install required packages:
   ```powershell
   pip install web3 python-dotenv
   ```
2. Check `.env` file exists with PRIVATE_KEY
3. Verify contract address matches in script
4. Ensure Python 3.8+ is installed
5. Check you have internet connection for RPC

**Run with verbose output**:
```powershell
python test_contract_functions.py
# Enter Token ID when prompted
# Enter financier address for transaction tests
```

---

### Problem: Transaction tests fail
**Symptoms**: Read tests pass but write tests fail

**Solutions**:
1. Check wallet has sufficient Sepolia ETH
2. Verify you're testing with owned tokens
3. For release test, ensure bill is actually financed
4. Wait for previous transaction to complete
5. Increase gas limit in script if needed

---

## 🔐 SECURITY ISSUES

### Problem: Private key not working
**Symptoms**: Backend can't mint NFTs

**Solutions**:
1. Check `.env` file format:
   ```
   PRIVATE_KEY=0x1234...
   ```
   (Must start with "0x")
2. Ensure no extra spaces or quotes
3. Verify the wallet has Sepolia ETH
4. Check the address matches:
   ```powershell
   python -c "from eth_account import Account; print(Account.from_key('YOUR_KEY').address)"
   ```
5. Never share private keys or commit to Git

---

## 📊 DATA/STATE ISSUES

### Problem: Status not updating
**Symptoms**: File shows wrong status in management tab

**Solutions**:
1. Refresh the page
2. Check blockchain.json file in outputs/
3. Verify tokenId field exists
4. Clear browser cache
5. Check if blockchain transaction actually completed

**Manual Check**:
```powershell
# Check specific blockchain file
cat outputs/YYYYMMDD_HHMMSS_blockchain.json
# Should have "tokenId": number
```

---

### Problem: Data mismatch
**Symptoms**: UI shows different data than blockchain

**Solutions**:
1. Query directly from blockchain (use 查詢提單數據)
2. Check Etherscan for latest state
3. Verify you're looking at correct Token ID
4. Refresh metadata from IPFS
5. Blockchain is source of truth, not local files

---

## 🆘 EMERGENCY DEBUGGING

### When all else fails:

1. **Check all logs**:
   ```powershell
   # Flask terminal output
   # Browser console (F12)
   # MetaMask activity
   # Etherscan transactions
   ```

2. **Restart everything**:
   ```powershell
   # Stop Flask (Ctrl+C)
   # Close browser
   # Restart MetaMask
   # Clear all caches
   # Start fresh: .\start.bat
   ```

3. **Test components individually**:
   - Wallet connection only
   - Read-only functions first
   - Single transaction test
   - Python script separately

4. **Verify environment**:
   ```powershell
   python --version    # Should be 3.8+
   node --version      # Should be 14+
   pip list | findstr web3
   npm list web3
   ```

5. **Check contract on Etherscan**:
   - Is it still deployed?
   - Are there recent transactions?
   - Does Token ID exist?
   - What's the owner address?

---

## 📞 Getting Help

If you're still stuck:

1. **Document the issue**:
   - What you were trying to do
   - Exact error message
   - Screenshots
   - Browser console output
   - Flask terminal output

2. **Check these resources**:
   - MetaMask support: https://support.metamask.io
   - Etherscan: https://sepolia.etherscan.io
   - Web3.js docs: https://web3js.readthedocs.io
   - Hardhat docs: https://hardhat.org/docs

3. **Test on different setup**:
   - Different browser
   - Different computer
   - Different wallet

---

## ✅ Prevention Tips

**Before starting work**:
- ✅ Check you have Sepolia ETH
- ✅ Verify correct network selected
- ✅ Confirm wallet connected
- ✅ Test with small amounts first
- ✅ Keep backup of private keys (safely)
- ✅ Document your Token IDs

**During testing**:
- ✅ Check browser console for errors
- ✅ Wait for transaction confirmations
- ✅ Verify on Etherscan
- ✅ Note transaction hashes
- ✅ Test read functions before write

**After issues**:
- ✅ Document what went wrong
- ✅ Note the solution
- ✅ Update this guide
- ✅ Test the fix

---

## 🎯 Quick Diagnosis

```
Problem Category:
├─ MetaMask won't connect? → Check installation, unlock wallet
├─ Wrong network? → Switch to Sepolia (11155111)
├─ Transaction fails? → Check gas, ownership, state
├─ Functions not working? → Browser console, reload page
├─ NFT mint fails? → Check backend wallet, Hardhat setup
├─ Data not showing? → Query blockchain directly
└─ Everything broken? → Restart all, check prerequisites
```

---

**Remember**: Sepolia is a test network. If things break catastrophically, you can always redeploy the contract and start fresh. No real money is at risk! 🚀
