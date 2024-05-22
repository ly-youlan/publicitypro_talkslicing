# from shortGPT.gpt import gpt_utils
import json

from TalkAutomation.gpt import gpt_utils
import time


def analyzeContent(content1, content2):
    chat, system = gpt_utils.load_local_yaml_prompt('prompt_templates/analyze_content.yaml')
    # system = system.replace("<<LANGUAGE>>", language)
    chat = chat.replace("<<CONTENT>>", content1)
    openai_api_key = " "

    # Call the GPT API for the first content
    result1 = gpt_utils.gpt3Turbo_completion(chat_prompt=chat, system=system, temp=1, api_key=openai_api_key)

    # Append the response to the conversation
    conversation = [
        {"role": "system", "content": system},
        {"role": "user", "content": chat.replace("<<CONTENT>>", content1)},
        {"role": "assistant", "content": result1}
    ]

    # Modify the prompt for the second content
    chat = chat.replace("<<CONTENT>>", content2)

    # Call the GPT API for the second content
    result2 = gpt_utils.gpt3Turbo_completion(chat_prompt=chat, system=system, temp=1, api_key=openai_api_key,
                                             conversation=conversation)

    return result1, result2


# Example usage:
_db_speech_blocks =[[[0, 1.26], '好 可以開始'], [[7.3, 19.08],
                                                               '教授您好請問您在深大多少年了我在深大24年了五年在深大讀書然後現在工作已經19年了'],
                                  [[19.98, 26.18], '那在畢業的時候是為什麼想要做這麼難過呢因為喜歡跟學生打交道'],
                                  [[27.0, 33.2], '是喜歡一直一直跟學生打交道所以選擇了做輔導員這個崗位'],
                                  [[34.3, 47.44],
                                   '希望這輩子的工作都是跟學生打交道如果說您現在可以擁有一個超能力您會選擇用什麼樣的超能力來更好地支持您的學生呢'],
                                  [[49.34, 69.16],
                                   '我現在希望我是一個模範女巫可以把所有學生的煩惱一模模的情緒都吸引過來然後把它做成世界上最快樂的糖果讓他們吃下去能每天都感受到世界上最快樂的那種感覺'],
                                  [[71.06, 83.82],
                                   '如果今年的工作要用三個詞來概括這三個詞會是什麼呢今年的工作對我而言是忙碌學習再出發'],
                                  [[84.94, 94.48],
                                   '因為就是已經做了這麼多年輔導員了直到今年才發現還有很多很多要學的所以希望是今年的學習之餘'],
                                  [[96.12, 99.98], '能再出發再去創造一下輔導員的其他奇蹟'], [[102.0, 109.34],
                                                                                             '在跟學生相處的過程中會不會有一些負面的情緒您是如何來排解這些情緒的呢'],
                                  [[110.5, 118.14], '負面的情緒肯定會有但是做輔導員年限越久就會越來越少'],
                                  [[119.42, 121.82], '排解這個最好的方法就是'],
                                  [[123.26, 127.48], '六狗鬥貓打孩子不行的話就罵一下老公吧'], [[129.84, 139.8],
                                                                                               '那今年的工作你是感覺累嗎挺累的每一年的工作其實都挺累的輔導員的工作是越來越細肯定會越來越累'],
                                  [[146.08, 153.02], '今年我最大的收穫是覺得我收穫了一個很好很好的小夥伴團隊'],
                                  [[154.12, 180.16],
                                   '因為在這之前學院裡的輔導員不多所以始終沒有是一個很積極相像的團隊然後現在我有了一個非常好的團隊有一幫很可愛的小夥伴還有就是所有人都能互相為對方著想互相為對方補台然後永遠都是遇到事情一起上這個是我覺得今年最大的收穫'],
                                  [[188.36, 194.54], '我相信力量吧力量應該說是從三個方面'], [[195.44, 231.72],
                                                                                             '一個是學生給我的力量真的是每年每年看著那些學生成功看著學生的喜怒哀樂然後看著他們一步步跨過很多坎他們給我的力量很足第二個方面是我的小夥伴團隊給我的力量真的是每一件事情大家都一起拼搏一起努力然後這個力量很足第三個力量應該說是家裡面給的力量因為家裡人都非常支持我這個工作所以說始終他們是最堅強的後盾'],
                                  [[240.9, 244.08], '還是喜歡跟學生打交道愛學生'], [[246.3, 246.66], '就這個'],
                                  [[248.0, 251.14], '講完了還有一個問題是'],
                                  [[252.14, 256.4], '您這邊要給對手說一句話的話你想說什麼'],
                                  [[259.0, 260.7], '人生苦短 即時行樂'], [[262.84, 263.8], '好 然後聽一下']]
content2 = "继续"

result1, result2 = analyzeContent(json.dumps(_db_speech_blocks), content2)

print("Result 1:", result1)
print("Result 2:", result2)
