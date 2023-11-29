# main.py
import io
import re
from flask import Flask, jsonify, request, render_template, make_response
from datetime import datetime
from shared_data import Instance
from _1_upload import upload
from _2_predict import predict
from _3_db_save import db_save
from _4_average import average
from config import AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION, AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY
from flask_restx import Api, Resource, reqparse
from flask_cors import CORS

# 전역변수 값 설정 
Instance.member_id = 4          # 사용자 아이디, 임시값 
Instance.member_nickname = ''   # 사용자 닉네임 초기화
Instance.member_age = 20        # 사용자 나이, 임시값 20
Instance.member_gender = '남자'  # 사용자 성별, 임시값 남자
Instance.member_percentage = 0  # 사용자 평균 대비 퍼센트

Instance.file_data = ''         # 사용자가 업로드한 이미지 데이터
Instance.image_url = ''         # S3에 저장한 이미지 URL

Instance.now = datetime.now()   # 현재 시간
Instance.url_time = re.sub(r"[^0-9]", "", str(Instance.now))
Instance.db_time = Instance.now.strftime('%Y-%m-%d %H:%M:%S')

Instance.model_path = 'aram_fine_crust231109.pt'    # 모델 경로
Instance.class_names = [0, 1, 2, 3]                 # 예측 클래스 이름(0,1,2,3)
Instance.result = [-1, -1, -1, -1, -1, -1]          # 예측 결과

app = Flask(__name__)
# 최대 8MB로 파일 업로드 용량 제한
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 *1024
api = Api(app, version='0.1', title='타바 프로젝트 - AI 이미지 분석 개발서버 Flask API',
          description='', docs='타바 프로젝트 - AI 이미지 분석 개발서버 Flask API 제공', doc='/api-docs')
test_api = api.namespace('test', description='swagger test')
image_analysis_api = api.namespace('analysis', description='AI 모델로 사용자 이미지 분석 및 이미지 업로드')
cors = CORS(app, resources={r"*": {"origins": "*"}})

@test_api.route('/')
class Test(Resource):
    def get(self):
        return jsonify({'msg': 'Response result message for test api.'})

@image_analysis_api.route('/')
class analysis(Resource):
    def post(self):
        if 'file' not in request.files:
            return 'No file part', 400
        
        Instance.file_data = request.files['file'].read()
        if not Instance.file_data:
            return 'No file data', 400

        Instance.member_nickname = request.form['nickname']
        
        # S3에 이미지 업로드
        upload()

        # 이미지 예측
        predict()

        # DB에 결과 데이터 저장
        db_save()

        # 동성, 동나이대 평균 반환
        average()
        
        return jsonify({'class': Instance.result, 'url': Instance.image_url, 'msg': 'Data saved to database successfully'})

if __name__ == '__main__':
    app.run(debug=True)
