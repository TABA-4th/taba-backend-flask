# main.py
import io
import re
from flask import Flask, jsonify, request, render_template, make_response
from datetime import datetime
from shared_data import Instance
from _1_upload import upload
from _2_predict import predict
from _3_db_save_image import db_save_image
from _4_average import average
from _5_db_save_survey import db_save_survey
from config import AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION, AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY
from flask_restx import Api, Resource, reqparse
from flask_cors import CORS

# 전역변수 값 설정 
Instance.member_id = 4                  # 사용자 아이디, 임시값 
Instance.member_nickname = ''           # 사용자 닉네임 초기화
Instance.member_age = 20                # 사용자 나이, 임시값 20
Instance.member_gender = '남자'         # 사용자 성별, 임시값 남자
Instance.member_use_age_term = ''       # 사용자 샴푸 사용 빈도
Instance.member_perm_term = ''          # 사용자 파마 빈도
Instance.member_dye_term = ''           # 사용자 염색 빈도
Instance.member_recommend_or_not = ''   # 사용자 제품 추천 여부
Instance.member_percentage = 0          # 사용자 평균 대비 퍼센트

Instance.file_data = ''         # 사용자가 업로드한 이미지 데이터
Instance.image_url = ''         # S3에 저장한 이미지 URL

Instance.now = datetime.now()   # 현재 시간
Instance.url_time = re.sub(r"[^0-9]", "", str(Instance.now))
Instance.db_time = Instance.now.strftime('%Y-%m-%d %H:%M:%S')

Instance.model_path0 = 'fine_crust_0.6024.pt'                               # 모델 경로
Instance.model_path1 = 'excess_sebum_0.6612.pt'                             # 모델 경로
Instance.model_path2 = 'erythema_between_hair_follicles_0.7573.pt'          # 모델 경로
Instance.model_path3 = 'dandruff_0.7468.pt'                                 # 모델 경로
Instance.model_path4 = 'hair_loss_0.7712.pt'                                # 모델 경로
Instance.model_path5 = 'erythema_pustules_0.7234.pt'                        # 모델 경로
Instance.class_names = [0, 1, 2, 3]                                     # 예측 클래스 이름 (0,1,2,3)
Instance.result = [-1, -1, -1, -1, -1, -1]                              # 예측 결과

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
        
        # S3에 이미지 업로드
        upload()

        # 이미지 예측
        for i in range(6):
            predict(i)

        # DB에 결과 데이터 저장
        db_save_image()
        
        return jsonify({'class': Instance.result, 'url': Instance.image_url, 'msg': 'Data saved to database successfully'})

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
        
        # DB에 결과 데이터 저장
        db_save_survey()

        # 동성, 동나이대 평균 반환
        return average()

if __name__ == '__main__':
    app.run(debug=True)
