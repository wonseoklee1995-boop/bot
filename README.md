# 충북대 법학전문대학원 공지사항 → 디스코드 알림 봇

법학전문대학원 석사 공지사항 게시판(bo_table=060102)을 30분마다 확인해서
새 글이 올라오면 디스코드로 알림을 보내는 봇입니다. 서버 없이 GitHub Actions로 무료 실행됩니다.

## 1. 디스코드 웹훅 URL 만들기

1. 알림받을 디스코드 채널에서 톱니바퀴(채널 설정) 클릭
2. **연동 > 웹후크 > 새 웹후크** 클릭
3. 이름 설정 후 **웹후크 URL 복사** (예: `https://discord.com/api/webhooks/...`)

## 2. GitHub 저장소 만들기

1. github.com에서 새 저장소(Public이든 Private이든 상관없음) 생성
2. 이 폴더에 있는 파일들을 그대로 그 저장소에 업로드
   - `check_notice.py`
   - `requirements.txt`
   - `.github/workflows/check_notice.yml`
   - `README.md`

## 3. 웹훅 URL을 비밀값(Secret)으로 등록

1. 저장소 페이지에서 **Settings > Secrets and variables > Actions**
2. **New repository secret** 클릭
3. Name: `DISCORD_WEBHOOK_URL`
4. Value: 1번에서 복사한 웹훅 URL 붙여넣기 → **Add secret**

## 4. 동작 확인

- **Actions** 탭 → `충북대 법전원 공지 체크` 워크플로우 선택 → **Run workflow** 로 수동 실행 가능
- 최초 실행 시에는 기존 글에 대해 알림을 보내지 않고, 현재 가장 최신 글 번호만 기준점으로 저장합니다.
  (안 그러면 처음 실행할 때 과거 글 수백 개가 한꺼번에 알림으로 옵니다.)
- 이후 실행부터는 새 글이 생기면 디스코드로 알림이 옵니다.
- 기본 주기는 30분이며, `.github/workflows/check_notice.yml` 의 `cron` 값을 바꾸면 주기를 조절할 수 있습니다.
  (참고: GitHub Actions의 스케줄은 정확히 그 시각에 실행되지 않고 몇 분 정도 지연될 수 있습니다.)

## 5. 다른 게시판으로 바꾸고 싶다면

`check_notice.py` 맨 위의 `BOARD_URL` 값만 원하는 게시판 주소로 바꾸면 됩니다.
예: 공통 게시판은 `bo_table=060101`, 박사는 `060103` 등.

## 참고

- 이 사이트는 로그인 없이 볼 수 있는 공개 게시판이라 별도 로그인 처리는 넣지 않았습니다.
- 사이트 구조(HTML)가 바뀌면 스크립트가 글을 못 읽어올 수 있습니다. 그 경우 `fetch_posts()` 함수의 선택자를 다시 확인해야 합니다.
