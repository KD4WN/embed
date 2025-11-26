# -*- coding: utf-8 -*-
import cv2
import numpy as np

class Image:
    def __init__(self):
        self.image = None
        self.centerPoint = (0, 0)

    def Process(self):
        """
        이미지를 처리하여 검은색 라인의 양쪽 경계를 찾고 중앙점을 계산
        Returns: 중앙점의 (x, y) 좌표
        """
        if self.image is None:
            return (0, 0)

        # BGR to HSV 변환
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)

        # 검은색 라인 검출을 위한 HSV 범위 설정
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 65])  # V값 65 이하 - 완전히 검은색만 인식

        # 마스크 생성
        mask = cv2.inRange(hsv, lower_black, upper_black)

        # 노이즈 제거 (morphology 연산)
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        height, width = mask.shape

        # 양쪽 경계 찾기
        left_edges = []
        right_edges = []

        # 각 행에서 검은색 픽셀의 양쪽 경계 찾기
        for y in range(height):
            row = mask[y, :]
            black_pixels = np.where(row > 0)[0]

            if len(black_pixels) > 0:
                left_edges.append(black_pixels[0])
                right_edges.append(black_pixels[-1])

        if len(left_edges) > 0 and len(right_edges) > 0:
            # 평균 왼쪽/오른쪽 경계
            avg_left = int(np.mean(left_edges))
            avg_right = int(np.mean(right_edges))

            # 중앙점 계산
            cx = (avg_left + avg_right) // 2
            cy = height // 2

            self.centerPoint = (cx, cy)

            # 시각화: 양쪽 경계선과 중앙선 그리기
            cv2.line(self.image, (avg_left, 0), (avg_left, height-1), (255, 0, 0), 2)  # 왼쪽 파란선
            cv2.line(self.image, (avg_right, 0), (avg_right, height-1), (0, 255, 0), 2)  # 오른쪽 초록선
            cv2.line(self.image, (cx, 0), (cx, height-1), (0, 0, 255), 2)  # 중앙 빨간선

            return (cx, cy)

        # 라인을 못 찾은 경우 이미지 중앙 반환
        self.centerPoint = (width // 2, height // 2)
        return self.centerPoint

    def GetCenterPoint(self):
        """무게중심 좌표 반환"""
        return self.centerPoint
