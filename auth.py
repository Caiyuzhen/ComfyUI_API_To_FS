import requests 
import io
import json
import os
import time
from flask import jsonify
from dotenv import load_dotenv # 用来加载环境变量
from requests_toolbelt import MultipartEncoder

# 从环境变量中获取 APP_ID 和 APP_SECRET
load_dotenv()  # 加载 .env 文件中的环境变量
APP_ID = os.environ.get('APP_ID')
APP_SECRET = os.environ.get('APP_SECRET')
PARENT_NODE = os.environ.get('PARENT_NODE')
BASE_APP_TOKEN = os.environ.get('BASE_APP_TOKEN')
BASE_TABLE_ID = os.environ.get('BASE_TABLE_ID')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')


# 获取 tenant_access_token ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
def get_tenant_access_token(): 
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" # 生成 tenant_access_token 的接口
    headers = {
		"Content-Type": "application/json"
	}
    payload = {
		"app_id": APP_ID,
		"app_secret": APP_SECRET
	}
    
    # 发送请求
    response = requests.post(url=url, headers=headers, json=payload)
    response_data = response.json()
    print("🔑 获得了 tenant_access_token: \n", response_data.get("tenant_access_token"), "\n")
    return response_data.get("tenant_access_token") # 返回 tenant_access_token
    

 
# 上传到文件夹 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
# 从获得的 tenant_access_token 来上传图片 https://open.feishu.cn/open-apis/drive/v1/files/upload_all
def upload_file_toBase(file_name, full_imageFile_path, tenant_access_token):
    file_size = os.path.getsize(full_imageFile_path) # 获取文件大小
    # url = "https://open.feishu.cn/open-apis/drive/v1/files/upload_all" # 上传接口 => 上传到文件夹, 文件夹内可见
    url = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all" # 上传接口 => 上传到文件夹, 且文件夹内不可见
   
    headers = { #🔥 需要先定义 header 才能在下方去更嗨 header 的 Content-Type !!
		"Authorization": "Bearer " + tenant_access_token,
	}
   # 👇提交到文件夹内 ___ 
    # # 以表单形式提交数据
    # form = {'file_name': file_name,
    #         'parent_type': 'explorer',
    #         'parent_node': BASE_APP_TOKEN, # 🔥上传到多维表格内!!
    #         'size': str(file_size),
    #         'file': (open(full_imageFile_path, 'rb'))}  
    # multi_form = MultipartEncoder(form)
    
    # headers['Content-Type'] = multi_form.content_type
    
    # 👇提交到多维表格内
	# 以表单形式提交数据
    form = {'file_name': file_name,
            'parent_type': 'bitable_image',
            'parent_node': BASE_APP_TOKEN, # 🔥上传到多维表格内!!
            'size': str(file_size),
            'file': (open(full_imageFile_path, 'rb'))}  
    multi_form = MultipartEncoder(form)
    
    # 验证 token + 设置 Content-Type
    headers['Content-Type'] = multi_form.content_type
    
   
    print("📤 开始上传文件...")
    response = requests.request("POST", url, headers=headers, data=multi_form)
    
    try:
        if response.status_code == 200:
            response_data = response.json()
		    # 返回 file_token

		    # return response_data
            file_token = response_data['data']['file_token']  # 提取 file_token
            print("📤 上传 base 文件成功, file_token 为: \n", file_token, "\n")
            return file_token
        else:
            print("❌ 上传 base 文件失败", response.status_code)
            print("错误详情：", response.text)  # 打印详细的错误信息
            return jsonify({"error": str(e)}), response.status_code
		
		    # file_token = response_data["file_token"]
		    # print(file_token)
    except Exception as e:
        print("❌ 上传 base 记录失败", response.status_code)
        print("错误详情：", response.text)  # 打印详细的错误信息
        return jsonify({"error": str(e)}), 500
    
    
