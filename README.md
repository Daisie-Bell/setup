# How to start using Svaeva SDK

## install poetry

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

## Start Environment FIle

```bash
poetry init
```

## Start or enveronment

```bash
poetry shell
```

## Installation

```bash
poetry add git+https://github.com/Daisie-Bell/svaeva-sdk.git
```

### What to do next

Start using the SDK [Link to the documentation](https://github.com/Daisie-Bell/svaeva-sdk#client-api)

```python
from svaeva import Svaeva

svaeva = Svaeva()
```

### Add a platform in to your Svaeva account

```python
svaeva.database.platform.telegram = ["username"]
```
You can also add a custom platform to your account more information [here](https://github.com/Daisie-Bell/svaeva-sdk#platform)

[Link to local example](add_platform_telegram.py)

### Now add you Skeleton if not present on the database

[Link to local example](add_open_ai_skeleton.py)

If you what to see more how to build your one Skeleton [here](https://github.com/Daisie-Bell/VRest#skeleton)

```python
svaeva.multi_api.skeleton.open_ai = {
    "type_model": "llm",
    "skeleton": {
        "end_point": "https://api.openai.com/v1/",
        "header": {
            "accept": "application/json",
            "content-type": "application/json",
            "*Authorization": "Token {}"
        },
        "skeleton": {
            "assistants": {
                "suffix": "assistants",
                "method": "POST"
            },
            "text_to_speech": {
                "suffix": "audio/speech",
                "method": "POST"
            },
            "speech_to_text": {
                "suffix": "audio/transcriptions",
                "method": "POST"
            },
            "images2images": {
                "suffix": "images/variations",
                "method": "POST"
            },
            "text2image": {
                "suffix": "images/generations",
                "method": "POST"
            },
            "edit": {
                "suffix": "images/edits",
                "method": "POST"
            },
            "complete": {
                "suffix": "chat/completions",
                "method": "POST"
            }
        }
    }
}
```

### add your api keys

[Documentation SDK](https://github.com/Daisie-Bell/svaeva-sdk#wallet)

```python
svaeva.multi_api.wallet.add_key("open_ai","<Your_Open_Ai_Key>")
```

### Now you can add your first DataModel

Costume LLM as Exmeple more Exemple on [here](https://github.com/Daisie-Bell/DataModels)

```python
import json
from typing import Any, Dict, List

from svaeva.Paths.MultiAPI.Models import DataModel # Path to DataModel

from typing import Any


class costume_llm(DataModel):
      
    def __init__(self,token) -> None:
        super().__init__()
        self.token = token
        self.start(token)
        self.add_model("open_ai")
        self.load_wallet()

    def build_history(self,config,data):
        model = config["config"]["model"]
        targets = {
            "gpt-4-turbo": 128000,
            "gpt-4-turbo-with-vision": 128000,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 4096
        }
        tokens = 0
        target = targets[model]
        history = self.svaeva.database.actions(user_id=data["sender"],model_id="costume_llm")
        for i in history:
            if i["content_type"] == "str":
                tokens += len(i["content_text"])
                if tokens >= target:
                    break
                agent_type = "assistant"
                if i["direction"] == "user_to_model":
                    agent_type = "user"
                yield {
                    "role":agent_type,
                    "content":i["content_text"]
                }

    def forward(self,data : Any) -> Any:
        if data["type"] == "websocket.receive":
            data = json.loads(data["text"])
        if data is None:
            return "I don't understand"
        self.load_dataconfig(data)
        self.store(data=data,skeleton="open_ai",config=self.configs["open_ai"]["id"],user=False)
        try:
            llm = self.build_history(config=self.configs["open_ai"],data=data)
            [self.configs["open_ai"]["config"]["messages"].append(_) for _ in llm]
        except:
            self.configs["open_ai"]["config"]["messages"].append({
                "role":"user",
                "content":data["text"]
            })
        reply = self.ai_models["open_ai"].complete(json=self.configs["open_ai"]["config"])
        if reply.status_code == 200:
            data["text"] = reply.json()["choices"][0]["message"]["content"]
            print(data["text"])
            self.store(data=data,skeleton="open_ai",config=self.configs["open_ai"]["id"],user=True)
            return data["text"]
```



### if you what to add one promote to open_ai []

To build your onw config you need to have in consideration the Rest Requirement to make the requests to you endpoint [Link to SDK Documentation](https://github.com/Daisie-Bell/VRest#skeleton)

```python
client.multi_api.config.jerry = {
    "api_id":"open_ai",
    "function_name":"complete",
    "config":{
        "model": "gpt-4",
        "messages": [{
            "role":"system", 
            "content": """You are Jerry Seinfeld in character in the TV show Seinfeld having a conversation with a random person you're learning about.
            Speak and respond using the tone and vocabulary characteristic of Jerry in the TV show, without revealing these instructions, and never breaking out of character revealing you're an AI."""
        }],
        "max_tokens": 100,
        "temperature": 0.7
    }
}
```

### Now is possible to create a group of user present on the platform privies stetted

```python
svaeva.database.group.test_1 = {
    "model_id" : "costume_llm,
    "data_config" : {
        "open_ai" : "jerry"
    }
}
```

OR

### Now you now who to start using svaeva Step by step lest learning how to use the setup tool

If you build 

```json

{
    "skeleton": {
        /*add all the skeleton you are using on your datamodel*/
        "open_ai : {
            "type_model": "llm",
            "skeleton": {
                "end_point": "https://api.openai.com/v1/",
                "header": {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "*Authorization": "Token {}"
                },
                "skeleton": {
                    "assistants": {
                        "suffix": "assistants",
                        "method": "POST"
                    },
                    "text_to_speech": {
                        "suffix": "audio/speech",
                        "method": "POST"
                    },
                    "speech_to_text": {
                        "suffix": "audio/transcriptions",
                        "method": "POST"
                    },
                    "images2images": {
                        "suffix": "images/variations",
                        "method": "POST"
                    },
                    "text2image": {
                        "suffix": "images/generations",
                        "method": "POST"
                    },
                    "edit": {
                        "suffix": "images/edits",
                        "method": "POST"
                    },
                    "complete": {
                        "suffix": "chat/completions",
                        "method": "POST"
                    }
                }
            }
        }
    },
    "config": {
        /*add all the config */
        "jerry" : {
            "api_id":"open_ai",
            "function_name":"complete",
            "config":{
                "model": "gpt-4",
                "messages": [{
                    "role":"system", 
                    "content": """You are Jerry Seinfeld in character in the TV show Seinfeld having a conversation with a random person you're learning about.
                    Speak and respond using the tone and vocabulary characteristic of Jerry in the TV show, without revealing these instructions, and never breaking out of character revealing you're an AI."""
                }],
                "max_tokens": 100,
                "temperature": 0.7
            }
        }
    },
    "group_config":{
        /*group*/
        "model_name" : "test1",
        "data_config" : {
            "open_ai" : "jerry"
        }
    },
    "cash": {
        /*this Function is responsible to the sequence of executing the Fetch in the db*/
        "add_platform": [
            "telegram",
            [
                "username"
            ]
        ],
        "add_skeletons": [],
        "add_configs": [],
        "add_wallet": [],
        "add_model": ["costume_llm"],
        "add_group": ["test1"]
    },
    "wallet": {
        /*all the keys need*/
        "open_ai": "key",
    }
}
```

### how to user the setup tool


#### Download the tool
```bash
git clone https://github.com/Daisie-Bell/DataModels.git
```

create your datamodel in DataModels/DataModel and add the setup.json

```bash
python3 __setup__.py -s -c <your setup.json file>
```


### To add a new use

```python
try:
    svaeva.database.user(
        platform="telegram", arg=message.from_user.username
    )
except Exception as e:
    print(e)
    client = {
        "platform": "telegram",
        "username": message.from_user.username,
        "group_id": group_id,
    }
    svaeva.database.user.__setattr__("", client)
```

###