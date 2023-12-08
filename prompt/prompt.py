PROMPT = {
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