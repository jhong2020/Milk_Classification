import cv2
import threading
from text_detection_utils import detect_text, is_expired
from detect_milk_size import detect_milk_size
from detect_color import detect_objects, get_color_name_from_binary
from database_utils import connect_to_database, save_milk_info, fetch_milk_info
from feature_matching_utils import compare_images
import os
import time
import numpy as np

# 환경 변수 설정 (offscreen 모드로 Qt 사용)
os.environ["QT_QPA_PLATFORM"] = "offscreen"

class CameraProcessor:
    def __init__(self, led_controller, sensor, sensor2, conver, socketio):
        self.led_controller = led_controller
        self.sensor = sensor
        self.sensor2 = sensor2
        self.conver = conver
        self.socketio = socketio

        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.lock = threading.Lock()
        self.stage = 1
        self.count = 1 
        self.force_sensor_off = False
        self.img_template = None

        # 데이터베이스 연결
        self.connection = connect_to_database()

    def log_to_console(self, message):
        """웹 콘솔로 로그 메시지 전송."""
        print(message)  # 서버 콘솔에 출력
        self.socketio.emit('console_log', {'message': message})  # 웹 콘솔에 전송
        

    def process_frame(self):
        with self.lock:
            ret, frame = self.cap.read()
            if not ret:
                return False, None
    
        final_log = ""  # 마지막에 출력할 로그 메시지를 저장할 변수
        sensor_detected = not self.force_sensor_off and self.sensor.is_object_detected()
        sensor_limited = self.sensor2.is_object_limits()

        if not sensor_detected:
            self.conver.forward(50)  # 객체 미감지 시 컨베이어 작동
        else:
            self.conver.stop()

            
            match self.stage:
                case 1:   #텍스트 검출
                    detected_text = detect_text(frame)
                    if "서울우유" in detected_text:
                        final_log = "Stage 1: '서울우유' 텍스트가 감지되었습니다."
                        self.log_to_console(final_log)
                        self.stage = 2
                    else:
                        final_log = "Stage 1: '서울우유' 텍스트가 감지되지 않았습니다."
                        self.log_to_console(final_log)
                        self.stage = 6 
                        return True, frame

                case 2:   #유통기한 검사
                    detected_text = detect_text(frame)
                    date_text = ""
                    for line in detected_text.splitlines():
                        if '.' in line and len(line.split('.')) == 2 and line.replace('.', '').isdigit():
                            date_text = line
                            break

                    final_log = f"Extracted Expiration Date: {date_text}"

                    if not date_text:
                       final_log = "Stage 2: 유통기한 없음."
                       self.log_to_console(final_log)
                                     
                    elif is_expired(date_text):
                       final_log = f"Stage 2: 유통기한 만료. ({date_text})"
                       print(final_log)  
                       self.log_to_console(final_log)  # 웹 콘솔에 출력
                       self.stage = 6
                       return True, frame
                    
                    else:
                        final_log = f"Stage 2: 유통기한 유효 ({date_text})"
                        self.stage = 3

                case 3:  # 사이즈 검출
                    detected, milk_width, milk_height, frame = detect_milk_size(self.cap)
                    if detected:
                        final_log = f"Stage 3: 우유 사이즈 검출 - Width = {milk_width}px, Height = {milk_height}px"
                        self.milk_width = milk_width  
                        self.milk_height = milk_height
                        self.stage = 4
                    else:
                        final_log = "Stage 3: 우유 사이즈 검출 실패"

                case 4: # 컬러 검출
                    objects = detect_objects(frame)
                    if not objects:
                        final_log = "Stage 4: 감지된 객체 없음"
                    for obj in objects:
                        try:
                            x = int(obj.bounding_poly.normalized_vertices[0].x * frame.shape[1])
                            y = int(obj.bounding_poly.normalized_vertices[0].y * frame.shape[0])
                            w = int((obj.bounding_poly.normalized_vertices[2].x - obj.bounding_poly.normalized_vertices[0].x) * frame.shape[1])
                            h = int((obj.bounding_poly.normalized_vertices[2].y - obj.bounding_poly.normalized_vertices[0].y) * frame.shape[0])

                            roi = frame[y:y+h, x:x+w]
                            dominant_color = get_color_name_from_binary(roi)

                            label = f"{dominant_color}"
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                            final_log = f"Stage 4: Detected color {dominant_color}"
                            self.dominant_color = dominant_color   
                        except Exception as e:
                            final_log = f"Error calculating object boundaries: {e}"
                            
                    self.stage = 5

                case 5: # 일치율 
                    try:
                        # Fetch all milk images and text from the database
                        cursor = self.connection.cursor(dictionary=True)
                        cursor.execute("SELECT id, text, image, color FROM Milks_Info")  # 'text' 필드 추가
                        rows = cursor.fetchall()

                        match_found = False
                        for row in rows:
                            db_image_blob = row['image']
                            db_color = row['color'].lower()
                            np_arr = np.frombuffer(db_image_blob, np.uint8)
                            db_image = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)

                            # Compare current frame with the database image
                            is_matched = compare_images(db_image, frame)
                            if is_matched and db_color == self.dominant_color.lower():
                                final_log = f"Stage 5: 매칭된 데이터 - {row['text']}"  # 'text' 필드 사용
                                match_found = True
                                break

                        # 색상 기반 텍스트 매핑
                        color_text_map = {
                            "red": "서울우유 딸기",
                            "green": "서울우유 흰",
                            "brown": "서울우유 커피",
                            "chocolate": "서울우유 초코",
                            "yellow": "서울우유 바나나"
                        }
                        save_text = color_text_map.get(self.dominant_color.lower(), "서울우유")

                        # Save current frame to database regardless of match
                        image_blob = cv2.imencode('.jpg', frame)[1].tobytes()
                        save_milk_info(
                            self.connection,
                            text=save_text,
                            color=self.dominant_color,
                            width=self.milk_width,
                            height=self.milk_height,
                            image_blob=image_blob
                        )

                        if match_found:
                            final_log += " - 기존 데이터와 매칭됨."
                        else:
                            final_log += f" - 새로운 데이터로 저장됨: {save_text}"

                        self.stage = 6
                    except Exception as e:
                        final_log = f"Stage 5: Error during database comparison or saving - {e}"


                case 6:  #stage1로 가고 적외선센서 초기화
                    final_log = "Stage 6 완료 후 Stage 1로 초기화"
                    self.stage = 1
                    self.count += 1
                    self.force_sensor_off = True
                    self.conver.forward(50)
                    time.sleep(2)
                    self.conver.stop()
                    self.force_sensor_off = False

        if sensor_limited:
            self.conver.stop()

        # 최종 로그 메시지 출력
        if final_log:
            self.log_to_console(final_log)

        return True, frame

    def release(self):
        self.cap.release()
