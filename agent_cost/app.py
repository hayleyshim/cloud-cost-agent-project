import redis
import json
from flask import Flask, request
import requests

app = Flask(__name__)
r = redis.Redis(host='redis', port=6379, db=0)

AWS_PRICES = {}

def get_aws_pricing():
    """공개 JSON 파일에서 AWS 가격을 가져와 딕셔너리를 채웁니다."""
    # 이 URL은 예시입니다. 직접 데이터를 만들어 GitHub에 올리고 사용해도 좋습니다.
    url = "https://raw.githubusercontent.com/hayleyshim/cloud-cost-agent-project/main/aws_prices.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        prices = response.json()
        
        AWS_PRICES.update(prices)
        print("Successfully fetched pricing data from JSON.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching pricing data: {e}")
        # 오류 발생 시 하드코딩된 예시 가격을 사용합니다.
        AWS_PRICES.update({
            "EC2": 15,
            "S3": 0.023,
            "RDS": 13,
            "ALB": 18
        })

get_aws_pricing()

@app.route('/calculate', methods=['POST'])
def calculate_cost():
    user_input = request.json.get('text', '').upper()
    items = {}

    if 'EC2' in user_input:
        items['EC2'] = user_input.count('EC2')
    if 'S3' in user_input:
        items['S3'] = user_input.count('S3')
    if 'RDS' in user_input:
        items['RDS'] = user_input.count('RDS')
    if 'ALB' in user_input:
        items['ALB'] = user_input.count('ALB')

    total_cost = 0
    cost_breakdown = {}
    for service, count in items.items():
        price = AWS_PRICES.get(service, 0)
        cost = price * count
        total_cost += cost
        cost_breakdown[service] = cost

    payload = json.dumps({
        'original_text': user_input,
        'total_cost': total_cost,
        'cost_breakdown': cost_breakdown
    })

    print("Publishing message to Redis...")
    r.publish('cost_channel', payload)
    return "Calculation sent to the report agent."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)