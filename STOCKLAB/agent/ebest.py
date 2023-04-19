import win32com.client
import pythoncom
import configparser
import time

class XASession:
    #로그인 상태를 확인하기 위한 클래스변수
    login_state = 0

    def OnLogin(self, code, msg):
        """
        로그인 시도 후 호출되는 이벤트.
        code가 0000이면 로그인 성공
        """
        if code == "0000":
            print(code, msg)
            XASession.login_state = 1
        else:
            print(code, msg)

    def OnDisconnect(self):
        """
        서버와 연결이 끊어지면 발생하는 이벤트
        """
        print("Session disconntected")
        XASession.login_state = 0

class EBest:
    QUERY_LIMIT_10MIN = 200
    LIMIT_SECONDS = 600 #10min
    """
        config.ini 파일을 로드해 사용자, 서버정보 저장
        query_cnt는 10분당 200개 TR 수행을 관리하기 위한 리스트
        xa_session_client는 XASession 객체
        :param mode:str - 모의서버는 DEMO 실서버는 PROD로 구분
    """
    def __init__(self, mode = None):
        if mode not in ["PROD", "DEMO"]:
            raise Exception("Need to run_mode[PROD, DEMO]")
        run_mode = "EBEST_" + mode
        config = configparser.ConfigParser()
        config.read('conf/config.ini')
        self.user = config[run_mode]['user']
        self.passwd = config[run_mode]['password']
        self.cert_passwd = config[run_mode]['cert_passwd']
        self.host = config[run_mode]['host']
        self.port = config[run_mode]['port']
        self.account = config[run_mode]['account']

        self.xa_session_client = win32com.client.DispatchWithEvents("XA_Session.XASession", XASession)

        self.query_cnt = []

    def login(self):
        self.xa_session_client.ConnectServer(self.host, self.port)
        self.xa_session_client.Login(self.user, self.passwd, self.cert_passwd, 0, 0)
        while XASession.login_state == 0:
            pythoncom.PumpWaitingMessages()

    def logout(self):
        XASession.login_state = 0
        self.xa_session_client.DisconnectServer()

    def _execute_query(self, res, in_block_name, out_block_name, *out_fields, **set_fields):
        """TR코드를 실행하기 위한 메소드입니다.
        :param res:str 리소스명(TR)
        :param in_block_name:str 인블록명
        :param out_blcok_name:str 아웃블록명
        :param out_params:list 출력필드 리스트
        :param in_params:dict 인블록에 설정할 필드 딕셔너리
        :return result:list 결과를 list에 담아 반환 
        """
        time.sleep(1)
        print("current query cnt:", len(self.query_cnt))
        print(res, in_block_name, out_block_name)
        while len(self.query_cnt) >= EBest.QUERY_LIMIT_10MIN:
            time.sleep(1)
            print("waiting for execute query... current query cnt:", len(self.query_cnt))
            self.query_cnt = list(filter(lambda x: (datetime.today() - x).total_seconds() < EBest.LIMIT_SECONDS, self.query_cnt))

        xa_query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQuery)
        xa_query.LoadFromResFile(XAQuery.RES_PATH + res+".res")

        #in_block_name 셋팅
        for key, value in set_fields.items():
            xa_query.SetFieldData(in_block_name, key, 0, value)
        errorCode = xa_query.Request(0)

        #요청 후 대기
        waiting_cnt = 0
        while xa_query.tr_run_state == 0:
            waiting_cnt +=1
            if waiting_cnt % 1000000 == 0 :
                print("Waiting....", self.xa_session_client.GetLastError())
            pythoncom.PumpWaitingMessages()

        #결과블럭 
        result = []
        count = xa_query.GetBlockCount(out_block_name)

        for i in range(count):
            item = {}
            for field in out_fields:
                value = xa_query.GetFieldData(out_block_name, field, i)
                item[field] = value
            result.append(item)

        """
        print("IsNext?", xa_query.IsNext)
        while xa_query.IsNext == True:
            time.sleep(1)
            errorCode = xa_query.Request(1)
            print("errorCode", errorCode)
            if errorCode < 0:
                break
            count = xa_query.GetBlockCount(out_block_name)
            print("count", count)
            if count == 0:
                break
            for i in range(count):
                item = {}
                for field in out_fields:
                    value = xa_query.GetFieldData(out_block_name, field, i)
                    item[field] = value
                print(item)
                result.append(item)
        """
        XAQuery.tr_run_state = 0
        self.query_cnt.append(datetime.today())

        #영문필드를 한글필드명으로 변환
        for item in result:
            for field in list(item.keys()):
                if getattr(Field, res, None):
                    res_field = getattr(Field, res, None)
                    if out_block_name in res_field:
                        field_hname = res_field[out_block_name]
                        if field in field_hname:
                            item[field_hname[field]] = item[field]
                            item.pop(field)
        return result
    


class XAQuery:
    RES_PATH ="C:\\eBEST\\xingAPI\\Res\\"
    tr_run_state = 0

    def OnReceiveData(self, code):
        print("OnReceiveData", code)
        XAQuery.tr_run_state = 1

    def OnReceiveMessage(self, error, code, message):
        print("OnReceiveMessage", error, code, message, XAQuery.tr_run_state)