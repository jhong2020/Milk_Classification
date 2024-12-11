import cv2
import numpy as np
from google.cloud import vision

try:
    client = vision.ImageAnnotatorClient.from_service_account_json("/home/pi/webapps/CoinProject/json/subtle-ethos-440907-i2-373a74ea1a8d.json")
except FileNotFoundError as e:
    print("Service account JSON 파일을 찾을 수 없습니다:", e)
    exit(1)
except Exception as e:
    print("Google Vision API 클라이언트를 초기화할 수 없습니다:", e)
    exit(1)

def detect_objects(frame):
    try:
        # 프레임을 JPEG 형식으로 인코딩
        _, encoded_image = cv2.imencode('.jpg', frame)
        content = encoded_image.tobytes()

        # 이미지 인식 요청
        image = vision.Image(content=content)
        response = client.object_localization(image=image)

        # 물체 인식 결과
        objects = response.localized_object_annotations
        return objects
    except Exception as e:
        print("Google Vision API 요청에 실패했습니다:", e)
        return []

def get_color_name_from_binary(roi):
    try:
        # HSV 색상공간으로 변환
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # 색상 범위에 따른 이진화 마스크 생성
        color_ranges = {
            "Red": [(0, 100, 100), (10, 255, 255)],
            "Yellow": [(20, 120, 120), (30, 255, 255)],
            "Green": [(30, 40, 40), (90, 255, 255)],  # 넓은 범위의 Green
            "Green": [(35, 20, 20), (90, 180, 120)],  # 어두운 공간에서 Green 검출
            "Chocolate": [(5, 40, 40), (30, 150, 150)],  # 어두운 공간에서 초코색 검출
            "Brown": [(10, 50, 50), (30, 255, 150)]  # 갈색 (커피색) 추가
        }

        # 각 색상 범위에 대해 마스크 생성 후 비중 확인
        max_area = 0
        dominant_color = "Unknown"

        for color_name, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            area = cv2.countNonZero(mask)

            if area > max_area:
                max_area = area
                dominant_color = color_name

        return dominant_color
    except cv2.error as e:
        print("색상 변환에 실패했습니다:", e)
        return "Error"
    

    