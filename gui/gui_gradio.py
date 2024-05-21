import gradio as gr
from gui.content_automation_ui import GradioContentAutomationUI
from gui.ui_abstract_base import AbstractBaseUI
from gui.ui_components_html import GradioComponentsHTML
from TalkAutomation.utils.cli import CLI


class PublicityProUI(AbstractBaseUI):
    '''Class for the GUI. This class is responsible for creating the UI and launching the server.'''

    def __init__(self):
        super().__init__(ui_name='gradio_PublicityPro')
        CLI.display_header()

    def create_interface(self):
        '''Create Gradio interface'''
        with gr.Blocks(css="footer {visibility: hidden}", title="PublicityPro Demo") as PublicityProUI:
            with gr.Row(variant='compact'):
                gr.HTML(GradioComponentsHTML.get_html_header())

            self.content_automation = GradioContentAutomationUI(PublicityProUI).create_ui()

        return PublicityProUI

    def launch(self):
        '''Launch the server'''
        PublicityProUI = self.create_interface()
        PublicityProUI.queue(concurrency_count=5, max_size=20).launch(server_port=31415, height=1000, server_name="localhost")


if __name__ == "__main__":
    app = PublicityProUI()
    app.launch()
