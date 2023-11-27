# shared_data.py
# 전역변수 선언
class SharedData:
    def __init__(self):
        self.now = None
        self.member_id = None
        self.url_time = None
        self.db_time = None
        self.model_path = None
        self.class_names = None
        self.result = None
        self.image_url = None
        self.file_data = None

Instance = SharedData()