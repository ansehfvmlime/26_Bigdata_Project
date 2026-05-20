import requests, os

API_KEY = os.environ.get('LOSTARK_API_KEY', '')
headers = {'accept': 'application/json', 'authorization': f'bearer {API_KEY}'}

def get_all_items(category_code):
    all_items = []
    page = 1
    while True:
        payload = {
            'Sort': 'CURRENT_MIN_PRICE',
            'CategoryCode': category_code,
            'PageNo': page,
            'SortCondition': 'ASC'
        }
        resp = requests.post(
            'https://developer-lostark.game.onstove.com/markets/items',
            headers=headers,
            json=payload
        )
        data = resp.json()
        items = data.get('Items') or []
        all_items.extend(items)
        if len(all_items) >= data.get('TotalCount', 0) or not items:
            break
        page += 1
    return all_items

targets = {
    '식물채집': 90200,
    '벌목':    90300,
    '채광':    90400,
    '수렵':    90500,
    '낚시':    90600,
    '고고학':  90700,
    '재련재료': 50010,
    '재련추가': 50020,
}

for name, code in targets.items():
    items = get_all_items(code)
    print(f'=== {name} ({len(items)}건) ===')
    for item in items:
        print(f'  {item.get("Name")}')