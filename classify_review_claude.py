"""
Classify remaining Review-flagged brands using Claude API (claude-haiku-4-5).
Reads brand_pf_output.csv, re-classifies Review rows, writes results back.
"""

import json
import os
import time

import anthropic
import pandas as pd

INPUT_OUTPUT_FILE = "brand_pf_output.csv"
MODEL = "claude-haiku-4-5"
BATCH_SIZE = 10

PF_CATEGORIES = ["Consumables", "Softlines", "TCEE", "OHL"]

SYSTEM_PROMPT = """You are a product classification expert for Allegro (Polish e-commerce).
Classify each brand into exactly one of these four Product Families based on the sample product titles provided:

- Consumables: Food, beverages, coffee, tea, pet food, cosmetics, personal care, supplements, vitamins, pharmacy/medicine, cleaning products, baby care, perfumes, skincare, haircare
- Softlines: Clothing, footwear, bags, luggage, sportswear, watches, jewelry, fitness equipment (wearable/portable), sports accessories
- TCEE: Consumer electronics, computers, laptops, tablets, phones, cameras, gaming consoles/games, audio/video equipment, printers, networking, storage, TV sets, smartwatches, EV chargers
- OHL: Furniture, home appliances (kitchen/household), tools, power tools, toys, books, board games, garden equipment, lighting, flooring, insulation, building materials, automotive parts, cookware, ladders, boilers

Rules:
- Respond ONLY with a JSON object: {"brand_name": "Category", ...}
- Use exact category names from the list above
- If genuinely ambiguous, prefer OHL as the default
- Base your decision on the product titles, not the brand name alone"""


def classify_batch(client: anthropic.Anthropic, batch: list[dict]) -> dict[str, str]:
    """Send one batch to Claude, return {brand: pf} mapping."""
    brands_text = "\n".join(
        f'Brand: {item["brand"]}\nTitles: {item["titles"]}'
        for item in batch
    )

    message = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Classify these {len(batch)} brands into one of: Consumables, Softlines, TCEE, OHL.\n\n{brands_text}\n\nRespond ONLY with JSON: {{\"brand_name\": \"Category\", ...}}",
            }
        ],
    )

    text = message.content[0].text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    df = pd.read_csv(INPUT_OUTPUT_FILE, encoding="utf-8-sig")
    review_mask = df["Product Family"] == "Review"
    review_df = df[review_mask].copy()

    print(f"Brands to classify via Claude API: {len(review_df)}")

    # Build list of {brand, titles} dicts
    items = [
        {
            "brand": row["Brand"],
            "titles": row["Sample Titles"] if pd.notna(row["Sample Titles"]) else "",
        }
        for _, row in review_df.iterrows()
    ]

    # Process in batches
    results: dict[str, str] = {}
    total_batches = (len(items) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(items), BATCH_SIZE):
        batch = items[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"  Batch {batch_num}/{total_batches} ({len(batch)} brands)...", end=" ", flush=True)

        for attempt in range(4):
            try:
                batch_results = classify_batch(client, batch)
                results.update(batch_results)
                print("ok")
                break
            except (json.JSONDecodeError, anthropic.APIError) as exc:
                wait = 2 ** attempt
                print(f"err ({exc}), retry in {wait}s...", end=" ", flush=True)
                time.sleep(wait)
        else:
            # All retries failed — mark as OHL (safe default)
            for item in batch:
                results[item["brand"]] = "OHL"
            print("failed, defaulted to OHL")

    # Update the dataframe
    updated = 0
    for idx, row in df[review_mask].iterrows():
        brand = row["Brand"]
        if brand in results and results[brand] in PF_CATEGORIES:
            df.at[idx, "Product Family"] = results[brand]
            df.at[idx, "Confidence"] = "claude-api"
            updated += 1

    df.to_csv(INPUT_OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"\nUpdated {updated} brands in {INPUT_OUTPUT_FILE}")
    print("\nFinal PF mix:")
    print(df["Product Family"].value_counts(dropna=False))


if __name__ == "__main__":
    main()
