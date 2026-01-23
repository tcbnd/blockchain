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
    
    try {
        if (!contract) {
            // Use default provider for read-only
            const provider = new Web3.providers.HttpProvider('https://ethereum-sepolia-rpc.publicnode.com');
            web3 = new Web3(provider);
            contract = new web3.eth.Contract(contractABI, contractAddress);
        }
        
        const billData = await contract.methods.getBillData(tokenId).call();
        
        let message = '📋 提單數據:\n\n';
        message += `提單編號: ${billData.billNumber}\n`;
        message += `IPFS Hash: ${billData.ipfsHash}\n`;
        message += `時間戳: ${new Date(billData.timestamp * 1000).toLocaleString()}\n`;
        message += `是否融資: ${billData.isFinanced ? '是' : '否'}\n`;
        if (billData.isFinanced) {
            message += `融資方: ${billData.financier}\n`;
            message += `融資金額: ${web3.utils.fromWei(billData.financedAmount.toString(), 'ether')} ETH\n`;
            message += `是否已釋放: ${billData.isReleased ? '是' : '否'}\n`;
        }
        
        alert(message);
        console.log('Bill Data:', billData);
        
    } catch (error) {
        console.error('查詢失敗:', error);
        alert('查詢失敗: ' + error.message);
    }
}

// 2. Check Transferable
async function callIsTransferable() {
    const tokenId = prompt('請輸入 Token ID:');
    if (!tokenId) return;
    
    try {
        if (!contract) {
            const provider = new Web3.providers.HttpProvider('https://ethereum-sepolia-rpc.publicnode.com');
            web3 = new Web3(provider);
            contract = new web3.eth.Contract(contractABI, contractAddress);
        }
        
        const transferable = await contract.methods.isTransferable(tokenId).call();
        alert(`Token ID ${tokenId} ${transferable ? '✅ 可以轉讓' : '❌ 不可轉讓'}`);
        
    } catch (error) {
        console.error('查詢失敗:', error);
        alert('查詢失敗: ' + error.message);
    }
}

// 3. Get Token URI
async function callTokenURI() {
    const tokenId = prompt('請輸入 Token ID:');
    if (!tokenId) return;
    
    try {
        if (!contract) {
            const provider = new Web3.providers.HttpProvider('https://ethereum-sepolia-rpc.publicnode.com');
            web3 = new Web3(provider);
            contract = new web3.eth.Contract(contractABI, contractAddress);
        }
        
        const uri = await contract.methods.tokenURI(tokenId).call();
        alert(`Token URI:\n${uri}`);
        window.open(uri, '_blank');
        
    } catch (error) {
        console.error('查詢失敗:', error);
        alert('查詢失敗: ' + error.message);
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
    
    try {
        const amountWei = web3.utils.toWei(amount, 'ether');
        
        const tx = await contract.methods
            .pledgeForFinancing(tokenId, financier, amountWei)
            .send({ from: userAccount });
        
        alert(`✅ 質押成功!\n交易哈希: ${tx.transactionHash}`);
        console.log('Transaction:', tx);
        
    } catch (error) {
        console.error('質押失敗:', error);
        alert('質押失敗: ' + error.message);
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
    
    try {
        const tx = await contract.methods
            .releaseOwnership(tokenId)
            .send({ from: userAccount });
        
        alert(`✅ 釋放成功!\n交易哈希: ${tx.transactionHash}`);
        console.log('Transaction:', tx);
        
    } catch (error) {
        console.error('釋放失敗:', error);
        alert('釋放失敗: ' + error.message);
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
