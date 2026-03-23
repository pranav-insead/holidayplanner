#!/usr/bin/env python3
import csv, argparse, time, random, re, unicodedata
from playwright.sync_api import sync_playwright
def pad_asin(asin):
    return asin.zfill(10) if asin.isdigit() else asin
def clean(text):
    if not text:
        return None
    text = unicodedata.normalize("NFC", text)
    for ch in ("\u00a0", "\u202f", "\u2009", "\u200b", "\u2060", "\ufeff"):
        text = text.replace(ch, " ")
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    return " ".join(text.split()) or None
def clean_price(text):
    if not text:
        return None
    stripped = re.sub(r'[^\d.,]', '', text.strip())
    return stripped if stripped else None
def pick_fastest_delivery(text):
    """Pick fastest delivery option from multiple lines with idag/imorgon support."""
    if not text:
        return None
    lines = [l.strip() for l in re.split(r'\n', text) if l.strip()]
    day_rank = {"idag": -2, "today": -2, "imorgon": -1, "tomorrow": -1,
                "måndag": 0, "tisdag": 1, "onsdag": 2, "torsdag": 3,
                "fredag": 4, "lördag": 5, "söndag": 6,
                "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                "friday": 4, "saturday": 5, "sunday": 6}
    delivery_lines = []
    for line in lines:
        if not re.search(r'leverans|bezorging|delivery|snabbast', line, re.IGNORECASE):
            continue
        display = re.sub(r'^[Ee]ller\s+', '', line).strip()
        rank = 999
        for day, r in day_rank.items():
            if day in line.lower():
                rank = r
                break
        delivery_lines.append((rank, display))
    if not delivery_lines:
        return clean(text)
    delivery_lines.sort(key=lambda x: x[0])
    return clean(delivery_lines[0][1])
def get_price(page):
    """Scope to buybox containers to avoid accessory prices."""
    for container_sel in ["#apex_desktop_qualifiedBuybox_feature_div",
                          "#corePriceDisplay_desktop_feature_div",
                          "#corePrice_feature_div",
                          "#buybox",]:
        container = page.query_selector(container_sel)
        if not container:
            continue
        for price_sel in [".a-price .a-offscreen", ".a-price-whole"]:
            el = container.query_selector(price_sel)
            if el:
                val = clean_price(el.inner_text())
                if val:
                    return val
    for sel in ["#priceblock_ourprice", "#priceblock_dealprice"]:
        el = page.query_selector(sel)
        if el:
            val = clean_price(el.inner_text())
            if val:
                return val
    return None
def get_price_from_offer(offer, page):
    """Extract price from offers page - try .a-offscreen first for full price."""
    for sel in [".a-price .a-offscreen",
                "#aod-price .a-offscreen",
                ".a-price-whole",]:
        el = offer.query_selector(sel) or page.query_selector(sel)
        if el:
            val = clean_price(el.inner_text())
            if val:
                return val
    return None
def get_seller_shipper(page):
    """Extract both seller AND shipper."""
    seller = None
    shipper = None
    for row in page.query_selector_all("#tabular-buybox tr"):
        tds = row.query_selector_all("td")
        if len(tds) < 2:
            continue
        label = clean(tds[0].inner_text()) or ""
        value = clean(tds[1].inner_text())
        if not value:
            continue
        if any(k in label for k in ["Säljare", "Säljs av", "Sold by"]):
            seller = value
        elif any(k in label for k in ["Avsändare", "Skickas från", "Ships from"]):
            shipper = value
    if not seller or not shipper:
        for i in range(8):
            trunc = page.query_selector(f"#tabular-buybox-truncate-{i}")
            if not trunc:
                continue
            val = clean(trunc.inner_text())
            try:
                label = page.evaluate("""el => {
                    const row = el.closest('tr');
                    const td = row ? row.querySelector('td') : null;
                    return td ? td.innerText : '';
                }""", trunc)
                label = clean(label or "") or ""
            except:
                label = ""
            if any(k in label for k in ["Säljare", "Säljs av", "Sold by"]) and not seller:
                seller = val
            elif any(k in label for k in ["Avsändare", "Skickas från", "Ships from"]) and not shipper:
                shipper = val
    if not seller:
        el = page.query_selector("#sellerProfileTriggerId")
        if el:
            seller = clean(el.inner_text())
    if not seller or not shipper:
        merchant = page.query_selector("#merchant-info")
        if merchant:
            text = merchant.inner_text()
            for pat in [r'Säljs av\s+([^\n]+)', r'Sold by\s+([^\n]+)']:
                m = re.search(pat, text)
                if m and not seller:
                    seller = clean(m.group(1))
            for pat in [r'Skickas från\s+([^\n]+)', r'Ships from\s+([^\n]+)']:
                m = re.search(pat, text)
                if m and not shipper:
                    shipper = clean(m.group(1))
    if not seller or not shipper:
        for sel in ["#apex_desktop_qualifiedBuybox_feature_div", "#buybox"]:
            block = page.query_selector(sel)
            if not block:
                continue
            text = block.inner_text()
            if not seller:
                for pat in [r'Säljare\s*[:\n]\s*([^\n]+)', r'Säljs av\s+([^\n]+)', r'Sold by\s+([^\n]+)']:
                    m = re.search(pat, text)
                    if m:
                        seller = clean(m.group(1))
                        break
            if not shipper:
                for pat in [r'Avsändare\s*[:\n]\s*([^\n]+)', r'Skickas från\s+([^\n]+)', r'Ships from\s+([^\n]+)']:
                    m = re.search(pat, text)
                    if m:
                        shipper = clean(m.group(1))
                        break
    if seller and "Amazon" in seller:
        seller = "Amazon"
        if not shipper:
            shipper = "Amazon"
    if shipper and "Amazon" in shipper:
        shipper = "Amazon"
    return seller, shipper
def get_delivery(page):
    for sel in [
        "#mir-layout-DELIVERY_BLOCK",
        "#deliveryBlockMessage",
        "#ddmDeliveryMessage",
        "#dynamicDeliveryMessage",
        "#fast-track-message",
        "#contextualIngressPt_feature_div",
        "#delivery-message",
    ]:
        el = page.query_selector(sel)
        if el:
            t = el.inner_text()
            if t and t.strip():
                return pick_fastest_delivery(t)
    return None
def scrape_amazon_product(page, asin, max_retries=3):
    padded_asin = pad_asin(asin)
    url = f"https://www.amazon.se/dp/{padded_asin}?th=1"
    for attempt in range(max_retries):
        try:
            print(f"  Navigating to: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(random.uniform(2, 3))
            el = page.query_selector("#productTitle")
            title = clean(el.inner_text()) if el else None
            el = page.query_selector("#bylineInfo")
            brand = clean(el.inner_text()) if el else None
            add_to_cart = page.query_selector("#add-to-cart-button")
            price = get_price(page) if add_to_cart else None
            seller, shipper = get_seller_shipper(page) if add_to_cart else (None, None)
            delivery = get_delivery(page) if add_to_cart else None
            has_buybox = add_to_cart is not None and price is not None
            print(f"  buybox={has_buybox} price={price} seller={seller} shipper={shipper}")
            if not price or not seller:
                print(f"  Missing data - trying offers page...")
                try:
                    btn = page.query_selector("a[href*='/gp/offer-listing/']")
                    if btn:
                        offers_url = btn.get_attribute("href")
                        if not offers_url.startswith("http"):
                            offers_url = "https://www.amazon.se" + offers_url
                        page.goto(offers_url, wait_until="domcontentloaded", timeout=30000)
                        time.sleep(random.uniform(2, 3))
                        offer = (page.query_selector("#aod-offer") or
                                page.query_selector(".a-row.a-spacing-mini.olpOffer") or
                                page.query_selector("[data-aod-atc-action]"))
                        if offer:
                            if not price:
                                price = get_price_from_offer(offer, page)
                                print(f"  offers price={price}")
                            if not seller:
                                sb = offer.query_selector("#aod-offer-soldBy")
                                if sb:
                                    for pat in [r'Säljs av\s+(.+)', r'Sold by\s+(.+)']:
                                        m = re.search(pat, sb.inner_text())
                                        if m:
                                            seller = clean(m.group(1))
                                            break
                                    if not seller:
                                        lnk = sb.query_selector("a")
                                        if lnk:
                                            seller = clean(lnk.inner_text())
                                print(f"  offers seller={seller}")
                            if not shipper:
                                sf = offer.query_selector("#aod-offer-shipsFrom")
                                if sf:
                                    for pat in [r'Skickas från\s+([^\n]+)', r'Ships from\s+([^\n]+)']:
                                        m = re.search(pat, sf.inner_text())
                                        if m:
                                            shipper = clean(m.group(1))
                                            break
                                    if not shipper and "Amazon" in sf.inner_text():
                                        shipper = "Amazon"
                                print(f"  offers shipper={shipper}")
                            if not delivery:
                                delivery = get_delivery(page)
                        else:
                            print(f"  No offer block found on offers page")
                    else:
                        print(f"  No offers button found")
                except Exception as e:
                    print(f"  Offers error: {e}")
            return {"asin": padded_asin, "title": title, "brand": brand,
                    "price": price, "seller": seller, "shipper": shipper,
                    "delivery": delivery, "scrape_status": "success",}
        except Exception as e:
            print(f"  Error attempt {attempt+1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(3, 5))
    return {"asin": pad_asin(asin), "title": None, "brand": None,
            "price": None, "seller": None, "shipper": None,
            "delivery": None, "scrape_status": "failed",}
def process_asins(input_file, output_file, headed=False):
    asins = [line.strip() for line in open(input_file, encoding="utf-8-sig") if line.strip()]
    print(f"Found {len(asins)} ASINs")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed,
                                    args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="sv-SE",
            viewport={"width": 1280, "height": 800},)
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()
        with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, ["asin", "title", "brand", "price", "seller", "shipper", "delivery", "scrape_status"])
            writer.writeheader()
            for idx, asin in enumerate(asins, 1):
                print(f"\n[{idx}/{len(asins)}] {asin}")
                result = scrape_amazon_product(page, asin)
                writer.writerow(result)
                f.flush()
                time.sleep(random.uniform(3, 6))
        browser.close()
    print(f"\nDone! Output: {output_file}")
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Text file with one ASIN per line")
    parser.add_argument("-o", "--output", default="amazon_se_output.csv")
    parser.add_argument("--headed", action="store_true", help="Show browser window")
    args = parser.parse_args()
    process_asins(args.input, args.output, headed=args.headed)
