from svaeva import Svaeva

from icecream import ic

svaeva = Svaeva()


try:
    ic(svaeva.multi_api.skeleton(id="open_ai"))
except Exception as e:
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