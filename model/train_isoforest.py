import pandas as pd, joblib, os
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import numpy as np

# 讀資料
df = pd.read_csv("data/traffic_stats_clean.csv")
X  = df[["pkt_count", "avg_pkt_len", "tcp_count",
         "udp_count", "syn_count"]]

# 訓練
iso = IsolationForest(
        n_estimators=100,
        contamination=0.01,
        random_state=42)
iso.fit(X)

os.makedirs("model", exist_ok=True)
joblib.dump(iso, "model/isoforest.joblib")
print("Model saved to model/isoforest.joblib")

# 預測異常比例
y_pred = iso.predict(X)
print("Anomaly ratio in training set:", (y_pred == -1).mean())

# 視覺化 
scores = iso.decision_function(X)
plt.hist(scores, bins=50)
plt.axvline(x=0, color='r', linestyle='--', label=' 0 threshold')
plt.axvline(x=-0.1, color='g', linestyle='--', label='-0.1 threshold')
plt.xlabel('decision_function score ')
plt.ylabel('numbers')
plt.legend()
plt.title('IsolationForest ')
plt.show()

