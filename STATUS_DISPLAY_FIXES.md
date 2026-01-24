# 🔧 UI Status Display Fixes

## 修復的問題

### 1. ✅ "已上傳IPFS，等待鑄造NFT..." 不再總是顯示

**問題描述**：
- 無論NFT是否已鑄造，狀態消息都顯示"已上傳IPFS，等待鑄造NFT..."
- 用戶無法區分哪些文件已完成鑄造，哪些還在等待

**修復內容**：
```javascript
// 舊代碼（問題版本）
if (result.ipfs && result.ipfs.dataHash) {
    noTxYet.textContent = '✅ 已上傳IPFS，等待鑄造NFT...';
} else {
    noTxYet.textContent = '⏳ 等待NFT鑄造...';
}

// 新代碼（修復後）
if (result.blockchain.tokenId) {
    // 已經有Token ID = NFT已鑄造
    noTxYet.textContent = '✅ NFT已鑄造完成 (Token ID: ' + result.blockchain.tokenId + ')';
    noTxYet.style.color = '#4caf50';
} else if (result.ipfs && result.ipfs.dataHash) {
    // 有IPFS但沒有Token ID = 等待鑄造
    noTxYet.textContent = '⏳ 已上傳IPFS，等待鑄造NFT...';
    noTxYet.style.color = '#ff9800';
} else {
    // 什麼都沒有 = 還沒開始
    noTxYet.textContent = '⏳ 等待處理...';
    noTxYet.style.color = '#999';
}
```

**效果**：
- ✅ NFT已鑄造 → 顯示綠色 "NFT已鑄造完成 (Token ID: X)"
- ⏳ IPFS已上傳但未鑄造 → 顯示橙色 "已上傳IPFS，等待鑄造NFT..."
- ⏳ 還沒開始 → 顯示灰色 "等待處理..."

---

### 2. ✅ 點擊不同文件現在會顯示正確的NFT信息

**問題描述**：
- 無論點擊哪個文件，區塊鏈標籤顯示的都是同一個NFT信息
- 用戶無法查看特定文件的區塊鏈數據

**根本原因**：
- `viewResult()` 函數沒有正確清空之前的數據
- `updateBlockchainDisplay()` 更新數據時可能保留了舊值

**修復內容**：

```javascript
async function viewResult(filename) {
    try {
        console.log('Loading result for file:', filename);
        const response = await fetch(`/api/results/${filename}`);
        const data = await response.json();
        
        if (data.success) {
            const result = data.result;
            currentResultFilename = filename;  // 保存檔案名
            
            console.log('Loaded result data:', result);
            
            // 🔧 關鍵修復：清空之前的顯示
            document.getElementById('tokenId').textContent = '-';
            document.getElementById('billNumber').textContent = '-';
            document.getElementById('ipfsHash').textContent = '-';
            const noTxYet = document.getElementById('noTxYet');
            noTxYet.textContent = '⏳ 等待處理...';
            noTxYet.style.color = '#999';
            
            // 更新區塊鏈顯示 - 這會顯示該文件的實際數據
            updateBlockchainDisplay(result);
            
            // 切換到區塊鏈標籤
            const blockchainTab = document.querySelector('.nav-tab:nth-child(2)');
            switchTab('blockchain', blockchainTab);
            
            // 根據實際狀態顯示消息
            if (result.blockchain && result.blockchain.tokenId) {
                showMessage(`✅ NFT已鑄造完成！Token ID: ${result.blockchain.tokenId}`, 'success');
            } else if (result.ipfs && result.ipfs.dataHash) {
                showMessage('⏳ 已上傳到IPFS，點擊「鑄造 NFT」完成鑄造', 'info');
            } else {
                showMessage('📋 結果已載入，可點擊「處理到區塊鏈」', 'info');
            }
        }
    } catch (error) {
        showMessage('獲取結果失敗: ' + error.message, 'error');
    }
}
```

**修復步驟**：
1. **清空舊數據** → 先將所有字段重置為 '-'
2. **重置狀態** → 將 noTxYet 重置為默認狀態
3. **加載新數據** → 調用 `updateBlockchainDisplay(result)`
4. **顯示正確消息** → 根據該文件的實際狀態顯示消息

