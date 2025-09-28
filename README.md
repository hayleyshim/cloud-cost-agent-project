💰 클라우드 비용 에이전트 자동화 및 보고서 생성 프로젝트
이 프로젝트는 클라우드 인프라 아키텍트의 실무를 돕기 위해 **Multi-Agent System (MAS)**을 구축하고, 사용자의 요청에 따라 AWS 예상 비용을 계산한 후, 엑셀(.xlsx) 보고서를 자동 생성하는 것을 목표로 합니다.
이 시스템은 A2A (Agent-to-Agent) 통신을 활용하여 비용 계산과 보고서 생성을 분리 처리하며, Git/GitHub Actions를 통해 개발 워크플로우를 자동화합니다.

🛠️ 기술 스택
분류	기술	역할
Agent Framework	Python 3.9+	주요 개발 언어
A2A 통신	Redis (Message Queue)	비용 계산 결과(JSON) 전달 및 워크플로우 제어
보고서 생성	Flask, openpyxl	비용 데이터를 받아 실무용 Excel 파일(.xlsx) 생성
HTTP 요청	Requests	(선택 사항) AWS 등 외부 웹사이트에서 최신 가격 데이터 크롤링
컨테이너	Docker, Docker Compose	각 에이전트와 Redis 서비스를 독립적으로 구동
자동화	GitHub Actions	테스트 및 컨테이너 이미지 빌드 자동화 (CI/CD)

🏗️ 프로젝트 구조
프로젝트는 두 개의 핵심 에이전트와 하나의 메시지 큐 서비스로 구성됩니다.

cloud-cost-agent/
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI/CD (GitHub Actions) 워크플로우
├── agent_cost/                    # 1. 비용 계산 에이전트 (포트 5001)
│   └── app.py                     # (사용자 입력 수신 및 비용 계산 로직)
├── agent_report/                  # 2. 보고서 생성 에이전트 (포트 5002)
│   └── app.py                     # (비용 데이터를 받아 Excel 파일 생성)
├── output/                        # 최종 결과물(.xlsx)이 저장되는 로컬 폴더 (Volume)
├── docker-compose.yml             # 모든 서비스 정의 파일
└── README.md

⚙️ 시작하는 방법 (Local Run)

1. 환경 설정 및 구동

필수 설치 항목: Python, Git, Docker Desktop
Dockerfile 업데이트: agent_cost와 agent_report 폴더의 Dockerfile과 requirements.txt에 필요한 라이브러리(특히 **openpyxl**과 requests)가 포함되었는지 확인하세요.
Bash

# 1. 프로젝트 폴더로 이동
# cd cloud-cost-agent

# 2. output 폴더 생성 (Volume Mapping을 위해 필수)
mkdir output

# 3. 모든 컨테이너 빌드 및 실행 (CI/CD를 위한 필수 과정)
docker compose up --build


2. 에이전트 워크플로우 테스트

REST Client 또는 curl을 사용하여 agent_cost에 JSON 형식의 요청을 보내 전체 시스템을 구동합니다.

요청 대상: agent_cost (포트 5001)
요청 내용 (JSON): 리소스 종류, 스펙, 수량은 **세미콜론 (;)**으로 구분합니다.
JSON

POST http://localhost:5001/calculate
Content-Type: application/json

{
    "text": "EC2: t2.micro, 2개; S3: standard, 100GB; RDS: db.t2.micro, 1개"
}


3. 결과 확인

요청이 성공적으로 처리되면, agent_cost는 계산 결과를 Redis에 발행합니다.
agent_report가 이 메시지를 구독하여 cost_report.xlsx 파일을 로컬의 ./output 폴더에 자동으로 생성합니다.


💡 개발 및 고도화 가이드

1. 동적 가격 데이터 통합 (Advanced)

문제: 현재 가격은 agent_cost/app.py에 하드코딩되어 있습니다.
해결책: requests와 BeautifulSoup 라이브러리를 사용하여 AWS의 온디맨드 요금 페이지와 같은 정적 HTML 페이지에서 최신 가격 데이터를 가져와 AWS_PRICES 딕셔너리를 업데이트하도록 코드를 수정할 수 있습니다.
2. 보고서 품질 향상

목표: 엑셀 보고서에 표 헤딩 외에 총 비용, 요청 정보, 계산 근거 등을 추가하여 실제 제안서 수준으로 만듭니다.
로직: agent_report/app.py에서 openpyxl을 사용하여 표 서식, 제목, 테두리 등을 추가하여 가독성을 높입니다.
