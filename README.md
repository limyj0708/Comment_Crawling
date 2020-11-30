## 유튜브 영상, 댓글 수집 코드

**1. Youtube Data API v3을 사용합니다.**
   아래와 같은 변수들을 지정하여 유튜브 영상, 댓글 정보 수집을 진행합니다.
   1. q : 검색어 (예 : Lost Centuria)
   2. part : 수집할 정보
   3. order : 정렬 기준 (예 : date)
   4. maxResults : 한 페이지 최대 출력 결과 (최대값 100)
   5. maxPage : 탐색할 최대 페이지 수
   6. part_c : comment, 댓글의 수집할 정보
   7. order_c : 댓글 정렬 기준
   8. maxResults_c : 댓글의 한 페이지 최대 출력 결과
   9. publishedAfter : 이 시점 이후로 업로드 된 비디오 출력
   10. publishedBefore : 이 시점 전으로 업로드 된 비디오 출력
   
**2. 결과 총합을 csv로, 비디오 하나의 결과를 json 파일로 저장합니다.**
   1. csv 컬럼 형태는 youtube_comment_crawling_sample.xlsx를 참고해 주세요.
      1. 구분자(delimiter)는 |(pipe) 입니다. 쉼표, 큰따옴표, 작은따옴표가 많은 텍스트 데이터 특성상, 구분자를 쉼표로 두면 데이터가 파싱이 제대로 안 될 확률이 높아집니다.
      2. 인코딩은 UTF-8 입니다.

**3. 항후 추가계획**
   1. 번역 API를 사용하여, 수집된 결과의 기계번역을 진행합니다.
      1. Google Cloud Translation (https://cloud.google.com/translate?hl=ko-KRhttp)
      2. 파파고 API (https://developers.naver.com/docs/papago/)
   2. Document Database에 축적하는 것이 좋은 구조의 데이터이기 때문에,
      아래 클라우드 서비스 중 하나를 선택하여 데이터를 저장합니다.
      1. Oracle NoSQL Database Cloud Service
      2. Amazon DocumentDB
      3. Google Cloud Firestore
