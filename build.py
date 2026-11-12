# Builds bestpicki/index.html and stay/index.html. Add items to PAGES (newest first), run: python3 build.py
# Thumbnail from a video frame (3:4, keeps the burned-in caption so it looks like the video):
#   ffmpeg -ss <sec> -i <video.mp4> -frames:v 1 -vf "crop=iw:iw*4/3,scale=360:480" -q:v 3 bestpicki/img/<slug>.jpg
import hashlib, html, re, pathlib

DISCLOSE = {
    "coupang": "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.",
    "naver": "이 포스팅은 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다.",
    "toss": "이 포스팅은 토스쇼핑 쉐어링크 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.",
    "mrt": "이 포스팅은 마이리얼트립 마케팅 파트너 활동의 일환으로, 이에 따른 수수료를 제공받습니다.",
}
SHOP = {"coupang": "쿠팡", "naver": "네이버", "toss": "토스쇼핑", "mrt": "마이리얼트립"}

PAGES = {
    "bestpicki": {
        "kind": "shop",
        "title": "베스트피키", "tag": "생활 꿀템",
        "handle": "@bestpicki",
        "bio": "영상 속 그 제품, 여기 다 모아뒀어요.",
        "empty": ("첫 꿀템은 11월 12일 저녁에 올라와요.", ""),
        # item: dict(name, note, date "11.12", thumb "img/x.jpg", links=[(shop, url)])
        "items": [],
    },
    "stay": {
        "kind": "stay",
        "title": "스테이피키", "tag": "숙소 골라드림",
        "handle": "@stay.picki",
        "bio": "영상 속 그 숙소, 가격은 여기서 비교해 보세요.",
        "empty": ("곧 첫 숙소가 올라와요.", ""),
        # item: dict(name, region, note, date, thumb, links=[(shop, url, label)])
        "items": [
            dict(name="양양 클리프비치 리조트&풀빌라", region="강원 양양", date="11월",
                 note="전 객실 오션뷰, 빌라동 온수 자쿠지. 객실·전망은 배정에 따라 달라요.",
                 thumb="img/cliffbeach.jpg",
                 links=[("coupang", "https://link.coupang.com/a/iyP6tjRoPc", "공구가 · 11/15까지"),
                        ("mrt", "https://myrealt.rip/10TdD5c", "11/15 이후 날짜는 여기서 비교")]),
        ],
    },
}

e = html.escape
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">')

BASE = """
*{box-sizing:border-box}html{color-scheme:light;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font-family:"Pretendard Variable",Pretendard,"Apple SD Gothic Neo",sans-serif;
line-height:1.55;letter-spacing:-.01em;word-break:keep-all}
img{display:block;max-width:100%;height:auto}a{color:inherit}
main{max-width:480px;margin:0 auto;padding-bottom:56px}
.hero{position:relative;aspect-ratio:3/2;overflow:hidden;background:var(--paper)}
.hero>img.art{position:absolute;top:0;left:20%;width:100%;height:100%;object-fit:cover;-webkit-mask-image:linear-gradient(90deg,transparent,#000 14%);mask-image:linear-gradient(90deg,transparent,#000 14%)}
.mast{position:absolute;left:20px;top:22px;max-width:48%}
.mast img{width:52px;height:52px;border-radius:50%;margin-bottom:10px}
.mast h1{margin:0;line-height:1}.mast .tag{display:block;margin-top:6px;font-size:14px;font-weight:600;color:var(--sub)}
.intro{padding:18px 20px 0}.intro .handle{font-size:13px;color:var(--sub);font-weight:600}
.intro p{margin:2px 0 0;font-size:16px;font-weight:600}
.ad{margin:14px 20px 0;font-size:11.5px;line-height:1.5;color:var(--sub)}
.ad b{display:inline-block;margin-right:6px;padding:0 6px;border:1.5px solid currentColor;border-radius:4px;font-size:11px;color:var(--ink)}
.ad div{margin-top:2px}
.empty{margin:36px 20px 0;padding:22px 0;border-top:2px dashed var(--line);border-bottom:2px dashed var(--line)}
.empty strong{display:block;font-size:17px}.empty span{display:block;margin-top:4px;font-size:14px;color:var(--sub)}
footer{margin:40px 20px 0;font-size:12px;color:var(--sub)}
a:focus-visible{outline:3px solid var(--ink);outline-offset:3px}
@media (prefers-reduced-motion:no-preference){
.rise{animation:rise .7s cubic-bezier(.22,1,.36,1) both}.rise:nth-child(2){animation-delay:.06s}.rise:nth-child(3){animation-delay:.12s}
@keyframes rise{from{opacity:0;transform:translateY(10px)}}}
"""

