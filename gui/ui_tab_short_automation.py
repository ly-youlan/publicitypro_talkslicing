import os
import traceback

import gradio as gr
# from gui.ui_components_html import GradioComponentsHTML
from gui.ui_abstract_component import AbstractComponentUI

# from TalkAutomation.config.asset_db import AssetDatabase, AssetType

from TalkAutomation.engine.talk_slicing_engine import TalkSlicingEngine


class TalkAutomationUI(AbstractComponentUI):
    def __init__(self, PubulicityProUI: gr.Blocks):
        self.PubulicityProUI = PubulicityProUI
        self.embedHTML = '<div style="display: flex; overflow-x: auto; gap: 20px;">'
        self.progress_counter = 0
        self.short_automation = None

    def create_ui(self):
        with (gr.Row(visible=False) as short_automation):
            with gr.Column():
                gr.Markdown("### 自定义模板")
                # short_type = gr.Radio(["单人发言素材", "多人发言素材"], label="素材发言人数", value="单人发言素材",
                #                       interactive=True)
                video_subject = gr.Textbox(label="这段视频素材的主要内容是什么，你希望如何去剪辑这些素材 (例如：...)",
                                           interactive=True, visible=True, value=
                                           """【场景】\n现在你在进行针对深圳大学辅导员访谈的剪辑，主要结构是一个人提出问题，然后由辅导员回答以此往复，有时候可能会出现拍摄现场时一些无关的对话信息，请你注意将他们剔除。\n我们希望从长视频中剪辑出若干个适合短视频平台，例如抖音，小红书的视频，并且每段视频切分的意义明确。\n【任务】\n1. 输出每一段视频所需要剪辑在一起的句子的时间戳；\n2. 提炼出每一段视频所在讨论的提问是什么，并作为标题；\n3. 概括出每一段的主题""",
                                           placeholder="""【场景】\n现在你在进行针对深圳大学辅导员访谈的剪辑，主要结构是一个人提出问题，然后由辅导员回答以此往复，有时候可能会出现拍摄现场时一些无关的对话信息，请你注意将他们剔除。\n我们希望从长视频中剪辑出若干个适合短视频平台，例如抖音，小红书的视频，并且每段视频切分的意义明确。\n【任务】\n1. 输出每一段视频所需要剪辑在一起的句子的时间戳；\n2. 提炼出每一段视频所在讨论的提问是什么，并作为标题；\n3. 概括出每一段的主题""",
                                           info="相当于输入给大模型的剪辑指令", lines=6)
                with gr.Row():
                    with gr.Column():
                        theme_font = gr.Radio(["字小魂天工宋", "字体2", "字体3"], label="标题与主题字体",value="字小魂天工宋")
                        caption_font = gr.Radio(["字小魂天工宋", "字体2", "字体3"], label="字幕字体",value="字小魂天工宋")
                    base_background_picture = gr.Image(label="背景图片选择")

                gr.Markdown("### 执行自动化")
                with gr.Accordion("➕ 选择你的素材", open=False) as accordion:
                    with gr.Column(visible=True) as localFileFlow:
                        video_upload = gr.Video(visible=True, source="upload", type="filepath", interactive=True)

                createButton = gr.Button("开始自动剪辑", label="Create Shorts")
                self.edited_video_display = gr.Video(visible=True)  # 初始设置为不可见
                # self.edited_video_display.update(
                #     value="/Users/youlan/Pictures/private/M4ROOT/CLIP/23年思政学风会议+采访/采访主机位-35mm-主声音/20231222_A0530.MP4",
                #     visible=True)

                # video_folder = gr.Button("📁", visible=True)

            # video_folder.click(lambda _: AssetComponentsUtils.start_file(os.path.abspath("videos/")))

            createButton.click(self.create_short,
                               inputs=[video_upload],
                               outputs=[self.edited_video_display]
                               )

        self.short_automation = short_automation
        return self.short_automation

    def create_short(self, videoPath, progress=gr.Progress()):
        '''Creates a short'''

        # videoPath = "/Users/youlan/Pictures/private/M4ROOT/CLIP/23年思政学风会议+采访/采访主机位-35mm-主声音/20231222_A0530.MP4"
        # Create an instance of TalkSlicingEngine
        talk_slicing_engine = TalkSlicingEngine(src_url=videoPath)
        num_steps = talk_slicing_engine.get_total_steps()

        try:
            # Perform the steps of the TalkSlicingEngine
            for step_number in range(1, num_steps + 1):
                talk_slicing_engine.stepDict[step_number]()

                def logger(prog_str):
                    progress(self.progress_counter / num_steps,
                             f"自动化剪辑中： {prog_str}")

                talk_slicing_engine.set_logger(logger)
            edited_video_path = talk_slicing_engine.get_output_video_path()

            return edited_video_path
        except Exception as e:
            traceback.print_exc()
            print(f"Error in main function: {str(e)}")
