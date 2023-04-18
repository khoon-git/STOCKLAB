import win32com.client


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


class XAQuery:
    RES_PATH ="C:\\eBEST\\xingAPI\\Res\\"
    tr_run_state = 0

    def OnReceiveData(self, code):
        print("OnReceiveData", code)
        XAQuery.tr_run_state = 1

    def OnReceiveMessage(self, error, code, message):
        print("OnReceiveMessage", error, code, message, XAQuery.tr_run_state)