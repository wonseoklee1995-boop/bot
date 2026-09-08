import os
import re
import json
import requests
from bs4 import BeautifulSoup

# ===== 설정 =====
BOARD_URL = "https://lawschool.chungbuk.ac.kr/bbs/board.php?bo_table=060102"
STATE_FILE = "last_seen.json"
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


def fetch_posts():
    """게시판 목록 페이지에서 글 목록을 가져온다."""
    res = requests.get(BOARD_URL, headers=HEADERS, timeout=15)
    res.raise_for_status()
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    posts = []
    # 그누보드 계열 게시판 공통 목록 구조: a[href*="wr_id="]
    for a in soup.select('a[href*="wr_id="]'):
        href = a.get("href", "")
        m = re.search(r"wr_id=(\d+)", href)
        if not m:
            continue
        wr_id = int(m.group(1))
        title = a.get_text(strip=True)
        if not title:
            continue
        # 절대 URL로 변환
        if href.startswith("http"):
            url = href
        else:
            url = "https://lawschool.chungbuk.ac.kr" + href
        posts.append({"wr_id": wr_id, "title": title, "url": url})

    # 중복 제거 (같은 wr_id가 여러 번 나올 수 있음), wr_id 기준 정렬
    seen = {}
    for p in posts:
        seen[p["wr_id"]] = p  # 나중 항목(본문 링크)이 title을 더 잘 담고 있는 경우가 많아 덮어씀
    result = list(seen.values())
    result.sort(key=lambda x: x["wr_id"], reverse=True)
    return result


def load_last_seen():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("last_wr_id", 0)
    return 0


def save_last_seen(wr_id):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_wr_id": wr_id}, f)


def send_discord(post):
    payload = {
        "content": f"📢 **새 공지사항이 올라왔어요!**\n**{post['title']}**\n{post['url']}"
    }
    res = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    res.raise_for_status()


def main():
    posts = fetch_posts()
    if not posts:
        print("게시글을 하나도 가져오지 못했습니다. 페이지 구조가 바뀌었을 수 있습니다.")
        return

    last_seen = load_last_seen()
    new_posts = [p for p in posts if p["wr_id"] > last_seen]

    if last_seen == 0:
        # 최초 실행: 알림을 보내지 않고 현재 최신 글 번호만 저장 (과거 글 폭탄 알림 방지)
        newest = max(p["wr_id"] for p in posts)
        save_last_seen(newest)
        print(f"최초 실행: 기준점을 wr_id={newest} 로 설정했습니다. (알림 없음)")
        return

    if new_posts:
        # 오래된 글부터 순서대로 알림
        for p in sorted(new_posts, key=lambda x: x["wr_id"]):
            send_discord(p)
            print(f"알림 전송: {p['title']}")
        newest = max(p["wr_id"] for p in new_posts)
        save_last_seen(newest)
    else:
        print("새 글 없음.")


if __name__ == "__main__":
    main()
