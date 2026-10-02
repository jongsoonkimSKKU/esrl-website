# ESRL · Energy Storage Research Lab

성균관대학교 김종순 교수 연구실 홈페이지입니다.

GitHub Pages 사용자 지정 도메인: `jkimbattery.com` (가비아 DNS 설정 및 HTTPS 발급 후 사용)

기존 GitHub Pages 주소: https://jongsoonkimskku.github.io/esrl-website/

기존 공개 시안: https://esrl-skku.racing-betta-6814.chatgpt.site/

## 콘텐츠 수정

`publications.json`에는 2026년 최신 논문과 메인 주요 논문 지정 정보가 있습니다.
`content.json`에는 이전 연도 논문, 구성원, 졸업생, 장비 데이터가 있습니다.
`journal_metrics.json`에는 출처를 포함한 연도별 IF·JCR 정보가 있습니다.
`lab_life.json`에는 2022–2026년 31개 앨범과 사진 목록이 있습니다.
Lithium과 Li, Sodium과 Na는 각각 같은 제목 키워드 필터에 포함되며 원소 기호가 들어간 화학식도 함께 검색합니다.
문구와 페이지 구성은 `build.py`, 스타일과 동작은 `dist/style.css`와 `dist/site.js`에서 수정합니다.

## GitHub Pages 배포

저장소 Settings → Pages → Build and deployment → Source를 **GitHub Actions**로 설정합니다.
그 뒤 `main`에 반영한 변경은 `.github/workflows/pages.yml`이 빌드하고 배포합니다.
Actions의 **Deploy ESRL to GitHub Pages → Run workflow**로 수동 배포할 수도 있습니다.

Python 3 표준 라이브러리만 사용합니다. 로컬 빌드 명령은 다음과 같습니다.

```sh
python3 scripts/prepare_github_pages.py --base-path ""
```

완성된 Pages 파일은 `_pages/`에 생성됩니다. 사용자 지정 도메인에서는 루트 경로(`/`)를 사용하며, 내부 링크와 이미지 파일의 존재 여부를 검사합니다. 기존 `dist/`도 루트 경로 기반으로 유지됩니다. 사용자 지정 도메인을 제거하여 기존 프로젝트 주소로 돌아갈 경우에는 배포 워크플로의 `--base-path`를 `/esrl-website`로 변경해야 합니다.

`jkimbattery.com`은 저장소 Settings → Pages → Custom domain에 등록되어 있습니다. 가비아 DNS 관리에서 `@`의 A 레코드를 GitHub Pages 주소 `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`으로, `www`의 CNAME을 `jongsoonkimskku.github.io.`로 설정해야 합니다. DNS 확인과 인증서 발급이 완료되면 Enforce HTTPS를 켭니다.

Lab life 사진 85장은 모두 `dist/assets/lab-life/`에 원본으로 보관합니다. 빌드 시 `scripts/pages-assets.json`의 SHA-256과 대조하며 외부 사이트에서 다시 내려받지 않습니다. 사진과 논문 PDF 모두 GitHub Pages가 직접 제공합니다.

## 반영 내용

AI 서버·배터리·EV를 연결한 가로형 메인 이미지와 한영 소개 및 모집 안내, 배터리 반딧불 로고, 논문 164편(게재·억셉 포함), 현재 구성원·졸업생, Lab life 전체 앨범을 포함합니다. 논문은 검색·연도·연구 키워드 필터, 인용문·BibTeX 다운로드와 확인 가능한 IF·JCR 정보를 제공합니다.

IF·JCR은 모든 논문에 대해 게재연도보다 1년 전 지표를 적용합니다. 예를 들어 2026년 논문은 2025년, 2025년 논문은 2024년 지표를 사용합니다. 메인 주요 논문도 같은 지표 데이터를 사용합니다. 출처가 확인되지 않은 지표는 표시하지 않습니다. Google Scholar 지표의 확인일은 2026-09-29이며 자동 갱신되지 않습니다.

GitHub Pages와 기존 Sites는 별도의 배포입니다. Wix 도메인 `energyscilab.com`과 DNS 설정은 변경하지 않았습니다.

## 논문 페이지와 PDF

논문 제목과 Article page 버튼은 DOI 또는 출판사 공식 논문 페이지로 연결됩니다. 공식 페이지를 확인하지 못한 국내 논문 1편은 Bibliographic record로 구분합니다. PDF 버튼은 저장소의 `dist/assets/papers/`에 보관한 원본을 GitHub Pages에서 직접 제공합니다. 기존 Wix 홈페이지에 의존하지 않습니다. 정식 논문 페이지가 아직 확인되지 않은 억셉 논문은 링크 없이 Accepted로 표시합니다. `publication_link_audit.json`에 논문 링크 확인 근거, PDF 원본 출처 및 SHA-256을 보관합니다. 잘못 연결됐던 PDF 3건은 원문 제목을 확인해 올바른 파일로 교체했습니다.

## 학생 연구 참여 안내

메인 화면의 모집 안내와 관심 분야별 연구 탐색 영역에 학생·졸업생의 사진 및 논문 성과를 함께 표시합니다. 같은 논문은 홈에서 한 번만 소개합니다. 성과 카드의 제1저자·공동 제1저자 표기는 논문 저자 목록에 근거하며, 사진과 이름은 현재 구성원 및 졸업생 데이터와 연결됩니다. 학생 인터뷰나 인용 발언은 사용하지 않습니다. `build.py`의 `STUDENT_STORIES`와 `RESEARCH_INTERESTS`에서 내용을 수정합니다. 주요 논문의 IF 내림차순 및 전년도 지표 기준은 유지됩니다.


## 2026-10-02 콘텐츠 정리

홈·Join·Professor에 논문 164편, 인용 10,964회, h-index 55를 표시합니다. Scholar 지표는 2026-09-29 확인값입니다. 장라현·권현지는 석사, 2026년 8월 졸업으로 등록하고 소속은 비워 둡니다. 졸업생 13명의 카드는 학위·졸업 시기·대표 논문을 우선 표시합니다. 권준하·이호석의 연구주제에 AI / cluster expansion (CASM)을 추가합니다.

Join에는 지원 서류·상시 사전 문의·면담 및 공식 입학 전형 절차를 안내합니다. AI·계산 분야에 새롭게 도전하는 학생도 환영한다는 메시지는 실험과 계산의 연구 역량을 넓히는 방향으로 표현합니다. 교수 학회 활동은 현재 한국전기화학회 총무위원·이차전지분과 실무위원, 한국세라믹학회 학술운영이사를 표시하며 확인되지 않은 시작 연도는 기재하지 않습니다. 2026년 심포지엄 Organizer와 K-BIG Project 제1간사도 포함합니다.

JCR 출처는 연도 텍스트로 표시하고 akaturk.com 링크는 제거합니다. Energy Storage Materials의 IF 링크는 Elsevier 공식 저널 페이지를 사용합니다. 온라인 출판되었으나 권호가 미배정인 논문은 Early View 또는 ASAP로 표시하며, Advanced Energy Materials e04664는 2025년 온라인 출판 기록을 사용합니다. 장비 22개 설명과 페이지별 검색 설명도 빌드 원본에서 관리합니다.
