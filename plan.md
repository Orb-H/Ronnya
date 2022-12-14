# 구상

### 프론트

- 표시할 내용
  - 필수
    - 닉네임
    - 등급(4마/3마는 선택 가능 또는 모두 보이게)
  - 선택
    - 랭크 포인트(이거 애니메이션 있으면 좋을 것 같긴 함)
    - 대표 캐릭터
    - 칭호
    - 캐릭터 테두리
- 형식
  - 이미지 동적 생성? SVG?
  - &lt;img&gt; 태그 또는 &lt;picture&gt; 태그 사용해서 불러올 수 있게끔 만드는 게 좋을 듯
  - 웹서버로 request를 보내면 이미지가 반환되는 형식
  - [Project mazassumnida](https://github.com/mazassumnida/mazassumnida)의 방식을 참고하는 것이 좋을 듯
- 디자인 어케 하지
  - 옵션1: 작혼 느낌 살려서
  - 옵션2: 모던한 느낌으로

### 백

- 웹
  - 작혼 서버로부터 데이터 request
    - request가 너무 잦으면 서버에서 밴을 때릴 수 있음
      - 일정 쿨타임(e.g. 10분) 이내에 request를 여러 번 보내지 않게 만듦
      - 갱신을 하지 않으면 새로 갱신이 올 때까지 request를 보내지 않음
    - 작혼 서버와는 WebSocket을 사용하여 통신해야 할 듯
    - 통신 시 Google의 protobuf를 사용하여 메시지 wrapping/unwrapping이 이뤄짐
    - protobuf에 의한 메시지 wrapping 구조는 가지고 있음
    - 작혼 전적 사이트 깃허브 참고할 것
  - 형식 정해지는 대로 해당 형식 렌더링하는 기능 필요
- DB
  - request를 보내지 않고도 같은 데이터를 계속 반환하려면 DB에 관련 데이터 저장이 불가피
  - 사용자 식별 방법은 크게 3가지가 있음
    - 친추 코드
    - 닉네임
    - UID(작혼 서버 내부적으로만 사용함)
  - 최소한 닉네임, UID와 이미지에 렌더링할 내용을 DB에 담고있는 것이 좋을 듯(법적 이슈 확인 필요)
