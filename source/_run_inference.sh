#!/bin/bash

# Tạo các integer payload với độ dài payload từ 10 đến 70 (bước nhảy 10)
for txt_out_len in {10..70..10}
do
    echo "<========== Payload với độ dài $txt_out_len ==========>"

    # Định dạng đường dẫn lưu file, 4000 payload, nhận vào 1 token, trả ra 10 token cho mỗi payload
    saving_format="../_integer_payload/nums_4000_in_1_out_${txt_out_len}.csv"

    # Tạo thư mục nếu chưa tồn tại
    mkdir -p "$(dirname "$saving_format")"

    # Chạy lệnh inference
    python inference.py \
        --lm_name="models/fine_tune_model_sql_modsecurity" \
        --ref_lm_name="models/pretrain_model_sql" \
        --total_nums=4000 \
        --txt_in_len=1 \
        --txt_out_len="$txt_out_len" \
        --save_path="$saving_format"

    # Kiểm tra và thông báo kết quả
    if [ -f "$saving_format" ]; then
        echo "-----> Successfully! Kết quả lưu tại $saving_format!"
    else
        echo "-----> Fail! Không tạo được file $saving_format!!!"
    fi
done