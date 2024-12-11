import cv2
from google.cloud import vision
import numpy as np
from datetime import datetime


client = vision.ImageAnnotatorClient.from_service_account_json("/home/pi/webapps/CoinProject/json/subtle-ethos-440907-i2-373a74ea1a8d.json")

#이미지에서 텍스트 감지하는 함수        
def detect_text(frame):
    _, encoded_image = cv2.imencode('.jpg', frame) 
    content = encoded_image.tobytes() # 이미지를 바이트 데이터 content로 변환 
                                      # Vision API는 이미지 데이터를 바이트 형식으로 받아야 함
    image = vision.Image(content=content) # 이미지 생성
    image_context = vision.ImageContext(language_hints=["ko", "en"]) # 언어 힌트
    response = client.text_detection(image=image, image_context=image_context) # 감지 요청 보내기 
    texts = response.text_annotations

    detected_text = ""
    for text in texts:
        detected_text += text.description + "\n"
    return detected_text.strip()


def is_expired(date_text):
    
    try:
         # "MM.DD" 형식의 날짜를 현재 연도와 결합
        current_year = datetime.now().year
        # '.'을 '-'으로 변경하여 날짜 형식을 "YYYY-MM-DD"로 맞추기
        date_text = date_text.replace('.', '-')
        expiry_date_str = f"{current_year}-{date_text}"  # 예: "2024-11-14"
        
        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()  # 날짜만 비교
        current_date = datetime.now().date()  # 현재 날짜만 가져오기

        print(f"유통기한: {expiry_date}, 현재 날짜: {current_date}")  # current_date도 출력
        return current_date > expiry_date  # 날짜만 비교
    except ValueError as e:
        print(f"형식 오류로 유통기한 만료 처리: {date_text}, 오류: {e}")
        return True  # 형식이 맞지 않으면 유통기한 만료로 처리

