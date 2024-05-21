import os
import traceback
from TalkAutomation.audio.eleven_voice_module import ElevenLabsVoiceModule
from TalkAutomation.audio.moyin_voice_module import MoyinVoiceModule
from TalkAutomation.audio.coqui_voice_module import CoquiVoiceModule
from TalkAutomation.config.languages import Language
from TalkAutomation.config.asset_db import AssetDatabase, AssetType

from TalkAutomation.engine.talk_short_engine import HonorShortEngine


class talkAutomation:
    def __init__(self):
        self.progress_counter = 0

    def create_short(self, numShorts, language_eleven, numImages, watermark, background_video_list,
                     background_music_list, facts_subject, voice_eleven):
        try:
            numShorts = int(numShorts)
            numImages = int(numImages) if numImages else None
            background_videos = (background_video_list * ((numShorts // len(background_video_list)) + 1))[:numShorts]
            background_musics = (background_music_list * ((numShorts // len(background_music_list)) + 1))[:numShorts]

            language = Language(language_eleven.lower().capitalize())
            # # 指定 ELEVEN LABS 的 API 密钥
            # eleven_labs_api_key = "d2cb3c18f01204d7445ef1c128c53d8f"
            # voice_module = ElevenLabsVoiceModule(eleven_labs_api_key, voice_eleven, checkElevenCredits=True)

            moyin_api_key = "552C7566356DF7A256C23D93466331F8"
            moyin_secret = "300591A6C20003089AE54C09D643310F"
            moyin_voiceName = "mercury_yunxi_24k@sad"
            # voice_module = MoyinVoiceModule(moyin_api_key, moyin_secret, moyin_voiceName)
            voice_module = CoquiVoiceModule("Ana Florence","zh-cn")

            for i in range(numShorts):
                shortEngine = self.create_short_engine(voice_module=voice_module, language=language,
                                                       numImages=numImages, watermark=watermark,
                                                       background_video=background_videos[i],
                                                       background_music=background_musics[i],
                                                       facts_subject=facts_subject)
                num_steps = shortEngine.get_total_steps()

                def logger(prog_str):
                    print(f"Making short {i + 1}/{numShorts} - {prog_str}")

                shortEngine.set_logger(logger)

                for step_num, step_info in shortEngine.makeContent():
                    print(f"Making short {i + 1}/{numShorts} - {step_info}")
                    self.progress_counter += 1

                video_path = shortEngine.get_video_output_path()
                save_path = os.path.join("videos", f"output_video_{i}.mp4")
                os.makedirs("videos", exist_ok=True)
                os.rename(video_path, save_path)

        except Exception as e:
            traceback_str = ''.join(traceback.format_tb(e.__traceback__))
            error_name = type(e).__name__.capitalize() + " : " + f"{e.args[0]}"
            print("Error", traceback_str)
            print(error_name)

    def create_short_engine(self, voice_module, language, numImages, watermark, background_video, background_music,
                            facts_subject):
        return HonorShortEngine(voice_module, facts_type=facts_subject, background_video_name=background_video,
                                background_music_name=background_music, num_images=50, watermark=watermark,
                                language=language)


# 创建 ShortAutomation 实例
talk_automation = talkAutomation()

# 添加初始化和数据添加步骤
# AssetDatabase.sync_local_assets()  # 同步本地资产
AssetDatabase.add_local_asset('Music dj quads', AssetType.BACKGROUND_MUSIC,
                              '/Users/youlan/ShortGPT/public/Music dj quads.wav')  # 添加 'Music dj quads' 本地资产
AssetDatabase.add_local_asset('huya', AssetType.BACKGROUND_VIDEO, '/Users/youlan/ShortGPT/shortGPT/public/huya.mp4')

# 调用 create_short 函数生成视频文件
talk_automation.create_short(numShorts=1, language_eleven="English", numImages=10, watermark="",
                             background_video_list=["huya"], background_music_list=["Music dj quads"], facts_subject="",
                             voice_eleven="Rachel")
