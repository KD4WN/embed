# -*- coding: utf-8 -*-
import numpy as np
import cv2

class Image:
    
    def __init__(self):
        self.image = None
        self.contourCenterX = 0
        self.MainContour = None
        
    def Process(self):
	#Hough Line Transform으로 직선 검출
        imgray = cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY) #Convert to Gray Scale
        ret, thresh = cv2.threshold(imgray,180,255,cv2.THRESH_BINARY_INV) #Get Threshold

        # Hough Line Transform - 직선 검출
        lines = cv2.HoughLinesP(thresh, rho=1, theta=np.pi/180, threshold=50,
                                minLineLength=40, maxLineGap=50)

        if lines is not None and len(lines) > 0:
            # 가장 아래쪽(y값이 큰) 라인 선택 - 가까운 라인에 집중
            bottom_line = max(lines, key=lambda line: (line[0][1] + line[0][3]) / 2)
            x1, y1, x2, y2 = bottom_line[0]

            # 라인의 중심점 계산
            line_center_x = (x1 + x2) // 2
            line_center_y = (y1 + y2) // 2
        
            self.height, self.width = self.image.shape[:2]
            self.middleX = int(self.width/2)
            self.middleY = int(self.height/2)

            # 라인 중심을 contourCenterX로 저장
            self.contourCenterX = line_center_x

            # 검출된 라인 그리기 (초록색)
            cv2.line(self.image, (x1, y1), (x2, y2), (0, 255, 0), 3)

            # 라인 중심점 표시 (흰색 원)
            cv2.circle(self.image, (line_center_x, line_center_y), 7, (255, 255, 255), -1)

            # 화면 중앙점 표시 (빨간 원)
            cv2.circle(self.image, (self.middleX, self.middleY), 3, (0, 0, 255), -1)

            # 편차 표시
            font = cv2.FONT_HERSHEY_SIMPLEX
            deviation = self.middleX - line_center_x
            cv2.putText(self.image, str(deviation), (line_center_x + 20, line_center_y),
                       font, 1, (200, 0, 200), 2, cv2.LINE_AA)

            return [line_center_x, line_center_y]

        # 라인을 찾지 못한 경우 기본값 반환
        height, width = self.image.shape[:2]
        return [width // 2, height // 2]

    def getContourCenter(self, contour):
        M = cv2.moments(contour)
        
        if M["m00"] == 0:
            return 0
        
        x = int(M["m10"]/M["m00"])
        y = int(M["m01"]/M["m00"])
        
        return [x,y]
        
    def getContourExtent(self, contour):
        area = cv2.contourArea(contour)
        x,y,w,h = cv2.boundingRect(contour)
        rect_area = w*h
        if rect_area > 0:
            return (float(area)/rect_area)
            
    def Aprox(self, a, b, error):
        if abs(a - b) < error:
            return True
        else:
            return False
            
    def correctMainContour(self, prev_cx):
        if abs(prev_cx-self.contourCenterX) > 5:
            for i in range(len(self.contours)):
                if self.getContourCenter(self.contours[i]) != 0:
                    tmp_cx = self.getContourCenter(self.contours[i])[0]
                    if self.Aprox(tmp_cx, prev_cx, 5) == True:
                        self.MainContour = self.contours[i]
                        if self.getContourCenter(self.MainContour) != 0:
                            self.contourCenterX = self.getContourCenter(self.MainContour)[0]
                            
