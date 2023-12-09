import json
import os
from urllib import request, parse
import random
import re
prompt_workflow = {
  "3": {
    "inputs": {
      "seed": 1124855505231818,
      "steps": 1,
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
      "text": "(1 girl: 1. 1), sitting on the throne, a wizard staff in hand, (close-up photo: 1. 2), sidelighting, perfect ligthing, bloom, cinematic lighting, film grain, ((masterpiece, best quality)),full body, chibi,",
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
      "steps": 1,
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

# 创建一个提示列表
prompt_list = []
prompt_list.append("photo of a man sitting in a cafe")
prompt_list.append("photo of a woman standing in the middle of a busy street")
prompt_list.append("drawing of a cat sitting in a tree")
prompt_list.append("beautiful scenery nature glass bottle landscape, purple galaxy bottle")





def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    prompt_list = []
    prompt_list.append("beautiful scenery nature glass bottle landscape, purple galaxy bottle")
    chkpoint_loader_node = prompt_workflow["4"]
    prompt_pos_node = prompt_workflow["6"]
    empty_latent_img_node = prompt_workflow["19"]
    ksampler_node = prompt_workflow["12"]
    
    chkpoint_loader_node["inputs"]["ckpt_name"] = "SD1-5/sd_v1-5_vae.ckpt"
    empty_latent_img_node["inputs"]["width"] = 512
    empty_latent_img_node["inputs"]["height"] = 640
    for index, prompt in enumerate(prompt_list): # enumerate 表示同时遍历索引和元素
        prompt_pos_node["inputs"]["text"] = prompt
        ksampler_node["inputs"]["seed"] = random.randint(1, 18446744073709551614)
	
    req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
    request.urlopen(req)  
 
if __name__ == "__main__":
    queue_prompt(prompt_workflow)
    print("Done")
