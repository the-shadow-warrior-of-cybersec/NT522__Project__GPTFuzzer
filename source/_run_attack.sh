#!/bin/bash

# Script thực hiện tấn công SQLi và thu kết quả cho các file payload đã transform
# Hỗ trợ thu thập các chỉ số để so sánh với GPTFuzzer và AdvSQLi

# Định nghĩa file log tổng hợp
LOG_FILE="../log/attack_script_log.txt"
mkdir -p "$(dirname "$LOG_FILE")"
echo "===== Bắt đầu chạy script: $(date) =====" >> "$LOG_FILE"

# Kiểm tra môi trường
echo "Kiểm tra môi trường..." | tee -a "$LOG_FILE"
if ! python -c "import psutil" 2>/dev/null; then
    echo "Lỗi: Thư viện psutil chưa được cài đặt. Cài đặt bằng: pip install psutil" | tee -a "$LOG_FILE"
    exit 1
fi

# Vòng lặp qua các độ dài payload
for txt_out_len in {10..70..10}
do
    echo "<========== Payload với độ dài $txt_out_len ==========>" | tee -a "$LOG_FILE"

    # Định nghĩa đường dẫn đầu vào và thư mục lưu kết quả
    data_path="../_transform_payload/payload_with_length_of_${txt_out_len}.csv"
    save_dir="../_attack_result"
    php_session_id="i1pb8srhvptnmpkrrtgjvr4ogh"
    url="http://localhost/DVWA/vulnerabilities/sqli/?id="
    security_level="low"

    # Kiểm tra file đầu vào
    if [ ! -f "$data_path" ]; then
        echo "-----> Lỗi: File đầu vào $data_path không tồn tại!" | tee -a "$LOG_FILE"
        continue
    fi

    # Tạo thư mục lưu kết quả
    mkdir -p "$save_dir"

    # Chạy lệnh tấn công với txt_out_len và waf_config
    echo "Chạy tấn công với file $data_path..." | tee -a "$LOG_FILE"
    python attack.py \
        --input_file="$data_path" \
        --save_dir="$save_dir" \
        --txt_out_len="$txt_out_len" \
        --php_session_id="$php_session_id" \
        --url="$url" \
        --security_level="$security_level" 2>&1 | tee -a "$LOG_FILE"

    # Kiểm tra và thông báo kết quả
    output_file="$save_dir/dataset_for_payload_length_${txt_out_len}.csv"
    summary_file="$save_dir/attack_summary_for_payload_length_${txt_out_len}.txt"

    if [ -f "$output_file" ] && [ -f "$summary_file" ]; then
        echo "-----> Thành công! Kết quả lưu tại $output_file" | tee -a "$LOG_FILE"
        echo "Tóm tắt chỉ số:" | tee -a "$LOG_FILE"
        grep -E "Success Rate|Total Payloads" "$summary_file" | tee -a "$LOG_FILE"
    else
        echo "-----> Lỗi: Không tạo được file $output_file hoặc $summary_file!" | tee -a "$LOG_FILE"
    fi
done

echo "===== Kết thúc script: $(date) =====" >> "$LOG_FILE"