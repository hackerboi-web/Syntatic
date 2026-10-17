import os
import requests

def get_supabase():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    from supabase import create_client
    return create_client(url, key)


def fetch_items():
    sb = get_supabase()
    if not sb:
        return []
    res = sb.table("roblox_items").select("*").order("created_at", desc=True).execute()
    return res.data or []


def import_items(item_ids):
    sb = get_supabase()
    if not sb:
        return []
    imported = []
    for item_id in item_ids:
        try:
            r = requests.get(f"https://catalog.roblox.com/v1/catalog/items/{item_id}/details", timeout=10)
            if not r.ok:
                continue
            data = r.json()
            row = {
                "title": data.get("Name", f"Item {item_id}"),
                "description": data.get("Description", ""),
                "robux_price": data.get("PriceInRobux", 0),
                "roblox_item_url": f"https://www.roblox.com/catalog/{item_id}",
                "sale_status": "for_sale" if data.get("IsForSale") else "offsale",
                "item_type": data.get("ItemType", "unknown"),
            }
            sb.table("roblox_items").upsert(row).execute()
            imported.append(item_id)
        except Exception:
            continue
    return imported
""" filePath">
/workspace/app/Syntatic/roblox.py