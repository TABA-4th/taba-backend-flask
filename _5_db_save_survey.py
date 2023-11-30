# _3_db_save_survey.py
import pyodbc
from datetime import datetime
from config import user, passwd
from shared_data import Instance

def db_save_survey():
    try:
        survey_id = int(Instance.url_time)

        conn = pyodbc.connect('DSN=tibero;UID='+user+';PWD='+passwd)
        conn.setdecoding(pyodbc.SQL_CHAR, encoding='euc-kr')
        conn.setdecoding(pyodbc.SQL_WCHAR, encoding='euc-kr')
        conn.setdecoding(pyodbc.SQL_WMETADATA, encoding='euc-kr')
        conn.setencoding(encoding='utf-8')
        curs = conn.cursor()

        # 현재 저장된 최대 survey_id 가져오기
        max_survey_id_query = "SELECT MAX(SURVEY_ID) FROM member_survey;"
        curs.execute(max_survey_id_query)
        max_survey_id = curs.fetchone()[0]

        # 사용자 닉네임에 해당하는 member_id 찾기
        curs.execute("""SELECT MEMBER_ID 
                                  FROM MEMBER 
                                  WHERE NICKNAME = ? ;""", Instance.member_nickname)
        Instance.member_id = curs.fetchone()[0]
    
        # result_id 1 증가
        survey_id = max_survey_id + 1 if max_survey_id is not None else 1

        # 사용자 ID, 설문 조사 결과, 날짜를 저장하는 쿼리
        sql = "INSERT INTO member_survey (SURVEY_ID, MEMBER_ID, DIAGNOSIS_DATE, GENDER, OLD, USE_AGE_TERM, PERM_TERM, DYE_TERM, RECOMMEND_OR_NOT) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        values = (survey_id, Instance.member_id, Instance.db_time, Instance.result[0], Instance.result[1], Instance.result[2], Instance.result[3], Instance.result[4], Instance.result[5])
        curs.execute(sql, values)
    
        conn.commit()
        conn.close()

    except Exception as ex:
        print(ex)