import base64
import logging

# 定义常量
MAX_ID_LEN = 16  # 假设 MAX_ID_LEN 为 32
MAX_KEY_LEN = 32  # 假设 MAX_KEY_LEN 为 32
MAX_SECRET_KEY_LEN = 8  # 假设 MAX_SECRET_KEY_LEN 为 32


class IDInfo:
    def __init__(self):
        self.sn = bytearray(MAX_ID_LEN)

class BurnInfo:
    def __init__(self, m_sn, m_key, m_secretKey):
        self.m_sn = m_sn
        self.m_key = m_key
        self.m_secretKey = m_secretKey

def decode_base64(data, buffer, buffer_size):
    decoded_data = base64.b64decode(data)
    buffer[:len(decoded_data)] = decoded_data
    return len(decoded_data)

def alloc_sn_to_device(burn_info):
    sn_buff = bytearray(MAX_ID_LEN)
    key_buff = bytearray(MAX_KEY_LEN)
    secret_key_buff = bytearray(MAX_SECRET_KEY_LEN)

    decode_base64(burn_info.m_sn, sn_buff, MAX_ID_LEN)
    decode_base64(burn_info.m_key, key_buff, MAX_KEY_LEN)
    decode_base64(burn_info.m_secretKey, secret_key_buff, MAX_SECRET_KEY_LEN)

    print(sn_buff)
    print(key_buff)
    print(secret_key_buff)
    id_info = IDInfo()
    for i in range(MAX_ID_LEN):
        id_info.sn[i] = sn_buff[i] ^ secret_key_buff[i % MAX_SECRET_KEY_LEN]
    print(id_info.sn)


# 示例用法 0C2ED480A49F3A0B
# 示例用法 0C2EFF��A4C7�l
sn="KSO+hOFs1q4bEdux016wzw=="
key="HUWLs4JVt8seF9yyhVq3lxlgjMGnKpKfaBf9s9Itl+g="
secretKey="KSO+hOFs1q4="
burn_info = BurnInfo(sn, key, secretKey)
alloc_sn_to_device(burn_info)