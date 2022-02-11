import socket
import hashlib
import base64
import time

config_dict = {
    'server_username': 'admin',                 #RTSP用户名
    'server_password': 'aaaaa11111',                #RTSP用户名对应密码
    'server_ip': '152.168.170.66',                  #RTSP服务器IP地址
    'server_port': 554,                         #RTSP服务器使用端口
    'server_path': '/h264/ch01/main/av_stream/',  #URL中端口之后的部份，测试发现不同服务器对这部份接受的值是不一样的，也就是说自己使用时很可能得自己修改这部份的值
    'cseq': 2,                                  #RTSP使用的请求起始序列码，不需要改动
    'user_agent': 'LibVLC/3.0.2 (LIVE555 Streaming Media v2016.11.28)', #自定义请求头部
    'buffer_len': 1024,                         #用于接收服务器返回数据的缓冲区的大小
    'auth_method': 'Digest',                    #RTSP使用的认证方法，Basic/Digest
    'header_normal_modify_allow': False,        #是否允许拼接其他协议规定的请求头的总开关，请些请求头的值为正常值（大多是RFC给出的示例）
    'header_overload_modify_allow': False,      #是否允许拼接其他协议规定的请求头的总开关，请些请求头的值为超长字符串
    'options_header_modify': True,              #OPTIONS请求中，是否允许拼接其他协议规定的请求头的开关
    'describe_header_modify': True,             #第一次DESCRIBE请求中，是否允许拼接其他协议规定的请求头的开关
    'describe_auth_header_modify': True,        #第二次DESCRIBE请求中，是否允许拼接其他协议规定的请求头的开关
    'setup_header_modify': True,                #第一次SETUP请求中，是否允许拼接其他协议规定的请求头的开关
    'setup_session_header_modify': True,        #第二次SETUP请求中，是否允许拼接其他协议规定的请求头的开关
    'play_header_modify': True,                 #PLAY请求中，是否允许拼接其他协议规定的请求头的开关
    'get_parameter_header_modify': True,        #GET PARAMETER请求中，是否允许拼接其他协议规定的请求头的开关
    'teardown_header_modify': True              #TEARDOWN请求中，是否允许拼接其他协议规定的请求头的开关
}

def log(s):
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print(s)
    print('---------------------------------------------------------')

