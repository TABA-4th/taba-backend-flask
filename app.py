# main.py
import io
import re
from flask import Flask, jsonify, request, render_template, make_response
from datetime import datetime
from pytz import timezone
from shared_data import Instance
from _0_validation import validate_image
from _1_upload import upload
from _2_predict import predict
from _3_db_save_image import db_save_image
from _4_percentile import percentile
from _5_db_save_survey import db_save_survey
from _6_product import product
from config import AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION, AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY
from flask_restx import Api, Resource, reqparse
from flask_cors import CORS

# 전역변수 값 설정 
Instance.member_id = 4                                               # 사용자 아이디, 임시값 4s
Instance.member_nickname = ''                                        # 사용자 닉네임 초기화
Instance.member_age = 20                                             # 사용자 나이, 임시값 20
Instance.member_gender = '남자'                                       # 사용자 성별, 임시값 남자
Instance.member_use_age_term = ''                                    # 사용자 샴푸 사용 빈도
Instance.member_perm_term = ''                                       # 사용자 파마 빈도
Instance.member_dye_term = ''                                        # 사용자 염색 빈도
Instance.member_recommend_or_not = ''                                # 사용자 제품 추천 여부
Instance.member_percentile = [-1, -1, -1, -1, -1, -1]                # 사용자 평균 대비 퍼센트 [합계, 미세각질, 피지과다, 모낭사이홍반,비듬, 탈모, 모낭홍반농포]

Instance.file_data = ''                                              # 사용자가 업로드한 이미지 데이터
Instance.image_url = ''                                              # S3에 저장한 이미지 URL

Instance.validation_model_path = 'init_thresh.pt'                    # 모델 경로 (사진 유효성 검사)
Instance.model_path0 = 'fine_crust.pt'                               # 모델 경로: 미세 각질
Instance.model_path1 = 'excess_sebum.pt'                             # 모델 경로: 피지 과다
Instance.model_path2 = 'erythema_between_hair_follicles.pt'          # 모델 경로: 모낭 사이 홍반
Instance.model_path3 = 'dandruff.pt'                                 # 모델 경로: 비듬
Instance.model_path4 = 'hair_loss.pt'                                # 모델 경로: 탈모
Instance.model_path5 = 'erythema_pustules.pt'                        # 모델 경로: 모낭 홍반 농포

Instance.class_names = [0, 1, 2, 3]                                  # 예측 클래스 이름(0,1,2,3)
Instance.result = [-1, -1, -1, -1, -1, -1]                           # 예측 결과

app = Flask(__name__)
# 최대 8MB로 파일 업로드 용량 제한
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 *1024
api = Api(app, version='0.1', title='타바 프로젝트 - AI 이미지 분석 개발서버 Flask API',
          description='', docs='타바 프로젝트 - AI 이미지 분석 개발서버 Flask API 제공', doc='/api-docs')
test_api = api.namespace('test', description='swagger test')
image_analysis_api = api.namespace('image', description='AI 모델로 사용자 이미지 분석 및 이미지 업로드')
survey_analysis_api = api.namespace('survey', description='사용자 설문 조사 분석 결과')
cors = CORS(app, resources={r"*": {"origins": "*"}})

@test_api.route('/')
class Test(Resource):
    def get(self):
        return jsonify({'msg': 'Response result message for test api.'})

@image_analysis_api.route('/')
class Image(Resource):
    def post(self):
        if 'file' not in request.files:
            return 'No file part', 400
        
        Instance.file_data = request.files['file'].read()
        if not Instance.file_data:
            return 'No file data', 400
        
        Instance.member_nickname = request.form['nickname']
        if not Instance.member_nickname:
            return 'No member_nickname data', 400
        
        # 사진 유효성 검사
        val = validate_image()
        if val == 0:
            return 'Invalid photo', 400

        # 현재 시간
        Instance.url_time = re.sub(r"[^0-9]", "", str(Instance.now))

        # S3에 이미지 업로드
        upload()

        # 이미지 예측
        for i in range(6):
            predict(i)

        # 동성, 동나이대 대비 백분위 계산, 전체 평균 반환
        averages = percentile()

        # 제품 타입 2가지
        product()

        # DB에 결과 데이터 저장
        db_save_image()
        
        return jsonify({'class': Instance.result, 'url': Instance.image_url, 'msg': 'Data saved to database successfully',
                            "dry": Instance.effect1 == "dry" or Instance.effect2 == "dry",
                            "greasy": Instance.effect1 == "greasy" or Instance.effect2 == "greasy",
                            "sensitive": Instance.effect1 == "sensitive" or Instance.effect2 == "sensitive",
                            "dermatitis": Instance.effect1 == "dermatitis" or Instance.effect2 == "dermatitis",
                            "neutral": Instance.effect1 == "neutral" or Instance.effect2 == "neutral",
                            "loss": Instance.effect1 == "loss" or Instance.effect2 == "loss",

                            'total': Instance.member_percentile[0], 
                            'FINE_DEAD_SKIN_CELLS': Instance.member_percentile[1],
                            'EXCESS_SEBUM': Instance.member_percentile[2], 
                            'ERYTHEMA_BETWEEN_HAIR_FOLLICLES': Instance.member_percentile[3], 
                            'DANDRUFF': Instance.member_percentile[4], 
                            'HAIR_LOSS': Instance.member_percentile[5],
                            'ERYTHEMA_PUSTULES': Instance.member_percentile[6], 

                            'avgClass': averages
                        })

@survey_analysis_api.route('/')
class Survey(Resource):
    def post(self):
        Instance.member_nickname = request.form['nickname']
        if not Instance.member_nickname:
            return 'No member_nickname data', 400
        
        Instance.member_gender = request.form['gender']
        if not Instance.member_gender:
            return 'No member_gender data', 400

        Instance.member_age = request.form['old']
        if not Instance.member_age:
            return 'No member_age data', 400

        Instance.member_use_age_term = request.form['use_age_term']
        if not Instance.member_use_age_term:
            return 'No member_use_age_term data', 400

        Instance.member_perm_term = request.form['perm_term']
        if not Instance.member_perm_term:
            return 'No member_perm_term data', 400

        Instance.member_dye_term = request.form['dye_term']
        if not Instance.member_dye_term:
            return 'No member_dye_term data', 400

        Instance.member_recommend_or_not = request.form['recommend_or_not']
        if not Instance.member_recommend_or_not:
            return 'No member_recommend_or_not data', 400
        
        Instance.member_reuse_image = request.form['reuse_image']
        if not Instance.member_reuse_image:
            return 'No reuse_image data', 400
        
        # 현재 시간
        Instance.now = datetime.now(timezone('Asia/Seoul'))
        Instance.url_time = re.sub(r"[^0-9]", "", str(Instance.now))
        
        # DB에 결과 데이터 저장
        # db_save_survey()

        return jsonify({'recommend_or_not' : Instance.member_recommend_or_not})
        
    
if __name__ == '__main__':
    app.run(debug=True)