# 新增一条 base 记录 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
def add_base_record(file_name, file_token, tenant_access_token):
    app_token = BASE_APP_TOKEN
    table_id = BASE_TABLE_ID
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records" # 新增 record 接口
    
	# 添加 app_id 跟 app_secret
    headers = {
		"Authorization": "Bearer " + tenant_access_token,
	}
    
    # 构建请求体的字典
    request_body = {
		"fields": {
			"name": file_name, # 🔥 生图后获得
			"file": [{
			"file_token": file_token # 🔥 上传到云文档后获得
			}]
		}
	}
    
	# 将字典转换为 JSON 格式的字符串
    # json_request_body = json.dumps(request_body)
    
	# 发送请求
    response = requests.post(url=url, headers=headers, json=request_body)
    print("📤 开始新增 base 记录...")
    
    try:
        if response.status_code == 200:
            response_data = response.json()
            print("📤 新增 base 记录成功: \n", response_data, "\n")
            return response_data
        else:
            print("❌ 新增 base 记录失败", response.status_code)
            print("错误详情：", response.text)  # 打印详细的错误信息
            return jsonify({"error": str(e)}), response.status_code
        
    except Exception as e:
        print("❌ 新增 base 记录失败", response.status_code)
        print("错误详情：", response.text)  # 打印详细的错误信息
        return jsonify({"error": str(e)}), 500
    
    
    
    
# 上传图片到 IM 内 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
def upload_img_toIM(full_imageFile_path, tenant_access_token):
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    form = {'image_type': 'message',
    		'image': (open(full_imageFile_path, 'rb'))}   # 🔥 打开生成好的图片, 并上传到 IM
    multi_form = MultipartEncoder(form)
    headers = {
        "Authorization": "Bearer " + tenant_access_token,
    }
    headers['Content-Type'] = multi_form.content_type
    
    print("⛰️ 开始上传图片到 IM...")
    response = requests.request("POST", url, headers=headers, data=multi_form)
    
    try:
        if response.status_code == 200:
            response_data = response.json()
            image_key = response_data['data']['image_key']  # 提取 image_key
            print("⛰️ 获得 img 的 key 成功:", response.content, "\n")  
            return image_key
        else:
            print("❌ 获取 img 的 key 失败", response.status_code)
            print("错误详情：", response.text)  # 打印详细的错误信息
            return jsonify({"error": str(e)}), response.status_code

    except Exception as e:
        print("❌ 图片上传失败", response.status_code)
        print("错误详情：", response.text)  # 打印详细的错误信息
        return jsonify({"error": str(e)}), 500
    
    
    
# 获取用户或机器人所在的群列表 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
def get_bot_in_group_info(tenant_access_token):
    url = "https://open.feishu.cn/open-apis/im/v1/chats"
    headers = {
		"Authorization": "Bearer " + tenant_access_token,
	}
    
    print("🔍 开始获取机器人所在的群列表...")
    response = requests.request("GET", url, headers=headers)
    try:
        if response.status_code == 200:
            response_data = response.json()
            chat_id = response_data["data"]["items"][0]["chat_id"]  # 提取 chat_id
			
            print("⛰️ 获得了 bot 所在的 的 chat_id:", response.content, "\n")  
            return chat_id
        else:
            print("❌ 获取 bot 所在的 chat_id 失败", response.status_code)
            print("错误详情：", response.text)  # 打印详细的错误信息
            return jsonify({"error": str(e)}), response.status_code
    except Exception as e:
        print("❌ 获取 bot 所在的 chat_id 异常", str(e))
        return jsonify({"error": str(e)}), 500
 
    
    
