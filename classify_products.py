import pandas as pd

df = pd.read_csv("List2p1K.csv")

df.columns = ["Brand", "Title"]
df["Title"] = df["Title"].str.lower().fillna("")


def classify(text):
    if any(k in text for k in ["kawa", "coffee", "karma", "food", "kosmet", "perf", "vet", "piel", "suplement", "witam", "odżyw"]):
        return "Consumables"
    elif any(k in text for k in ["buty", "odzie", "sport"]):
        return "Softlines"
    elif any(k in text for k in ["smart", "laptop", "kamera", "pc", "ssd", "ram", "druk", "monitor", "konsol"]):
        return "TCEE"
    else:
        return "OHL"


df["PF"] = df["Title"].apply(classify)

result = (
    df.groupby("Brand")["PF"]
    .agg(lambda x: x.value_counts().idxmax())
    .reset_index()
)

result.to_csv("brands_pf.csv", index=False)

print(result.head())
