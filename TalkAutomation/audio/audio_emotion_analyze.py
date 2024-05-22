import librosa
import numpy as np
import keras
from keras.models import load_model


# 假设模型和标签映射已经定义好
MODEL_PATH = 'path_to_your_saved_model.keras'
EMOTIONS = ['angry', 'fear', 'happy', 'neutral', 'sad', 'surprise']

def load_audio_features(file_path, max_pad_length=174):
    """从给定路径加载音频文件，并提取特征."""
    signal, sr = librosa.load(file_path, sr=None)
    mfccs = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=40)
    pad_width = max_pad_length - mfccs.shape[1]
    mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)), mode='constant')
    return mfccs.T[np.newaxis, ..., np.newaxis]

def predict_emotion(file_path):
    """加载音频文件，预测情感，并返回预测结果."""
    # 加载训练好的模型
    model = load_model(MODEL_PATH)
    # 提取音频特征
    features = load_audio_features(file_path)
    # 使用模型进行预测
    predictions = model.predict(features)
    # 找到最可能的情感
    predicted_emotion = EMOTIONS[np.argmax(predictions)]
    return predicted_emotion

# 如果其他模块想要使用这个函数进行预测，只需要导入并调用 predict_emotion 即可
# 例如：emotion = predict_emotion('path_to_your_audio_file.wav')
