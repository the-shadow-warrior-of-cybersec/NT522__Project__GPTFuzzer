# GPTFuzzer - Đồ án NT522

## Thành viên nhóm

| STT | Họ và tên             | MSSV     | Vai trò     |
| --- | --------------------- | -------- | ----------- |
| 1   | Trần Thanh Phong      | 22521093 | Trưởng nhóm |
| 2   | Nguyễn Lê Bảo Phúc    | 22521131 | Thành viên  |
| 3   | Võ Quốc Bảo           | 23520146 | Thành viên  |
| 4   | Nguyễn Đoàn Gia Khánh | 23520720 | Thành viên  |

## Giới thiệu

GPTFuzzer là một khung kiểm thử Web Application Firewall (WAF) tiên tiến dựa trên các mô hình ngôn ngữ biến đổi (Transformer). Thay vì phụ thuộc vào ngữ pháp cố định và bộ dữ liệu seed lớn, GPTFuzzer sử dụng mô hình GPT-2 kết hợp với học tăng cường để tự động sinh ra các payload tấn công có khả năng vượt qua WAF cao.

### Tính cấp thiết của kiểm thử WAF

Hầu hết các WAF hoạt động theo mô hình blacklist với tập hợp quy tắc chặn các payload tấn công đã biết. Tuy nhiên, các quy tắc này không thể cập nhật tự động khi các phương thức tấn công mới xuất hiện, do đó cần kiểm thử WAF liên tục để phát hiện các payload có khả năng vượt qua bảo mật.

### Ưu điểm của GPTFuzzer

-   **Không cần ngữ pháp cố định**: Tự động học cấu trúc và ngữ cảnh của payload tấn công
-   **Hiệu quả cao**: Sử dụng học tăng cường với hàm phần thưởng để tối ưu xác suất vượt qua WAF
-   **Tránh tối ưu cục bộ**: Áp dụng kỹ thuật điều chỉnh phạt KL và reward model
-   **Linh hoạt**: Hỗ trợ nhiều loại tấn công (SQLi, XSS, RCE)

## Cấu trúc hệ thống

GPTFuzzer hoạt động theo 5 giai đoạn chính:

1. **[A] Thu thập và tiền xử lý dữ liệu**
2. **[B] Huấn luyện trước mô hình ngôn ngữ (Language Model Pre-Training)**
3. **[C] Huấn luyện mô hình phần thưởng (Reward Model)**
4. **[D] Học tăng cường (Reinforcement Learning) với PPO**
5. **[E] Sinh payload và đánh giá trên WAF**

## Yêu cầu hệ thống

-   **Python**: 3.8 (được test trên Python 3.8.20)
-   **Môi trường ảo**: khuyến nghị sử dụng venv
-   **Dependencies**: xem `requirements.txt`

## Cài đặt

1. Tạo môi trường ảo:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows
```

2. Cài đặt dependencies:

```bash
pip install -r requirements.txt
```

## Cách sử dụng

### Bước 1: Inference - Tạo payload dạng integer

Sinh ra các payload dạng integer để phục vụ cho các quy trình tiếp theo:

```bash
cd source
./_run_inference.sh
```

**Output**: Các file CSV trong thư mục `_integer_payload/` với format:

-   `nums_4000_in_1_out_[length].csv` (length: 10, 20, 30, 40, 50, 60, 70) với length là độ dài của payload.

### Bước 2: Data Transform - Chuyển đổi payload

Chuyển hóa integer payload sang payload thực sự dựa trên ngữ pháp tấn công:

```bash
cd source
./_run_transform.sh
```

**Output**: Các file CSV trong thư mục `_transform_payload/` với format:

-   `payload_with_length_of_[length].csv` (length: 10, 20, 30, 40, 50, 60, 70) với length là độ dài của payload.

### Bước 3: Attack - Thực hiện tấn công

Thực hiện tấn công môi trường thực nghiệm để thu thập các thông số:

```bash
cd source
./_run_attack.sh
```

**Môi trường thực nghiệm**:

-   DVWA (Damn Vulnerable Web Application)
-   ModSecurity WAF
-   OWASP Core Rule Set (CRS)

**Output**: Kết quả tấn công được lưu trong các thư mục `_attack_result/`:

-   `attack_summary_for_payload_length_[length].txt`: Tóm tắt kết quả tấn công
-   `dataset_for_payload_length_[length].csv`: Dataset chi tiết kết quả tấn công

## Cấu trúc thư mục

```
.
├── README.md                           # File hướng dẫn này
├── requirements.txt                    # Dependencies Python
├── _integer_payload/                   # Payload dạng integer từ inference
├── _transform_payload/                 # Payload đã chuyển đổi
├── _attack_result_[0-2]/              # Kết quả tấn công (3 lần chạy)
├── attack_grammar/                     # Ngữ pháp tấn công (EBNF)
├── log/                               # File log hệ thống
├── models/                            # Mô hình đã huấn luyện
│   ├── pretrain_model_sql/            # Mô hình tiền huấn luyện
│   └── fine_tune_model_sql_modsecurity/ # Mô hình tinh chỉnh
└── source/                            # Mã nguồn chính
    ├── _run_inference.sh              # Script chạy inference
    ├── _run_transform.sh              # Script chuyển đổi payload
    ├── _run_attack.sh                 # Script tấn công
    ├── inference.py                   # Module inference
    ├── transform.py                   # Module chuyển đổi
    ├── attack.py                      # Module tấn công
    └── utilities.py                   # Utilities hỗ trợ
```

## Kết quả

Sau khi chạy đầy đủ 3 bước, bạn sẽ có:

1. **Payload được sinh tự động**: Không cần định nghĩa ngữ pháp thủ công
2. **Kết quả kiểm thử WAF**: Thống kê chi tiết về khả năng vượt qua WAF
3. **Dữ liệu phân tích**: CSV files chứa thông tin chi tiết về từng payload

## Ghi chú

-   Đảm bảo môi trường thực nghiệm (DVWA + ModSecurity + OWASP CRS) đã được cài đặt và cấu hình đúng
-   Kết quả có thể khác nhau giữa các lần chạy do tính ngẫu nhiên của mô hình AI
-   Thời gian chạy phụ thuộc vào cấu hình phần cứng và số lượng payload cần sinh

## Tham khảo

1. RAT: Reinforcement Learning-Guided Adversarial Testing for Web Application Firewalls
2. ML-Driven Fuzzing: A Generic Approach to Grammar-Based Fuzzing
3. ML-Driven Grammar-Based Fuzzing for Web Applications
4. WAF-A-MoLE: Evading Web Application Firewalls through Adversarial Machine Learning
5. GPTFuzzer: Generative Pre-Trained Transformer-Based Reinforcement Learning for Testing Web Application Firewalls
6. AdvSQLi: Generating Adversarial SQL Injections against Real-world WAF-as-a-service

---

_Đồ án NT522 - Nghiên cứu ứng dụng GPTFuzzer trong kiểm thử WAF_
