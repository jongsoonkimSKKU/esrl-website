# ESRL · Energy Storage Research Lab

성균관대학교 김종순 교수 연구실 홈페이지 소스입니다.

현재 공개 홈페이지: https://esrl-skku.racing-betta-6814.chatgpt.site
기존 도메인: https://www.energyscilab.com/

## 구성

- `content.json`: 논문, 현재 구성원, 졸업생, 장비 및 사진 데이터
- `build.py`: 콘텐츠 데이터로 페이지를 생성하는 Python 스크립트
- `dist/`: 배포 가능한 정적 홈페이지 전체
- `dist/assets/`: 로고, 연구 이미지, 구성원 사진
- `dist/style.css`, `dist/site.js`: 디자인과 메뉴 동작
- `.openai/hosting.json`: 기존 Sites 프로젝트 연결 정보

## 수정과 확인

Python 3만 필요하며 별도 패키지 설치는 필요하지 않습니다.

```sh
python build.py
python -m http.server 8000 --directory dist
```

브라우저에서 http://localhost:8000 을 엽니다.
논문과 구성원은 `content.json`, 페이지 문구와 구성은 `build.py`에서 수정합니다.
수정 후 `python build.py`를 실행하고 변경된 소스와 `dist`를 함께 커밋합니다.

## 현재 반영 내용

2026-09-29 기준: AI 서버·배터리 소재·전기차를 연결하는 가로형 메인 이미지,
한영 모집 안내, 배터리 반딧불 로고, 2009–2026년 논문 163편,
현재 구성원 및 졸업생 11명, 연도별/구성원별 선택 메뉴를 포함합니다.
Publications는 제목·저자·학술지 검색, 연도·제목 키워드 필터, 인용문 복사 및 BibTeX 다운로드를 제공합니다.
Google Scholar 지표는 2026-09-29 확인값(인용 10,964회, h-index 55, i10-index 126)이며 자동 갱신되지 않습니다.

## 배포와 도메인

이 저장소는 홈페이지 소스와 정적 파일을 보관합니다.
GitHub 커밋만으로 현재 `chatgpt.site` 홈페이지가 자동 갱신되지는 않습니다.
Sites에서 수정/배포한 경우 최신 소스를 이 저장소에도 반영해야 합니다.

다른 정적 호스팅으로 옮길 때는 `dist`를 사이트 루트로 사용합니다.
현재 링크는 루트 경로(`/assets/`, `/people/` 등)를 기준으로 작성되어 있습니다.
GitHub Pages의 `/esrl-website/` 하위 경로로 배포하려면 해당 접두어에 맞게 링크를 조정해야 합니다.
`energyscilab.com`을 연결하기 전에는 기존 Wix의 논문 PDF와 사진 아카이브 링크도 이전해야 합니다.
현재 Wix 도메인과 DNS 설정은 변경하지 않았습니다.

## ESRL의 연구 정체성

양극과 고체전해질이 핵심 연구 분야이며, AI·제일원리계산·합성·고도분석은 이 두 분야의 소재 설계와 작동 메커니즘 이해를 연결합니다. Publications는 검색 패널과 연구 기록을 좌우로 나눈 ESRL 고유 디자인을 사용합니다.
