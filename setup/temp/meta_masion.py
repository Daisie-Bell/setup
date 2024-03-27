import asyncio
import json
from svaeva.Paths.MultiAPI.Models import DataModel

from typing import Any
import base64

class meta_masion(DataModel):

    def __init__(self,token):
        super().__init__(token)
        self.add_model("open_ai")
        self.add_model("deepgram")
        self.add_model("elevanlabs")
        self.load_wallet()
        self.load_config("auto_deep")
        self.load_config("voice_rachel_elevanlabs")
        self.load_config("psyco-llm")
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
                tokens += len(i["content_text"])/2
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
    
    async def processer(self):
        while True:
            if not self.incoming_messages.empty():
                work_data = await self.incoming_messages.get()
                if work_data["type"] == "voice":
                    config = self.configs["auto_deep"]
                    self.store(data=work_data,skeleton="deepgram",config=config["id"])
                    deep_reply = self.ai_models["deepgram"].pre_recode(params=config,json={"url":work_data["voice"]})
                    work_data["text"] = deep_reply.json()
                    work_data["text"] = work_data["text"]["results"]["channels"][0]
                    work_data["text"] = work_data["text"]["alternatives"][0]
                    work_data["text"] = work_data["text"]["transcript"]
                    work_data["text"] = work_data["text"]
                    self.store(data=work_data,skeleton="deepgram",config=config["id"])
                    work_data["type"] = "text"
                    work_data["output"] = "voice"
                    await self.incoming_messages.put(work_data)
                elif work_data["type"] == "text":
                    self.store(data=work_data,skeleton="open_ai",config=None,user=True)
                    open_reply_text = self.svaeva.multi_api.forward.send(model_id="costume_llm",input_data=work_data)
                    work_data["text"] = open_reply_text
                    if "output" in work_data.keys():
                        if work_data["output"] == "voice":
                            audio_reply = self.ai_models["elevanlabs"].text_to_speech(url_params=self.configs["voice_rachel_elevanlabs"]["config"]["url_params"],json={"text":work_data["text"]})
                            if audio_reply.status_code == 200:
                                work_data["text"] = None
                                work_data["type"] = "voice"
                                work_data["voice"] = base64.b64encode(audio_reply.content)
                                self.store(data=work_data,skeleton="elevanlabs",config=self.configs["voice_rachel_elevanlabs"]["id"],user=False)
                                await self.ongoing_messages.put(work_data)
                    else:
                        self.ongoing_messages.put_nowait(work_data)
                elif work_data["type"] == "image":
                    config = self.configs["psych-vision"]
                    config["config"]["messages"][0]["content"][1]["image_url"]["url"] = work_data["image"]
                    row_output_open_ai = self.ai_models["open_ai"].complete(json=self.configs["vision"]["config"])
                    if row_output_open_ai.status_code == 200:
                        work_data["text"] = row_output_open_ai.json()["choices"][0]["message"]["content"]
                        await self.incoming_messages.put(work_data)
                else:
                    await self.ongoing_messages.put({
                            "type" : "text",
                            "text" : "I don't understand"
                        })
                    

    def forward(self, data: Any) -> Any:
        self.incoming_messages = asyncio.Queue()
        self.ongoing_messages = asyncio.Queue()

        if data["type"] == "websocket.receive":
            data = json.loads(data["text"])
        if data is None:
            return "I don't understand"
        self.incoming_messages.put_nowait(data)
        asyncio.run(self.processer())  # Modified line
        while self.ongoing_messages.empty():
            pass
        return self.ongoing_messages.get_nowait()