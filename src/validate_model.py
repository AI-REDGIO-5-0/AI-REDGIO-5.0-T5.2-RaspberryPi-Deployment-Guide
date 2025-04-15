import os
import numpy as np
import logging
from config import Config
import tflite_runtime.interpreter as tflite

def validate_tflite_model(model_path, input_shape):
    logging.basicConfig(level=logging.INFO)

    # Verifica existencia y tamaño del archivo
    if not os.path.exists(model_path):
        logging.error(f"Modelo no encontrado: {model_path}")
        return False
    if os.path.getsize(model_path) < 1024:
        logging.error(f"El archivo {model_path} parece estar vacío o corrupto.")
        return False

    try:
        # Intenta cargar el modelo
        interpreter = tflite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # Verifica el tipo de dato esperado
        expected_dtype = input_details[0]['dtype']
        expected_shape = tuple(input_details[0]['shape'])

        if tuple(input_shape) != expected_shape:
            logging.warning(f"Forma esperada por el modelo: {expected_shape}, pero settings.yaml tiene: {input_shape}")

        # Genera input dummy con dtype correcto
        dummy_input = (np.random.rand(*expected_shape) * 255).astype(expected_dtype)

        interpreter.set_tensor(input_details[0]['index'], dummy_input)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])

        logging.info("Modelo cargado y ejecutado correctamente.")
        logging.info(f"Output shape: {output.shape}, dtype: {output.dtype}")
        return True

    except Exception as e:
        logging.exception(f"Error durante validación del modelo: {e}")
        return False

if __name__ == "__main__":
    cfg = Config()
    model_path = cfg.get("model", "path")
    input_shape = cfg.get("model", "input_shape")

    valid = validate_tflite_model(model_path, input_shape)
    if not valid:
        print("Validación fallida.")
    else:
        print("Validación exitosa.")