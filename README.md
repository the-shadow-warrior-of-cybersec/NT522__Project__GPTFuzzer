# Đồ án NT522 - GPTFuzzer

## Note
- Phải setup môi trường trước khi chạy repo (sẽ bổ bung guidelines trong tương lai)

## 1. Chạy inference: tạo ra payload dạng integer để phục vụ cho các quy trình sau
```
cd source
./_run_inference.sh
```

## 2. Data transform: chuyển hóa integer payload sang payload thật sự dựa trên ngữ pháp tấn công
```
cd source
./_run_transform.sh
```

## 3. Attack: thực hiện tấn công môi trường thực nghiệm để thu về các thông số
- Môi trường thực nghiệm gồm: DVWA + ModSecurity WAF + OWASP CRS (sẽ bổ sung guidelines sau)
```
cd source
./_run_attack.sh
```
