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
from datetime import datetime


url = "http://127.0.0.1:8188" # comfyUI 的服务器地址
app = Flask(__name__)
IMG_ID = None


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


# 生图服务的路由
@app.route('/generate', methods=['POST'])
def index():
    # text = request.args.get('text')  # 从查询字符串中获取 text 参数 => 🌟 例如 http://127.0.0.1:5000/generate-image?text=girl
    input_text = request.json.get('text') #  从 【POST】请求的 【JSON】 数据中获取 【text】 参数,
    # print("拿到了 text :" , input_text)
    
    if not input_text:
        return jsonify({"❌ 缺少 input_text 参数"}), 400
    else: # 返回数据
        # 更新提示词
        random_number = random.randint(0, 184467470956145)  # 生成一个随机数 665437340080956
        PROMPT["6"]["inputs"]["text"] = input_text # 修改传入的传入提示词
        PROMPT["3"]["inputs"]["seed"] = random_number # 修改随机种子参数
 
		# 文生图 - 【发送生图请求】 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
        payload = {"prompt": PROMPT} # 准备好要发送的数据, 把提示词替换为传入的提示词
        
        # 发送请求, 开始进入队列进行生图, 接口会返回一个生图队列的 id
        response = requests.post(url=f'{url}/prompt', json=payload) 
        response_jsonData = response.json() # 不会马上响应, 只会返回个队列 ID , 如果有 id 了则是生成好了图片
        # return response_jsonData["prompt_id"] # "prompt_id": "024f126e-8457-4b7e-b2ca-1ee5b4e2b4b3"
        
        #  获得下发的生图任务 id
        time.sleep(5)
        prompt_id = response_jsonData["prompt_id"]
        # print("返回了任务 id: ", prompt_id) ##✅

  		# 查看下 output
        if prompt_id:
            try:
                # 文生图 - 【2 : 获得生图结果】 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
                res = ''
                # 👉 传入 comfyUI 的生图任务 ID, 查询生图进度
                res = check_image_status(prompt_id)
                res_data = res.get_json() # 在 Flask 中, 当使用 jsonify() 创建一个响应时，实际上是返回了一个 Flask Response 对象, 其中包含了 JSON 格式的字符串作为其数据。要访问这个数据, 需要先检查响应的状态码, 然后解析响应内容为 JSON
                img_name = res_data["9"]['images'][0]['filename']
                # image_url = f'{url}/view?filename={img_name}&subfolder=&type=temp' # 🔥 使用view 接口来获取图片信息
                view_image_path = f'{url}/view?filename={img_name}' # 🔥 使用view 接口来获取图片信息
                print("👍 生成了图片: \n", img_name, "\n")
                return view_image_path
                # print("🌟调试: ", view_image_url)
    
				# 🔥请求保存到服务器上的图片地址, 跟从网络上请求图片的逻辑一样！然后可以进一步的取保存为 base64 的图片数据
                # if res:
                    # res = requests.get(view_image_url) # print("🌟调试:", res.content[:100]) ## 调试：打印响应内容的前几个字节
                    # img_encode  = Image.open(io.BytesIO(res.content)) # 将图片转换为二进制流
                    # final_img = encode_pil_to_base64(img_encode) # 把二进制流编码为 base64 的图片数据
                    # return final_img # 返回编码后的图片数据流 => 图像数据的 Base64 编码。Base64 是一种编码方法，可以将二进制数据转换成 ASCII 字符串
            except Exception as e:
            	return jsonify({"❌ Error": str(e)}), 500

# 初始化 __main__
if __name__ == "__main__":
	app.run(port=5000, debug=True)


