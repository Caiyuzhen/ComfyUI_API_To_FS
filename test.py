import requests 
import io
import json
import base64
from PIL import Image
from flask import Flask, request, jsonify
from prompt.prompt import PROMPT


url = "http://127.0.0.1:8188" # comfyUI 的服务器地址

# 构建要发送到图片生成服务的数据
payload = {"prompt": PROMPT} # 假设图片生成服务需要一个名为'prompt'的字段
response = requests.post(url=f'{url}/prompt', json=payload) 
response.json() # 不会马上响应, 只会返回个队列 ID , 如果有 id 则是生成好了图片
prompt_id = response.json()["prompt_id"]
# print("返回了图片 id: ", prompt_id)

if prompt_id : # 如果有 id 则是生成好了图片
	# 文生图 - 【2 : 获得生图结果】 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
	img_response_data = requests.get(url=f'{url}/history/{prompt_id}') # 🌟 这一步需要看一下返回的数据, 需要看下返回的 outputs 在哪个节点号！
	formatted_json = json.dumps(img_response_data.json() , indent=2, ensure_ascii=False)
	print("返回了生成的数据: ", formatted_json)
 
	img_name = img_response_data.json()[prompt_id]['outputs']['16']['images'][0]['filename'] # 👈拼接出图片的文件名, 图片名需要看在哪个节点 !
	# print("图片名:", img_name)

	image_url = f'{url}/view?filename={img_name}&subfolder=&type=temp' # 🔥 view 接口来获取图片信息
	# print("图片地址:", image_url) # 🚀 最终获得了图片地址   =>   http://127.0.0.1:8188/view?filename=ComfyUI_temp_sgyjm_00001_.png&subfolder=&type=temp

	# 生成好的图片地址 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
	# rqu_img_url = requests.get(image_url)
	# if rqu_img_url.status_code == 200:
	#     with open('downloaded_image.png', 'wb') as file:
	# 		# file.write(rqu_img_url.content)
	#         print("图片已保存为 downloaded_image.png")
	#         return image_url

	# else:
	#     print("获取图片失败，状态码：", rqu_img_url.status_code)
		
	# return image_url



