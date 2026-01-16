// Global variables
let provider;
let signer;
let contract;
let userAddress;
let chainId;

// Initialize app when page loads
document.addEventListener('DOMContentLoaded', () => {
    setupTabNavigation();
    checkWalletConnection();
    
    // Hide tabs until wallet is connected
    const tabs = document.querySelector('.tabs');
    const tabContents = document.querySelectorAll('.tab-content');
    if (!userAddress) {
        tabs.style.display = 'none';
        tabContents.forEach(tab => tab.style.display = 'none');
    }
});

// Setup tab navigation
function setupTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
}

// Check if wallet is already connected
async function checkWalletConnection() {
    if (typeof window.ethereum !== 'undefined') {
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });
        if (accounts.length > 0) {
            await connectWallet();
        }
    }
}

// Connect wallet button
document.getElementById('connectWallet').addEventListener('click', connectWallet);

async function connectWallet() {
    try {
        if (typeof window.ethereum === 'undefined') {
            alert('Please install MetaMask or another Web3 wallet!');
            return;
        }

        // Request account access
        await window.ethereum.request({ method: 'eth_requestAccounts' });
        
        // Setup provider and signer
        provider = new ethers.providers.Web3Provider(window.ethereum);
        signer = provider.getSigner();
        userAddress = await signer.getAddress();
        
        // Get network info
        const network = await provider.getNetwork();
        chainId = network.chainId;
        
        // Setup contract
        contract = new ethers.Contract(
            CONTRACT_CONFIG.CONTRACT_ADDRESS,
            CONTRACT_CONFIG.CONTRACT_ABI,
            signer
        );
        
        // Update UI
        updateWalletInfo();
        
        // Setup event listeners
        setupEventListeners();
        
        showMessage('success', 'Wallet connected successfully!');
        
    } catch (error) {
        console.error('Error connecting wallet:', error);
        showMessage('error', 'Failed to connect wallet: ' + error.message);
    }
}

async function updateWalletInfo() {
    const balance = await provider.getBalance(userAddress);
    const networkInfo = CONTRACT_CONFIG.NETWORKS[chainId] || { name: 'Unknown Network', nativeCurrency: { symbol: 'ETH' } };
    
    document.getElementById('walletInfo').style.display = 'block';
    document.getElementById('walletAddress').textContent = 
        userAddress.substring(0, 6) + '...' + userAddress.substring(38);
    document.getElementById('networkName').textContent = networkInfo.name;
    document.getElementById('walletBalance').textContent = 
        ethers.utils.formatEther(balance).substring(0, 8) + ' ' + networkInfo.nativeCurrency.symbol;
    
    document.getElementById('connectWallet').textContent = 'Connected';
    document.getElementById('connectWallet').disabled = true;
    
    // Hide welcome message and show tabs
    const welcomeMsg = document.getElementById('welcomeMessage');
    if (welcomeMsg) welcomeMsg.style.display = 'none';
    
    const tabs = document.querySelector('.tabs');
    const tabContents = document.querySelectorAll('.tab-content');
    tabs.style.display = 'flex';
    document.querySelector('.tab-content.active').style.display = 'block';
}

// Setup contract event listeners
function setupEventListeners() {
    // Listen for account changes
    window.ethereum.on('accountsChanged', (accounts) => {
        if (accounts.length === 0) {
            location.reload();
        } else {
            connectWallet();
        }
    });
    
    // Listen for network changes
    window.ethereum.on('chainChanged', () => {
        location.reload();
    });
    
    // Listen for contract events
    contract.on('BillMinted', (tokenId, shipper, billNumber) => {
        console.log('Bill Minted:', { tokenId: tokenId.toString(), shipper, billNumber });
        showMessage('success', `New bill minted! Token ID: ${tokenId.toString()}`);
    });
    
    contract.on('BillFinanced', (tokenId, financier, amount) => {
        console.log('Bill Financed:', { tokenId: tokenId.toString(), financier, amount: amount.toString() });
    });
    
    contract.on('BillReleased', (tokenId) => {
        console.log('Bill Released:', tokenId.toString());
    });
}

