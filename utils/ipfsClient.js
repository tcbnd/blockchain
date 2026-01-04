const { create } = require('ipfs-http-client');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

/**
 * IPFS客户端配置
 * 支持Infura和本地IPFS节点
 */
class IPFSClient {
  constructor() {
    // 优先使用Infura配置
    if (process.env.IPFS_PROJECT_ID && process.env.IPFS_PROJECT_SECRET) {
      const auth = 'Basic ' + Buffer.from(
        process.env.IPFS_PROJECT_ID + ':' + process.env.IPFS_PROJECT_SECRET
      ).toString('base64');

      this.client = create({
        host: 'ipfs.infura.io',
        port: 5001,
        protocol: 'https',
        headers: {
          authorization: auth,
        },
      });
      console.log('✅ 使用Infura IPFS服务');
    } 
    // 使用本地IPFS节点
    else {
      this.client = create({
        host: 'localhost',
        port: 5001,
        protocol: 'http',
      });
      console.log('✅ 使用本地IPFS节点');
    }
  }

  /**
   * 上传文件到IPFS
   * @param {string} filePath - 文件路径
   * @returns {Promise<string>} IPFS哈希
   */
  async uploadFile(filePath) {
    try {
      const file = fs.readFileSync(filePath);
      const result = await this.client.add(file);
      console.log(`✅ 文件上传成功: ${result.path}`);
      return result.path;
    } catch (error) {
      console.error('❌ 文件上传失败:', error.message);
      throw error;
    }
  }

  /**
   * 上传JSON数据到IPFS
   * @param {Object} data - JSON对象
   * @returns {Promise<string>} IPFS哈希
   */
  async uploadJSON(data) {
    try {
      const jsonString = JSON.stringify(data, null, 2);
      const result = await this.client.add(jsonString);
      console.log(`✅ JSON上传成功: ${result.path}`);
      return result.path;
    } catch (error) {
      console.error('❌ JSON上传失败:', error.message);
      throw error;
    }
  }

  /**
   * 从IPFS下载文件
   * @param {string} hash - IPFS哈希
   * @returns {Promise<Buffer>} 文件内容
   */
  async downloadFile(hash) {
    try {
      const chunks = [];
      for await (const chunk of this.client.cat(hash)) {
        chunks.push(chunk);
      }
      const content = Buffer.concat(chunks);
      console.log(`✅ 文件下载成功: ${hash}`);
      return content;
    } catch (error) {
      console.error('❌ 文件下载失败:', error.message);
      throw error;
    }
  }

  /**
   * 从IPFS获取JSON数据
   * @param {string} hash - IPFS哈希
   * @returns {Promise<Object>} JSON对象
   */
  async getJSON(hash) {
    try {
      const content = await this.downloadFile(hash);
      const data = JSON.parse(content.toString());
      return data;
    } catch (error) {
      console.error('❌ JSON获取失败:', error.message);
      throw error;
    }
  }

  /**
   * 生成IPFS网关URL
   * @param {string} hash - IPFS哈希
   * @returns {string} 网关URL
   */
  getGatewayUrl(hash) {
    return `https://ipfs.io/ipfs/${hash}`;
  }

  /**
   * Pin文件（保持文件在IPFS网络中）
   * @param {string} hash - IPFS哈希
   */
  async pinFile(hash) {
    try {
      await this.client.pin.add(hash);
      console.log(`✅ 文件已Pin: ${hash}`);
    } catch (error) {
      console.error('❌ Pin失败:', error.message);
      throw error;
    }
  }
}

module.exports = IPFSClient;
