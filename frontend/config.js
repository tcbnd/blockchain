// Contract Configuration
const CONTRACT_CONFIG = {
    // Replace with your deployed contract address
    CONTRACT_ADDRESS: "0xfB18AA14dBC3A6A3cCa47150b29055F83134C63b",
    
    // Contract ABI - Generated from your smart contract
    CONTRACT_ABI: [
        "function mintBill(address shipper, string billNumber, string ipfsHash, string dataHash, string _tokenURI) public returns (uint256)",
        "function pledgeForFinancing(uint256 tokenId, address financier, uint256 amount) public",
        "function releaseOwnership(uint256 tokenId) public",
        "function getBillData(uint256 tokenId) public view returns (tuple(string billNumber, string ipfsHash, string dataHash, string tokenURI, uint256 timestamp, bool isFinanced, address financier, uint256 financedAmount, bool isReleased))",
        "function ownerOf(uint256 tokenId) public view returns (address)",
        "function balanceOf(address owner) public view returns (uint256)",
        "function transferFrom(address from, address to, uint256 tokenId) public",
        "function safeTransferFrom(address from, address to, uint256 tokenId) public",
        "function isTransferable(uint256 tokenId) public view returns (bool)",
        "function tokenURI(uint256 tokenId) public view returns (string)",
        "function owner() public view returns (address)",
        "event BillMinted(uint256 indexed tokenId, address indexed shipper, string billNumber)",
        "event BillFinanced(uint256 indexed tokenId, address indexed financier, uint256 amount)",
        "event BillReleased(uint256 indexed tokenId)",
        "event Transfer(address indexed from, address indexed to, uint256 indexed tokenId)"
    ],
    
    // Network Configuration
    NETWORKS: {
        80002: {
            name: "Polygon Amoy Testnet",
            rpcUrl: "https://rpc-amoy.polygon.technology",
            blockExplorer: "https://amoy.polygonscan.com",
            nativeCurrency: {
                name: "MATIC",
                symbol: "MATIC",
                decimals: 18
            }
        },
        11155111: {
            name: "Sepolia Testnet",
            rpcUrl: "https://ethereum-sepolia-rpc.publicnode.com",
            blockExplorer: "https://sepolia.etherscan.io",
            nativeCurrency: {
                name: "ETH",
                symbol: "ETH",
                decimals: 18
            }
        },
        137: {
            name: "Polygon Mainnet",
            rpcUrl: "https://polygon-rpc.com",
            blockExplorer: "https://polygonscan.com",
            nativeCurrency: {
                name: "MATIC",
                symbol: "MATIC",
                decimals: 18
            }
        },
        1: {
            name: "Ethereum Mainnet",
            rpcUrl: "https://eth.llamarpc.com",
            blockExplorer: "https://etherscan.io",
            nativeCurrency: {
                name: "ETH",
                symbol: "ETH",
                decimals: 18
            }
        },
        31337: {
            name: "Hardhat Local",
            rpcUrl: "http://127.0.0.1:8545",
            blockExplorer: "",
            nativeCurrency: {
                name: "ETH",
                symbol: "ETH",
                decimals: 18
            }
        }
    }
};
