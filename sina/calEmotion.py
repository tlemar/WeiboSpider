import requests
import md5sign
 
 
def get_content(plus_item):
    # 聊天的API地址
    url = "https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat"  
    # 获取请求参数  
    plus_item = plus_item.encode('utf-8')  
    payload = md5sign.get_params(plus_item)
    # r = requests.get(url,params=payload)
    r = requests.post(url,data=payload)
    print(r.content)
    return r.json()["data"]["answer"]  
  
  
if __name__ == '__main__':
    while True:
        comment = input('我：')   
        if comment == 'q':   
            break
        answer=get_content(comment)
        print('机器人：'+answer) 