import requests 
from PIL import Image
import io
import base64

# url = "http://127.0.0.1:8188/"

# def decode_base64_to_image(encoding):
#     if encoding.startswith("data:image/"):
#         encoding = encoding.split(";")[1].split(",")[1]
#     image = Image.open(io.BytesIO(base64.b64encode(encoding)))
#     return image

# def encode_pil_to_base64(image):
#     with io.BytesIO() as output_bytes:
#         image.save(output_bytes, format="PNG")
#         bytes_data = output_bytes.getvalue()
#     return base64.b64decode(bytes_data).decode("utf-8")
import json
url = "http://127.0.0.1:8188"
img_name = None
rqu_img_url = None



def textToImage(text):
	# 🌟 checkpoints list (读取所有节点信息)
	response = requests.get(url=f'{url}/object_info/CheckpointLoaderSimple') # 读取所有 checkpoint 节点信息
	response = requests.get(url=f'{url}/object_info/VAELoader') # 读取所有 VAE 节点信息
	formatted_json = json.dumps(json.loads(response.text), indent=4) # 将 JSON 字符串转换为 Python 字典，然后使用 json.dumps 将字典转换回格式化的字符串。indent=4 参数意味着它将使用4个空格进行缩进
	# print(formatted_json)


	# 🌟 文生图 - 【1 : 发送生图请求】 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
	PROMPT = {	 # 导入工作流
		"3": {
			"inputs": {
			"seed": 865437340080956,
			"steps": 15,
			"cfg": 8,
			"sampler_name": "euler",
			"scheduler": "karras",
			"denoise": 1,
			"model": [
				"4",
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
			"ckpt_name": "3d_Toon_Diffusion_XL.fp16.safetensors"
			},
			"class_type": "CheckpointLoaderSimple"
		},
		"5": {
			"inputs": {
			"width": 512,
			"height": 512,
			"batch_size": 1
			},
			"class_type": "EmptyLatentImage"
		},
		"6": {
			"inputs": {
			"text": text,
			"clip": [
				"4",
				1
			]
			},
			"class_type": "CLIPTextEncode"
		},
		"7": {
			"inputs": {
			"text": "text, watermark",
			"clip": [
				"4",
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
	print("返回了图片 id: ", prompt_id)


	if prompt_id :
		# 🌟 文生图 - 【2 : 获得生图结果】 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
		img_response_data = requests.get(url=f'{url}/history/{prompt_id}') # 看一下返回的数据, 需要看下返回的 outputs 在哪个节点号！
		# print("返回了生成的数据: ", img_response_data.json())

		img_name = img_response_data.json()[prompt_id]['outputs']['10']['images'][0]['filename'] # 👈拼接出图片的文件名, 图片名需要看在哪个节点 !
		print("图片名:", img_name)

		image_url = f'{url}/view?filename={img_name}&subfolder=&type=temp' # 🔥 view 接口来获取图片信息
		print("图片地址:", image_url) # 🚀 最终获得了图片地址   =>   http://127.0.0.1:8188/view?filename=ComfyUI_temp_sgyjm_00001_.png&subfolder=&type=temp


		# 🌟 【get 请求】生成好的图片地址 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
		rqu_img_url = requests.get(image_url)
		# image = Image.open(io.BytesIO(response.content)) # 把 io 字节流转换为 PIL.Image.Image 对象
		print("图片:", rqu_img_url)
		# encode_pil_to_base64(image) # 将图片转换为 base64 编码
		# print("图片 base64 编码后的图片:", image)
		# return rqu_img_url
		if rqu_img_url.status_code == 200:
			with open('downloaded_image.png', 'wb') as file:
				file.write(rqu_img_url.content)
				img_name = None
				rqu_img_url = None
			print("图片已保存为 downloaded_image.png")
		else:
			print("获取图片失败，状态码：", rqu_img_url.status_code)



def chooseWorkflow(workflow_name):
# 🌟 通过接口请求自定义的工作流 ————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————
	workflow_A = r(f"/Users/ai/Desktop/{workflow_name}.json") # 读取工作流 json 文件
	with open(workflow_A, "r", encoding='utf-8') as f: # 读取工作流 json 文件
		prompt_text = f.read()
	
	prompt2 = json.loads(prompt_text) # 将 json 字符串转换为 Python 字典数据
	p2 = {"prompt": prompt2} # 接下来的流程同上...



# 初始化 __main__
if __name__ == "__main__":
	textInfo = 'a boy'
	res = textToImage(textInfo)
	print("👍最终获得图片:", res)