class RtspClient():
    def __init__(self, server, port=554, path="", username="", password=""):
        self.server = server
        self.port = port
        self.path = path
        self.username = username
        self.password = password
        self.cseq = 1
        self.user_agent = "LibVLC 1.0"
        self.auth_method = 'Digest'
        self.uri = "rtsp://%s:%s%s" % (self.server, self.port, self.path)
        self.realm = ''
        self.nonce = ''
        self.session = ''
        self.socket_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_send.settimeout(5)
        self.socket_send.connect((self.server, self.port))

    def __get_cseq(self):
        self.cseq += 1
        return self.cseq
    
    def __req_gen(self, *req_part):
        return "\r\n".join(req_part) + "\r\n\r\n"

    def __auth_header(self, public_method):
        if self.auth_method == 'Basic':
            auth_64 = base64.b64encode("%s:%s" % (self.username, self.password)).encode("utf-8").decode()
            return 'Authorization: Basic %s ' % auth_64
        else:
            frist_pre_md5_value = hashlib.md5((self.username + ':' + self.realm + ':' + self.password).encode()).hexdigest()
            first_post_md5_value = hashlib.md5((public_method+':' + self.uri).encode()).hexdigest()
            response = hashlib.md5((frist_pre_md5_value + ':' + self.nonce + ':' + first_post_md5_value).encode()).hexdigest()
            auth_header = 'Authorization: Digest username="%s", realm="%s", nonce="%s", uri="%s", response="%s"'
            auth_header = auth_header % (self.username, self.realm, self.nonce, self.uri, response)
            return auth_header
    
    #生成options请求头部
    def gen_options_header(self, need_auth=False):
        req_sp = [
            'OPTIONS %s RTSP/1.0',
            'CSeq: %s',
            'User-Agent: %s',
            'Session: %s',
        ]
        if need_auth:
            req_sp.append(self.__auth_header('OPTIONS'))
        req = self.__req_gen(*req_sp) % (self.uri, self.__get_cseq(), self.user_agent, self.session)
        return req
    
    #生成describe请求头部
    def gen_describe_header(self, need_auth=False):
        req_sp = [
            'DESCRIBE %s RTSP/1.0',
            'CSeq: %s',
            'User-Agent: %s',
            'Accept: application/sdp',
        ]
        if need_auth:
            req_sp.append(self.__auth_header('DESCRIBE'))
        req = self.__req_gen(*req_sp) % (self.uri, self.__get_cseq(), self.user_agent)
        return req
        
    
    #生成setup请求头部
    def gen_setup_header(self, need_auth=False):
        req_sp = [
            'SETUP %strackID=video RTSP/1.0',
            'CSeq: %s',
            'User-Agent: %s',
            'Transport: RTP/AVP/UDP;unicast;client_port=50166-50167',
        ]
        if need_auth:
            req_sp.append(self.__auth_header('SETUP'))
        req = self.__req_gen(*req_sp) % (self.uri, self.__get_cseq(), self.user_agent)
        return req
    
    
    #生成play请求头部
    def gen_play_header(self, need_auth=False):
        req_sp = [
            'PLAY %s RTSP/1.0',
            'CSeq: %s',
            'User-Agent: %s',
            'Session: %s',
            'Range: npt=0.000-',
        ]
        if need_auth:
            req_sp.append(self.__auth_header('PLAY'))
        req = self.__req_gen(*req_sp) % (self.uri, self.__get_cseq(), self.user_agent, self.session)
        return req
    
    #生成GET_PARAMETER请求头部
    def gen_get_parameter_header(self, need_auth=False):
        req_sp = [
            'GET_PARAMETER %s RTSP/1.0',
            'CSeq: %s',
            'User-Agent: %s',
            'Session: %s',
        ]
        if need_auth:
            req_sp.append(self.__auth_header('GET_PARAMETER'))
        req = self.__req_gen(*req_sp) % (self.uri, self.__get_cseq(), self.user_agent, self.session)
        return req
    
    #生成teardown请求头部
    def gen_teardown_header(self, need_auth=False):
        req_sp = [
            'TEARDOWN %s RTSP/1.0',
            'CSeq: %s',
            'User-Agent: %s',
            'Session: %s',
        ]
        if need_auth:
            req_sp.append(self.__auth_header('TEARDOWN'))
        req = self.__req_gen(*req_sp) % (self.uri, self.__get_cseq(), self.user_agent, self.session)
        return req

    def send_data(self, data):
        log(data)
        self.socket_send.send(data.encode())

    def recv_data(self):
        buff_size = 1024
        data = self.socket_send.recv(buff_size).decode()
        print(data)
        print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
        return data

    def parse_realm(self, data):
        realm_pos = data.find('realm')
        realm_value_begin_pos = data.find('"', realm_pos)+1
        realm_value_end_pos = data.find('"', realm_pos + 8)
        self.realm = data[realm_value_begin_pos:realm_value_end_pos]

    def parse_nonce(self, data):
        nonce_pos = data.find('nonce')
        nonce_value_begin_pos = data.find('"', nonce_pos)+1
        nonce_value_end_pos = data.find('"', nonce_pos + 8)
        self.nonce = data[nonce_value_begin_pos:nonce_value_end_pos]
    
    def parse_session(self, data):
        session_pos = data.find('Session')
        session_value_begin_pos = data.find(' ',session_pos+8)+1
        session_value_end_pos = data.find(';',session_pos+8)
        session_value = data[session_value_begin_pos:session_value_end_pos]
        self.session = session_value
    
    #执行一次完整的rtsp播放请求，OPTIONS/DESCRIBE/SETUP/PLAY/GET PARAMETER/TEARDOWN，如果某个请求不正确则中止
    #此方法推荐用于则试服务端是否正确实现RTSP服务
    def exec_full_request(self):
        
        
        print('now start to check options operation')
        str_options_header = self.gen_options_header()
        self.send_data(str_options_header)
        msg_recv = self.recv_data()
        if '200 OK' in msg_recv:
            print('OPTIONS request is OK')
        else:
            print('OPTIONS request is BAD')
        str_describe_header = self.gen_describe_header()
        self.send_data(str_describe_header)
        msg_recv = self.recv_data()
        
        if msg_recv.find('401 Unauthorized') == -1 & False:
            msg_recv_dict = msg_recv.split('\r\n')
            print('first DESCRIBE request occur error: ')
            print(msg_recv_dict[0])
        else:
            print('first DESCRIBE is ok,now we will execute second DESCRIBE for auth')
            realm_pos = msg_recv.find('realm')
            realm_value_begin_pos = msg_recv.find('"', realm_pos)+1
            realm_value_end_pos = msg_recv.find('"', realm_pos + 8)
            realm_value = msg_recv[realm_value_begin_pos:realm_value_end_pos]
            nonce_pos = msg_recv.find('nonce')
            nonce_value_begin_pos = msg_recv.find('"', nonce_pos)+1
            nonce_value_end_pos = msg_recv.find('"', nonce_pos + 8)
            nonce_value = msg_recv[nonce_value_begin_pos:nonce_value_end_pos]
            str_describe_auth_header = self.gen_describe_auth_header(realm_value, nonce_value)
            self.send_data(str_describe_auth_header)
            msg_recv = self.recv_data()
            if msg_recv.find('200 OK') == -1:
                msg_recv_dict = msg_recv.split('\r\n')
                print('second DESCRIBE request occur error: ')
                print(msg_recv_dict)
                return
            
            print('second DESCRIBE is ok,now we will execute first SETUP for session')
            str_setup_header = self.gen_setup_header(realm_value, nonce_value)
            
            self.send_data(str_setup_header)
            msg_recv = self.recv_data()
            if msg_recv.find('200 OK') == -1:
                msg_recv_dict = msg_recv.split('\r\n')
                print('first SETUP request occur error: ')
                print(msg_recv_dict)
                return
            
            print('first SETUP is ok,now we will execute second SETUP')
            session_pos = msg_recv.find('Session')
            session_value_begin_pos = msg_recv.find(' ',session_pos+8)+1
            session_value_end_pos = msg_recv.find(';',session_pos+8)
            session_value = msg_recv[session_value_begin_pos:session_value_end_pos]
            str_setup_session_header = self.gen_setup_session_header(realm_value, nonce_value,session_value)
            
            self.send_data(str_setup_session_header)
            msg_recv = self.recv_data()
            if msg_recv.find('200 OK') == -1:
                msg_recv_dict = msg_recv.split('\r\n')
                print('second SETUP request occur error: ')
                print(msg_recv_dict[0])
                return 

            print('second SETUP is ok, now we wil execute PLAY')
            str_play_header = self.gen_play_header(realm_value, nonce_value, session_value)
            
            self.send_data(str_play_header)
            msg_recv = self.recv_data()
            if msg_recv.find('200 OK') == -1:
                msg_recv_dict = msg_recv.split('\r\n')
                print('PLAY request occur error: ')
                print(msg_recv_dict[0])
                return 
            print('PLAY is ok, we will execute GET_PARAMETER every 10 seconds and 5 times total')
            for i in range(3):
                str_get_parameter_header = self.gen_get_parameter_header(realm_value, nonce_value, session_value)
                
                self.send_data(str_get_parameter_header)
                msg_recv = self.recv_data()
                msg_recv_dict = msg_recv.split('\r\n')
                print(str(i)+'*10:'+msg_recv_dict[0])
                time.sleep(10)
            print('\nnow we will execute TEARDOWN to disconnect with server')
            str_teardown_header = self.gen_teardown_header(realm_value, nonce_value, session_value)
            
            self.send_data(str_teardown_header)
            msg_recv = self.recv_data()
            print(msg_recv)
            print('program execute finished, thank you')
        self.socket_send.close()

    def make_req(self):
        option_header = self.gen_options_header()
        self.send_data(option_header)
        msg_recv = self.recv_data()
        if msg_recv.find('401 Unauthorized'):
            self.parse_nonce(msg_recv)
            self.parse_realm(msg_recv)
            self.send_data(self.gen_options_header(True))
            msg_recv = self.recv_data()
            self.send_data(self.gen_describe_header(True))
            msg_recv = self.recv_data()
            self.send_data(self.gen_setup_header(True))
            msg_recv = self.recv_data()
            self.parse_session(msg_recv)
            self.send_data(self.gen_play_header(True))
            msg_recv = self.recv_data()

            # self.send_data(self.gen_get_parameter_header(True))
            # msg_recv = self.recv_data()

            
            # self.path = "/h264/ch02/main/av_stream/"
            # self.uri = "rtsp://%s:%s%s" % (self.server, self.port, self.path)
            # self.send_data(self.gen_options_header(True))
            # msg_recv = self.recv_data()
            time.sleep(10)

            self.send_data(self.gen_teardown_header(True))
            msg_recv = self.recv_data()

        



if __name__ == '__main__':
    # for i in range(1, 27):
    #     print(i)
    rtsp_client = RtspClient('152.168.164.11', 554, "/h264/ch%02d/main/av_stream/" % 8, "admin", "hik12345+")
    rtsp_client.make_req()