// Mint new bill
async function mintBill() {
    try {
        if (!contract) {
            showMessage('error', 'Please connect your wallet first!');
            return;
        }
        
        const shipperAddress = document.getElementById('shipperAddress').value;
        const billNumber = document.getElementById('billNumber').value;
        const ipfsHash = document.getElementById('ipfsHash').value;
        const dataHash = document.getElementById('dataHash').value;
        const tokenURI = document.getElementById('tokenURI').value;
        
        if (!shipperAddress || !billNumber || !ipfsHash || !dataHash || !tokenURI) {
            showMessage('error', 'Please fill in all fields!', 'mintResult');
            return;
        }
        
        if (!ethers.utils.isAddress(shipperAddress)) {
            showMessage('error', 'Invalid shipper address!', 'mintResult');
            return;
        }
        
        showLoading(true);
        showMessage('info', 'Minting bill... Please confirm the transaction in your wallet.', 'mintResult');
        
        const tx = await contract.mintBill(
            shipperAddress,
            billNumber,
            ipfsHash,
            dataHash,
            tokenURI
        );
        
        showMessage('info', 'Transaction submitted. Waiting for confirmation...', 'mintResult');
        const receipt = await tx.wait();
        
        // Extract token ID from events
        const event = receipt.events.find(e => e.event === 'BillMinted');
        const tokenId = event.args.tokenId.toString();
        
        showLoading(false);
        showMessage('success', `Bill minted successfully! Token ID: ${tokenId}. Transaction hash: ${receipt.transactionHash}`, 'mintResult');
        
        // Clear form
        document.getElementById('shipperAddress').value = '';
        document.getElementById('billNumber').value = '';
        document.getElementById('ipfsHash').value = '';
        document.getElementById('dataHash').value = '';
        document.getElementById('tokenURI').value = '';
        
    } catch (error) {
        showLoading(false);
        console.error('Error minting bill:', error);
        showMessage('error', 'Failed to mint bill: ' + (error.reason || error.message), 'mintResult');
    }
}

// Get bill details
async function getBillDetails() {
    try {
        if (!contract) {
            showMessage('error', 'Please connect your wallet first!');
            return;
        }
        
        const tokenId = document.getElementById('viewTokenId').value;
        
        if (!tokenId) {
            showMessage('error', 'Please enter a token ID!');
            return;
        }
        
        showLoading(true);
        
        const billData = await contract.getBillData(tokenId);
        const owner = await contract.ownerOf(tokenId);
        const isTransferable = await contract.isTransferable(tokenId);
        
        const billDetailsDiv = document.getElementById('billDetails');
        billDetailsDiv.innerHTML = `
            <h3>Bill Details - Token ID: ${tokenId}</h3>
            <p><strong>Bill Number:</strong> ${billData.billNumber}</p>
            <p><strong>Owner:</strong> ${owner}</p>
            <p><strong>IPFS Hash:</strong> <a href="https://ipfs.io/ipfs/${billData.ipfsHash}" target="_blank">${billData.ipfsHash}</a></p>
            <p><strong>Data Hash:</strong> ${billData.dataHash}</p>
            <p><strong>Token URI:</strong> <a href="${billData.tokenURI}" target="_blank">${billData.tokenURI}</a></p>
            <p><strong>Timestamp:</strong> ${new Date(billData.timestamp * 1000).toLocaleString()}</p>
            <p><strong>Status:</strong> 
                ${billData.isFinanced ? '<span class="status-badge financed">Financed</span>' : ''}
                ${billData.isReleased ? '<span class="status-badge released">Released</span>' : ''}
                ${!billData.isFinanced ? '<span class="status-badge available">Available</span>' : ''}
                ${isTransferable ? '<span class="status-badge available">Transferable</span>' : ''}
            </p>
            ${billData.isFinanced ? `
                <p><strong>Financier:</strong> ${billData.financier}</p>
                <p><strong>Financed Amount:</strong> ${ethers.utils.formatEther(billData.financedAmount)} ETH</p>
            ` : ''}
        `;
        
        showLoading(false);
        
    } catch (error) {
        showLoading(false);
        console.error('Error getting bill details:', error);
        showMessage('error', 'Failed to get bill details: ' + (error.reason || error.message));
    }
}

