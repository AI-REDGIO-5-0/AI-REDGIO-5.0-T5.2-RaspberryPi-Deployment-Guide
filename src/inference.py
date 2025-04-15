import numpy as np
from config import Config
import logging
import os

# For TFLite
import tflite_runtime.interpreter as tflite

# Optional: ONNX
try:
    import onnxruntime as ort
except ImportError:
    ONNX_AVAILABLE = False

class InferenceEngine:
    def __init__(self, config_path="config/settings.yaml"):
        self.config = Config(config_path)
        self.model_path = self.config.get("model", "path")
        self.input_shape = self.config.get("model", "input_shape")
        self.threshold = self.config.get("model", "threshold", default=0.5)

        if self.model_path.endswith(".tflite"):
            self.backend = "tflite"
            self.interpreter = tflite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
        elif self.model_path.endswith(".onnx") and ONNX_AVAILABLE:
            self.backend = "onnx"
            self.session = ort.InferenceSession(self.model_path)
            self.input_name = self.session.get_inputs()[0].name
        else:
            raise ValueError("Unsupported model format or missing ONNXRuntime.")

        logging.info(f"Model loaded from {self.model_path} using {self.backend.upper()} backend")
        print("Expected input shape:", self.input_shape)
        print("Model input details:", self.input_details)


    def predict(self, input_data: np.ndarray):
        # Reshape y tipo correctos
        input_data = input_data.astype(np.uint8).reshape(self.input_shape)

        if self.backend == "tflite":
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            self.interpreter.invoke()
            output = self.interpreter.get_tensor(self.output_details[0]['index'])
        elif self.backend == "onnx":
            output = self.session.run(None, {self.input_name: input_data})[0]
        else:
            raise RuntimeError("Unsupported backend")

        return output


# Basic Test
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    try:
        engine = InferenceEngine()
        dummy_input = (np.random.rand(1, 224, 224, 3) * 255).astype(np.uint8)
        output = engine.predict(dummy_input)
        print("Output:", output)
    except Exception as e:
        print("Error during inference:", e)