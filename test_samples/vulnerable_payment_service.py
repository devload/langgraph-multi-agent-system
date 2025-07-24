"""
결제 서비스 - 보안, 성능, 아키텍처 이슈가 있는 샘플 코드
테스트 목적으로 의도적으로 문제가 있는 코드를 포함합니다.
"""

import sqlite3
import hashlib
import time
from typing import Dict, List, Any

# 하드코딩된 시크릿 (보안 이슈)
API_KEY = "sk_live_1234567890abcdef"
DB_PASSWORD = "admin123"

class PaymentService:
    def __init__(self):
        # 데이터베이스 연결을 매번 새로 생성 (성능 이슈)
        self.db_path = "payments.db"
        
    def process_payment(self, user_id: str, amount: float, card_number: str):
        """결제 처리 - 여러 문제점 포함"""
        
        # SQL 인젝션 취약점
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE id = '{user_id}'"
        cursor.execute(query)
        user = cursor.fetchone()
        
        if not user:
            return {"error": "User not found"}
        
        # 약한 암호화 (MD5 사용)
        card_hash = hashlib.md5(card_number.encode()).hexdigest()
        
        # N+1 쿼리 문제
        transactions = []
        cursor.execute("SELECT id FROM transactions WHERE user_id = ?", (user_id,))
        transaction_ids = cursor.fetchall()
        
        for tid in transaction_ids:
            cursor.execute("SELECT * FROM transactions WHERE id = ?", (tid[0],))
            transactions.append(cursor.fetchone())
        
        # 메모리 누수 가능성 (연결을 닫지 않음)
        # conn.close()  # 주석 처리됨
        
        # 하나의 메서드가 너무 많은 책임 (SOLID 위반)
        # - 사용자 검증
        # - 카드 정보 암호화
        # - 트랜잭션 조회
        # - 결제 처리
        # - 이메일 발송
        # - 로깅
        
        # 에러 처리 없음
        payment_result = self._charge_card(card_hash, amount)
        self._send_email(user[1], f"Payment of ${amount} processed")
        self._log_transaction(user_id, amount, card_hash)
        
        return {"status": "success", "transaction_id": "txn_" + str(time.time())}
    
    def _charge_card(self, card_hash: str, amount: float):
        # 외부 API 호출 시뮬레이션
        time.sleep(0.1)  # 동기 블로킹 (성능 이슈)
        return True
    
    def _send_email(self, email: str, message: str):
        # 이메일 발송 로직
        print(f"Sending email to {email}: {message}")
    
    def _log_transaction(self, user_id: str, amount: float, card_hash: str):
        # 로깅 로직
        with open("transactions.log", "a") as f:
            f.write(f"{time.time()},{user_id},{amount},{card_hash}\n")
    
    def get_user_balance(self, user_id):
        """사용자 잔액 조회 - XSS 취약점"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 사용자 입력을 그대로 HTML에 포함 (XSS 취약점)
        html_response = f"<div>User {user_id} balance: $<span id='balance'>0</span></div>"
        
        # 비효율적인 집계 쿼리
        total = 0
        cursor.execute("SELECT amount FROM transactions WHERE user_id = ?", (user_id,))
        for row in cursor.fetchall():
            total += row[0]  # 메모리에서 합계 계산 (DB에서 SUM 사용해야 함)
        
        conn.close()
        return html_response.replace("0", str(total))

# 전역 변수 사용 (아키텍처 이슈)
payment_cache = {}

def validate_payment(payment_data: Dict[str, Any]) -> bool:
    """결제 유효성 검증 - 테스트하기 어려운 코드"""
    # 하드코딩된 외부 의존성
    import requests
    response = requests.post("https://api.payment-validator.com/validate", 
                           json=payment_data,
                           headers={"API-Key": API_KEY})
    
    # 복잡한 로직에 주석 없음
    if response.status_code == 200:
        data = response.json()
        score = data.get("risk_score", 100)
        flags = data.get("flags", [])
        
        if score > 70 or "high_risk" in flags:
            return False
        elif score > 50 and len(flags) > 2:
            return False
        else:
            return True
    
    return False

# 문서화되지 않은 복잡한 함수
def calculate_fee(amount, user_type, country, is_premium, has_discount, 
                  previous_transactions, current_time):
    base_fee = amount * 0.029
    
    if user_type == "business":
        base_fee *= 0.8
    elif user_type == "enterprise":
        base_fee *= 0.6
    
    if country in ["US", "CA", "UK"]:
        base_fee += 0.30
    else:
        base_fee += 0.50
    
    if is_premium and has_discount:
        base_fee *= 0.9
    
    if len(previous_transactions) > 100:
        base_fee *= 0.95
    
    # 시간대별 수수료 (문서화 안됨)
    hour = current_time.hour
    if hour >= 0 and hour < 6:
        base_fee *= 1.1
    elif hour >= 18 and hour < 24:
        base_fee *= 1.05
    
    return round(base_fee, 2)