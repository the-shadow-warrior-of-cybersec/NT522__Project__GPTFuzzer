# GPTFuzzer – Đồ án NT522

## 👥 Thành viên nhóm

| STT | Họ và tên             | MSSV     | Vai trò     |
| --- | --------------------- | -------- | ----------- |
| 1   | Trần Thanh Phong      | 22521093 | Trưởng nhóm |
| 2   | Nguyễn Lê Bảo Phúc    | 22521131 | Thành viên  |
| 3   | Võ Quốc Bảo           | 23520146 | Thành viên  |
| 4   | Nguyễn Đoàn Gia Khánh | 23520720 | Thành viên  |

## 📌 Giới thiệu

**GPTFuzzer** là một khung kiểm thử **Web Application Firewall (WAF)** tiên tiến dựa trên các mô hình ngôn ngữ biến đổi (_Transformer_). Thay vì dựa vào ngữ pháp cố định hay tập seed lớn, GPTFuzzer tận dụng **GPT-2** kết hợp **học tăng cường (Reinforcement Learning – RL)** để tự động sinh ra các payload tấn công có khả năng vượt qua WAF cao.

### Tính cấp thiết của kiểm thử WAF

Hầu hết WAF hiện nay hoạt động theo mô hình _blacklist_ với tập quy tắc cố định. Khi xuất hiện kỹ thuật tấn công mới, các quy tắc không thể tự động cập nhật, dẫn đến nguy cơ bỏ sót. Việc kiểm thử WAF liên tục giúp phát hiện kịp thời lỗ hổng bảo mật.

### Ưu điểm của GPTFuzzer

- **Không cần ngữ pháp cố định:** Tự động học cấu trúc và ngữ cảnh payload tấn công.
    
- **Hiệu quả cao:** Sử dụng RL với hàm phần thưởng tối ưu khả năng vượt qua WAF.
    
- **Tránh tối ưu cục bộ:** Áp dụng điều chỉnh phạt KL và reward model.
    
- **Linh hoạt:** Hỗ trợ nhiều loại tấn công (SQLi, XSS, RCE…).
    

## 🏗️ Cấu trúc hệ thống

GPTFuzzer gồm 5 giai đoạn chính:

1. **[A] Thu thập & tiền xử lý dữ liệu**
    
2. **[B] Huấn luyện trước mô hình ngôn ngữ** (_Language Model Pre-Training_)
    
3. **[C] Huấn luyện mô hình phần thưởng** (_Reward Model_)
    
4. **[D] Học tăng cường với PPO**
    
5. **[E] Sinh payload & đánh giá trên WAF**
    

## 💻 Yêu cầu hệ thống

- **Python:** ≥3.8 (đã test trên 3.8.20)
    
- **Môi trường ảo:** khuyến nghị `venv`
    
- **Dependencies:** xem `requirements.txt`
    
- **Phần cứng khuyến nghị:** CPU ≥4 cores, RAM ≥8GB. Nếu có GPU (CUDA) sẽ tăng tốc huấn luyện.
    

## ⚙️ Cài đặt

1. **Tạo môi trường ảo:**
    

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
# hoặc trên Windows:
venv\Scripts\activate
```

2. **Cài đặt dependencies:**
    

```bash
pip install -r requirements.txt
```

## 🚀 Cách sử dụng

### Bước 1 – Inference: Tạo payload dạng integer

Sinh payload dạng số nguyên phục vụ các bước tiếp theo:

```bash
cd source
./_run_inference.sh
```

**Output:** CSV trong `_integer_payload/`, ví dụ:

`nums_4000_in_1_out_[length].csv` (length: 10, 20, 30, 40, 50, 60, 70).

### Bước 2 – Data Transform: Chuyển đổi payload

Chuyển integer payload thành payload thực dựa trên ngữ pháp tấn công:

```bash
cd source
./_run_transform.sh
```

**Output:** CSV trong `_transform_payload/`, ví dụ:

`payload_with_length_of_[length].csv`.

### Bước 3 – Attack: Thực hiện tấn công

Tấn công môi trường thực nghiệm để thu thập thông số:

```bash
cd source
./_run_attack.sh
```

**Môi trường thực nghiệm:**

- DVWA (Damn Vulnerable Web Application)
    
- ModSecurity WAF
    
- OWASP Core Rule Set (CRS)
    

**Output:** kết quả trong `_attack_result/`:

- `attack_summary_for_payload_length_[length].txt`: Tóm tắt kết quả
    
- `dataset_for_payload_length_[length].csv`: Dữ liệu chi tiết
    

## 📂 Cấu trúc thư mục

```
.
├── README.md                           # File hướng dẫn
├── requirements.txt                    # Dependencies Python
├── _integer_payload/                   # Payload dạng integer từ inference
├── _transform_payload/                 # Payload đã chuyển đổi
├── _attack_result_[0-2]/               # Kết quả tấn công (3 lần chạy)
├── attack_grammar/                     # Ngữ pháp tấn công (EBNF)
├── log/                                # File log hệ thống
├── models/                             # Mô hình đã huấn luyện
│   ├── pretrain_model_sql/             # Mô hình tiền huấn luyện
│   └── fine_tune_model_sql_modsecurity/ # Mô hình tinh chỉnh
└── source/                             # Mã nguồn chính
    ├── _run_inference.sh               # Script chạy inference
    ├── _run_transform.sh               # Script chuyển đổi payload
    ├── _run_attack.sh                  # Script tấn công
    ├── inference.py                    # Module inference
    ├── transform.py                    # Module chuyển đổi
    ├── attack.py                       # Module tấn công
    └── utilities.py                    # Utilities hỗ trợ
```

## 🧪 Kết quả

Sau khi chạy đầy đủ 3 bước, bạn có:

1. **Payload tự động sinh:** không cần định nghĩa ngữ pháp thủ công.
    
2. **Kết quả kiểm thử WAF:** thống kê chi tiết khả năng vượt qua WAF.
    
3. **Dữ liệu phân tích:** CSV chứa thông tin từng payload.
    

## 📝 Ghi chú

- Đảm bảo DVWA + ModSecurity + OWASP CRS đã cài đặt & cấu hình trước khi tấn công.
    
- Kết quả có thể thay đổi giữa các lần chạy do tính ngẫu nhiên của mô hình.
    
- Thời gian chạy phụ thuộc cấu hình phần cứng & số lượng payload sinh ra.
    

## 📚 Tham khảo

1. RAT: Reinforcement Learning-Guided Adversarial Testing for Web Application Firewalls
    
2. ML-Driven Fuzzing: A Generic Approach to Grammar-Based Fuzzing
    
3. ML-Driven Grammar-Based Fuzzing for Web Applications
    
4. WAF-A-MoLE: Evading Web Application Firewalls through Adversarial Machine Learning
    
5. GPTFuzzer: Generative Pre-Trained Transformer-Based Reinforcement Learning for Testing Web Application Firewalls
    
6. AdvSQLi: Generating Adversarial SQL Injections against Real-world WAF-as-a-service
    

---

_Đồ án NT522 – Nghiên cứu ứng dụng GPTFuzzer trong kiểm thử WAF_

---
