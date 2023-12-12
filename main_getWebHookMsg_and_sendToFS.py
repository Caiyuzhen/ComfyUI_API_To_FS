import requests 
import io
import os
import json
import base64
import time
import random
import getpass
import threading
from PIL import Image
from flask import Flask, request, jsonify
from prompt.prompt import PROMPT
from threading import Thread
from datetime import datetime
from threading import Lock
from apscheduler.schedulers.background import BackgroundScheduler
from auth import get_tenant_access_token, upload_img_toIM, get_bot_in_group_info, send_msg, get_webHookMsgAndSendInfo


url = "http://127.0.0.1:8188" # comfyUI 的服务器地址
app = Flask(__name__)


# 全局变量
WEBHOOK_DATA = None
is_Processing = False  # 标志变量，表示是否正在进行生图任务, 如果在执行生图任务则不 hook 新的数据
lock = Lock()  # 线程锁，用于线程安全地访问和修改全局变量


# 每隔 1 小时获取一遍 tenant_access_token 的函数
def get_token_every_90_minutes():
    global TENAUT_ACCESS_TOKEN
    while True:
        TENAUT_ACCESS_TOKEN = get_tenant_access_token()
        print("⏰ Tenant_access_token 已经刷新为: ", TENAUT_ACCESS_TOKEN)
        # 等待 1.5 小时 (5400秒)
        time.sleep(5400)



# ⌛️ 轮询方法, 等待生图完成
def check_image_status(prompt_id, timeout=60, interval=2):
    """检查图片状态, 知道生成完图片或者图片生成超时"""
    stast_time = time.time()
    while time.time() - stast_time < timeout: # 当前时间 - 开始时间 < 超时时间
        img_response = requests.get(url=f'{url}/history/{prompt_id}') # 请求生图结果
        if img_response.status_code == 200:
            data = img_response.json().get(prompt_id, {}).get('outputs', {}) # 等价于 data = img_response_data.json()[prompt_id], 但这种方式有弊端, 如果 output 不存在会报错  <==  看下返回的 outputs 在哪个节点号！ => 哪个节点有 image
            if data:
                return jsonify(data) # flask 的 jsonify() 方法可以将字典转换为 json 字符串
        time.sleep(interval) # 每隔 interval 秒轮询一次
			
   
# ⛰️ 处理请求网络图片的方法
def decode_base64_to_image(encoding): # 解码图像
    if encoding.startswith("data:image/"):
        encoding = encoding.split(";")[1].split(",")[1]
    image = Image.open(io.BytesIO(base64.b64decode(encoding)))
    return image


def encode_pil_to_base64(image): # 给图像编码
    with io.BytesIO() as output_bytes:
        image.save(output_bytes, format="PNG")
        bytes_data = output_bytes.getvalue()
    return base64.b64encode(bytes_data).decode("utf-8")



# ⭕️ 不断的获取 webhook 数据
def refresh_get_webhook_data():
	global WEBHOOK_DATA, is_Processing # 👈 获得全局变量
	with lock:
		if not is_Processing:
			WEBHOOK_DATA = get_webHookMsgAndSendInfo()
			print("🔥🔥🔥 WEBHOOK_DATA 已经刷新为: ", WEBHOOK_DATA)



