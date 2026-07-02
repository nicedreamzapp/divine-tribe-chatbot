#!/usr/bin/env python3
"""Refresh products_clean.json from live WooCommerce and rebuild embeddings.

Keeps the exact schema the chatbot expects ({metadata, products:[{name,
description, url, category}]}). Run whenever the store changes:
    python3 refresh_products.py            # refresh json + rebuild pkl
Reads WOOCOMMERCE_KEY/SECRET from ../.env (the ineedhemp website .env).
"""
import json, os, re, base64, urllib.request
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = os.path.join(HERE, "..", ".env")

def load_env(path):
    env = {}
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def strip_html(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", s).strip()

def categorize(p):
    cats = [c["slug"] for c in p.get("categories", [])]
    return cats[0] if cats else "uncategorized"

def main():
    env = load_env(ENV)
    auth = base64.b64encode(f"{env['WOOCOMMERCE_KEY']}:{env['WOOCOMMERCE_SECRET']}".encode()).decode()
    products, page = [], 1
    while True:
        req = urllib.request.Request(
            f"https://ineedhemp.com/wp-json/wc/v3/products?per_page=100&page={page}&status=publish",
            headers={"Authorization": f"Basic {auth}"})
        batch = json.loads(urllib.request.urlopen(req, timeout=40).read())
        if not batch:
            break
        for p in batch:
            desc = strip_html(p.get("short_description") or p.get("description"))[:900]
            price = p.get("price") or ""
            if price:
                desc = f"{desc} Current price: ${price}."
            products.append({
                "name": p["name"],
                "description": desc,
                "url": p.get("permalink", ""),
                "category": categorize(p),
            })
        page += 1
    out = {
        "metadata": {
            "total_products": len(products),
            "source": "WooCommerce REST API (live)",
            "refreshed": str(date.today()),
            "note": "Parent products only, published",
        },
        "products": products,
    }
    with open(os.path.join(HERE, "products_clean.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {len(products)} products")

    # rebuild embeddings so RAG matches the fresh data
    pkl = os.path.join(HERE, "product_embeddings.pkl")
    if os.path.exists(pkl):
        os.rename(pkl, pkl + ".old")
        print("moved old embeddings aside; they rebuild on next chatbot start")

if __name__ == "__main__":
    main()
