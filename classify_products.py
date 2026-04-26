import re
import unicodedata
from pathlib import Path

import pandas as pd


INPUT_FILE = "List2p1K.csv"
OUTPUT_FILE = "brand_pf_output.csv"

BRAND_COL = 0
TITLE_COL = 1


PF_KEYWORDS = {
    "Consumables": [
        "kawa", "coffee", "herbata", "tea", "czekolad", "cukier", "miod", "sok",
        "oliwa", "olej", "maka", "mąka", "kasza", "ryz", "ryż", "makaron",
        "karma", "przysmak", "pies", "psa", "kot", "kota", "zwirek", "żwirek",
        "pet", "dog", "cat", "food", "grocery",
        "kosmet", "perfum", "woda perfum", "szampon", "odzywka", "odżywka",
        "krem", "balsam", "serum", "zel", "żel", "pasta do zebow", "pasta do zębów",
        "szczoteczka", "irygator", "golarka", "oneblade", "depilator",
        "suplement", "witamin", "omega", "kolagen", "probiotyk", "kaps",
        "tabletki", "lek", "aptecz", "medycz", "dezynfek", "higien",
        "pieluch", "baby", "dzieck", "niemowl",
        "cleaner", "detergent", "domestos", "plyn", "płyn", "adblue"
    ],

    "Softlines": [
        "buty", "obuwie", "sneakers", "odziez", "odzież", "kurtka", "spodnie",
        "koszulka", "bluza", "bielizna", "skarpet", "czapka", "rekawiczki",
        "rękawiczki", "plecak", "torba", "walizka", "bagaz", "bagaż",
        "zegarek", "watch", "jewelry", "bizuteria", "biżuteria",
        "sportowy zegarek", "g-shock",
        "sport", "fitness", "trening", "biegan", "rower treningowy", "bieznia", "bieżnia",
        "hantel", "ławka treningowa", "lawka treningowa", "mata do cwiczen", "mata do ćwiczeń"
    ],

    "TCEE": [
        "smartfon", "telefon", "tablet", "laptop", "komputer", "pc", "monitor",
        "drukarka", "printer", "ssd", "dysk", "ram", "karta graficzna",
        "kamera", "camera", "projektor", "router", "wifi", "bluetooth",
        "konsola", "playstation", "xbox", "nintendo", "gra ps5", "gra xbox",
        "sluchawki", "słuchawki", "audio", "video", "tv", "smartwatch",
        "pendrive", "microSD", "microsd", "usb", "gamingowy", "gaming"
    ],

    "OHL": [
        "meble", "materac", "łóżko", "lozko", "krzeslo", "krzesło", "biurko",
        "regał", "regal", "szafka", "toaletka", "narzedz", "narzędz", "pilarka",
        "wiertarka", "akumulator", "prostownik", "odkurzacz", "mop", "frytkownica",
        "ekspres", "czajnik", "blender", "robot kuchenny", "kosiarka", "agregat",
        "opona", "dywan", "lampa", "oswietlen", "oświetlen", "abażur", "abazur",
        "zabawka", "klocki", "lego", "hot wheels", "pokemon", "pokémon",
        "ksiazka", "książka", "wydawnictwo", "gra planszowa"
    ],
}

