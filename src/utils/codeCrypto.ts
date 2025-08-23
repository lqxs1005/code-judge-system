import CryptoJS from 'crypto-js'

const keyB64 = import.meta.env.VITE_CODE_ENCRYPTION_KEY
const ivB64 = import.meta.env.VITE_CODE_ENCRYPTION_IV

function getKeyAndIV() {
  if (!keyB64 || !ivB64) {
    throw new Error('加密密钥或IV未配置，请检查环境变量')
  }
  const key = CryptoJS.enc.Base64.parse(keyB64)
  const iv = CryptoJS.enc.Base64.parse(ivB64)
  return { key, iv }
}

/**
 * AES-256-CBC 加密，返回Base64字符串
 */
export function encryptCode(plainCode: string): string {
  try {
    const { key, iv } = getKeyAndIV()
    const encrypted = CryptoJS.AES.encrypt(plainCode, key, {
      iv,
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7
    })
    return encrypted.ciphertext.toString(CryptoJS.enc.Base64)
  } catch (e) {
    throw new Error('代码加密失败: ' + (e as Error).message)
  }
}
