import json
from typing import Any, Dict, List

from svaeva.Paths.MultiAPI.Models import DataModel

from typing import Any


class costume_llm(DataModel):
      
    def __init__(self,token) -> None:
        super().__init__(token)
        self.token = token
        print(self.svaeva)
        self.add_model("open_ai")
        self.load_wallet()

    def build_history(self,config,data):
        model = config["config"]["model"]
        targets = {
            "gpt-4-turbo": 128000,
            "gpt-4-turbo-with-vision": 128000,
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
        self.store(data=data,skeleton="open_ai",config=self.configs["open_ai"]["id"],user=True)
        try:
            llm = self.build_history(config=self.configs["open_ai"],data=data)
            [self.configs["open_ai"]["config"]["messages"].append(_) for _ in llm]
        except Exception as e:
            print(e)
            self.configs["open_ai"]["config"]["messages"].append({
                "role":"user",
                "content":data["text"]
            })
        reply = self.ai_models["open_ai"].complete(json=self.configs["open_ai"]["config"])
        if reply.status_code == 200:
            print(reply.json())
            data["text"] = reply.json()["choices"][0]["message"]["content"]
            print(data["text"])
            self.store(data=data,skeleton="open_ai",config=self.configs["open_ai"]["id"],user=False)
            return data["text"]
        print(reply.status_code)
        print(reply.text)
        return "I don't understand"