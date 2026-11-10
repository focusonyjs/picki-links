# Builds bestpicki/index.html and stay/index.html. Add items to PAGES, run: python3 build.py
import html, pathlib

DISCLOSE = {
    "coupang": "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.",
    "naver": "이 포스팅은 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다.",
    "toss": "이 포스팅은 토스쇼핑 쉐어링크 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.",
    "mrt": "이 포스팅은 마이리얼트립 마케팅 파트너 활동의 일환으로, 이에 따른 수수료를 제공받습니다.",
}
SHOP = {"coupang": "쿠팡", "naver": "네이버", "toss": "토스쇼핑", "mrt": "마이리얼트립"}

PAGES = {
    "bestpicki": {
        "title": "베스트피키 | 생활 꿀템",
        "handle": "@bestpicki",
        "bio": "영상에 나온 생활 꿀템, 여기서 바로 보세요",
        "accent": "#F5B700", "ink": "#2B2100",
        "empty": "첫 추천은 11월 12일(목) 저녁에 올라와요",
        # newest first: (name, note, shop, url)
        "items": [],
    },
    "stay": {
        "title": "스테이피키 | 숙소 골라드림",
        "handle": "@stay.picki",
        "bio": "영상에 나온 숙소, 날짜별 가격은 여기서 확인하세요",
        "accent": "#14A3A3", "ink": "#03302F",
        "empty": "곧 첫 숙소가 올라와요",
        "items": [
            ("양양 클리프비치 리조트&풀빌라", "전 객실 오션뷰 · 빌라동 온수 자쿠지 · 객실·전망은 배정에 따라 달라요",
             "coupang", "https://link.coupang.com/a/iyP6tjRoPc"),
        ],
    },
}

CSS = """
:root{--bg:#FAFAF7;--card:#fff;--text:#1C1C1A;--sub:#6B6B66;--line:#E7E5DF}
@media (prefers-color-scheme:dark){:root{--bg:#141413;--card:#1F1F1D;--text:#F2F1EC;--sub:#A3A29C;--line:#33322F}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);
font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;line-height:1.5}
main{max-width:480px;margin:0 auto;padding:32px 16px 48px}
header{text-align:center}header img{width:88px;height:88px;border-radius:50%;border:3px solid var(--accent)}
h1{font-size:20px;margin:12px 0 2px}.handle{color:var(--sub);font-size:14px}
.bio{margin:8px 0 0;font-size:15px}
.ad{margin:20px 0 16px;padding:10px 12px;border-radius:10px;background:var(--card);border:1px solid var(--line);
font-size:12.5px;color:var(--sub)}
.ad b{color:var(--text)}
a.item{display:block;text-decoration:none;color:inherit;background:var(--card);border:1px solid var(--line);
border-left:6px solid var(--accent);border-radius:14px;padding:14px 16px;margin:10px 0}
a.item:active{transform:scale(.99)}
.name{font-weight:700;font-size:16px}.note{font-size:13.5px;color:var(--sub);margin-top:2px}
.go{display:inline-block;margin-top:8px;font-size:13px;font-weight:700;color:var(--ink);background:var(--accent);
padding:4px 10px;border-radius:99px}
.empty{text-align:center;color:var(--sub);padding:28px 0}
footer{text-align:center;font-size:12px;color:var(--sub);margin-top:28px}
"""

def page(key, p):
    used = sorted({i[2] for i in p["items"]})
    ad = "".join(f"<div>{html.escape(DISCLOSE[s])}</div>" for s in used)
    items = "".join(
        f'<a class="item" href="{html.escape(u)}" rel="sponsored noopener" target="_blank">'
        f'<div class="name">{html.escape(n)}</div><div class="note">{html.escape(t)}</div>'
        f'<span class="go">{SHOP[s]}에서 보기 →</span></a>'
        for n, t, s, u in p["items"]) or f'<p class="empty">{html.escape(p["empty"])}</p>'
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(p["title"])}</title><meta name="robots" content="noindex">
<link rel="icon" href="logo.png"><style>:root{{--accent:{p["accent"]};--ink:{p["ink"]}}}{CSS}</style></head>
<body><main><header><img src="logo.png" alt=""><h1>{html.escape(p["title"])}</h1>
<div class="handle">{p["handle"]}</div><p class="bio">{html.escape(p["bio"])}</p></header>
{f'<div class="ad"><b>광고</b> · 아래 링크로 구매하면 수수료를 받아요.{ad}</div>' if used else ''}
{items}<footer>{p["handle"]}</footer></main></body></html>
"""

root = pathlib.Path(__file__).parent
for k, p in PAGES.items():
    (root / k / "index.html").write_text(page(k, p), encoding="utf-8")
(root / "index.html").write_text('<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>picki</title>'
    '<p><a href="bestpicki/">베스트피키</a> · <a href="stay/">스테이피키</a></p>', encoding="utf-8")
print("built", list(PAGES))
