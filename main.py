import requests 
import io
import json
import base64
import time
import random
from PIL import Image
from flask import Flask, request, jsonify
from prompt.prompt import PROMPT
from threading import Thread



url = "http://127.0.0.1:8188" # comfyUI 的服务器地址

app = Flask(__name__)

IMG_ID = None

 
 
 
# http://127.0.0.1:5000/generate
@app.route('/generate', methods=['POST']) # 访问 🔥 http://127.0.0.1:5000/generate?text=girl
def index():
    # text = request.args.get('text')  # 从查询字符串中获取 text 参数 => 🌟 例如 http://127.0.0.1:5000/generate-image?text=girl
    input_text = request.json.get('text') #  从POST数据中获取text参数
    print("拿到了 text :" , input_text)
    
    if not input_text:
        return jsonify({"error": "缺少 input_text 参数"}), 400
    else: # 返回数据
        # 替换原来的提示词(非必需)
        random_number = random.randint(0, 18446744073709551614)  # 生成一个随机数
        PROMPT["6"]["inputs"]["text"] = input_text # 修改传入的传入提示词
        PROMPT["3"]["inputs"]["seed"] = random_number # 修改随机种子参数
        # PROMPT["3"]["inputs"]["seed"] = 665437340080956 # 修改随机种子参数
 
 
		# 查看下 output
        img_response_data = requests.get(url=f'{url}/history/{prompt_id}') # 🌟 这一步需要看一下返回的数据, 需要看下返回的 outputs 在哪个节点号！
        formatted_json = json.dumps(img_response_data.json() , indent=2, ensure_ascii=False)
        print("返回需要生成的预先数据: ", formatted_json)
 
 
		# 🌟 文生图 - 【1 : 发送生图请求】 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
        payload = {"prompt": PROMPT} # 准备好要发送的数据
        
        
        response = requests.post(url=f'{url}/prompt', json=payload)  # 发送请求, 获取【生成后的图片数据】
        response_jsonData = response.json() # 不会马上响应, 只会返回个队列 ID , 如果有 id 则是生成好了图片
        
        
        
        prompt_id = response_jsonData["prompt_id"]
		# print("返回了图片 id: ", prompt_id)

        if prompt_id : # 如果有 id 则是生成好了图片
			# 🌟 文生图 - 【2 : 获得生图结果】 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
            img_response_data = requests.get(url=f'{url}/history/{prompt_id}')# 🌟 这一步需要看一下返回的数据, 需要看下返回的 outputs 在哪个节点号！

            img_name = img_response_data.json()[prompt_id]['outputs']['16']['images'][0]['filename'] # 👈拼接出图片的文件名, 图片名需要看在哪个节点 !
			# print("图片名:", img_name)

            image_url = f'{url}/view?filename={img_name}&subfolder=&type=temp' # 🔥 view 接口来获取图片信息
			# print("图片地址:", image_url) # 🚀 最终获得了图片地址   =>   http://127.0.0.1:8188/view?filename=ComfyUI_temp_sgyjm_00001_.png&subfolder=&type=temp
   
            return image_url
        return jsonify({"error": "无法找到生成的图片名称"}), 500




# 初始化 __main__
if __name__ == "__main__":
	app.run(port=5000, debug=True)