SHOP_CSS = """
:root{--paper:#FDF2E1;--ink:oklch(24% .012 70);--sub:oklch(46% .03 75);--line:oklch(86% .04 90);
--sun:oklch(85% .16 85);--sun-deep:oklch(76% .16 78)}
.mast h1{font-family:"Gasoek One",sans-serif;font-weight:400;font-size:36px;letter-spacing:-.02em}
.feat .tagd{background:var(--ink);color:var(--sun)}.feat .tagd::before{background:var(--sun)}
.tagd{position:relative;display:inline-block;padding:2px 10px 2px 18px;background:var(--sun);color:var(--ink);
font-size:12px;font-weight:800;font-variant-numeric:tabular-nums;border-radius:3px 4px 4px 3px;
clip-path:polygon(8px 0,100% 0,100% 100%,8px 100%,0 50%)}
.tagd::before{content:"";position:absolute;left:8px;top:50%;width:5px;height:5px;margin-top:-2.5px;border-radius:50%;background:var(--paper)}
.feat{display:grid;grid-template-columns:38% 1fr;gap:16px;align-items:end;margin:26px 0 0;padding:20px;background:var(--sun);text-decoration:none}
.feat img{width:100%;aspect-ratio:3/4;object-fit:cover;border-radius:6px;transform:rotate(-1.5deg);box-shadow:0 1px 0 var(--sun-deep),0 10px 24px -14px oklch(30% .05 70/.6)}
.feat .k{font-size:12px;font-weight:800;letter-spacing:.04em}
.feat h2{margin:6px 0 6px;font-size:22px;line-height:1.25}
.feat p{margin:0 0 14px;font-size:14px}
.buy{display:inline-block;padding:9px 14px;background:var(--ink);color:var(--sun);font-weight:800;font-size:14px;border-radius:999px}
.feat:active .buy,.row:active{opacity:.85}
.more{margin:30px 20px 4px;font-size:13px;font-weight:800;color:var(--sub)}
.row{display:grid;grid-template-columns:66px 1fr auto;gap:14px;align-items:center;margin:0 20px;padding:14px 0;
border-bottom:2px dashed var(--line);text-decoration:none}
.row img{width:66px;aspect-ratio:3/4;object-fit:cover;border-radius:4px}
.row h3{margin:4px 0 0;font-size:16px;line-height:1.3}.row p{margin:2px 0 0;font-size:13px;color:var(--sub);
display:-webkit-box;-webkit-line-clamp:1;-webkit-box-orient:vertical;overflow:hidden}
.row .go{font-size:13px;font-weight:800;white-space:nowrap}
.find{display:block;width:calc(100% - 40px);margin:18px 20px 0;padding:11px 14px;border:2px solid var(--line);border-radius:10px;
background:transparent;font:inherit;font-size:15px;color:var(--ink)}
.find:focus{outline:none;border-color:var(--ink)}
"""

