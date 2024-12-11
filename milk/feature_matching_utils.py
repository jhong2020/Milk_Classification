# feature_matching_utils.py
import cv2
import numpy as np

# ORB 객체 생성
orb = cv2.ORB_create()

# 특징점 및 디스크립터 추출 함수
def extract_features(img):
    keypoints, descriptors = orb.detectAndCompute(img, None)
    return keypoints, descriptors

# 두 이미지의 디스크립터를 매칭하는 함수
def match_features(descriptors1, descriptors2):
    if descriptors1 is None or descriptors2 is None:
        print("디스크립터가 없습니다.")
        return []

    descriptors1 = np.uint8(descriptors1)
    descriptors2 = np.uint8(descriptors2)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    return matches

# 이미지 비교 함수
def compare_images(img_template, frame, roi_coords=None):
    keypoints_template, descriptors_template = extract_features(img_template)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if roi_coords:
        x, y, w, h = roi_coords
        roi_frame = frame_gray[y:y+h, x:x+w]
    else:
        roi_frame = frame_gray

    keypoints_frame, descriptors_frame = extract_features(roi_frame)
    matches = match_features(descriptors_template, descriptors_frame)
    matches = sorted(matches, key=lambda x: x.distance)
    num_good_matches = 50
    good_matches = matches[:min(num_good_matches, len(matches))]

    if good_matches:
        sum_distances = sum([match.distance for match in good_matches])
        avg_distance = sum_distances / len(good_matches)
        max_distance = 100.0
        match_ratio = (1.0 - avg_distance / max_distance) * 100.0
        match_ratio = max(0.0, min(100.0, match_ratio))

        print(f"일치율: {match_ratio}%")
        return match_ratio > 70
    else:
        print("매칭된 특징점이 없습니다.")
    return False
