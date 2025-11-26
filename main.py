import time
import cv2
import numpy as np
import serial
from picamera2 import Picamera2

from Image import *
from Utils import *
from pyzbar.pyzbar import decode

# img size
WIDTH = 320
HEIGHT = 240

TOLERANCE = 145
TURN_MAX = 70   # 큰 회전 임계값 - 더 쉽게 큰 회전 발생
TURN_MID = 25   # 작은 회전 임계값 - 더 쉽게 작은 회전 발생

# cmd define
direction = 0

def in_tolerance(n):
    if n < -TOLERANCE:
        return False
    if n > TOLERANCE:
        return False
    return True

def get_cmd(y1, y2, y3, y4, y5, y6):
    print(f"y1: {y1}")
    print(f"y2: {y2}")
    print(f"y3: {y3}")
    print(f"y4: {y4}")
    print(f"y5: {y5}")
    print(f"y6: {y6}")
    num_valid = 6
    
    y1 -= WIDTH/2
    y2 -= WIDTH/2
    y3 -= WIDTH/2
    y4 -= WIDTH/2
    y5 -= WIDTH/2
    y6 -= WIDTH/2
    
    master_point = 0
    
    # +: right
    # -: left
    if in_tolerance(y1) == False:
        num_valid -= 1
        y1 = 0
    if in_tolerance(y2) == False:
        num_valid -= 1
        y2 = 0
    if in_tolerance(y3) == False:
        num_valid -= 1
        y3 = 0
    if in_tolerance(y4) == False:
        num_valid -= 1
        y4 = 0
    if in_tolerance(y5) == False:
        num_valid -= 1
        y5 = 0
    if in_tolerance(y6) == False:
        num_valid -= 1
        y6 = 0
    
    # 간단한 가중 평균 - 하단 슬라이스(가까운 곳)에 더 높은 가중치
    # y6이 가장 아래(카메라에 가까움), y1이 가장 위(카메라에서 멀음)
    # 하단 슬라이스를 더 신뢰함
    master_point = (y1 * 0.5 + y2 * 0.7 + y3 * 0.9 + y4 * 1.1 + y5 * 1.3 + y6 * 1.5) / 6.0

    # back
    if num_valid < 2:
        direction = 'B'		# 후진
    else:
        direction = 'G'		# 전진
        if master_point > TURN_MID and master_point < TURN_MAX :
            direction = 'r'	# 작은 우회전
        if master_point < -TURN_MID and master_point > -TURN_MAX :
            direction = 'l'	# 작은 좌회전
        if master_point >= TURN_MAX :
            direction = 'R'	# 큰 우회전
        if master_point <= -TURN_MAX :
            direction = 'L'	# 큰 좌회전

    cmd = ("%c\n" % (direction)).encode('ascii')

    # Direction display
    direction_map = {
        'G': 'GO (Forward)',
        'B': 'BACK',
        'r': 'Right-small',
        'R': 'Right-BIG',
        'l': 'Left-small',
        'L': 'Left-BIG'
    }
    direction_text = direction_map.get(direction, 'Unknown')

    print(">>> master_point:%d, Direction:%s" % (master_point, direction_text))

    ser.write(cmd)
    print("send")
    time.sleep(0.4)  # 아두이노 처리 시간 고려한 통신 주기 (초당 약 3회)

##################################################################################################

# setting arduino
ser = serial.Serial('/dev/ttyACM0', 9600)

print('start')
time.sleep(1)

Images = []
N_SLICES = 6

for _ in range(N_SLICES):
    Images.append(Image())

### setting camera
camera = Picamera2()
camera_config = camera.create_preview_configuration(
    main={"size": (320, 240)},
    controls={"FrameRate": 30,
             "Brightness": 0.2,  # 0-1.0 scale # 밝은 환경용으로 낮춤
             "Contrast": 1.8,    # 대비를 높여 라인 인식 향상
              "ExposureTime": 2500}  # 밝은 환경에서 노출 시간 감소
)
camera.configure(camera_config)
camera.start()

time.sleep(0.1)

try:
	i = 0
	while True:
		# Capture frame
		frame = camera.capture_array("main")
		frame = cv2.flip(frame, -1)  # 카메라 이미지를 180도 뒤집습니다 (카메라 거꾸로 설치됨)

		# QR 코드 인식
		codes = decode(frame)
		# 디코딩된 데이터가 있으면 출력
		if codes:
			for code in codes:
				print("QR 코드 데이터:", code.data.decode('utf-8'))
				qr_cmd = "S\n".encode('ascii')
				ser.write(qr_cmd)
				print(f"send {qr_cmd}")
				time.sleep(0.7)


		# Ensure BGR format for OpenCV compatibility
		if frame.shape[2] == 4:  # If RGBA
			frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
			
		image = cv2.resize(frame, (320, 240))

		# 이미지를 조각내서 윤곽선을 표시하게 무게중심 점을 얻는다
		Points = SlicePart(image, Images, N_SLICES)

		# 조각난 이미지를 한 개로 합친다
		fm = RepackImages(Images)

		i += 1
		print(i)
		get_cmd(Points[0][0], Points[1][0], Points[2][0], Points[3][0], Points[4][0], Points[5][0])

		# Display the resulting frame
		cv2.imshow('frame', fm)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			print("Stopped!")
			break

except KeyboardInterrupt:
    print("Program stopped by user")
finally:
    # Cleanup
    camera.stop()
    cv2.destroyAllWindows()
    ser.close()
