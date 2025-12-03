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
TURN_MAX = 190
TURN_MID = 90

# cmd define
direction = 0

def in_tolerance(n):
    if n < -TOLERANCE:
        return False
    if n > TOLERANCE:
        return False
    return True

def get_cmd(x1, x2, x3, x4, x5, x6):
    print(f"x1: {x1}")
    print(f"x2: {x2}")
    print(f"x3: {x3}")
    print(f"x4: {x4}")
    print(f"x5: {x5}")
    print(f"x6: {x6}")
    num_valid = 6

    # 각 구역에서 선이 실제로 감지되었는지 확인
    if x1 == 0:
        num_valid -= 1
    if x2 == 0:
        num_valid -= 1
    if x3 == 0:
        num_valid -= 1
    if x4 == 0:
        num_valid -= 1
    if x5 == 0:
        num_valid -= 1
    if x6 == 0:
        num_valid -= 1

    x1 -= WIDTH/2
    x2 -= WIDTH/2
    x3 -= WIDTH/2
    x4 -= WIDTH/2
    x5 -= WIDTH/2
    x6 -= WIDTH/2

    master_point = 0

    # +: right
    # -: left
    if in_tolerance(x1) == False:
        x1 = 0
    if in_tolerance(x2) == False:
        x2 = 0
    if in_tolerance(x3) == False:
        x3 = 0
    if in_tolerance(x4) == False:
        x4 = 0
    if in_tolerance(x5) == False:
        x5 = 0
    if in_tolerance(x6) == False:
        x6 = 0

    master_point = 2.65 * (x1 * 0.7 + x2 * 0.85 + x3 + x4 * 1.1 + x5 * 1.2 + x6 * 1.35) / (num_valid + 0.1)

    master_point += x1 * 0.5
    master_point += x2 * 0.4
    master_point += x3 * 0.3
    master_point -= x4 * 0.4
    master_point -= x5 * 0.5
    master_point -= x6 * 0.6

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

    print(">>> master_point:%d, cmd:%s" % (master_point, cmd))
    
    ser.write(cmd)
    print("send")
    time.sleep(0.5)

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
             "Brightness": 0.4,  # 0-1.0 scale # 낮을수록 밝은 환경에서 좋음
             "Contrast": 1.4,    # 2x default contrast
              "ExposureTime": 4000}  # 100ms exposure time # 노출 시간: 밝은 환경에서는 낮아야함
)
camera.configure(camera_config)
camera.start()

time.sleep(0.1)

# QR 코드 인식 쿨다운
last_qr_time = 0
QR_COOLDOWN = 5.0  # QR 인식 후 5초 동안 재인식 방지

try:
	i = 0
	while True:
		# Capture frame
		frame = camera.capture_array("main")

		# QR 코드 인식을 위한 이미지 전처리
		# 밝은 환경에서 QR 인식을 개선하기 위해 전처리 적용
		qr_frame = frame.copy()
		if qr_frame.shape[2] == 4:  # If RGBA
			qr_frame = cv2.cvtColor(qr_frame, cv2.COLOR_RGBA2BGR)

		# 그레이스케일 변환
		gray_qr = cv2.cvtColor(qr_frame, cv2.COLOR_BGR2GRAY)

		# 밝기 조정 (gamma correction으로 밝은 부분 억제)
		gamma = 0.6  # 1.0보다 작으면 어두워짐
		inv_gamma = 1.0 / gamma
		table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
		gray_qr = cv2.LUT(gray_qr, table)

		# Adaptive thresholding으로 QR 코드 강조
		# 밝은 환경에서도 QR 코드의 경계를 명확하게 만듦
		qr_enhanced = cv2.adaptiveThreshold(
			gray_qr, 255,
			cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
			cv2.THRESH_BINARY,
			11, 2
		)

		# QR 코드 인식
		codes = decode(qr_enhanced)
		current_time = time.time()

		# 디코딩된 데이터가 있으면 출력
		if codes and (current_time - last_qr_time) > QR_COOLDOWN:
			for code in codes:
				try:
					print("QR detected:", code.data.decode('utf-8'))
				except:
					print("QR detected")
				qr_cmd = "S\n".encode('ascii')
				ser.write(qr_cmd)
				print("send stop command")
				last_qr_time = current_time
				time.sleep(3.0)  # 3초 동안 정지
			continue  # 라인 트래킹 건너뛰기


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
		
		try :
		    cv2.imshow('frame', fm)
		    
		    if cv2.waitKey(1) & 0xFF == ord('q') : break
			
		except cv2.error:
		    pass


		
		#cv2.imshow('frame', fm)

		#if cv2.waitKey(1) & 0xFF == ord('q'):
		#	print("Stopped!")
		#	break
		

except KeyboardInterrupt:
    print("Program stopped by user")
finally:
    # Cleanup
    camera.stop()
    cv2.destroyAllWindows()
    ser.close()
