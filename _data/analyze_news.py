import json
with open('/Users/sujaekong/tech-engineer-blog/_data/news_raw.json') as f:
    data = json.load(f)
seen = {}
for a in data['articles']:
    t = a['title']
    if t not in seen:
        seen[t] = {'sources': [], 'pub_date': a['pub_date'], 'keyword': a['keyword']}
    seen[t]['sources'].append(a['source'])
print(f"Total: {data['total']}, Unique: {len(seen)}")
print('---')
for t, info in seen.items():
    print(f"[{len(info['sources'])}|{info['pub_date']}|{info['keyword']}] {t}")
