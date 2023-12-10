import pandas as pd
import pickle
import numpy as np

with open("average_df.pkl", "rb") as file:
    average_df = pickle.load(file)

print(average_df.head(20))


# 반복되는 순서 정의
desired_order = [0, 1, 2, 3, 6, 4, 5]

# gender와 age 값을 기준으로 데이터프레임을 그룹화한 후, value를 기준으로 행 전체를 정렬
sorted_dfs = []
for (age, gender), group_df in average_df.groupby(['Age', 'Gender']):
    repeated_order = desired_order * (len(group_df) // len(desired_order)) + desired_order[:len(group_df) % len(desired_order)]
    group_df['Value'] = repeated_order
    sorted_group_df = group_df.sort_values(by='Value')
    sorted_dfs.append(sorted_group_df)

# 수정된 데이터프레임을 다시 합치기
sorted_df = pd.concat(sorted_dfs)

# 인덱스 리셋
sorted_df = sorted_df.reset_index(drop=True)

# 결과 확인
print(sorted_df.head(20))


pickle.dump(sorted_df, open("average_df.pkl", "wb"))

with open("average_df.pkl", "rb") as file:
    average_df = pickle.load(file)

print(average_df.head(20))
