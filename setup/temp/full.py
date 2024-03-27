import base64
import json
from svaeva.Paths.MultiAPI.Models import DataModel

from typing import Any


class full(DataModel):

    def __init__(self,token):
        super().__init__(token)
        self.add_model("open_ai")
        self.add_model("deepgram")
        self.add_model("elevanlabs")
        self.load_wallet()
        self.load_config("auto_deep")
        self.load_config("voice_rachel_elevanlabs")
        self.load_config("psych-vision")

    def build_history(self,config,data):
        model = config["config"]["model"]
        targets = {
            "gpt-4-turbo": 128000,
            "gpt-4-vision-preview": 128000,
            "gpt-4": 8192,
            "gpt-4-0613": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-32k-0613": 32768,
            "gpt-3.5-turbo-1106": 16385,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
            "gpt-3.5-turbo-instruct": 4097,
            "gpt-3.5-turbo-0613": 4096,
            "gpt-3.5-turbo-16k-0613": 16384,
            "text-davinci-003": 4097,
            "text-davinci-002": 4097,
            "code-davinci-002": 8001
        }
        tokens = 0
        target = targets[model]
        list_action = []
        history = self.svaeva.database.actions(user_id=data["sender"],model_id="costume_llm")
        for i in history[::-1]:
            if i["content_type"] == "str":
                tokens += len(i["content_text"])
                if tokens >= target:
                    break
                agent_type = "assistant"
                if i["direction"] == "user_to_model":
                    agent_type = "user"
                list_action.append({
                    "role":agent_type,
                    "content":i["content_text"]
                })
        [config["config"]["messages"].append(_) for _ in list_action[::-1]]
        return config

    def forward(self,data : Any) -> Any:
        if data["type"] == "websocket.receive":
            data = json.loads(data["text"])
        if data is None:
            return "I don't understand"
        output = {
            "sender":data["sender"],
            "type":"text",
            "text": "I don't understand",
            "platform": data["platform"]
        }
        if data["type"] == "voice":
            # Voice to text
            for i in range(3):
                try:
                    config = self.configs["auto_deep"]
                    deep_reply = self.ai_models["deepgram"].pre_recode(params=config["config"]["param"],json={"url":data["voice"]})
                    data["text"] = deep_reply.json()
                    data["text"] = data["text"]["results"]["channels"][0]
                    data["text"] = data["text"]["alternatives"][0]
                    data["text"] = data["text"]["transcript"]
                    output["text"] = data["text"]
                    self.store(data=data,skeleton="deepgram",config=config["id"],user=False)
                    # Text to text
                    open_reply_text = self.svaeva.multi_api.forward.send(model_id="costume_llm",input_data=output)
                    if ":" in open_reply_text:
                        open_reply_text = open_reply_text.split(":")[-1]
                        if open_reply_text.startswith("** "):
                            open_reply_text = open_reply_text[2:]
                    # Text to speech
                    output["text"] = open_reply_text
                    audio_reply = self.ai_models["elevanlabs"].text_to_speech(url_params=self.configs["voice_rachel_elevanlabs"]["config"]["url_params"],json={"text":open_reply_text})
                    if audio_reply.status_code == 200:
                        output["text"] = None
                        output["type"] = "voice"
                        output["voice"] = base64.b64encode(audio_reply.content).decode('utf-8')
                        self.store(data=output,skeleton="elevanlabs",config=self.configs["voice_rachel_elevanlabs"]["id"],user=False)               
                        return output
                except Exception as e:
                    print(e)
                    return output
            return output
        elif data["type"] == "text":
            output["text"] = data["text"]
            open_reply_text = self.svaeva.multi_api.forward.send(model_id="costume_llm",input_data=output)
            if ":" in open_reply_text:
                open_reply_text = open_reply_text.split(":")[-1]
                if open_reply_text.startswith("** "):
                    open_reply_text = open_reply_text[2:]
            output["text"] = open_reply_text
            return output
        elif data["type"] == "image":
            # Image to text
            history = self.build_history(config=self.configs["psych-vision"],data=data)
            config = history["config"]["messages"].pop(0)
            if "text" in data.keys():
                config["content"][0]["text"] = data["text"]
                config["content"][1]["image_url"] = {
                    "url":data["image"]
                }
            history["config"]["messages"].append(config)
            reply = self.ai_models["open_ai"].complete(json=history["config"])
            if reply.status_code == 200:
                output["text"] = reply.json()["choices"][0]["message"]["content"]
                
                output["text"] = self.svaeva.multi_api.forward.send(model_id="costume_llm",input_data=output)
                #if ":" in open_reply_text:
                #    output["text"] = output["text"].split(":")[-1]
                #    if open_reply_text.startswith("** "):
                #        open_reply_text = open_reply_text[2:]
                return output
            output["text"] = str(reply.text)
            return output      
        return output