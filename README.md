# Đồ án NT522 - GPTFuzzer

### 2. Data transform

```
cd Inference
python transform.py \
--grammar_path=grammar/bnf-sql.txt \
--data_path=sql_mod.csv
```

## 3. Attack

-   Chuẩn bị file sql_mod.csv đã transform sang payload hợp lệ

```
cd Attack
python attack.py
```
