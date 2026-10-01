# ESRL · Energy Storage Research Lab

성균관대학교 김종순 교수 연구실 홈페이지입니다.

GitHub Pages 배포 주소: https://jongsoonkimskku.github.io/esrl-website/

기존 공개 시안: https://esrl-skku.racing-betta-6814.chatgpt.site/

## 콘텐츠 수정

`content.json`에는 논문, 구성원, 졸업생, 장비 데이터가 있습니다.
`journal_metrics.json`에는 출처를 포함한 연도별 IF·JCR 정보가 있습니다.
`lab_life.json`에는 2022–2026년 31개 앨범과 사진 목록이 있습니다.
문구와 페이지 구성은 `build.py`, 스타일과 동작은 `dist/style.css`와 `dist/site.js`에서 수정합니다.

## GitHub Pages 배포

저장소 Settings → Pages → Build and deployment → Source를 **GitHub Actions**로 설정합니다.
그 뒤 `main`에 반영한 변경은 `.github/workflows/pages.yml`이 빌드하고 배포합니다.
Actions의 **Deploy ESRL to GitHub Pages → Run workflow**로 수동 배포할 수도 있습니다.

Python 3 표준 라이브러리만 사용합니다. 로컬 빌드 명령은 다음과 같습니다.

```sh
python3 scripts/prepare_github_pages.py --base-path /esrl-website
```

완성된 Pages 파일은 `_pages/`에 생성됩니다. 빌드할 때 메뉴·이미지·CSS 경로에 `/esrl-website/`가 적용되며, 내부 링크와 이미지 파일의 존재 여부를 검사합니다. 기존 `dist/`는 루트 경로 기반으로 유지됩니다.

Lab life 사진 85장은 `scripts/pages-assets.json`의 공개 원본 사본에서 빌드 시 복원하고 SHA-256으로 검증합니다. 배포 결과에는 사진 파일 자체가 포함되므로 방문자의 브라우저에서는 GitHub Pages가 사진을 제공합니다. 사진 파일을 동일한 `dist/assets/lab-life/` 경로에 커밋하면 빌드 중 다시 다운로드하지 않습니다.

## 반영 내용

AI 서버·배터리·EV를 연결한 가로형 메인 이미지와 한영 소개 및 모집 안내, 배터리 반딧불 로고, 논문 163편, 현재 구성원·졸업생, Lab life 전체 앨범을 포함합니다. 논문은 검색·연도·연구 키워드 필터, 인용문·BibTeX 다운로드와 확인 가능한 IF·JCR 정보를 제공합니다.

IF·JCR은 모든 논문에 대해 게재연도보다 1년 전 지표를 적용합니다. 예를 들어 2026년 논문은 2025년, 2025년 논문은 2024년 지표를 사용합니다. 메인 주요 논문도 같은 지표 데이터를 사용합니다. 출처가 확인되지 않은 지표는 표시하지 않습니다. Google Scholar 지표의 확인일은 2026-09-29이며 자동 갱신되지 않습니다.

GitHub Pages와 기존 Sites는 별도의 배포입니다. Wix 도메인 `energyscilab.com`과 DNS 설정은 변경하지 않았습니다.

## 논문 페이지와 PDF

논문 제목과 Article page 버튼은 DOI 또는 출판사 공식 논문 페이지로 연결됩니다. 공식 페이지를 확인하지 못한 국내 논문 1편은 Bibliographic record로 구분합니다. PDF 버튼은 저장소의 `dist/assets/papers/`에 보관한 원본을 GitHub Pages에서 직접 제공합니다. 기존 Wix 홈페이지에 의존하지 않습니다. `publication_link_audit.json`에 논문 링크 확인 근거, PDF 원본 출처 및 SHA-256을 보관합니다. 잘못 연결됐던 PDF 3건은 원문 제목을 확인해 올바른 파일로 교체했습니다.
