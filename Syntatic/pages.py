GROUPS = {
    "roblox": {
        "title": "Roblox",
        "description": "Roblox games and tools built by Syntatic.",
        "pages": [
            {
                "title": "Orbitix Roblox",
                "slug": "orbitix-roblox",
                "description": "Roblox integration for Orbitix.",
                "implemented": False,
                "template": None,
                "model_id": "qwen/qwen3.8-27b",
                "model_name": "Orbitix Roblox",
                "thinking_levels": {
                    "low": "qwen/qwen3.8-27b",
                    "med": "openai/gpt-oss-20b",
                    "max": "openai/gpt-oss-120b",
                },
                "system_prompt": "You are Orbitix Roblox. Only help with this page and its Roblox features. Do not provide code, exploits, or anything usable against any service.",
            },
        ],
    },
    "discord-bots": {
        "title": "Discord Bots",
        "description": "Discord bots and utilities built by Syntatic.",
        "pages": [
            {
                "title": "Orbitix Bot",
                "slug": "orbitix-bot",
                "description": "Discord bot powered by Orbitix.",
                "implemented": False,
                "template": None,
                "model_id": "qwen/qwen3.8-27b",
                "model_name": "Orbitix Bot",
                "thinking_levels": {
                    "low": "qwen/qwen3.8-27b",
                    "med": "openai/gpt-oss-20b",
                    "max": "openai/gpt-oss-120b",
                },
                "system_prompt": "You are Orbitix Bot. Only help with this page and its Discord bot features. Do not provide code, exploits, or anything usable against any service.",
            },
        ],
    },
    "other-websites": {
        "title": "Other Websites",
        "description": "Other websites and web tools built by Syntatic.",
        "pages": [
            {
                "title": "Orbitix Web",
                "slug": "orbitix-web",
                "description": "Web version of Orbitix.",
                "implemented": True,
                "template": "pages/other-websites/orbitix-web.html",
                "model_id": "qwen/qwen3.8-27b",
                "model_name": "Orbitix Web",
                "thinking_levels": {
                    "low": "qwen/qwen3.8-27b",
                    "med": "openai/gpt-oss-20b",
                    "max": "openai/gpt-oss-120b",
                },
                "system_prompt": "You are Orbitix Web. Only help with this page and its web features. Do not provide code, exploits, or anything usable against any service.",
            },
        ],
    },
}


def find_page(group, slug):
    group_data = GROUPS.get(group)
    if not group_data:
        return None
    for page in group_data["pages"]:
        if page["slug"] == slug:
            return page, group_data
    return None
""" filePath">
/workspace/app/Syntatic/pages.py