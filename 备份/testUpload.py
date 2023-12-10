import requests 
import io
import json
import os
import time
from dotenv import load_dotenv # 用来加载环境变量
from requests_toolbelt import MultipartEncoder


def upload_file():
    file_size = os.path.getsize("/Users/XXX/ComfyUI/output/ComfyUI_00116_.png") # 获取文件大小
    url = "https://open.feishu.cn/open-apis/drive/v1/files/upload_all" # 上传接口
    
    # 以表单形式提交数据
    form = {'file_name': 'ComfyUI_00115_',
            'parent_type': 'explorer',
            'parent_node': "XXX",
            'size': str(file_size),
            'file': (open('/Users/XXX/ComfyUI/output/ComfyUI_00116_.png', 'rb'))}  
    multi_form = MultipartEncoder(form)
    
    # 验证 token + 设置 Content-Type
    headers = {
		"Authorization": "Bearer t-XXX",
	}
    
    headers['Content-Type'] = multi_form.content_type
    
    print("📤 开始上传文件... \n")
    response = requests.request("POST", url, headers=headers, data=multi_form)
    response_data = response.json()
    # 返回 file_token
    print("📤 上传文件成功: \n", response_data)
    
    
if __name__ == '__main__':
    upload_file()