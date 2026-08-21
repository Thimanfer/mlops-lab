import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

with open("params.yaml") as f:
    params = yaml.safe_load(f)

# 1. Đánh giá trên 2998 mẫu (Phase 1)
df_all = pd.read_csv("data/train_phase1.csv")
df_phase1 = df_all.iloc[:2998]
df_eval = pd.read_csv("data/eval.csv")

X_p1 = df_phase1.drop("target", axis=1)
y_p1 = df_phase1["target"]
X_eval = df_eval.drop("target", axis=1)
y_eval = df_eval["target"]

clf_p1 = RandomForestClassifier(**params, random_state=42)
clf_p1.fit(X_p1, y_p1)
preds_p1 = clf_p1.predict(X_eval)

acc_p1 = accuracy_score(y_eval, preds_p1)
f1_p1 = f1_score(y_eval, preds_p1, average="weighted")

print("=============================================")
print("=== KET QUA PHASE 1 (2.998 MAU BAN DAU) ===")
print(f"Accuracy : {acc_p1:.4f} ({acc_p1})")
print(f"F1-Score : {f1_p1:.4f} ({f1_p1})")
print("=============================================")

# 2. Danh gia tren toan bo 5996 mau (Phase 2 tich luy)
X_p2 = df_all.drop("target", axis=1)
y_p2 = df_all["target"]

clf_p2 = RandomForestClassifier(**params, random_state=42)
clf_p2.fit(X_p2, y_p2)
preds_p2 = clf_p2.predict(X_eval)

acc_p2 = accuracy_score(y_eval, preds_p2)
f1_p2 = f1_score(y_eval, preds_p2, average="weighted")

print("\n=============================================")
print("=== KET QUA PHASE 2 (5.996 MAU TICH LUY) ===")
print(f"Accuracy : {acc_p2:.4f} ({acc_p2})")
print(f"F1-Score : {f1_p2:.4f} ({f1_p2})")
print("=============================================")
