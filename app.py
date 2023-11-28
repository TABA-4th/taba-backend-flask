# main.py
import io
import re
from flask import Flask, jsonify, request
from datetime import datetime
from shared_data import Instance
from _1_upload import upload
from _2_predict import predict
from _3_db_save import db_save
from config import AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION, AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY
from flask_restx import Api, Resource, reqparse

# 전역변수 값
Instance.now = datetime.now()
Instance.member_id = 4  # 임시로 4로 설정
Instance.url_time = re.sub(r"[^0-9]", "", str(Instance.now))
Instance.db_time = Instance.now.strftime('%Y-%m-%d %H:%M:%S')
Instance.model_path = 'aram_fine_crust231109.pt'
Instance.class_names = [0, 1, 2, 3]
Instance.result = [-1, -1, -1, -1, -1, -1]
Instance.image_url = ''
Instance.file_data = ''

app = Flask(__name__)
api = Api(app, version='0.1', title='타바 프로젝트 - AI 이미지 분석 개발서버 Flask API',
          description='', docs='타바 프로젝트 - AI 이미지 분석 개발서버 Flask API 제공', doc='/api-docs')
test_api = api.namespace('test', description='swagger test')
image_analysis_api = api.namespace('analysis', description='AI 모델로 사용자 이미지 분석 및 이미지 업로드')

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
        
        # S3에 이미지 업로드
        upload()

        # 이미지 예측
        predict()

        # DB에 결과 데이터 저장
        db_save()
        
        return jsonify({'class': Instance.result, 'url': Instance.image_url, 'msg': 'Data saved to database successfully'})


if __name__ == '__main__':
    app.run(debug=True)
