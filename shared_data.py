# shared_data.py
# 전역변수 선언
class SharedData:
    def __init__(self):
        self.member_id = None           # 사용자 ID
        self.member_nickname = None     # 사용자 닉네임
        self.member_age = None          # 사용자 나이
        self.member_gender = None       # 사용자 성별
        self.member_percentage = None   # 사용자 평균 대비 퍼센트

        self.file_data = None           # 사용자가 업로드한 이미지 데이터
        self.image_url = None           # S3에 저장한 이미지 URL
        
        self.now = None                 # 현재 시간
        self.url_time = None            # url 이름에 사용할 시간
        self.db_time = None             # DB에 저장할 시간

        self.model_path0 = None         # 모델 경로 (미세 각질)
        self.model_path1 = None         # 모델 경로 (피지 과다)
        self.model_path2 = None         # 모델 경로 (모낭 사이 홍반)
        self.model_path3 = None         # 모델 경로 (비듬)
        self.model_path4 = None         # 모델 경로 (탈모)
        self.model_path5 = None         # 모델 경로 (모낭 홍반 농포)
        self.class_names = None         # 예측 클래스 이름(0,1,2,3)
        self.result = None              # 예측 결과

Instance = SharedData()