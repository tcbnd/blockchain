// Web3 Wallet Integration for Bill of Lading NFT System

let web3;
let userAccount = null;
let contract;
const contractAddress = '0x89e89036f3f4dCdFE8DdA8C78E54FfA2D09095ED';
const sepoliaChainId = '0xaa36a7'; // 11155111 in hex

// Contract ABI
const contractABI = [
    {"inputs":[],"stateMutability":"nonpayable","type":"constructor"},
    {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},
    {"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator","type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},
    {"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"},{"indexed":true,"internalType":"address","name":"financier","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"BillFinanced","type":"event"},
    {"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"},{"indexed":true,"internalType":"address","name":"shipper","type":"address"},{"indexed":false,"internalType":"string","name":"billNumber","type":"string"}],"name":"BillMinted","type":"event"},
    {"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"BillReleased","type":"event"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getBillData","outputs":[{"components":[{"internalType":"string","name":"billNumber","type":"string"},{"internalType":"string","name":"ipfsHash","type":"string"},{"internalType":"string","name":"dataHash","type":"string"},{"internalType":"string","name":"tokenURI","type":"string"},{"internalType":"uint256","name":"timestamp","type":"uint256"},{"internalType":"bool","name":"isFinanced","type":"bool"},{"internalType":"address","name":"financier","type":"address"},{"internalType":"uint256","name":"financedAmount","type":"uint256"},{"internalType":"bool","name":"isReleased","type":"bool"}],"internalType":"struct BillOfLadingNFT.BillData","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"isTransferable","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address","name":"shipper","type":"address"},{"internalType":"string","name":"billNumber","type":"string"},{"internalType":"string","name":"ipfsHash","type":"string"},{"internalType":"string","name":"dataHash","type":"string"},{"internalType":"string","name":"_tokenURI","type":"string"}],"name":"mintBill","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"},{" internalType":"address","name":"financier","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"pledgeForFinancing","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"releaseOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}
];

// Connect Wallet
async function connectWallet() {
    if (typeof window.ethereum === 'undefined') {
        alert('請安裝 MetaMask! \n\n請訪問: https://metamask.io');
        return;
    }
    
    try {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        userAccount = accounts[0];
        
        web3 = new Web3(window.ethereum);
        contract = new web3.eth.Contract(contractABI, contractAddress);
        
        // Check network
        const chainId = await window.ethereum.request({ method: 'eth_chainId' });
        if (chainId !== sepoliaChainId) {
            alert('請切換到 Sepolia 測試網!\n\n當前網絡錯誤');
            try {
                await window.ethereum.request({
                    method: 'wallet_switchEthereumChain',
                    params: [{ chainId: sepoliaChainId }],
                });
            } catch (switchError) {
                console.error('切換網絡失敗:', switchError);
            }
        }
        
        updateWalletUI();
        console.log('Wallet connected:', userAccount);
        
    } catch (error) {
        console.error('連接錢包失敗:', error);
        alert('連接錢包失敗: ' + error.message);
    }
}

// Disconnect Wallet
function disconnectWallet() {
    userAccount = null;
    web3 = null;
    contract = null;
    updateWalletUI();
    console.log('Wallet disconnected');
}

// Update Wallet UI
function updateWalletUI() {
    const walletAddressEl = document.getElementById('walletAddress');
    const networkNameEl = document.getElementById('networkName');
    const connectBtn = document.getElementById('connectWalletBtn');
    const disconnectBtn = document.getElementById('disconnectWalletBtn');
    
    if (userAccount) {
        walletAddressEl.textContent = userAccount.substring(0, 6) + '...' + userAccount.substring(38);
        walletAddressEl.title = userAccount;
        networkNameEl.textContent = 'Sepolia Testnet';
        connectBtn.style.display = 'none';
        disconnectBtn.style.display = 'block';
    } else {
        walletAddressEl.textContent = '未連接';
        networkNameEl.textContent = '-';
        connectBtn.style.display = 'block';
        disconnectBtn.style.display = 'none';
    }
}

// Contract Functions

// 1. Get Bill Data
async function callGetBillData() {
    const tokenId = prompt('請輸入 Token ID:');
    if (!tokenId) return;
    
    // Show loading
    showFunctionResult('🔄 正在查詢中...', 'loading');
    
    try {
        if (!contract) {
            // Use default provider for read-only
            const provider = new Web3.providers.HttpProvider('https://ethereum-sepolia-rpc.publicnode.com');
            web3 = new Web3(provider);
            contract = new web3.eth.Contract(contractABI, contractAddress);
        }
        
        const billData = await contract.methods.getBillData(tokenId).call();
        const owner = await contract.methods.ownerOf(tokenId).call();
        
        let html = `<div style="color: #333;">
<h3 style="color: #4caf50; margin-bottom: 20px;">✅ 提單數據查詢成功</h3>

<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
    <div style="display: grid; grid-template-columns: 150px 1fr; gap: 10px; line-height: 2;">
        <strong>Token ID:</strong> <span>${tokenId}</span>
        <strong>提單編號:</strong> <span style="color: #667eea; font-weight: 600;">${billData.billNumber}</span>
        <strong>所有者:</strong> <span style="font-family: monospace; font-size: 0.85rem;">${owner}</span>
        <strong>IPFS Hash:</strong> <span style="font-family: monospace; font-size: 0.85rem;">${billData.ipfsHash}</span>
        <strong>鑄造時間:</strong> <span>${new Date(billData.timestamp * 1000).toLocaleString('zh-CN')}</span>
    </div>
</div>

<div style="background: ${billData.isFinanced ? '#fff3e0' : '#e8f5e9'}; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
    <strong style="color: ${billData.isFinanced ? '#f57c00' : '#2e7d32'};">
        ${billData.isFinanced ? '🔒 融資狀態: 已質押' : '🔓 融資狀態: 未質押'}
    </strong>
    ${billData.isFinanced ? `
    <div style="margin-top: 10px; padding-left: 10px; border-left: 3px solid #ff9800;">
        <div><strong>融資方:</strong> <span style="font-family: monospace; font-size: 0.85rem;">${billData.financier}</span></div>
        <div><strong>融資金額:</strong> <span style="color: #f57c00; font-weight: 600;">${web3.utils.fromWei(billData.financedAmount.toString(), 'ether')} ETH</span></div>
        <div><strong>已釋放:</strong> ${billData.isReleased ? '✅ 是' : '❌ 否'}</div>
    </div>
    ` : '<div style="margin-top: 10px; color: #555;">提單可自由轉讓</div>'}
</div>

<div style="background: #e3f2fd; padding: 15px; border-radius: 8px;">
    <strong style="color: #1976d2;">🔗 元數據URI</strong>
    <div style="margin-top: 10px;">
        <a href="${billData.tokenURI}" target="_blank" style="color: #2196f3; word-break: break-all;">${billData.tokenURI}</a>
    </div>
</div>
</div>`;
        
        showFunctionResult(html, 'success');
        console.log('Bill Data:', billData);
        
    } catch (error) {
        console.error('查詢失敗:', error);
        showFunctionResult(`<div style="color: #d32f2f;">
            <h3>❌ 查詢失敗</h3>
            <p style="margin-top: 10px; background: #ffebee; padding: 15px; border-radius: 8px;">
                ${error.message}
            </p>
        </div>`, 'error');
    }
}

// 2. Check Transferable
async function callIsTransferable() {
    const tokenId = prompt('請輸入 Token ID:');
    if (!tokenId) return;
    
    showFunctionResult('🔄 正在檢查中...', 'loading');
    
    try {
        if (!contract) {
            const provider = new Web3.providers.HttpProvider('https://ethereum-sepolia-rpc.publicnode.com');
            web3 = new Web3(provider);
            contract = new web3.eth.Contract(contractABI, contractAddress);
        }
        
        const transferable = await contract.methods.isTransferable(tokenId).call();
        
        const html = `<div style="color: #333;">
<h3 style="color: ${transferable ? '#4caf50' : '#f57c00'}; margin-bottom: 20px;">
    ${transferable ? '✅ 可以轉讓' : '⚠️ 不可轉讓'}
</h3>

<div style="background: ${transferable ? '#e8f5e9' : '#fff3e0'}; padding: 20px; border-radius: 10px;">
    <div style="text-align: center; margin-bottom: 15px;">
        <div style="font-size: 4rem; margin-bottom: 10px;">${transferable ? '🔓' : '🔒'}</div>
        <strong style="font-size: 1.2rem;">Token ID: ${tokenId}</strong>
    </div>
    
    <div style="background: white; padding: 15px; border-radius: 8px; margin-top: 15px;">
        <h4 style="margin-bottom: 10px; color: #333;">💡 說明</h4>
        ${transferable ? `
            <p style="color: #2e7d32; margin: 0;">
                此提單NFT目前未被質押，可以自由轉讓給其他地址。
                使用標準ERC-721轉讓功能即可完成轉移。
            </p>
        ` : `
            <p style="color: #e65100; margin: 0;">
                此提單NFT目前已被質押用於融資，暫時不可轉讓。
                需等融資方調用「釋放所有權」功能後才能轉讓。
            </p>
        `}
    </div>
</div>
</div>`;
        
        showFunctionResult(html, 'success');
        
    } catch (error) {
        console.error('查詢失敗:', error);
        showFunctionResult(`<div style="color: #d32f2f;">
            <h3>❌ 查詢失敗</h3>
            <p style="margin-top: 10px; background: #ffebee; padding: 15px; border-radius: 8px;">
                ${error.message}
            </p>
        </div>`, 'error');
    }
}

// 3. Get Token URI
async function callTokenURI() {
    const tokenId = prompt('請輸入 Token ID:');
    if (!tokenId) return;
    
    showFunctionResult('🔄 正在獲取中...', 'loading');
    
    try {
        if (!contract) {
            const provider = new Web3.providers.HttpProvider('https://ethereum-sepolia-rpc.publicnode.com');
            web3 = new Web3(provider);
            contract = new web3.eth.Contract(contractABI, contractAddress);
        }
        
        const uri = await contract.methods.tokenURI(tokenId).call();
        
        const html = `<div style="color: #333;">
<h3 style="color: #2196f3; margin-bottom: 20px;">✅ 元數據URI獲取成功</h3>

<div style="background: #e3f2fd; padding: 20px; border-radius: 10px;">
    <div style="text-align: center; margin-bottom: 15px;">
        <div style="font-size: 3rem; margin-bottom: 10px;">🔗</div>
        <strong style="font-size: 1.1rem;">Token ID: ${tokenId}</strong>
    </div>
    
    <div style="background: white; padding: 15px; border-radius: 8px; margin-top: 15px;">
        <h4 style="margin-bottom: 10px; color: #1976d2;">📋 IPFS元數據鏈接</h4>
        <div style="background: #f5f5f5; padding: 12px; border-radius: 6px; word-break: break-all; font-family: monospace; font-size: 0.9rem; margin-bottom: 15px;">
            ${uri}
        </div>
        <a href="${uri}" target="_blank" class="external-link" style="display: inline-block; background: linear-gradient(135deg, #2196f3, #42a5f5); color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s;">
            🌐 在新標籤頁打開
        </a>
    </div>
    
    <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin-top: 15px;">
        <strong style="color: #f57c00;">💡 提示</strong>
        <p style="margin: 10px 0 0; color: #555;">
            此URI指向IPFS上永久存儲的NFT元數據，包含提單的完整信息。
            符合ERC-721標準，可被所有NFT市場和錢包識別。
        </p>
    </div>
</div>
</div>`;
        
        showFunctionResult(html, 'success');
        
    } catch (error) {
        console.error('查詢失敗:', error);
        showFunctionResult(`<div style="color: #d32f2f;">
            <h3>❌ 獲取失敗</h3>
            <p style="margin-top: 10px; background: #ffebee; padding: 15px; border-radius: 8px;">
                ${error.message}
            </p>
        </div>`, 'error');
    }
}

// 4. Pledge for Financing (Requires Wallet)
async function callPledgeForFinancing() {
    if (!userAccount) {
        alert('請先連接錢包!');
        await connectWallet();
        if (!userAccount) return;
    }
    
    const tokenId = prompt('請輸入 Token ID:');
    if (!tokenId) return;
    
    const financier = prompt('請輸入融資方地址:');
    if (!financier) return;
    
    const amount = prompt('請輸入融資金額 (ETH):');
    if (!amount) return;
    
    showFunctionResult('⏳ 正在處理交易，請在MetaMask中確認...', 'loading');
    
    try {
        const amountWei = web3.utils.toWei(amount, 'ether');
        
        const tx = await contract.methods
            .pledgeForFinancing(tokenId, financier, amountWei)
            .send({ from: userAccount });
        
        const html = `<div style="color: #333;">
<h3 style="color: #4caf50; margin-bottom: 20px;">✅ 質押成功！</h3>

<div style="background: #e8f5e9; padding: 20px; border-radius: 10px;">
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="font-size: 4rem;">💰</div>
        <strong style="font-size: 1.2rem;">提單已成功質押</strong>
    </div>
    
    <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
        <h4 style="margin-bottom: 10px; color: #2e7d32;">📋 交易詳情</h4>
        <div style="display: grid; grid-template-columns: 120px 1fr; gap: 10px; line-height: 2; font-size: 0.95rem;">
            <strong>Token ID:</strong> <span>${tokenId}</span>
            <strong>融資方:</strong> <span style="font-family: monospace; font-size: 0.85rem;">${financier}</span>
            <strong>融資金額:</strong> <span style="color: #f57c00; font-weight: 600;">${amount} ETH</span>
            <strong>交易哈希:</strong> <span style="font-family: monospace; font-size: 0.85rem; word-break: break-all;">${tx.transactionHash}</span>
        </div>
    </div>
    
    <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
        <strong style="color: #f57c00;">🔒 質押狀態</strong>
        <p style="margin: 10px 0 0; color: #555;">
            提單已被鎖定，暫時不可轉讓。
            只有指定的融資方可以釋放所有權。
        </p>
    </div>
    
    <div style="text-align: center; margin-top: 15px;">
        <a href="https://sepolia.etherscan.io/tx/${tx.transactionHash}" target="_blank" class="external-link" style="display: inline-block; background: linear-gradient(135deg, #4caf50, #66bb6a); color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">
            🔍 在Etherscan查看交易
        </a>
    </div>
</div>
</div>`;
        
        showFunctionResult(html, 'success');
        console.log('Transaction:', tx);
        
    } catch (error) {
        console.error('質押失敗:', error);
        showFunctionResult(`<div style="color: #d32f2f;">
            <h3>❌ 質押失敗</h3>
            <p style="margin-top: 10px; background: #ffebee; padding: 15px; border-radius: 8px;">
                ${error.message}
            </p>
            <p style="margin-top: 10px; color: #666; font-size: 0.9rem;">
                常見原因：用戶取消交易、Gas不足、不是NFT所有者、提單已被質押
            </p>
        </div>`, 'error');
    }
}

// 5. Release Ownership (Requires Wallet)
async function callReleaseOwnership() {
    if (!userAccount) {
        alert('請先連接錢包!');
        await connectWallet();
        if (!userAccount) return;
    }
    
    const tokenId = prompt('請輸入 Token ID:');
    if (!tokenId) return;
    
    if (!confirm(`確定要釋放 Token ID ${tokenId} 的所有權嗎?`)) {
        return;
    }
    
    showFunctionResult('⏳ 正在處理交易，請在MetaMask中確認...', 'loading');
    
    try {
        const tx = await contract.methods
            .releaseOwnership(tokenId)
            .send({ from: userAccount });
        
        const html = `<div style="color: #333;">
<h3 style="color: #4caf50; margin-bottom: 20px;">✅ 釋放成功！</h3>

<div style="background: #e3f2fd; padding: 20px; border-radius: 10px;">
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="font-size: 4rem;">🔓</div>
        <strong style="font-size: 1.2rem;">所有權已釋放</strong>
    </div>
    
    <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
        <h4 style="margin-bottom: 10px; color: #1976d2;">📋 交易詳情</h4>
        <div style="display: grid; grid-template-columns: 120px 1fr; gap: 10px; line-height: 2; font-size: 0.95rem;">
            <strong>Token ID:</strong> <span>${tokenId}</span>
            <strong>操作者:</strong> <span style="font-family: monospace; font-size: 0.85rem;">${userAccount}</span>
            <strong>交易哈希:</strong> <span style="font-family: monospace; font-size: 0.85rem; word-break: break-all;">${tx.transactionHash}</span>
        </div>
    </div>
    
    <div style="background: #e8f5e9; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
        <strong style="color: #2e7d32;">✅ 解鎖狀態</strong>
        <p style="margin: 10px 0 0; color: #555;">
            提單質押已解除，現在可以自由轉讓。
            原所有者恢復完整控制權。
        </p>
    </div>
    
    <div style="text-align: center; margin-top: 15px;">
        <a href="https://sepolia.etherscan.io/tx/${tx.transactionHash}" target="_blank" class="external-link" style="display: inline-block; background: linear-gradient(135deg, #2196f3, #42a5f5); color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">
            🔍 在Etherscan查看交易
        </a>
    </div>
</div>
</div>`;
        
        showFunctionResult(html, 'success');
        console.log('Transaction:', tx);
        
    } catch (error) {
        console.error('釋放失敗:', error);
        showFunctionResult(`<div style="color: #d32f2f;">
            <h3>❌ 釋放失敗</h3>
            <p style="margin-top: 10px; background: #ffebee; padding: 15px; border-radius: 8px;">
                ${error.message}
            </p>
            <p style="margin-top: 10px; color: #666; font-size: 0.9rem;">
                常見原因：用戶取消交易、Gas不足、不是融資方、提單未被質押
            </p>
        </div>`, 'error');
    }
}

// Initialize on page load
window.addEventListener('load', async () => {
    // Check if MetaMask is connected
    if (typeof window.ethereum !== 'undefined') {
        try {
            const accounts = await window.ethereum.request({ method: 'eth_accounts' });
            if (accounts.length > 0) {
                userAccount = accounts[0];
                web3 = new Web3(window.ethereum);
                contract = new web3.eth.Contract(contractABI, contractAddress);
                updateWalletUI();
            }
        } catch (error) {
            console.log('No connected accounts');
        }
        
        // Listen for account changes
        window.ethereum.on('accountsChanged', (accounts) => {
            if (accounts.length > 0) {
                userAccount = accounts[0];
                web3 = new Web3(window.ethereum);
                contract = new web3.eth.Contract(contractABI, contractAddress);
                updateWalletUI();
            } else {
                disconnectWallet();
            }
        });
        
        // Listen for chain changes
        window.ethereum.on('chainChanged', () => {
            window.location.reload();
        });
    }
});

// Helper function to show results in enhanced display area
function showFunctionResult(content, type = 'success') {
    const resultDisplay = document.getElementById('functionResultDisplay');
    const resultContent = document.getElementById('functionResultContent');
    
    if (type === 'loading') {
        resultContent.innerHTML = `<div style="text-align: center; padding: 40px; color: #666;">
            <div style="font-size: 3rem; margin-bottom: 15px; animation: spin 1s linear infinite;">⚙️</div>
            <div style="font-size: 1.1rem;">${content}</div>
        </div>
        <style>
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
        </style>`;
    } else {
        resultContent.innerHTML = content;
    }
    
    resultDisplay.style.display = 'block';
    resultDisplay.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