// Pledge for financing
async function pledgeForFinancing() {
    try {
        if (!contract) {
            showMessage('error', 'Please connect your wallet first!');
            return;
        }
        
        const tokenId = document.getElementById('financeTokenId').value;
        const financierAddress = document.getElementById('financierAddress').value;
        const amount = document.getElementById('financeAmount').value;
        
        if (!tokenId || !financierAddress || !amount) {
            showMessage('error', 'Please fill in all fields!', 'financeResult');
            return;
        }
        
        if (!ethers.utils.isAddress(financierAddress)) {
            showMessage('error', 'Invalid financier address!', 'financeResult');
            return;
        }
        
        showLoading(true);
        showMessage('info', 'Pledging for financing... Please confirm the transaction.', 'financeResult');
        
        const amountWei = ethers.utils.parseEther(amount);
        const tx = await contract.pledgeForFinancing(tokenId, financierAddress, amountWei);
        
        showMessage('info', 'Transaction submitted. Waiting for confirmation...', 'financeResult');
        const receipt = await tx.wait();
        
        showLoading(false);
        showMessage('success', `Bill pledged successfully! Transaction hash: ${receipt.transactionHash}`, 'financeResult');
        
        // Clear form
        document.getElementById('financeTokenId').value = '';
        document.getElementById('financierAddress').value = '';
        document.getElementById('financeAmount').value = '';
        
    } catch (error) {
        showLoading(false);
        console.error('Error pledging for financing:', error);
        showMessage('error', 'Failed to pledge: ' + (error.reason || error.message), 'financeResult');
    }
}

// Release ownership
async function releaseOwnership() {
    try {
        if (!contract) {
            showMessage('error', 'Please connect your wallet first!');
            return;
        }
        
        const tokenId = document.getElementById('releaseTokenId').value;
        
        if (!tokenId) {
            showMessage('error', 'Please enter a token ID!', 'releaseResult');
            return;
        }
        
        showLoading(true);
        showMessage('info', 'Releasing ownership... Please confirm the transaction.', 'releaseResult');
        
        const tx = await contract.releaseOwnership(tokenId);
        
        showMessage('info', 'Transaction submitted. Waiting for confirmation...', 'releaseResult');
        const receipt = await tx.wait();
        
        showLoading(false);
        showMessage('success', `Ownership released successfully! Transaction hash: ${receipt.transactionHash}`, 'releaseResult');
        
        document.getElementById('releaseTokenId').value = '';
        
    } catch (error) {
        showLoading(false);
        console.error('Error releasing ownership:', error);
        showMessage('error', 'Failed to release: ' + (error.reason || error.message), 'releaseResult');
    }
}

// Transfer bill
async function transferBill() {
    try {
        if (!contract) {
            showMessage('error', 'Please connect your wallet first!');
            return;
        }
        
        const tokenId = document.getElementById('transferTokenId').value;
        const recipientAddress = document.getElementById('recipientAddress').value;
        
        if (!tokenId || !recipientAddress) {
            showMessage('error', 'Please fill in all fields!', 'transferResult');
            return;
        }
        
        if (!ethers.utils.isAddress(recipientAddress)) {
            showMessage('error', 'Invalid recipient address!', 'transferResult');
            return;
        }
        
        // Check if transferable
        const isTransferable = await contract.isTransferable(tokenId);
        if (!isTransferable) {
            showMessage('error', 'This bill is financed and cannot be transferred!', 'transferResult');
            return;
        }
        
        showLoading(true);
        showMessage('info', 'Transferring bill... Please confirm the transaction.', 'transferResult');
        
        const tx = await contract.safeTransferFrom(userAddress, recipientAddress, tokenId);
        
        showMessage('info', 'Transaction submitted. Waiting for confirmation...', 'transferResult');
        const receipt = await tx.wait();
        
        showLoading(false);
        showMessage('success', `Bill transferred successfully! Transaction hash: ${receipt.transactionHash}`, 'transferResult');
        
        // Clear form
        document.getElementById('transferTokenId').value = '';
        document.getElementById('recipientAddress').value = '';
        
    } catch (error) {
        showLoading(false);
        console.error('Error transferring bill:', error);
        showMessage('error', 'Failed to transfer: ' + (error.reason || error.message), 'transferResult');
    }
}

// Utility functions
function showLoading(show) {
    document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
}

function showMessage(type, message, elementId = null) {
    const className = type === 'success' ? 'success' : type === 'error' ? 'error' : 'info';
    const html = `<div class="result-message ${className}">${message}</div>`;
    
    if (elementId) {
        document.getElementById(elementId).innerHTML = html;
    } else {
        // Show as a temporary notification at the top
        const notification = document.createElement('div');
        notification.className = `result-message ${className}`;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '1001';
        notification.style.maxWidth = '400px';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}
