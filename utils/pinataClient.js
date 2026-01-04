const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
require('dotenv').config();

/**
 * Pinata IPFS服务客户端
 * 使用Pinata提供更稳定的IPFS固定服务
 */
class PinataClient {
  constructor() {
    this.apiKey = process.env.PINATA_API_KEY;
    this.secretKey = process.env.PINATA_SECRET_KEY;
    this.baseUrl = 'https://api.pinata.cloud';
    
    if (!this.apiKey || !this.secretKey) {
      console.warn('⚠️ Pinata配置未找到，请设置环境变量');
    }
  }

  /**
   * 测试Pinata连接
   */
  async testAuthentication() {
    try {
      const url = `${this.baseUrl}/data/testAuthentication`;
      const response = await axios.get(url, {
        headers: {
          pinata_api_key: this.apiKey,
          pinata_secret_api_key: this.secretKey
        }
      });
      console.log('✅ Pinata认证成功');
      return response.data;
    } catch (error) {
      console.error('❌ Pinata认证失败:', error.message);
      throw error;
    }
  }

  /**
   * 上传文件到Pinata
   * @param {string} filePath - 文件路径
   * @param {Object} metadata - 元数据
   * @returns {Promise<Object>} 上传结果
   */
  async uploadFile(filePath, metadata = {}) {
    try {
      const url = `${this.baseUrl}/pinning/pinFileToIPFS`;
      const data = new FormData();
      
      data.append('file', fs.createReadStream(filePath));
      
      if (metadata.name) {
        data.append('pinataMetadata', JSON.stringify({
          name: metadata.name,
          keyvalues: metadata.keyvalues || {}
        }));
      }
      
      const response = await axios.post(url, data, {
        maxBodyLength: 'Infinity',
        headers: {
          'Content-Type': `multipart/form-data; boundary=${data._boundary}`,
          pinata_api_key: this.apiKey,
          pinata_secret_api_key: this.secretKey
        }
      });
      
      console.log(`✅ 文件上传到Pinata成功: ${response.data.IpfsHash}`);
      return response.data;
    } catch (error) {
      console.error('❌ Pinata上传失败:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * 上传JSON到Pinata
   * @param {Object} jsonData - JSON数据
   * @param {Object} metadata - 元数据
   * @returns {Promise<Object>} 上传结果
   */
  async uploadJSON(jsonData, metadata = {}) {
    try {
      const url = `${this.baseUrl}/pinning/pinJSONToIPFS`;
      
      const data = {
        pinataContent: jsonData,
        pinataMetadata: {
          name: metadata.name || 'bill-of-lading-data',
          keyvalues: metadata.keyvalues || {}
        }
      };
      
      const response = await axios.post(url, data, {
        headers: {
          'Content-Type': 'application/json',
          pinata_api_key: this.apiKey,
          pinata_secret_api_key: this.secretKey
        }
      });
      
      console.log(`✅ JSON上传到Pinata成功: ${response.data.IpfsHash}`);
      return response.data;
    } catch (error) {
      console.error('❌ Pinata JSON上传失败:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * 获取Pin列表
   * @returns {Promise<Array>} Pin列表
   */
  async getPinList() {
    try {
      const url = `${this.baseUrl}/data/pinList`;
      const response = await axios.get(url, {
        headers: {
          pinata_api_key: this.apiKey,
          pinata_secret_api_key: this.secretKey
        }
      });
      return response.data.rows;
    } catch (error) {
      console.error('❌ 获取Pin列表失败:', error.message);
      throw error;
    }
  }

  /**
   * 取消Pin
   * @param {string} hash - IPFS哈希
   */
  async unpinFile(hash) {
    try {
      const url = `${this.baseUrl}/pinning/unpin/${hash}`;
      await axios.delete(url, {
        headers: {
          pinata_api_key: this.apiKey,
          pinata_secret_api_key: this.secretKey
        }
      });
      console.log(`✅ 文件Unpin成功: ${hash}`);
    } catch (error) {
      console.error('❌ Unpin失败:', error.message);
      throw error;
    }
  }

  /**
   * 生成IPFS网关URL
   * @param {string} hash - IPFS哈希
   * @returns {string} 网关URL
   */
  getGatewayUrl(hash) {
    return `https://gateway.pinata.cloud/ipfs/${hash}`;
  }
}

module.exports = PinataClient;
