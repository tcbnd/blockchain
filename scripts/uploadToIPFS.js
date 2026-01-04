const crypto = require('crypto');
const IPFSClient = require('../utils/ipfsClient');
const PinataClient = require('../utils/pinataClient');
require('dotenv').config();

/**
 * 提单数据上传到IPFS
 * 这个脚本演示如何将OCR提取的提单数据上传到IPFS
 */

// 选择使用的IPFS服务
const USE_PINATA = process.env.PINATA_API_KEY ? true : false;

/**
 * 创建提单元数据
 * @param {Object} billData - OCR提取的提单数据
 * @returns {Object} 元数据对象
 */
function createBillMetadata(billData) {
  return {
    name: `Bill of Lading - ${billData.billNumber}`,
    description: "Digital Bill of Lading NFT",
    image: billData.imageIPFS || "", // 原始提单图片的IPFS哈希
    attributes: [
      {
        trait_type: "Bill Number",
        value: billData.billNumber
      },
      {
        trait_type: "Shipper",
        value: billData.shipper
      },
      {
        trait_type: "Consignee",
        value: billData.consignee
      },
      {
        trait_type: "Vessel",
        value: billData.vessel
      },
      {
        trait_type: "Port of Loading",
        value: billData.portOfLoading
      },
      {
        trait_type: "Port of Discharge",
        value: billData.portOfDischarge
      },
      {
        trait_type: "Cargo Description",
        value: billData.cargoDescription
      },
      {
        trait_type: "Issue Date",
        value: billData.issueDate
      }
    ],
    properties: {
      billData: billData,
      uploadTimestamp: new Date().toISOString()
    }
  };
}

/**
 * 计算数据哈希
 * @param {Object} data - 数据对象
 * @returns {string} SHA256哈希
 */
function calculateDataHash(data) {
  const jsonString = JSON.stringify(data);
  return crypto.createHash('sha256').update(jsonString).digest('hex');
}

/**
 * 上传提单数据到IPFS
 * @param {Object} billData - OCR提取的提单数据
 * @returns {Promise<Object>} 上传结果
 */
async function uploadBillToIPFS(billData) {
  try {
    console.log('\n=== 开始上传提单到IPFS ===');
    console.log('提单编号:', billData.billNumber);
    
    // 1. 创建元数据
    const metadata = createBillMetadata(billData);
    console.log('\n✅ 元数据创建成功');
    
    // 2. 计算数据哈希
    const dataHash = calculateDataHash(billData);
    console.log('数据哈希:', dataHash);
    
    // 3. 上传到IPFS
    let ipfsHash;
    let gatewayUrl;
    
    if (USE_PINATA) {
      console.log('\n使用Pinata服务上传...');
      const pinata = new PinataClient();
      
      // 测试认证
      await pinata.testAuthentication();
      
      // 上传元数据
      const result = await pinata.uploadJSON(metadata, {
        name: `BOL-${billData.billNumber}`,
        keyvalues: {
          billNumber: billData.billNumber,
          type: 'bill-of-lading',
          timestamp: Date.now().toString()
        }
      });
      
      ipfsHash = result.IpfsHash;
      gatewayUrl = pinata.getGatewayUrl(ipfsHash);
    } else {
      console.log('\n使用IPFS客户端上传...');
      const ipfs = new IPFSClient();
      
      // 上传元数据
      ipfsHash = await ipfs.uploadJSON(metadata);
      gatewayUrl = ipfs.getGatewayUrl(ipfsHash);
      
      // Pin文件
      await ipfs.pinFile(ipfsHash);
    }
    
    console.log('\n✅ 上传完成!');
    console.log('IPFS哈希:', ipfsHash);
    console.log('网关URL:', gatewayUrl);
    console.log('数据哈希:', dataHash);
    
    return {
      ipfsHash,
      dataHash,
      gatewayUrl,
      metadata
    };
    
  } catch (error) {
    console.error('\n❌ 上传失败:', error.message);
    throw error;
  }
}

/**
 * 从IPFS获取提单数据
 * @param {string} ipfsHash - IPFS哈希
 * @returns {Promise<Object>} 提单数据
 */
async function getBillFromIPFS(ipfsHash) {
  try {
    console.log('\n=== 从IPFS获取提单数据 ===');
    console.log('IPFS哈希:', ipfsHash);
    
    let billData;
    
    if (USE_PINATA) {
      // 使用Pinata网关
      const pinata = new PinataClient();
      const url = pinata.getGatewayUrl(ipfsHash);
      const axios = require('axios');
      const response = await axios.get(url);
      billData = response.data;
    } else {
      // 使用IPFS客户端
      const ipfs = new IPFSClient();
      billData = await ipfs.getJSON(ipfsHash);
    }
    
    console.log('✅ 获取成功');
    console.log('提单编号:', billData.properties.billData.billNumber);
    
    return billData;
    
  } catch (error) {
    console.error('\n❌ 获取失败:', error.message);
    throw error;
  }
}

// 示例：测试上传和获取
async function main() {
  // 示例提单数据（从OCR系统提取）
  const sampleBillData = {
    billNumber: "BOL-2026-001",
    shipper: "ABC Trading Co., Ltd.",
    consignee: "XYZ Import Export Inc.",
    vessel: "COSCO SHIPPING GEMINI",
    portOfLoading: "Shanghai, China",
    portOfDischarge: "Los Angeles, USA",
    cargoDescription: "Electronics and Components - 100 Cartons",
    issueDate: "2026-01-03",
    weight: "2000 KG",
    volume: "50 CBM"
  };
  
  try {
    // 上传到IPFS
    const uploadResult = await uploadBillToIPFS(sampleBillData);
    
    console.log('\n=== 上传结果 ===');
    console.log(JSON.stringify(uploadResult, null, 2));
    
    // 等待几秒后从IPFS获取
    console.log('\n等待3秒后验证...');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // 从IPFS获取
    const retrievedData = await getBillFromIPFS(uploadResult.ipfsHash);
    
    console.log('\n=== 验证数据完整性 ===');
    const retrievedHash = calculateDataHash(retrievedData.properties.billData);
    console.log('原始哈希:', uploadResult.dataHash);
    console.log('获取哈希:', retrievedHash);
    console.log('验证结果:', uploadResult.dataHash === retrievedHash ? '✅ 匹配' : '❌ 不匹配');
    
  } catch (error) {
    console.error('执行失败:', error);
    process.exit(1);
  }
}

// 导出函数供其他脚本使用
module.exports = {
  uploadBillToIPFS,
  getBillFromIPFS,
  createBillMetadata,
  calculateDataHash
};

// 如果直接运行此脚本
if (require.main === module) {
  main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
    });
}
