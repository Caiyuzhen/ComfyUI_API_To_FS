import requests 
import io
import json
from PIL import Image
import base64
from flask import Flask, request, jsonify


url = "http://127.0.0.1:8188"

app = Flask(__name__)


@app.route('/generate') # 访问 🔥 http://127.0.0.1:5000/generate?text=girl
def index():
    text = request.args.get('text')  # 从查询字符串中获取 text 参数 => 🌟 例如 http://127.0.0.1:5000/generate-image?text=girl
    if not text:
        return "缺少 text 参数", 400  # 如果 text 参数不存在，则返回错误
    else:
        # return "1"
        # img_name = None
# 		image_url = None
# 		rqu_img_url = None

		# 🌟 checkpoints list (读取所有节点信息)
		response = requests.get(url=f'{url}/object_info/CheckpointLoaderSimple') # 读取所有 checkpoint 节点信息
		response = requests.get(url=f'{url}/object_info/VAELoader') # 读取所有 VAE 节点信息
		formatted_json = json.dumps(json.loads(response.text), indent=4) # 将 JSON 字符串转换为 Python 字典，然后使用 json.dumps 将字典转换回格式化的字符串。indent=4 参数意味着它将使用4个空格进行缩进
		# print(formatted_json)


		# 🌟 文生图 - 【1 : 发送生图请求】 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
		PROMPT = {	 # 导入工作流
			"3": {
		"inputs": {
		"seed": 1124855505231818,
		"steps": 20,
		"cfg": 8,
		"sampler_name": "euler",
		"scheduler": "karras",
		"denoise": 1,
		"model": [
			"17",
			0
		],
		"positive": [
			"6",
			0
		],
		"negative": [
			"7",
			0
		],
		"latent_image": [
			"5",
			0
		]
		},
		"class_type": "KSampler"
		},
		"4": {
		"inputs": {
		"ckpt_name": "rev-animated-v1-2-2.safetensors"
		},
		"class_type": "CheckpointLoaderSimple"
		},
		"5": {
		"inputs": {
		"width": 816,
		"height": 512,
		"batch_size": 1
		},
		"class_type": "EmptyLatentImage"
		},
		"6": {
		"inputs": {
		"text": text,
		"clip": [
			"17",
			1
		]
		},
		"class_type": "CLIPTextEncode"
		},
		"7": {
		"inputs": {
		"text": "embedding: BadDream,\n(embedding: UnrealisticDream: 1. 2)",
		"clip": [
			"17",
			1
		]
		},
		"class_type": "CLIPTextEncode"
		},
		"8": {
		"inputs": {
		"samples": [
			"3",
			0
		],
		"vae": [
			"4",
			2
		]
		},
		"class_type": "VAEDecode"
		},
		"10": {
		"inputs": {
		"images": [
			"8",
			0
		]
		},
		"class_type": "PreviewImage"
		},
		"11": {
		"inputs": {
		"lora_name": "blindbox_v1_mix.safetensors",
		"strength_model": 1,
		"strength_clip": 1,
		"model": [
			"4",
			0
		],
		"clip": [
			"4",
			1
		]
		},
		"class_type": "LoraLoader"
		},
		"12": {
		"inputs": {
		"seed": 1124855505231818,
		"steps": 20,
		"cfg": 8,
		"sampler_name": "euler",
		"scheduler": "karras",
		"denoise": 1,
		"model": [
			"4",
			0
		],
		"positive": [
			"13",
			0
		],
		"negative": [
			"14",
			0
		],
		"latent_image": [
			"19",
			0
		]
		},
		"class_type": "KSampler"
		},
		"13": {
		"inputs": {
		"text": "(1 girl: 1. 1), sitting on the throne, a wizard staff in hand, (close-up photo: 1. 2), sidelighting, perfect ligthing, bloom, cinematic lighting, film grain, ((masterpiece, best quality))",
		"clip": [
			"4",
			1
		]
		},
		"class_type": "CLIPTextEncode"
		},
		"14": {
		"inputs": {
		"text": "embedding: BadDream,\n(embedding: UnrealisticDream: 1. 2)",
		"clip": [
			"4",
			1
		]
		},
		"class_type": "CLIPTextEncode"
		},
		"16": {
		"inputs": {
		"images": [
			"18",
			0
		]
		},
		"class_type": "PreviewImage"
		},
		"17": {
		"inputs": {
		"lora_name": "superPaperlora.pt",
		"strength_model": 1,
		"strength_clip": 1,
		"model": [
			"11",
			0
		],
		"clip": [
			"11",
			1
		]
		},
		"class_type": "LoraLoader"
		},
		"18": {
		"inputs": {
		"samples": [
			"12",
			0
		],
		"vae": [
			"4",
			2
		]
		},
		"class_type": "VAEDecode"
		},
		"19": {
		"inputs": {
		"width": 512,
		"height": 512,
		"batch_size": 1
		},
		"class_type": "EmptyLatentImage"
		}
		}


		# 替换原来的提示词(非必需)
		PROMPT["6"]["inputs"]["text"] = "a girl"
		PROMPT["3"]["inputs"]["seed"] = 665437340080956

		# 请求信息块
		p = {"prompt": PROMPT}
		response = requests.post(url=f'{url}/prompt', json=p)
		response.json() # 不会马上响应, 只会返回个队列 ID 
		prompt_id = response.json()["prompt_id"]
		# print("返回了图片 id: ", prompt_id)


		if prompt_id :
			# 🌟 文生图 - 【2 : 获得生图结果】 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
			img_response_data = requests.get(url=f'{url}/history/{prompt_id}') # 🌟 这一步需要看一下返回的数据, 需要看下返回的 outputs 在哪个节点号！
			# print("返回了生成的数据: ", img_response_data.json())
			# return img_response_data.json()

			## from
			img_name = img_response_data.json()[prompt_id]['outputs']['16']['images'][0]['filename'] # 👈拼接出图片的文件名, 图片名需要看在哪个节点 !
			# print("图片名:", img_name)

			image_url = f'{url}/view?filename={img_name}&subfolder=&type=temp' # 🔥 view 接口来获取图片信息
			# print("图片地址:", image_url) # 🚀 最终获得了图片地址   =>   http://127.0.0.1:8188/view?filename=ComfyUI_temp_sgyjm_00001_.png&subfolder=&type=temp


			# 🌟 【get 请求】生成好的图片地址 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
			rqu_img_url = requests.get(image_url)
			# image = Image.open(io.BytesIO(response.content)) # 把 io 字节流转换为 PIL.Image.Image 对象
			# print("图片:", rqu_img_url)
			# encode_pil_to_base64(image) # 将图片转换为 base64 编码
			# print("图片 base64 编码后的图片:", image)
			# return rqu_img_url
			if rqu_img_url.status_code == 200:
				with open('downloaded_image.png', 'wb') as file:
					# file.write(rqu_img_url.content)
					print("图片已保存为 downloaded_image.png")
					img_name = None
					image_url = None
					rqu_img_url = None
					return image_url
			else:
				print("获取图片失败，状态码：", rqu_img_url.status_code)
				
			return image_url
			## end





# 初始化 __main__
if __name__ == "__main__":
	app.run(debug=True)
	# textInfo = 'a boy'
	# res = textToImage(textInfo)
	# print("👍最终获得图片:", res)


