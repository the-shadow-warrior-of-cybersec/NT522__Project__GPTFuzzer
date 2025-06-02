# Khai báo thư viện
from utilities import GPT2HeadWithValueModel, respond_to_batch
from transformers import GPT2Tokenizer
from tqdm import tqdm
import pandas as pd
import argparse
import datetime
import torch
import logging
import os

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("inference_log.txt"),
        logging.StreamHandler(),
    ],
)

# Cài đặt các thông số
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
tqdm.pandas()

# Khởi tạo parser cho tham số dòng lệnh
parser = argparse.ArgumentParser(description="Inference script for GPT-2 model")
parser.add_argument("--lm_name", type=str, help="Name of the language model")
parser.add_argument("--ref_lm_name", type=str, help="Name of the reference language model")
parser.add_argument("--total_nums", type=int, help="Total number of responses to generate")
parser.add_argument("--txt_in_len", type=int, help="Input text length")
parser.add_argument("--txt_out_len", type=int, help="Output text length")
parser.add_argument("--save_path", type=str, help="Path to save the results")
args = parser.parse_args()

# Gán giá trị từ tham số
lm_name = args.lm_name
ref_lm_name = args.ref_lm_name
total_nums = int(args.total_nums)
txt_in_len = int(args.txt_in_len)
txt_out_len = int(args.txt_out_len)
save_path = args.save_path

# Tạo thư mục đầu ra nếu chưa tồn tại
os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)

# Khởi tạo tokenizer và model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
gpt2_model = GPT2HeadWithValueModel.from_pretrained(lm_name)
gpt2_model_ref = GPT2HeadWithValueModel.from_pretrained(ref_lm_name)

# Cấu hình thiết bị và chuyển model sang thiết bị
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logging.info(f"Using device: {device}")
gpt2_model.eval()
gpt2_model.to(device)
gpt2_model_ref.eval()
gpt2_model_ref.to(device)

# Quá trình inference
batch_size = 64
waf_data = pd.DataFrame()
waf_data["content"] = ["0" for _ in range(30000)]  # Tạo placeholder
waf_data["tokens"] = waf_data["content"].progress_apply(
    lambda x: tokenizer.encode(x, return_tensors="pt").to(device)[0, :txt_in_len]
)
waf_data["query"] = waf_data["tokens"].progress_apply(lambda x: tokenizer.decode(x))

response_list = []
start_time = datetime.datetime.now()

while len(response_list) < total_nums:
    torch.cuda.empty_cache()
    df_batch = waf_data.sample(batch_size)
    query_tensors = torch.stack(df_batch["tokens"].tolist())
    response_tensors = respond_to_batch(
        gpt2_model, gpt2_model_ref, query_tensors, txt_len=txt_out_len
    )
    response_list += [
        tokenizer.decode(response_tensors[i, :]).split("!")[0] for i in range(batch_size)
    ]

end_time = datetime.datetime.now()
print(f"Time taken: {(end_time - start_time).seconds} seconds")

# Trích xuất và lưu kết quả
df_results = pd.DataFrame()
df_results["response"] = response_list
df_results["query"] = "0"
df_results["data"] = df_results["query"] + df_results["response"]
df_results[["data"]].to_csv(save_path, index=False)