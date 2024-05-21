import gradio as gr

from gui.ui_tab_short_automation import TalkAutomationUI
from gui.ui_tab_video_automation import VideoAutomationUI
# from gui.ui_tab_video_translation import VideoTranslationUI


class GradioContentAutomationUI:
    def __init__(self, PublicityPro):
        self.PublicityPro = PublicityPro
        self.content_automation_ui = None

    def create_ui(self):
        '''Create Gradio interface'''
        with gr.Tab("公众力Pro Demo") as self.content_automation_ui:
            gr.Markdown("# 🏆 打造最舒适的宣传工作体验 🚀")
            gr.Markdown("## 选择你想使用的AISaaS功能")
            choice = gr.Radio(['🎬 自动批量化制作', '🎞️ 基于资产库生成新视频'], label="选择")
            video_automation_ui = VideoAutomationUI(self.PublicityPro).create_ui()
            short_automation_ui = TalkAutomationUI(self.PublicityPro).create_ui()
            # video_translation_ui = VideoTranslationUI(self.PublicityPro).create_ui()
            choice.change(lambda x: gr.update(visible=x == choice.choices[0]), [choice], [short_automation_ui])

        return self.content_automation_ui
