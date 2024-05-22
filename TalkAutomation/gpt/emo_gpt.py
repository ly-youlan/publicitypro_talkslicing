from shortGPT.gpt import gpt_utils
import json

def generateFacts(facts_type):
    chat, system = gpt_utils.load_local_yaml_prompt('/Users/youlan/ShortGPT/TalkAutomation/prompt_templates'
                                                    '/facts_generator.yaml')
    chat = chat.replace("<<FACTS_TYPE>>", facts_type)
    # 在这里手动指定 OpenAI 的 API 密钥
    openai_api_key = ""
    result = gpt_utils.gpt3Turbo_completion(chat_prompt=chat, system=system, temp=1.3, api_key=openai_api_key)
    #result = gpt_utils.gpt3Turbo_completion(chat_prompt=chat, system=system, temp=1.3)
    print(f"emo_gpy return result:{result}")
    return result
def genreateEmoStory():
    chat, system = gpt_utils.load_local_yaml_prompt('/Users/youlan/ShortGPT/TalkAutomation/prompt_templates'
                                                    '/emo_generator.yaml')
    # chat = chat.replace("<<FACTS_TYPE>>", facts_type)
    # 在这里手动指定 OpenAI 的 API 密钥
    openai_api_key = " "
    result = gpt_utils.gpt3Turbo_completion(chat_prompt=chat, system=system, temp=1.3, api_key=openai_api_key)
    # result = gpt_utils.gpt3Turbo_completion(chat_prompt=chat, system=system, temp=1.3)
    # print(f"in emo_gpy return result:{result}") #debug
    return result

def generateFactSubjects(n):
    out = []
    chat, system = gpt_utils.load_local_yaml_prompt('prompt_templates/facts_subjects_generation.yaml')
    chat = chat.replace("<<N>>", f"{n}")
    count = 0
    while len(out) != n:
        result = gpt_utils.gpt3Turbo_completion(chat_prompt=chat, system=system, temp=1.69)
        count+=1
        try:
            out = json.loads(result.replace("'", '"'))
        except Exception as e:
            print(f"INFO - Failed generating {n} fact subjects after {count} trials", e)
            pass
        
    return out