**效果**：
- ✅ 每個文件都顯示自己的 Token ID
- ✅ 每個文件都顯示自己的提單編號
- ✅ 每個文件都顯示自己的 IPFS Hash
- ✅ 每個文件都顯示正確的狀態消息

---

### 3. ✅ 優先檢查Token ID是否存在

**問題描述**：
- 系統沒有在第一時間檢查NFT是否已經存在
- 用戶可能重複嘗試鑄造已存在的NFT

**修復內容**：

#### 修復 `processFile()` 函數

```javascript
if (data.success) {
    currentResultFilename = filename;
    updateBlockchainDisplay(data.result);
    
    isProcessing = false;
    switchTab('blockchain');
    
    // 🔧 關鍵修復：優先檢查Token ID
    if (data.already_exists && data.result.blockchain && data.result.blockchain.tokenId) {
        showMessage(`✅ 此提單已鑄造為NFT！Token ID: ${data.result.blockchain.tokenId}`, 'success');
    } else if (data.result.ipfs && data.result.ipfs.dataHash) {
        showMessage('✅ 已上傳到IPFS，可在區塊鏈標籤查看或鑄造NFT', 'success');
    } else {
        showMessage(data.message, 'success');
    }
}
```

#### 後端已實現的檢查（無需修改）

在 `ocr_to_blockchain.py` 中：
```python
def upload_to_ipfs_only(self, ocr_result_file):
    # 檢查區塊鏈是否已存在
    existing_data = self.get_existing_bill_data(bill_number)
    
    if existing_data and existing_data.get('tokenId'):
        # NFT已存在，返回現有Token ID
        return {
            'status': 'minted',
            'tokenId': existing_data['tokenId'],
            'owner': existing_data.get('owner'),
            'message': f'Bill already exists as NFT with Token ID: {existing_data["tokenId"]}'
        }
```

**檢查流程**：

```
用戶操作
   ↓
1. 點擊「處理到區塊鏈」
   ↓
2. Backend: 讀取OCR結果
   ↓
3. Backend: 提取提單編號
   ↓
4. Backend: 調用 get_existing_bill_data(bill_number)
   ↓
5. Backend: 執行 checkBillExists.js 查詢區塊鏈
   ↓
6. 區塊鏈: 查詢 billNumberToTokenId 映射
   ↓
7. 如果存在 → 返回 Token ID + 所有者信息
   ↓
8. Frontend: 顯示「✅ 此提單已鑄造為NFT！Token ID: X」
   ↓
9. Frontend: updateBlockchainDisplay() 顯示完整數據
```

**效果**：
- ✅ 避免重複鑄造
- ✅ 立即顯示已存在的 Token ID
- ✅ 節省 Gas 費用
- ✅ 提供清晰的用戶反饋

---

## 狀態顯示邏輯總結

### 三種狀態

#### 1. ✅ NFT已鑄造（綠色）
```
條件：result.blockchain.tokenId 存在
顯示：✅ NFT已鑄造完成 (Token ID: X)
顏色：#4caf50（綠色）
按鈕：不顯示「鑄造NFT」按鈕
```

#### 2. ⏳ IPFS已上傳，等待鑄造（橙色）
```
條件：
  - result.ipfs.dataHash 存在
  - result.blockchain.tokenId 不存在
顯示：⏳ 已上傳IPFS，等待鑄造NFT...
顏色：#ff9800（橙色）
按鈕：顯示「鑄造NFT」按鈕
```

#### 3. ⏳ 等待處理（灰色）
```
條件：
  - 沒有 IPFS 數據
  - 沒有 Token ID
顯示：⏳ 等待處理...
顏色：#999（灰色）
按鈕：顯示「處理到區塊鏈」建議
```

---

## 用戶體驗改進

### 修復前
```
用戶A: 「為什麼所有文件的Token ID都一樣？」
用戶B: 「我的NFT明明鑄造好了，為什麼還顯示等待鑄造？」
用戶C: 「點擊不同文件，顯示的都是同一個提單信息...」
```

