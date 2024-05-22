from shortGPT.api_utils.eleven_api import ElevenLabsAPI
from shortGPT.audio.voice_module import VoiceModule
from TalkAutomation.api_utils.moyin_api import MoyinAPI


class MoyinVoiceModule(VoiceModule):
    def __init__(self, api_key, secret, voiceName):
        self.api_key = api_key
        self.voiceName = voiceName
        self.secret = secret
        self.moyin_api = MoyinAPI(self.api_key, self.secret, self.voiceName)

        # self.remaining_credits = None
        # self.eleven_labs_api = ElevenLabsAPI(self.api_key)
        super().__init__()

    def update_usage(self):
        self.remaining_credits = self.eleven_labs_api.get_remaining_characters()
        return self.remaining_credits

    def get_remaining_characters(self):
        return self.remaining_credits if self.remaining_credits else self.eleven_labs_api.get_remaining_characters()

    def generate_voice(self, text, outputfile):
        # file_path =self.eleven_labs_api.generate_voice(text=text, character=self.voiceName, filename=outputfile)
        file_path = self.moyin_api.generate_voice(text=text, filename=outputfile, voiceName=self.voiceName)
        # self.update_usage()
        return file_path
