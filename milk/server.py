from flask import Flask, Response, render_template, jsonify
from flask_socketio import SocketIO, emit
import cv2
import threading
from led_controller import LEDController
from camera_processor import CameraProcessor
from sensor import InfraredSensor, InfraredSensor2
from conve import ConvControl

# Flask 애플리케이션 초기화
app = Flask(__name__)
socketio = SocketIO(app)  # SocketIO 활성화

# 카메라, LED 제어, 적외선 센서, 컨베이어 객체 초기화
led_control = LEDController()       # LED 제어 객체
ir_sensor = InfraredSensor()      
ir_sensor2 = InfraredSensor2()  # 적외선 센서 객체
concont = ConvControl()             # 컨베이어 제어 객체

concont.stop() # 컨베이어 초기 상태(프로그램 시작시 정지)
camera_processor = CameraProcessor(led_control, ir_sensor,ir_sensor2, concont, socketio)  # 카메라 처리 객체 생성

# 상태 변수 (컨베이어 상태: 시작/정지)
conveyor_running = False
manual_stop = True  # 수동 정지 상태를 위한 플래그

# 카메라 자원 동기화를 위한 Lock 객체 생성
lock = threading.Lock()


# 비디오 피드를 위한 프레임 생성 함수
def generate_frames():
    global conveyor_running, manual_stop
    while True:
        with lock:
            success, frame = camera_processor.process_frame()
        if not success or frame is None:
            print("프레임 캡처 실패")
            break
        else:
            # manual_stop이 False일 때만 센서2 상태에 따라 컨베이어 제어
            if not manual_stop:
                if ir_sensor2.is_object_limits():
                    # 센서2가 감지되면 컨베이어 정지
                    concont.stop()
                    conveyor_running = False
                elif not conveyor_running:
                    # 센서2가 감지되지 않고 컨베이어가 멈춘 상태면 다시 시작
                    concont.forward(50)
                    conveyor_running = True
            else:
                concont.stop()  # manual_stop이 True일 때는 계속 멈춘 상태 유지
            
            # 프레임을 JPEG로 인코딩
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# 홈페이지 라우트
@app.route('/')
def index():
    return render_template('index.html')  # index.html 파일 렌더링

# 비디오 피드를 위한 라우트
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

# 컨베이어 시작 라우트
@app.route('/start', methods=['POST'])
def start_conveyor():
    global conveyor_running, manual_stop
    manual_stop = False
    conveyor_running = True
    concont.forward(50)  # 실제 컨베이어 제어 객체의 시작 함수 호출
    return jsonify({"status": "started"})

@app.route('/stop', methods=['POST'])
def stop_conveyor():
    global conveyor_running, manual_stop
    manual_stop = True
    conveyor_running = False
    concont.stop()  # 실제 컨베이어 제어 객체의 정지 함수 호출
    return jsonify({"status": "stopped"})


# Flask 서버와 비디오 스트리밍 실행
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=9000, debug=False)
