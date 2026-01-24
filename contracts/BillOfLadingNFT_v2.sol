// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title BillOfLadingNFT
 * @dev 提单NFT智能合约 - ERC-721标准
 * 使用18位数字的Token ID
 */
contract BillOfLadingNFT is ERC721, Ownable {
    // 从一个大数字开始，生成18位Token ID
    uint256 private _tokenIdCounter = 100000000000000000; // 18 digits starting number
    
    struct BillData {
        string billNumber;
        string ipfsHash;
        string dataHash;
        string tokenURI;
        uint256 timestamp;
        bool isFinanced;
        address financier;
        uint256 financedAmount;
        bool isReleased;
    }
    
    mapping(uint256 => BillData) public bills;
    mapping(string => uint256) public billNumberToTokenId;
    
    event BillMinted(uint256 indexed tokenId, address indexed shipper, string billNumber);
    event BillFinanced(uint256 indexed tokenId, address indexed financier, uint256 amount);
    event BillReleased(uint256 indexed tokenId);
    
    constructor() ERC721("BillOfLading", "BOL") Ownable(msg.sender) {}
    
    function mintBill(
        address shipper,
        string memory billNumber,
        string memory ipfsHash,
        string memory dataHash,
        string memory _tokenURI
    ) public onlyOwner returns (uint256) {
        require(bytes(billNumber).length > 0, "Bill number required");
        require(billNumberToTokenId[billNumber] == 0, "Bill already exists");
        
        uint256 tokenId = _tokenIdCounter++;
        _safeMint(shipper, tokenId);
        
        bills[tokenId] = BillData({
            billNumber: billNumber,
            ipfsHash: ipfsHash,
            dataHash: dataHash,
            tokenURI: _tokenURI,
            timestamp: block.timestamp,
            isFinanced: false,
            financier: address(0),
            financedAmount: 0,
            isReleased: false
        });
        
        billNumberToTokenId[billNumber] = tokenId;
        emit BillMinted(tokenId, shipper, billNumber);
        
        return tokenId;
    }
    
    function pledgeForFinancing(uint256 tokenId, address financier, uint256 amount) public {
        require(ownerOf(tokenId) == msg.sender, "Not owner");
        require(!bills[tokenId].isFinanced, "Already financed");
        
        bills[tokenId].isFinanced = true;
        bills[tokenId].financier = financier;
        bills[tokenId].financedAmount = amount;
        
        emit BillFinanced(tokenId, financier, amount);
    }
    
    function releaseOwnership(uint256 tokenId) public {
        require(bills[tokenId].financier == msg.sender, "Not financier");
        bills[tokenId].isReleased = true;
        emit BillReleased(tokenId);
    }
    
    function getBillData(uint256 tokenId) public view returns (BillData memory) {
        require(_ownerOf(tokenId) != address(0), "Token not exist");
        return bills[tokenId];
    }
    
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "Token not exist");
        return bills[tokenId].tokenURI;
    }
    
    function isTransferable(uint256 tokenId) public view returns (bool) {
        return !bills[tokenId].isFinanced || bills[tokenId].isReleased;
    }
    
    function _update(address to, uint256 tokenId, address auth) internal override returns (address) {
        address from = _ownerOf(tokenId);
        if (from != address(0)) {
            require(isTransferable(tokenId), "Bill financed");
        }
        return super._update(to, tokenId, auth);
    }
}
