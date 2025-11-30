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
        num_valid -= 1
        x1 = 0
    if in_tolerance(x2) == False:
        num_valid -= 1
        x2 = 0
    if in_tolerance(x3) == False:
        num_valid -= 1
        x3 = 0
    if in_tolerance(x4) == False:
        num_valid -= 1
        x4 = 0
    if in_tolerance(x5) == False:
        num_valid -= 1
        x5 = 0
    if in_tolerance(x6) == False:
        num_valid -= 1
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

try:
	i = 0
	while True:
		# Capture frame
		frame = camera.capture_array("main")
        
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
