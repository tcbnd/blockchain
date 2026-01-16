# Bill of Lading NFT - Frontend DApp

A decentralized application (DApp) for interacting with the Bill of Lading NFT smart contract. Users can connect their wallets and perform all contract operations through an intuitive web interface.

## Features

- 🔐 **Wallet Connection**: Connect MetaMask or other Web3 wallets
- 📦 **View Bills**: Check bill details and ownership information
- 🎨 **Mint NFTs**: Create new bill of lading NFTs (owner only)
- 💰 **Finance Management**: Pledge bills for financing and release ownership
- 🔄 **Transfer Bills**: Transfer ownership of bill NFTs
- 📱 **Responsive Design**: Works on desktop and mobile devices
- ⛓️ **Multi-Network**: Supports Polygon, Ethereum, and local networks

## Setup Instructions

### 1. Update Contract Configuration

Open `config.js` and update the contract address:

```javascript
const CONTRACT_CONFIG = {
    CONTRACT_ADDRESS: "0xYourContractAddressHere",
    // ... rest of the config
};
```

To get your contract address:
- Deploy your contract using: `npm run deploy:amoy` (or your target network)
- Copy the deployed contract address from the console output
- Paste it into `config.js`

### 2. Deploy the Frontend

#### Option A: Local Development Server (Python)

```bash
# Navigate to frontend directory
cd frontend

# Python 3
python3 -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000
```

Then open: http://localhost:8000

#### Option B: Node.js Development Server

```bash
# Install http-server globally
npm install -g http-server

# Navigate to frontend directory
cd frontend

# Start server
http-server -p 8000
```

Then open: http://localhost:8000

#### Option C: VS Code Live Server

1. Install "Live Server" extension in VS Code
2. Right-click on `index.html`
3. Select "Open with Live Server"

### 3. Setup MetaMask

1. Install [MetaMask](https://metamask.io/) browser extension
2. Add the network you deployed to (e.g., Polygon Amoy):
   - Network Name: Polygon Amoy Testnet
   - RPC URL: https://rpc-amoy.polygon.technology
   - Chain ID: 80002
   - Currency Symbol: MATIC
   - Block Explorer: https://amoy.polygonscan.com

3. Get test tokens:
   - Polygon Amoy: https://faucet.polygon.technology/
   - Sepolia: https://sepoliafaucet.com/

## Usage Guide

### Connect Wallet

1. Click "Connect Wallet" button
2. Approve the connection in MetaMask
3. Your wallet address and balance will be displayed

### View Bills

1. Go to "View Bills" tab
2. Enter a Token ID
3. Click "Get Bill Details"
4. View complete bill information including status, financing details, and IPFS links

### Mint New Bill (Owner Only)

1. Go to "Mint New Bill" tab
2. Fill in all required fields:
   - **Shipper Address**: The wallet address that will own the bill
   - **Bill Number**: Unique identifier (e.g., BOL-2026-001)
   - **IPFS Hash**: Hash of the document stored on IPFS
   - **Data Hash**: Hash of the bill data for verification
   - **Token URI**: Full IPFS metadata URI
3. Click "Mint Bill NFT"
4. Confirm transaction in MetaMask
5. Wait for confirmation

### Finance Management

#### Pledge for Financing:
1. Go to "Finance Management" tab
2. Enter Token ID of your bill
3. Enter Financier's wallet address
4. Enter financing amount in ETH/MATIC
5. Click "Pledge for Financing"
6. Confirm transaction

#### Release Ownership (Financier Only):
1. Enter Token ID
2. Click "Release Ownership"
3. This allows the bill to be transferred again

### Transfer Bill

1. Go to "Transfer Bill" tab
2. Enter Token ID
3. Enter recipient's wallet address
4. Click "Transfer Bill"
5. Note: Cannot transfer financed bills unless released

## Supported Networks

- **Polygon Amoy Testnet** (Chain ID: 80002)
- **Ethereum Sepolia Testnet** (Chain ID: 11155111)
- **Polygon Mainnet** (Chain ID: 137)
- **Ethereum Mainnet** (Chain ID: 1)
- **Hardhat Local** (Chain ID: 31337)

## File Structure

```
frontend/
├── index.html       # Main HTML page
├── styles.css       # Styling and responsive design
├── config.js        # Contract configuration
├── app.js          # Main application logic
└── README.md       # This file
```

## Troubleshooting

### "Please connect your wallet first"
- Make sure MetaMask is installed and unlocked
- Click "Connect Wallet" button
- Approve the connection in MetaMask

### "Please switch to the correct network"
- Your wallet is on a different network than where the contract is deployed
- Switch to the correct network in MetaMask
- Or add the network if it's not in your list

### Transaction Failed
- Check you have enough balance for gas fees
- Verify you have permission to perform the action (e.g., owner-only functions)
- Check if the bill is in the correct state (e.g., not financed for transfers)

### "Invalid address"
- Make sure all addresses start with "0x"
- Verify the address is a valid Ethereum address
- Copy-paste addresses to avoid typos

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never share your private keys**
2. **Always verify the contract address** before interacting
3. **Double-check transaction details** before confirming
4. **Test on testnets first** before using mainnet
5. **Keep your MetaMask updated**
6. **Be cautious of phishing sites** - bookmark the correct URL

## Production Deployment

For production deployment:

1. **Use HTTPS**: Deploy on a secure server with SSL certificate
2. **Update config.js**: Set the mainnet contract address
3. **Test thoroughly**: Test all functions on testnet first
4. **Monitor gas prices**: Implement gas estimation and warnings
5. **Add error handling**: Improve error messages for users
6. **Consider hosting**:
   - IPFS (decentralized)
   - Vercel/Netlify (easy deployment)
   - AWS S3 + CloudFront (scalable)

## Next Steps

- Add event history display
- Implement bill search functionality
- Add bulk operations
- Create admin dashboard
- Integrate with IPFS upload directly from UI
- Add notifications for events
- Implement bill metadata viewer

## Support

For issues or questions:
1. Check the console for error messages (F12 in browser)
2. Verify your network and contract address
3. Check transaction on block explorer
4. Review smart contract documentation

## License

MIT
