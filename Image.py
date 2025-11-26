# -*- coding: utf-8 -*-
import cv2
import numpy as np

class Image:
    def __init__(self):
        self.image = None
        self.centerPoint = (0, 0)

    def Process(self):
        """
        이미지를 처리하여 검은색 라인을 찾고 무게중심을 계산
        Returns: 무게중심의 x좌표 (또는 (x, y) 튜플)
        """
        if self.image is None:
            return (0, 0)

        # BGR to HSV 변환
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

        # 검은색 라인 검출을 위한 HSV 범위 설정
        # 검은색: 낮은 명도(V)를 가진 모든 색상
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 65])  # V값 65 이하 - 완전히 검은색만 인식

        # 마스크 생성
        mask = cv2.inRange(hsv, lower_black, upper_black)

        # 노이즈 제거 (morphology 연산)
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # 윤곽선 찾기
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            # 가장 큰 윤곽선 찾기 (라인으로 가정)
            largest_contour = max(contours, key=cv2.contourArea)

            # 윤곽선 그리기 (초록색)
            cv2.drawContours(self.image, [largest_contour], -1, (0, 255, 0), 2)

            # 모멘트를 이용한 무게중심 계산
            M = cv2.moments(largest_contour)

            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                self.centerPoint = (cx, cy)

                # 무게중심에 원 그리기 (빨간색)
                cv2.circle(self.image, (cx, cy), 5, (0, 0, 255), -1)

                return (cx, cy)

        # 라인을 찾지 못한 경우 이미지 중앙 반환
        height, width = self.image.shape[:2]
        self.centerPoint = (width // 2, height // 2)
        return self.centerPoint

    def GetCenterPoint(self):
        """무게중심 좌표 반환"""
        return self.centerPoint
