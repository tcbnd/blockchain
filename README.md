# 提单NFT区块链系统 (Bill of Lading NFT)

基于ERC-721标准的提单NFT智能合约系统，支持提单的铸造、转移、销毁和融资功能，集成IPFS去中心化存储。

## 🎯 功能特点

### 智能合约功能
- ✅ **ERC-721 NFT**: 符合标准的NFT实现
- ✅ **铸造提单**: 将实体提单数字化为NFT
- ✅ **转移功能**: 支持提单所有权转移
- ✅ **销毁功能**: 支持提单NFT销毁
- ✅ **融资抵押**: 提单可用于供应链金融
- ✅ **货权释放**: 融资方控制货权释放
- ✅ **数据验证**: SHA256哈希验证数据完整性

### IPFS集成
- ✅ **去中心化存储**: 提单数据存储在IPFS
- ✅ **双客户端支持**: 支持Infura和Pinata服务
- ✅ **元数据管理**: NFT元数据存储在IPFS
- ✅ **Pin固定**: 确保数据持久性

## 📁 项目结构

```
blockchain/
├── contracts/              # 智能合约
│   └── BillOfLadingNFT.sol
├── scripts/               # 部署和交互脚本
│   ├── deploy.js          # 部署合约
│   ├── interact.js        # 合约交互测试
│   ├── uploadToIPFS.js    # IPFS上传工具
│   └── mintWithIPFS.js    # 完整铸造流程
├── test/                  # 测试文件
│   └── BillOfLadingNFT.test.js
├── utils/                 # 工具类
│   ├── ipfsClient.js      # IPFS客户端
│   └── pinataClient.js    # Pinata客户端
├── hardhat.config.js      # Hardhat配置
├── package.json           # 项目依赖
└── .env.example          # 环境变量模板
```

## 🚀 快速开始

### 1. 安装依赖

```powershell
cd blockchain
npm install
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```powershell
Copy-Item .env.example .env
```

编辑 `.env` 文件：

```env
# 部署账户私钥（从MetaMask导出）
PRIVATE_KEY=your_private_key_here

# RPC节点
MUMBAI_RPC_URL=https://rpc-mumbai.maticvigil.com
POLYGON_RPC_URL=https://polygon-rpc.com

# IPFS配置（选择一个）
# 方案1: 使用Pinata（推荐）
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key

# 方案2: 使用Infura
IPFS_PROJECT_ID=your_ipfs_project_id
IPFS_PROJECT_SECRET=your_ipfs_project_secret
```

### 3. 编译合约

```powershell
npm run compile
```

### 4. 运行测试

```powershell
npm test
```

### 5. 部署合约

#### 本地测试网络

```powershell
# 启动本地节点
npm run node

# 在新窗口部署
npm run deploy:local
```

#### Polygon Mumbai测试网

```powershell
npm run deploy:mumbai
```

部署后保存合约地址，设置环境变量：

```powershell
$env:CONTRACT_ADDRESS="0xYourContractAddress"
```

## 📝 使用说明

### 获取测试币

#### Polygon Mumbai测试网
- 访问 [Mumbai Faucet](https://faucet.polygon.technology/)
- 输入钱包地址获取测试MATIC

#### Sepolia测试网
- 访问 [Sepolia Faucet](https://sepoliafaucet.com/)
- 获取测试ETH

### IPFS服务配置

#### 方案1: 使用Pinata（推荐）

1. 注册 [Pinata](https://www.pinata.cloud/)
2. 获取API Key和Secret Key
3. 配置到 `.env` 文件

#### 方案2: 使用本地IPFS节点

```powershell
# 安装IPFS Desktop
# 下载: https://docs.ipfs.tech/install/ipfs-desktop/

# 启动IPFS节点
ipfs daemon
```

### 完整使用流程

#### 1. 上传提单到IPFS

```powershell
node scripts/uploadToIPFS.js
```

这将：
- 创建提单元数据
- 上传到IPFS
- 返回IPFS哈希和数据哈希

#### 2. 铸造提单NFT

```powershell
# 设置合约地址
$env:CONTRACT_ADDRESS="0xYourContractAddress"