BRAND_OVERRIDES = {
    "lavazza": "Consumables",
    "dallmayr": "Consumables",
    "davidoff": "Consumables",
    "gevalia": "Consumables",
    "movenpick": "Consumables",
    "mk cafe": "Consumables",
    "jacobs": "Consumables",
    "tchibo": "Consumables",
    "l'oréal": "Consumables",
    "loreal": "Consumables",
    "kerastase": "Consumables",
    "kérastase": "Consumables",
    "lancôme": "Consumables",
    "lancome": "Consumables",
    "estée lauder": "Consumables",
    "estee lauder": "Consumables",
    "nestlé": "Consumables",
    "nestle": "Consumables",
    "royal canin": "Consumables",
    "purina": "Consumables",
    "acana": "Consumables",
    "brit": "Consumables",
    "whiskas": "Consumables",
    "sheba": "Consumables",
    "vetexpert": "Consumables",
    "vet expert": "Consumables",

    "samsung": "TCEE",
    "sony": "TCEE",
    "asus": "TCEE",
    "acer": "TCEE",
    "xiaomi": "TCEE",
    "huawei": "TCEE",
    "philips": "TCEE",
    "canon": "TCEE",
    "epson": "TCEE",
    "brother": "TCEE",
    "logitech": "TCEE",
    "nintendo": "TCEE",
    "playstation": "TCEE",
    "xbox": "TCEE",

    "adidas": "Softlines",
    "nike": "Softlines",
    "brubeck": "Softlines",
    "4f": "Softlines",

    "lego": "OHL",
    "karcher": "OHL",
    "kärcher": "OHL",
}


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    return text


def score_title(title: str) -> dict[str, int]:
    scores = {pf: 0 for pf in PF_KEYWORDS}

    for pf, keywords in PF_KEYWORDS.items():
        for kw in keywords:
            if kw in title:
                scores[pf] += 1

    if re.search(r"\b(kawa|coffee|karma|żwirek|zwirek|perfum|szampon|krem|suplement|witamin)", title):
        scores["Consumables"] += 3

    if re.search(r"\b(smartfon|laptop|monitor|ssd|ram|drukarka|konsola|playstation|xbox|nintendo)\b", title):
        scores["TCEE"] += 3

    if re.search(r"\b(buty|odzież|odziez|plecak|torba|zegarek|sport|fitness|trening)\b", title):
        scores["Softlines"] += 2

    return scores


def classify_brand(brand: str, titles: pd.Series) -> tuple[str, str, int, int]:
    brand_norm = normalize_text(brand)

    if brand_norm in BRAND_OVERRIDES:
        return BRAND_OVERRIDES[brand_norm], "override", 999, len(titles)

    total_scores = {pf: 0 for pf in PF_KEYWORDS}

    for title in titles.dropna():
        scores = score_title(normalize_text(title))
        for pf, score in scores.items():
            total_scores[pf] += score

    ranked = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)
    top_pf, top_score = ranked[0]
    second_score = ranked[1][1]

    if top_score == 0:
        return "Review", "low", 0, len(titles)

    if top_pf == "OHL" and top_score <= second_score + 1 and second_score > 0:
        top_pf = ranked[1][0]
        top_score = ranked[1][1]

    if top_score >= second_score + 5:
        confidence = "high"
    elif top_score >= second_score + 2:
        confidence = "medium"
    else:
        confidence = "low"

    return top_pf, confidence, top_score, len(titles)


def main() -> None:
    path = Path(INPUT_FILE)

    try:
        df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(path, sep=None, engine="python", encoding="latin1")

    brand_col = df.columns[BRAND_COL]
    title_col = df.columns[TITLE_COL]

    df = df[[brand_col, title_col]].copy()
    df.columns = ["Brand", "Title"]

    df["Brand"] = df["Brand"].astype(str).str.strip()
    df = df[df["Brand"].ne("")]
    df = df[~df["Brand"].str.lower().isin(["nan", "bez marki", "unknown", "uknown"])]

    results = []

    for brand, group in df.groupby("Brand", sort=True):
        pf, confidence, signal_score, row_count = classify_brand(brand, group["Title"])
        sample_titles = " | ".join(group["Title"].dropna().astype(str).head(3).tolist())

        results.append({
            "Brand": brand,
            "Product Family": pf,
            "Confidence": confidence,
            "Signal Score": signal_score,
            "Rows Used": row_count,
            "Sample Titles": sample_titles,
        })

    out = pd.DataFrame(results).sort_values(["Product Family", "Brand"])
    out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"Input rows: {len(df):,}")
    print(f"Unique brands: {len(out):,}")
    print("\nPF mix:")
    print(out["Product Family"].value_counts(dropna=False))
    print(f"\nSaved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
