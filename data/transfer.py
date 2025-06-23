import pandas as pd

df = pd.read_csv("data/traffic_stats.csv", header=None,
    names=["timestamp", "pkt_count", "avg_pkt_len", "tcp_count", "udp_count", "syn_count"])

# 把要比大小的欄位強制轉成數字
for col in ["pkt_count", "avg_pkt_len", "tcp_count", "udp_count", "syn_count"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

cond = (
    (df["pkt_count"]   <  20)   &    
    (df["udp_count"]   <  20)   &    
    (df["tcp_count"]   <  20)   &    
    (df["syn_count"]   <= 2)    &    
    (df["avg_pkt_len"] < 800)       
)

df_clean = df[cond]

print(df_clean)
df_clean.to_csv("data/traffic_stats_clean.csv", index=False)