# 执行完整流程（IPFS上传 + NFT铸造）
node scripts/mintWithIPFS.js
```

#### 3. 与合约交互

```powershell
node scripts/interact.js
```

这将测试：
- 铸造NFT
- 查询提单信息
- 抵押融资
- 释放货权
- 转移提单

### 智能合约主要函数

#### 铸造提单
```javascript
await contract.mintBill(
  shipperAddress,    // 托运人地址
  billNumber,        // 提单编号
  ipfsHash,          // IPFS哈希
  dataHash,          // 数据SHA256哈希
  tokenURI           // Token URI
);
```

#### 抵押融资
```javascript
await contract.pledgeForFinancing(
  tokenId,           // Token ID
  financierAddress,  // 融资方地址
  amount             // 融资金额（wei）
);
```

#### 释放货权
```javascript
await contract.releaseOwnership(tokenId);
```

#### 查询提单信息
```javascript
const billData = await contract.getBillData(tokenId);
const billByNumber = await contract.getBillByNumber(billNumber);
```

#### 验证数据完整性
```javascript
const isValid = await contract.verifyBillData(tokenId, dataHash);
```

#### 转移提单
```javascript
await contract.transferFrom(fromAddress, toAddress, tokenId);
```

#### 销毁提单
```javascript
await contract.burn(tokenId);
```

## 🔗 与OCR系统集成

如果你已经有OCR系统提取提单信息，集成步骤如下：

### 1. OCR数据格式

```javascript
const ocrData = {
  billNumber: "BOL-2026-001",
  shipper: "ABC Trading Co., Ltd.",
  consignee: "XYZ Import Export Inc.",
  vessel: "COSCO SHIPPING GEMINI",
  portOfLoading: "Shanghai, China",
  portOfDischarge: "Los Angeles, USA",
  cargoDescription: "Electronics - 100 Cartons",
  issueDate: "2026-01-03",
  weight: "2000 KG",
  volume: "50 CBM"
};
```

### 2. 集成代码示例

```javascript
const { uploadBillToIPFS } = require('./scripts/uploadToIPFS');
const hre = require("hardhat");

async function processOCRResult(ocrData) {
  // 1. 上传到IPFS
  const ipfsResult = await uploadBillToIPFS(ocrData);
  
  // 2. 连接合约
  const contract = await hre.ethers.getContractAt(
    "BillOfLadingNFT",
    process.env.CONTRACT_ADDRESS
  );
  
  // 3. 铸造NFT
  const mintTx = await contract.mintBill(
    shipperAddress,
    ocrData.billNumber,
    ipfsResult.ipfsHash,
    "0x" + ipfsResult.dataHash,
    `ipfs://${ipfsResult.ipfsHash}`
  );
  
  await mintTx.wait();
  console.log("NFT铸造成功!");
  
  return {
    tokenId: await contract.billNumberToTokenId(ocrData.billNumber),
    ipfsHash: ipfsResult.ipfsHash,
    transactionHash: mintTx.hash
  };
}
```

## 🧪 测试

### 运行所有测试
```powershell
npm test
```

### 运行特定测试
```powershell
npx hardhat test test/BillOfLadingNFT.test.js
```

### 测试覆盖率
```powershell
npx hardhat coverage
```

## 🔍 验证合约

部署到测试网后验证合约：

```powershell
npx hardhat verify --network mumbai YOUR_CONTRACT_ADDRESS
```

## 📊 合约功能流程图

```
OCR系统提取提单数据
        ↓
上传到IPFS（获取哈希）
        ↓
铸造NFT（链上记录）
        ↓
    提单NFT创建成功
        ↓
   ┌────┴────┐
   ↓         ↓
转移提单   抵押融资
   ↓         ↓
查询验证   释放货权
   ↓         ↓
销毁提单   还款解押
```

## 🛡️ 安全注意事项

1. **私钥安全**: 
   - 永远不要提交 `.env` 文件到git
   - 使用硬件钱包存储主网私钥
   - 测试网和主网使用不同的钱包

2. **合约安全**:
   - 部署前进行全面测试
   - 考虑进行专业审计
   - 使用OpenZeppelin的安全合约

3. **IPFS数据**:
   - 重要数据使用Pin固定
   - 考虑多个IPFS服务备份
   - 定期验证数据可访问性

## 📚 技术栈

- **智能合约**: Solidity ^0.8.20
- **开发框架**: Hardhat
- **NFT标准**: ERC-721 (OpenZeppelin)
- **存储**: IPFS (Infura/Pinata)
- **测试**: Chai, Mocha
- **网络**: Polygon, Ethereum

## 🌐 支持的区块链网络

- Polygon Mumbai (测试网)
- Polygon Mainnet (主网)
- Ethereum Sepolia (测试网)
- 本地Hardhat网络

## 📖 相关资源

- [OpenZeppelin文档](https://docs.openzeppelin.com/)
- [Hardhat文档](https://hardhat.org/docs)
- [IPFS文档](https://docs.ipfs.tech/)
- [Polygon文档](https://docs.polygon.technology/)
- [ERC-721标准](https://eips.ethereum.org/EIPS/eip-721)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## ⚠️ 免责声明

本项目仅用于学习和测试目的。在生产环境使用前，请确保：
1. 进行充分的安全审计
2. 完善的测试覆盖
3. 合规性审查
4. 用户数据保护措施

---

**祝你使用愉快！如有问题，请提交Issue。** 🚀
