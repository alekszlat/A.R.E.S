import sounddevice as sd
import numpy as np
from openwakeword.model import Model

class WakeWord_Listener:
    def __init__(self):
        # Paths to models (ensure these filenames match what you downloaded)
        self.onnx_path = "models/oww_pack/hey_jarvis_v0.1.onnx"
        self.mel_path = "models/oww_pack/melspectrogram.onnx"
        self.emb_path = "models/oww_pack/embedding_model.onnx"
        self.inference_framework = "onnx"

       # Audio settings: 16 kHz mono, 80 ms chunk (1280 samples)
        self.dtype     = "int16"
        self.channels  = 1
        self.rate      = 16000
        self.chunk     = 1280  # 80 ms @ 16 kHz

        # Create the raw input stream (bytes)
        self.stream = sd.RawInputStream(
            samplerate=self.rate,
            blocksize=self.chunk,
            dtype=self.dtype,
            channels=self.channels,
        )

        # Load openWakeWord model
        self.owwModel = Model(wakeword_models=[self.onnx_path],
                    melspec_model_path=str(self.mel_path),
                    embedding_model_path=str(self.emb_path),
                    inference_framework=self.inference_framework)

        self.n_models = len(self.owwModel.models.keys())

    def listen(self) -> bool:
        """
        Blocks until any loaded wakeword exceeds the demo threshold (0.5).
        Returns True when detected.
        """
        self.stream.start()
        try:
            while True:
                # Read one chunk (80 ms) from mic
                data, overflowed = self.stream.read(self.chunk)
                if overflowed:
                    # Error handling for overflow (not critical)
                    raise RuntimeWarning("Input overflow detected")

                # Convert bytes -> int16 numpy
                audio = np.frombuffer(data, dtype=np.int16)

                # Run openWakeWord on this chunk
                _ = self.owwModel.predict(audio)

                # Check the latest score in the prediction buffer for each model
                for mdl in self.owwModel.prediction_buffer.keys():
                    scores = self.owwModel.prediction_buffer[mdl]
                    if scores and scores[-1] > 0.5:  # demo threshold
                        print(f"{mdl} detected! Score: {scores[-1]:.3f}")
                        return True
        finally:
            # Always stop/close the stream
            try:
                self.stream.stop()
            finally:
                self.stream.close()
    
if __name__ == "__main__":
    listener = WakeWord_Listener()
    listener.listen()