STAY_CSS = """
:root{--paper:#FBEEDD;--ink:oklch(26% .035 245);--sub:oklch(47% .03 220);--line:oklch(87% .025 80);--sea:oklch(64% .1 195)}
.mast h1{font-family:"Hahmlet",serif;font-weight:700;font-size:38px;letter-spacing:-.03em}
.stay{margin:30px 20px 0}
.stay .ph{position:relative}
.stay .ph img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:2px}
.stay .no{position:absolute;left:-1px;top:14px;padding:3px 10px 3px 9px;background:var(--paper);font-family:"Hahmlet",serif;font-size:13px;font-weight:600}
.stay .meta,.srow .meta{font-size:12.5px;font-weight:700;color:var(--sea);letter-spacing:.02em}.stay .meta{margin-top:14px}
.stay h2{margin:2px 0 6px;font-family:"Hahmlet",serif;font-size:24px;font-weight:600;line-height:1.25;letter-spacing:-.03em}
.stay p{margin:0;font-size:14.5px;color:var(--sub)}
.stay ul,.srow ul{list-style:none;margin:16px 0 0;padding:0;border-top:1px solid var(--ink)}
.stay li a,.srow li a{display:flex;justify-content:space-between;gap:12px;align-items:baseline;padding:13px 0;border-bottom:1px solid var(--line);text-decoration:none}
.stay li b,.srow li b{font-size:16px}.stay li span,.srow li span{font-size:13px;color:var(--sub);text-align:right}
.stay li a:active,.srow li a:active{background:oklch(94% .02 195)}
.more{margin:34px 20px 4px;font-family:"Hahmlet",serif;font-size:15px;font-weight:600}
.srow{margin:0 20px;border-bottom:1px solid var(--line)}
.srow summary{display:grid;grid-template-columns:64px 1fr auto;gap:14px;align-items:center;padding:12px 0;cursor:pointer;list-style:none}
.srow summary::-webkit-details-marker{display:none}
.srow summary img{width:64px;aspect-ratio:1;object-fit:cover;border-radius:2px}
.srow h3{margin:1px 0 0;font-family:"Hahmlet",serif;font-size:17px;font-weight:600;line-height:1.3}
.srow .pm{font-size:20px;line-height:1;color:var(--sub);transition:transform .3s cubic-bezier(.22,1,.36,1)}
.srow[open] .pm{transform:rotate(45deg)}
.srow ul{margin:0 0 14px}.srow li:last-child a{border-bottom:0}
.find{display:block;width:calc(100% - 40px);margin:14px 20px 4px;padding:11px 14px;border:1.5px solid var(--line);border-radius:2px;
background:transparent;font:inherit;font-size:15px;color:var(--ink)}
.find:focus{outline:none;border-color:var(--ink)}
"""


def ad_block(items):
    used = sorted({l[0] for it in items for l in it["links"]})
    if not used:
        return ""
    return ('<div class="ad"><b>광고</b>아래 링크로 구매하면 수수료를 받아요.'
            + "".join(f"<div>{e(DISCLOSE[s])}</div>" for s in used) + "</div>")


def empty(p):
    a, b = p["empty"]
    return f'<div class="empty"><strong>{e(a)}</strong>{f"<span>{e(b)}</span>" if b else ""}</div>'


def shop_body(p):
    its = p["items"]
    if not its:
        return empty(p)
    f, rest = its[0], its[1:]
    s, u = f["links"][0]
    out = (f'<a class="feat rise" href="{e(u)}" rel="sponsored noopener" target="_blank">'
           f'<img src="{e(f["thumb"])}" alt="" width="360" height="480">'
           f'<div><span class="tagd">{e(f["date"])} 영상</span><div class="k" style="margin-top:12px">가장 최근 영상</div>'
           f'<h2>{e(f["name"])}</h2><p>{e(f["note"])}</p><span class="buy">{SHOP[s]}에서 보기</span></div></a>')
    if rest:
        out += '<div class="more">지난 영상 꿀템</div>'
        if len(its) >= 12:  # ponytail: plain substring filter; add categories when the list gets long enough to need them
            out += ('<input class="find" type="search" placeholder="물건 이름이나 날짜(11.12)로 찾기" aria-label="꿀템 찾기" '
                    'oninput="var q=this.value.trim();document.querySelectorAll(\'.row\').forEach(function(r){r.hidden=q&&r.dataset.k.indexOf(q)<0})">')
        for it in rest:
            s, u = it["links"][0]
            out += (f'<a class="row" data-k="{e(it["name"] + " " + it["date"])}" href="{e(u)}" rel="sponsored noopener" target="_blank">'
                    f'<img src="{e(it["thumb"])}" alt="" width="66" height="88" loading="lazy">'
                    f'<div><span class="tagd">{e(it["date"])}</span><h3>{e(it["name"])}</h3><p>{e(it["note"])}</p></div>'
                    f'<span class="go">{SHOP[s]} →</span></a>')
    return out


