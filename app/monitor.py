from bcc import BPF
import time, csv, os, ctypes, argparse
import joblib, numpy as np
from bcc import BPF
import time, csv, os, ctypes, argparse
import joblib, numpy as np
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# 解析參數 
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--iface", required=True)
args = parser.parse_args()

# 掛XDP 
b = BPF(src_file="../ebpf/xdp_prog.c", cflags=["-w"])
fn = b.load_func("xdp_prog_main", BPF.XDP)
b.attach_xdp(args.iface, fn, 0)

# 初始化 
key = ctypes.c_uint(0)
b["last_ts"][key] = ctypes.c_ulonglong(time.time_ns())

# CSV 檔 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.abspath(os.path.join(BASE_DIR, "../data/traffic_stats.csv"))
os.makedirs(os.path.dirname(csv_file), exist_ok=True)
if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="") as f:
        csv.writer(f).writerow(
            ["timestamp", "pkt_count", "avg_pkt_len",
             "tcp_count", "udp_count", "syn_count"]
        )

# 讀取 IsolationForest
iso_path = os.path.abspath(os.path.join(BASE_DIR, "../model/isoforest.joblib"))
iso_model = joblib.load(iso_path)

#預設0,越小越異常 
THRESHOLD = -0.05                

print("Monitoring traffic …  Ctrl-C 結束")

try:
    while True:
        per_cpu = b["stats"][0]
        pkt_count   = sum(s.pkt_count   for s in per_cpu)
        pkt_len_sum = sum(s.pkt_len_sum for s in per_cpu)
        tcp_count   = sum(s.tcp_count   for s in per_cpu)
        udp_count   = sum(s.udp_count   for s in per_cpu)
        syn_count   = sum(s.syn_count   for s in per_cpu)
        timestamp   = max(s.timestamp   for s in per_cpu)

        if pkt_count:
            avg_pkt_len = round(pkt_len_sum / pkt_count, 2)
            row = [timestamp, pkt_count, avg_pkt_len,
                   tcp_count, udp_count, syn_count]
            print("XDP stats:", row)

            # IsolationForest 推理 
            X = np.array([[pkt_count, avg_pkt_len,
                           tcp_count, udp_count, syn_count]])
            score = float(iso_model.decision_function(X)[0])  
            if score < THRESHOLD:
                print(f"!Anomaly!  IsoF score = {score:.2f}")
            
            else:
                print(f"Normal.   IsoF score = {score:.2f}")
            

            with open(csv_file, "a", newline="") as f:
                csv.writer(f).writerow(row)
        time.sleep(1)

except KeyboardInterrupt:
    pass
finally:
    b.remove_xdp(args.iface, 0)

