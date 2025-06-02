#!/bin/bash

# Chuyển các integer payload sang payload có thể tận dụng cho các payload có độ dài từ 10 đến 70, bước nhảy 10
for txt_out_len in {10..70..10}
do
    echo "<========== Payload với độ dài $txt_out_len ==========>"

    # Định nghĩa đường dẫn đầu vào và đầu ra
    data_path="../_integer_payload/nums_4000_in_1_out_${txt_out_len}.csv"
    save_path="../_transform_payload/payload_with_length_of_${txt_out_len}.csv"

    # Tạo thư mục nếu chưa tồn tại
    mkdir -p "$(dirname "$save_path")"

    # Chạy lệnh transform.py
    python transform.py \
        --grammar_path=../attack_grammar/sql_ebnf.txt \
        --data_path="${data_path}" \
        --save_path="${save_path}"
done