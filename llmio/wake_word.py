import pyaudio
import numpy as np
from openwakeword.model import Model

class WakeWord_Listener:
    def __init__(self):
        # Paths to models
        self.onnx_path = "models/oww_pack/hey_jarvis_v0.1.onnx"
        self.mel_path = "models/oww_pack/melspectrogram.onnx"
        self.emb_path = "models/oww_pack/embedding_model.onnx"
        self.inference_framework = "onnx"

        # Get microphone stream
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1280
        audio = pyaudio.PyAudio()
        self.mic_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        self.owwModel = Model(wakeword_models=[self.onnx_path],
                    melspec_model_path=str(self.mel_path),
                    embedding_model_path=str(self.emb_path),
                    inference_framework=self.inference_framework)

        self.n_models = len(self.owwModel.models.keys())

    def listen(self) -> bool:

        while True:
            # Get audio
            audio = np.frombuffer(self.mic_stream.read(1280), dtype=np.int16)

            # Feed to openWakeWord model
            prediction = self.owwModel.predict(audio)

            for mdl in self.owwModel.prediction_buffer.keys():
                # Add scores in formatted table
                scores = list(self.owwModel.prediction_buffer[mdl])
                if scores[-1] > 0.5:
                    print(f"\033[{(list(self.owwModel.models.keys()).index(mdl)*3)+3}A", end="")
                    print(f"{mdl} detected! Score: {scores[-1]:.3f}")
                    return True
    
if __name__ == "__main__":
    listener = WakeWord_Listener()
    listener.listen()

