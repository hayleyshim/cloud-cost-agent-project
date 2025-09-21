import redis
import json
from flask import Flask, request
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)
r = redis.Redis(host='redis', port=6379, db=0)

# 셀레늄 드라이버 초기화 함수
def get_driver():
    options = Options()
    options.add_argument('--headless') # 브라우저 창을 띄우지 않는 모드
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/5.0 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/5.0')

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# AWS 웹사이트에서 비용을 계산하는 함수
def calculate_aws_cost(services):
    driver = get_driver()
    driver.get('https://calculator.aws/#/estimate')
    time.sleep(5) # 페이지 로딩 대기

    total_cost = 0

    # EC2 비용 계산
    if 'EC2' in services:
        try:
            # EC2 서비스 추가 버튼 클릭
            driver.find_element(By.XPATH, "//button[contains(.,'Add a new estimate')]/following-sibling::div[1]//span[contains(.,'EC2')]").click()
            time.sleep(2)
            # 인스턴스 수 입력
            driver.find_element(By.XPATH, "//input[@data-testid='input-instance-count']").send_keys(str(services['EC2']))
            time.sleep(2)
        except Exception as e:
            print(f"EC2 input failed: {e}")

    # S3 비용 계산
    if 'S3' in services:
        try:
            # S3 서비스 추가
            driver.find_element(By.XPATH, "//button[contains(.,'Add a new estimate')]/following-sibling::div[1]//span[contains(.,'S3')]").click()
            time.sleep(2)
            # 스토리지 용량 입력 (테스트를 위해 100GB 고정)
            driver.find_element(By.XPATH, "//input[@data-testid='input-storage']").send_keys("100")
            time.sleep(2)
        except Exception as e:
            print(f"S3 input failed: {e}")

    # 총 비용 추출
    try:
        total_cost_element = driver.find_element(By.XPATH, "//span[@data-testid='label-total-monthly-cost']")
        total_cost = float(total_cost_element.text.replace('$', '').replace(',', ''))
        print(f"Scraped total cost: {total_cost}")
    except Exception as e:
        print(f"Could not scrape total cost: {e}")

    driver.quit()
    return total_cost, {} # 상세 내역은 복잡하므로 여기서는 총 비용만 반환

@app.route('/calculate', methods=['POST'])
def calculate_cost_from_web():
    user_input = request.json.get('text', '').upper()
    services = {}
    if 'EC2' in user_input:
        services['EC2'] = user_input.count('EC2')
    if 'S3' in user_input:
        services['S3'] = user_input.count('S3')

    total_cost, cost_breakdown = calculate_aws_cost(services)

    payload = json.dumps({
        'original_text': user_input,
        'total_cost': total_cost,
        'cost_breakdown': cost_breakdown
    })

    r.publish('cost_channel', payload)
    return "Calculation sent to the report agent."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)