# 发送消息卡片到指定的群 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
def send_msgCard(receive_id, tran_json_string, tenant_access_token):
    url = "https://open.feishu.cn/open-apis/im/v1/messages" # 真实请求地址: #  url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    
    # 🔥查询参数
    params = {"receive_id_type": "chat_id"} # 发送到指定的 chat 内
    
    headers = {
		"Authorization": "Bearer " + tenant_access_token,
  		'Content-Type': 'application/json'
	}
    
     # 构建请求体的字典
    request_body = {
		"receive_id": receive_id, # 可以指定 open_id 或 chat_id 或 user_id 等, ⚡️ 这里其实就是传入 chat_id
  		"msg_type": "interactive",
		"content": json.dumps(tran_json_string) # 将 Json 转为字符串
	}
    
    payload = json.dumps(request_body)
       
    print("💬 准备发送消息到群聊...")
    response = requests.request("POST", url, params=params, headers=headers, data=payload) # 👈这里拼接了查询参数!! 真实请求地址: https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id
    
    try:
        if response.status_code == 200:
            response_data = response.json()
            print("💬 群聊消息发送成功！:", response_data, "\n")  
            return json.dumps(response_data["data"]) # 使用 jsonify 来返回 JSON 响应
        else:
            print("❌ 群聊消息发送失败", response.status_code)
            print("错误详情：", response.text)  # 打印详细的错误信息
            return json.dumps({"error": str(e)}), response.status_code
    except Exception as e:
        print("❌ 群聊消息发送异常", str(e))
        return json.dumps({"error": str(e)}), 500

 
 
# 发送消息到指定的群 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
def send_normalMsg(receive_id, msg_json, tenant_access_token):  
    url = "https://open.feishu.cn/open-apis/im/v1/messages" # 真实请求地址: #  url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    
    # 🔥查询参数
    params = {"receive_id_type": "chat_id"} # 发送到指定的 chat 内
    
    headers = {
		"Authorization": "Bearer " + tenant_access_token,
  		'Content-Type': 'application/json'
	}
    
     # 构建请求体的字典
    request_body = {
		"receive_id": receive_id, # 可以指定 open_id 或 chat_id 或 user_id 等, ⚡️ 这里其实就是传入 chat_id
  		"msg_type": "post",
		"content": json.dumps(msg_json) # 将 Json 转为字符串
	}
    
    payload = json.dumps(request_body)
       
    print("💬 准备发送消息到群聊...")
    response = requests.request("POST", url, params=params, headers=headers, data=payload) # 👈这里拼接了查询参数!! 真实请求地址: https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id
    
    try:
        if response.status_code == 200:
            response_data = response.json()
            print("💬 群聊消息发送成功！:", response_data, "\n")  
            return json.dumps(response_data["data"]) # 使用 jsonify 来返回 JSON 响应
        else:
            print("❌ 群聊消息发送失败", response.status_code)
            print("错误详情：", response.text)  # 打印详细的错误信息
            return json.dumps({"error": str(e)}), response.status_code
    except Exception as e:
        print("❌ 群聊消息发送异常", str(e))
        return json.dumps({"error": str(e)}), 500



# 获得用户 @Bot 的 webhook 消息, 并解析出 content
def get_webHookMsgAndSendInfo():
    url = WEBHOOK_URL
    text_content = None
    
    response = requests.request("GET", url)
    
    try:
        if response.status_code == 200:
            response_data = response.json()
            print("📤 获得了 webhook 消息: \n", response_data, "\n\n")
            content_data = response_data['event']['message']['content']
            
            # 第一步：解析 JSON 字符串 => 把 str 转为 json
            parsed_data = json.loads(content_data) # "content": "{\"text\":\"@_user_1 dog\"}",
            
            # 第二步：提取 text 字段
            text = parsed_data['text']
            
            # 第三步, 提取出 @ 的人跟 内容
            parts = text.split(' ', 1)  # 🔥从 ' ' 空格处开始分割, 分割成两部分
            if len(parts) > 1:
                text_content = parts[1]
            else:
                text_content = ""  # 没有第二部分，设置为空字符串
            return text_content # 直接返回文本内容
            # return json.dumps({"user": at_user, "content": text_content}) # 返回 @人 跟内容
        elif response.status_code == 404:
            return None
                
    except Exception as e:
        print("❌ webhook 消息获取失败", response.status_code)
        print("错误详情：", response.text)  # 打印详细的错误信息
        return jsonify({"error": str(e)}), 500
        
    
    
    

