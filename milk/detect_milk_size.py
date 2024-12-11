import cv2

def detect_milk_size(cap):
    milk_width, milk_height = None, None  # 우유 크기 저장 변수 초기화

    # 고정된 ROI 좌표와 크기 설정
    roi_x, roi_y, roi_w, roi_h = 180, 25, 280, 390  # 원하는 ROI 좌표와 크기

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # ROI 영역 추출
        roi = frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
        
        # 그레이스케일 및 블러 처리
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)  # 그레이스케일 변환
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # 블러처리(가우시안 블러)
        edges = cv2.Canny(blurred, 50, 150)  # 캐니 엣지

        # 컨투어 찾기
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # 우유 크기 조건 확인
            if 180 < w < 300 and 200 < h < 400:
                milk_width, milk_height = w, h

                # 원본 프레임에서 표시할 위치로 좌표 조정
                cv2.putText(frame, f"Size: {w}px x {h}px", (roi_x + x, roi_y + y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # 크기 검출 완료, 크기 반환
                return True, milk_width, milk_height, frame

        # 결과 출력
        cv2.imshow("Milk Size Detection (Fixed ROI)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    return False, milk_width, milk_height, frame  # 검출 실패 시 False 반환
