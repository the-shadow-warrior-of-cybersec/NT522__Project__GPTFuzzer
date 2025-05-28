# Đồ án NT522 - GPTFuzzer

## Thành viên nhóm

## Môi trường
1. Python 3.8.5
2. Pytorch 1.7.1
3. Hugging Face Transformers 2.6.0

## Model inference
### 1. Model loading and data generation
```
cd Inference
python inference.py \
--lm_name=models/fine_tune_model_sql_modsecurity \
--ref_lm_name=models/pretrain_model_sql \
--total_nums=128 \
--txt_in_len=1 \
--txt_out_len=75 \
--savePath=sql_mod.csv
```

### 2. Data transform
```
cd Inference
python transform.py \
--grammar_path=grammar/bnf-sql.txt \
--data_path=sql_mod.csv
```

## 3. Attack
- Chuẩn bị file sql_mod.csv đã transform sang payload hợp lệ
```
cd Attack
python attack.py
```