import pandas as pd
import pickle
from flask import jsonify
from shared_data import Instance
from scipy.stats import norm

# 설문조사 데이터
# 1. 성별          # ['남자', '여자']
# 2. 연령대         # ['0대','10대', '20대', '30대', '40대', '50대', '60대', '70대', '80대']

# average_df: [Age, Gender, Value, Average, Variance, Standard Deviation]

# 1. 사용자 입력값 파싱
# 2. 사용자 입력값에 해당하는 데이터 검색
# 3. 데이터를 바탕으로 합계, 1, 2, 3, 4, 5, 6번째 지표에 대한 백분율 값 계산 및 반환


# 데이터프레임에서 사용자 그룹의 해당 지표에 대한 평균, 표준편차 추출
def get_var(idx, member_group, avgs):
    average = member_group['Average'].values[idx]
    std_dev = member_group['Standard Deviation'].values[idx]
    if idx != 0:
        avgs[idx-1] = average

    return average, std_dev

# 백분위 계산하여 Instance.member_percentile에 저장
def percentile():
    # 데이터프레임 로드
    with open( "average_df.pkl", "rb" ) as file:
        average_df = pickle.load(file)

    raw_score = [-1, -1, -1, -1, -1, -1, -1]        # 원점수: [합계, 미세각질, 피지과다, 모낭사이홍반, 비듬, 탈모, 모낭홍반농포,]
    Instance.member_percentile = [-1, -1, -1, -1, -1, -1, -1]

    raw_score[0] = sum(map(int, Instance.result))   # 합계
    for i in range(6):                              # 1, 2, 3, 4, 5, 6번째 지표
        raw_score[i+1] = int(Instance.result[i])

    # 사용자 입력값 파싱
    age_dict = {'0대': 0, '10대': 10, '20대': 20, '30대': 30, '40대': 40, '50대': 50, '60대': 60, '70대': 70, '80대': 80}
    gender_dict = {'남자': 0, '여자': 1}
    age_group = age_dict.get(Instance.member_age)
    gender_group = gender_dict.get(Instance.member_gender)

    average = 0
    std_dev = 0

    avgs = [-1, -1, -1, -1, -1, -1]

    # 데이터프레임에서 사용자그룹 추출
    member_group = average_df[(average_df['Age'] == age_group) & (average_df['Gender'] == gender_group)]

    # 사용자 그룹의 해당 지표에 대한 평균, 표준편차 추출
    for i in range(7):
        average, std_dev = get_var(i, member_group, avgs)

        # 표준 편차가 0이거나 NaN이 아닌 경우에 백분위 계산
        if std_dev != 0 and not pd.isna(std_dev):
            z_score = (raw_score[i] - average) / std_dev
            result = norm.cdf(z_score) * 100
            Instance.member_percentile[i] = round(result, 1)
        # 표준편자가 0이거나 NaN인 경우
        else:
            Instance.member_percentile[i] = -1

    return avgs




