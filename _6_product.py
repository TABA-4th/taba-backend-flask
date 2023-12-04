# _6_product.py
import pyodbc
from flask import jsonify
import numpy as np
from shared_data import Instance

    # 건성: dry
    # 지성: greasy
    # 탈모성: loss
    # 중성: neutral
    # 민감성: sensitive
    # 피부염성: dermatitis

    # 미세각질  : 0.15
    # 피지과다  : 0.15
    # 모낭홍반  : 0.15
    # 비듬     : 0.15
    # 탈모     : 0.25
    # 홍반농포  : 0.15

    # 미세각질->지성,중성,건성
    # 피지과다->지성,피부염성
    # 모낭홍반->피부염성, 민감성
    # 비듬->지성,건성,중성
    # 탈모 -> 탈모성
    # 홍반농포->민감성,피부염성

# 1. 예측 결과 - 제품 기능: 코사인 유사도 축정
# 2. 상위 2개 제품 기능 추출
# 3. 알맞는 제품 추천 - db에서 가져오기

def product():


    effect = {'dry': 0, 'greasy': 1, 'loss': 2, 'neutral': 3, 'sensitive': 4, 'dermatitis': 5} # 제품 타입 딕셔너리
    w = [0.15, 0.15, 0.15, 0.15, 0.15, 0.15] # 각 지표 별 가중치: [미세각질, 피지과다, 모낭홍반, 비듬, 탈모, 홍반농포]
    type_score = [0, 0, 0, 0, 0, 0]    # 최종 제품 타입 점수: [건성, 지성, 탈모성, 중성, 민감성, 피부염성]

    for i in range(len(w)):
        w[i] = w[i] * Instance.result[i]

    # 행 - 사용자 지표: [미세각질, 피지과다, 모낭홍반, 비듬, 탈모, 홍반농포]
    # 열 - 제품 타입: [건성, 지성, 탈모성, 중성, 민감성, 피부염성]
    correspond = [[1, 1, 0, 1, 0, 0],
                [0, 1, 0, 0, 0, 1],
                [0, 0, 0, 0, 1, 1],
                [1, 1, 0, 1, 0, 0],
                [0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 1, 1]]

    for i in range(len(correspond)):
        correspond[i] = np.array(correspond[i]) * w[i]
        for j in range(len(correspond[i])):
            type_score[j] += correspond[i][j]

    # Find the indices of the top two elements in correspond_score
    top_indices = np.argsort(type_score)[-2:]

    # Assign the indices to rec1 and rec2
    rec1, rec2 = top_indices[0], top_indices[1]

    # Map the indices to the correspondesponding effect keys
    Instance.effect1 = effect.get(rec1)
    Instance.effect2 = effect.get(rec2)
