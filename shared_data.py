# shared_data.py
# 전역변수 선언
class SharedData:
    def __init__(self):
        self.member_id = None               # 사용자 ID
        self.member_nickname = None         # 사용자 닉네임
        self.member_age = None              # 사용자 나이
        self.member_gender = None           # 사용자 성별
        self.member_use_age_term = None     # 사용자 샴푸 사용 빈도
        self.member_perm_term = None        # 사용자 파마 빈도
        self.member_dye_term = None         # 사용자 염색 빈도
        self.member_recommend_or_not = None # 사용자 제품 추천 여부
        self.member_percentile = None       # 사용자 평균 대비 퍼센트

        self.file_data = None               # 사용자가 업로드한 이미지 데이터
        self.image_url = None               # S3에 저장한 이미지 URL
            
        self.now = None                     # 현재 시간
        self.url_time = None                # url 이름에 사용할 시간
        self.db_time = None                 # DB에 저장할 시간

#         self.validation_model_path = None   # 모델 경로 (사진 유효성 검사)
        self.model_path0 = None             # 모델 경로 (미세 각질)
        self.model_path1 = None             # 모델 경로 (피지 과다)
        self.model_path2 = None             # 모델 경로 (모낭 사이 홍반)
        self.model_path3 = None             # 모델 경로 (모낭 홍반 농포)
        self.model_path4 = None             # 모델 경로 (비듬)
        self.model_path5 = None             # 모델 경로 (탈모)

        self.class_names = None             # 예측 클래스 이름(0,1,2,3)
        self.result = [-1, -1, -1, -1, -1, -1]  # 예측 결과: [미세각질, 피지과다, 모낭사이홍반, 모낭홍반농포, 비듬, 탈모]

        self.effect1 = None                 # 제품타입1
        self.effect2 = None                 # 제품타입2

Instance = SharedData()