# 生图服务(不通过路由了, 通过 Bot 获得 prompt)
def generate_img():
    global WEBHOOK_DATA, is_Processing # 👈 获得全局变量
    # print("👀 预备生图 -> ", "WEBHOOK_DATA: ", {WEBHOOK_DATA},  "is_Processing: ", {is_Processing}, "\n")
    
    # with lock:
    print("👀 预备生图 -> ", "WEBHOOK_DATA: ", {WEBHOOK_DATA},  "is_Processing: ", {is_Processing}, "\n")
    if not WEBHOOK_DATA:
        return "❌ 缺少 WEBHOOK_DATA 数据"
    elif WEBHOOK_DATA: 
        print("✅ 预备生图 -> ", "WEBHOOK_DATA: ", {WEBHOOK_DATA},  "is_Processing: ", {is_Processing}, "\n")
		# 更新提示词
        random_number = random.randint(0, 184467470956145)  # 生成一个随机数 665437340080956
        PROMPT["6"]["inputs"]["text"] = WEBHOOK_DATA # 修改传入的传入提示词
        PROMPT["3"]["inputs"]["seed"] = random_number # 修改随机种子参数

		# 文生图 - 【发送生图请求】 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
        payload = {"prompt": PROMPT} # 准备好要发送的数据, 把提示词替换为传入的提示词
	
		# 发送请求, 开始进入队列进行生图, 接口会返回一个生图队列的 id
        print("🖌️ 开始生成图片...")
        response = requests.post(url=f'{url}/prompt', json=payload) 
        response_jsonData = response.json() # 不会马上响应, 只会返回个队列 ID , 如果有 id 了则是生成好了图片
	
        print("🔥🔥生图任务:", response_jsonData)

		#  获得下发的生图任务 id
		# time.sleep(5)
        prompt_id = response_jsonData["prompt_id"]

		# 查看下 output
        if prompt_id:
            try:
                res = ''
                res = check_image_status(prompt_id)
                res_data = res.get_json() # 在 Flask 中, 当使用 jsonify() 创建一个响应时，实际上是返回了一个 Flask Response 对象, 其中包含了 JSON 格式的字符串作为其数据。要访问这个数据, 需要先检查响应的状态码, 然后解析响应内容为 JSON
                img_name = res_data["9"]['images'][0]['filename']
				# view_image_path = f'{url}/view?filename={img_name}' # 🔥 使用view 接口来获取图片信息
				# print("👍 生成了图片:", view_image_path)
                print("👍 生成了图片: \n", img_name, "\n")
			
				# 获得存放图片的文件夹路径
                username = getpass.getuser() # 获取当前用户名
                folder_path = f'/Users/{username}/ComfyUI/output'
                full_imageFile_path = os.path.join(folder_path, img_name)  # 构建图片的完整路径
				# return full_imageFile_path ## 🌟返回了图片的绝对地址

                if TENAUT_ACCESS_TOKEN:
                    img_key = upload_img_toIM(full_imageFile_path, TENAUT_ACCESS_TOKEN) # 使用守护线程每隔 1.5 小时获取一遍 tenant_access_token
                    chat_id = get_bot_in_group_info(TENAUT_ACCESS_TOKEN)
                    tran_json_string = ''
				
                    # 打开 json_card 文件
                    with open("json_card.json", "r") as f:
                        json_card_origin = json.load(f)
					
						# 修改 json_card 文件内的 img_key
                        json_card_origin["elements"][0]["img_key"] = img_key
					
						# 发送群聊消息
                        res = send_msg(chat_id, json_card_origin, TENAUT_ACCESS_TOKEN)
                        is_Processing = False # 生图任务完成, 重置标志变量
                        WEBHOOK_DATA = None # 生图任务完成, 重置 WEBHOOK_DATA
                        return res
            except Exception as e:
                return "❌ Error"
    


# 通过 WEBHOOK_DATA 以及 is_Processing 来判断是否要执行 generate_img() 函数
def checkFor_RunMainGenerateFn():
    global WEBHOOK_DATA, is_Processing # 👈 获得全局变量
    print("🔒 Check 线程锁 来执行 main -> ", "WEBHOOK_DATA: ", {WEBHOOK_DATA},  "is_Processing: ", {is_Processing}, "\n")
    
    with lock:
        if WEBHOOK_DATA and not is_Processing: # 如果有 WEBHOOK_DATA 数据且没在生图任务
            is_Processing = True # 改变标志变量, 表示正在进行生图任务
            generate_img()  # 调用生成图片的函数
        else:
            print(f"{WEBHOOK_DATA} , 为空或者正在进行生图任务")


# 初始化 __main__
if __name__ == "__main__":
 	# 启动定时任务线程, 不断的获取 token
    token_thread = threading.Thread(target=get_token_every_90_minutes)
    token_thread.daemon = True  # 将线程设置为守护线程, 为其他线程或整个程序提供服务
    token_thread.start()
    
    
	# 启动定时任务线程, 不断的获取 webhook 数据
    scheduler = BackgroundScheduler() # 创建定时器任务
    scheduler.add_job(refresh_get_webhook_data, 'interval', seconds=5) # 每隔 5s 刷新获得最新的数据
    scheduler.add_job(checkFor_RunMainGenerateFn, 'interval', seconds=3) # 每隔 3s 刷新获得最新的数据
    scheduler.start()
 
 
    # 开启服务
    app.run(port=5000, debug=True)
	# Thread(target=lambda: app.run(port=5000, debug=True, use_reloader=False)).start() # 独立开个线程运行服务
 


 
