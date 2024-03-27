from pathlib import Path
from typing import Generator, List, Tuple

from svaeva import Svaeva

import os

import time

from icecream import ic

from dotenv import load_dotenv

load_dotenv()

class Handler():

    cashed_error = {}

    def __init__(self,working_dir="./temp",environment_dir="./env") -> None:

        self.svaeva = Svaeva(f'http://{os.getenv("SVAEVA_IP")}:{os.getenv("SVAEVA_PORT")}',os.getenv("Svaeva_Key"))
        self.work = Path(working_dir)
        self.env = Path(environment_dir)
        self.add_working_paths()

    def add_working_paths(self) -> None:
        self.work.mkdir(parents=True,exist_ok=True)
        self.env.mkdir(parents=True,exist_ok=True)

    def get_platform(self,model_name) -> List[str]:
        for path in Path("./Output/").glob(f"{model_name}*.json"):
            return path.name.split("_")[-1].split(".")[0]
    
    def download_models(self) -> None:
        for models in self.svaeva.multi_api.virtual():
            if models["id"] not in [_ for _ in self.load_models()]:
                with open(self.env / "models.json","a") as file:
                    file.write(f"{models['id']} \n")
            with open(self.work / f"{models['id']}.py","w") as file:
                file.write(models["row_code"])
    
    def input_platform(self,model_name) -> str:
        platform_name = ""
        while True:
            if self.get_platform(model_name) is None:
                print("Platform not found!")
                platform_name  = input("Please insert the platform name: ")
                if platform_name == "":
                    print("Platform name cannot be empty!")
                else:
                    if platform_name not in [_["id"] for _ in self.svaeva.database.platform()]:
                        print("Platform not found!")
                    else:
                        break
            else:
                platform_name = self.get_platform(model_name)
                break
        return platform_name
    
    def update_row_code(self,model_name) -> bool:
        print("\nChecking for changes in [{}]...        ".format(model_name), end="\r")
        if model_name.endswith(".py"):
            model_name = model_name.replace(".py","")
        if model_name not in [_ for _ in self.load_models()]:
            return False
        try:
            models = self.svaeva.multi_api.virtual(id=model_name)
        except Exception as e:
            open(self.env / "models.json","w").write("\n".join([_ for _ in open(self.env / "models.json").read().split("\n") if _.split(" ")[0] != model_name]))
            return True
        if models["status"] is not None:
            if models["status"] == "error":
                if model_name not in self.cashed_error.keys():
                    self.cashed_error[model_name] = models["error"]
                    ic(models["error"])
                    return False
                elif self.cashed_error[model_name] != models["error"]:
                    print("\033[A"*len(self.cashed_error[model_name].split("\n")))
                    self.cashed_error[model_name] = models["error"]
                    ic(models["error"])
                    return False
        try:
            local_code = open(self.work / f"{models['id']}.py","r").read()
            if local_code != models["row_code"]:
                self.svaeva.multi_api.virtual.update(models["id"],{"row_code":local_code})
                if model_name in self.cashed_error.keys():
                    print("                 \033[A"*(len(self.cashed_error[model_name].split("\n")*2)))
                    self.cashed_error[model_name] = None
                print()
                return True
            elif models["row_code"] != local_code:
                with open(self.work / f"{models['id']}.py","w") as file:
                    file.write(models["row_code"])
                    return True
        except Exception as e:
            ic(model_name)
            with open(self.work / f"{models['id']}.py","w") as file:
                file.write(models["row_code"])
                return True
        return False

    def load_models(self) -> Generator[str,None,None]:
        models= [_.split(" ")[0] for _ in open(self.env / "models.json").read().split("\n")]
        models.append('')
        for new_model in Path(self.work).glob("*.py"):
            new_model = new_model.name.removesuffix('.py')
            if new_model not in models:
                with open(self.env / "models.json","a") as file:
                    models.append(new_model)
                    file.write(f"{new_model} {self.input_platform(new_model)}\n")
        for _ in open(self.env / "models.json").read().split("\n"):
            if _ != "":
                yield _.split(" ")[0]

    def continues_integration(self) -> None:
        chash_error = {}
        while True:
            for model_name in self.load_models():
                if self.update_row_code(model_name):
                    if not Path(f"./Output/{model_name}_{self.get_platform(model_name)}.json").exists():
                        platform_name = self.input_platform(model_name)
                        os.system("sudo poetry run python3 __setup__.py --build --model_name {} --platform_name {}".format(model_name,platform_name))
                    else:
                        platform_name = self.get_platform(model_name)
                    os.system("sudo poetry run python3 __setup__.py --setup --config ./Output/{}".format(model_name+"_"+platform_name))
                    if model_name.endswith(".py"):
                        model_name.replace(".py","")
                    messages =  self.svaeva.database.actions(model_id=model_name)
                    if isinstance(messages,list):
                        for _ in messages:
                            message = {
                                "type": _["content_type"],
                                _["content_type"]: _["content_text"],
                                "sender": _["user_id"],
                                "platform": _["platform"]
                            }
                            self.svaeva.multi_api.forward.send(model_id=model_name,input_data=message)
                        check = self.svaeva.multi_api.virtual(id=model_name.replace(".py",""))
                        if check["status"] == "error":
                            if model_name not in chash_error.keys():
                                chash_error[model_name] = None
                            if chash_error[model_name] is not None and chash_error[model_name] != check["error"]:
                                chash_error[model_name] = check["error"]
                                ic(check["error"])
                else:
                    print("                                      \033[A\033[A")
                    print("No changes detected no [{}]!         ".format(model_name),end="")
                    
                    time.sleep(0.5)

if __name__ == "__main__":
    handler = Handler()
    handler.download_models()
    handler.continues_integration()