import pandas as pd
import pickle
from flask import jsonify
from shared_data import Instance

# 설문조사 데이터
# 1. 성별           # ['남자', '여자']
# 2. 연령대         # ['10대미만','10대', '20대', '30대', '40대', '50대', '60대', '70대', '80대']
# 3. 샴푸 사용빈도
# 4. 염색 주기
# 5. 제품 추천 동의

def average():
    with open( "average_df.pkl", "rb" ) as file:
        average_df = pickle.load(file)

    member_sum = 0
    for i in range(6):
        member_sum += int(Instance.result[i])

    # 사용자 입력값 파싱
    parsed_column_name = f"{Instance.member_age.replace('미만', '')}{Instance.member_gender.replace('자', '')}"
            
    # 사용자 입력에 해당하는 데이터 출력
    if parsed_column_name in average_df.columns:
    
        # B가 A보다 몇 퍼센트 높거나 낮은지 계산
        x = average_df[parsed_column_name][6]
        y = member_sum
        Instance.member_percentage = ((y - x) / abs(x)) * 100
        z = Instance.member_percentage
        
        # 결과 출력
        if z > 0:
            return jsonify({f"평균보다 {z:.2f}% 안좋습니다."})
        elif z < 0:
            return jsonify({f"평균보다 {(z*(-1)):.2f}% 좋습니다."})
        else:
            return jsonify({f"평균과 동일합니다."})  
    else:
        return jsonify({f"데이터를 찾을 수 없습니다."})