def stay_links(it):
    return "".join(f'<li><a href="{e(u)}" rel="sponsored noopener" target="_blank"><b>{SHOP[s]}</b><span>{e(lab)} →</span></a></li>'
                   for s, u, lab in it["links"])


def stay_body(p):
    its = p["items"]
    if not its:
        return empty(p)
    f, rest = its[0], its[1:]
    out = (f'<section class="stay rise"><div class="ph"><img src="{e(f["thumb"])}" alt="{e(f["name"])}" width="576" height="576">'
           f'<span class="no">No. {len(its):02d}</span></div>'
           f'<div class="meta">{e(f["region"])} · {e(f["date"])} 영상</div><h2>{e(f["name"])}</h2><p>{e(f["note"])}</p>'
           f'<ul>{stay_links(f)}</ul></section>')
    if rest:
        # older stays fold into one-line rows; tap opens the shop links
        out += '<div class="more">지난 숙소</div>'
        if len(its) >= 12:
            out += ('<input class="find" type="search" placeholder="지역이나 숙소 이름으로 찾기" aria-label="숙소 찾기" '
                    'oninput="var q=this.value.trim();document.querySelectorAll(\'.srow\').forEach(function(r){r.hidden=q&&r.dataset.k.indexOf(q)<0})">')
        for n, it in enumerate(rest, 2):
            out += (f'<details class="srow" data-k="{e(it["name"] + " " + it["region"])}"><summary>'
                    f'<img src="{e(it["thumb"])}" alt="" width="64" height="64" loading="lazy">'
                    f'<div><div class="meta">No. {len(its) - n + 1:02d} · {e(it["region"])}</div><h3>{e(it["name"])}</h3></div>'
                    f'<span class="pm" aria-hidden="true">+</span></summary><ul>{stay_links(it)}</ul></details>')
    return out


def page(key, p):
    shop = p["kind"] == "shop"
    gfont = "Gasoek+One" if shop else "Hahmlet:wght@600;700"
    css = BASE + (SHOP_CSS if shop else STAY_CSS)
    body = shop_body(p) if shop else stay_body(p)
    items = p["items"] if shop else [dict(links=[(s, u) for s, u, _ in it["links"]]) for it in p["items"]]
    note = "판매처마다 모양·가격이 조금씩 달라요. 구매 전에 상세를 꼭 확인하세요." if shop else "가격·객실은 날짜마다 달라요. 예약 전에 조건을 꼭 확인하세요."
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="{'#FDF2E1' if shop else '#FBEEDD'}">
<title>{e(p["title"])} | {e(p["tag"])}</title><meta name="robots" content="noindex">
<link rel="icon" href="logo.png">{FONTS}<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={gfont}&display=swap">
<style>{css}</style></head>
<body><main>
<header class="hero"><img class="art" src="hero.jpg" alt="" width="1200" height="800">
<div class="mast rise"><img src="logo.png" alt=""><h1>{e(p["title"])}</h1><span class="tag">{e(p["tag"])}</span></div></header>
<div class="intro"><div class="handle">{e(p["handle"])}</div><p>{e(p["bio"])}</p></div>
{ad_block(items)}
{body}
<footer>{note}<br>{e(p["handle"])}</footer>
</main></body></html>
"""


def build(root, pages):
    for k, p in pages.items():
        (root / k).mkdir(parents=True, exist_ok=True)
        d = root / k
        # file-hash query so phones never show a stale image after it is replaced
        bust = lambda m: f'{m[1]}="{m[2]}?v={hashlib.md5((d / m[2]).read_bytes()).hexdigest()[:8]}"' if (d / m[2]).is_file() else m[0]
        (d / "index.html").write_text(re.sub(r'(src|href)="([^":?#]+\.(?:jpg|png))"', bust, page(k, p)), encoding="utf-8")


if __name__ == "__main__":
    root = pathlib.Path(__file__).parent
    build(root, PAGES)
    (root / "index.html").write_text('<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>picki</title>'
        '<p><a href="bestpicki/">베스트피키</a> · <a href="stay/">스테이피키</a></p>', encoding="utf-8")
    print("built", list(PAGES))
