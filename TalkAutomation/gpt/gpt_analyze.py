from TalkAutomation.gpt import gpt_utils
def analyzeContent(content):
    chat, system = gpt_utils.load_local_yaml_prompt('prompt_templates/analyze_content_no_detail.yaml')
    # system = system.replace("<<LANGUAGE>>", language)
    chat = chat.replace("<<CONTENT>>", content)
    openai_api_key = ""

    result = gpt_utils.gpt3Turbo_completion(chat_prompt=chat, system=system, temp=1, api_key=openai_api_key)
    return result