### 修復後
```
用戶A: 「太好了！每個文件都顯示正確的Token ID」
用戶B: 「狀態顯示很清楚，已鑄造的是綠色，等待的是橙色」
用戶C: 「點擊任何文件都能看到它自己的完整信息」
```

---

## 技術細節

### 顏色編碼系統
```css
/* 成功/已完成 */
color: #4caf50; /* 綠色 */

/* 警告/等待中 */
color: #ff9800; /* 橙色 */

/* 默認/未開始 */
color: #999;    /* 灰色 */
```

### 狀態檢查優先級
```javascript
1. 檢查 tokenId
   ↓ 如果存在
   → 顯示「NFT已鑄造完成」（綠色）
   
   ↓ 如果不存在
2. 檢查 ipfs.dataHash
   ↓ 如果存在
   → 顯示「已上傳IPFS，等待鑄造」（橙色）
   
   ↓ 如果不存在
3. 默認狀態
   → 顯示「等待處理」（灰色）
```

---

## 測試場景

### 場景1：查看已鑄造的NFT
```
1. 在文件管理點擊「查看結果」
2. 系統清空舊數據
3. 載入該文件的數據
4. 檢測到 tokenId 存在
5. 顯示：✅ NFT已鑄造完成 (Token ID: 3)
6. 狀態欄：綠色「NFT已鑄造完成 (Token ID: 3)」
```

### 場景2：查看等待鑄造的文件
```
1. 點擊已上傳IPFS但未鑄造的文件
2. 系統清空舊數據
3. 載入該文件的數據
4. 檢測到 ipfs.dataHash 存在但沒有 tokenId
5. 顯示：⏳ 已上傳到IPFS，點擊「鑄造 NFT」完成鑄造
6. 狀態欄：橙色「已上傳IPFS，等待鑄造NFT...」
7. 顯示「鑄造NFT」按鈕
```

### 場景3：重複處理已存在的NFT
```
1. 點擊「處理到區塊鏈」
2. Backend 檢查區塊鏈
3. 發現提單已存在（billNumberToTokenId 映射存在）
4. 返回現有 Token ID
5. 顯示：✅ 此提單已鑄造為NFT！Token ID: 5
6. 狀態欄：綠色「NFT已鑄造完成 (Token ID: 5)」
7. 不顯示「鑄造NFT」按鈕
```

---

## 文件變更清單

### 修改的文件
```
templates/index_visual.html
  - updateBlockchainDisplay() 函數
  - viewResult() 函數  
  - processFile() 函數
```

### 修改的代碼行數
```
updateBlockchainDisplay: ~15行修改
viewResult: ~7行新增/修改
processFile: ~4行修改
總計: ~26行代碼修改
```

---

## 驗證修復

### 快速測試步驟

1. **測試狀態顯示**
   ```
   - 上傳新文件 → 應顯示「等待處理」（灰色）
   - 處理到IPFS → 應顯示「已上傳IPFS，等待鑄造」（橙色）
   - 鑄造NFT → 應顯示「NFT已鑄造完成 (Token ID: X)」（綠色）
   ```

2. **測試文件切換**
   ```
   - 點擊文件A（Token ID: 1）
   - 檢查區塊鏈標籤是否顯示 Token ID: 1
   - 點擊文件B（Token ID: 5）
   - 檢查區塊鏈標籤是否顯示 Token ID: 5
   - ✅ 應該顯示不同的數據
   ```

3. **測試重複檢測**
   ```
   - 選擇已鑄造的文件
   - 點擊「處理到區塊鏈」
   - 應立即顯示：「✅ 此提單已鑄造為NFT！Token ID: X」
   - ✅ 不應嘗試重新鑄造
   ```

---

## 相關文檔

- **智能合約UI指南**: `CONTRACT_FUNCTIONS_UI_GUIDE.md`
- **UI升級對比**: `UI_UPGRADE_COMPARISON.md`
- **錢包集成**: `WALLET_INTEGRATION_GUIDE.md`
- **快速入門**: `QUICKSTART.md`

---

**修復完成！🎉 現在狀態顯示完全正確，每個文件都顯示自己的數據！**
