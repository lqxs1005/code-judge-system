import os
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def get_key_and_iv():
    key_b64 = os.environ.get('CODE_ENCRYPTION_KEY')
    iv_b64 = os.environ.get('CODE_ENCRYPTION_IV')
    if not key_b64 or not iv_b64:
        raise ValueError('加密密钥或IV未配置，请检查环境变量')
    key = base64.b64decode(key_b64)
    iv = base64.b64decode(iv_b64)
    if len(key) != 32 or len(iv) != 16:
        raise ValueError('密钥需32字节，IV需16字节')
    return key, iv

def decrypt_code(encrypted_code_b64: str) -> str:
    try:
        key, iv = get_key_and_iv()
        ciphertext = base64.b64decode(encrypted_code_b64)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plain = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return plain.decode('utf-8')
    except Exception as e:
        raise ValueError(f'Failed to decrypt code: {e}')
