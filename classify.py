import os
import numpy as np
from PIL import Image

from keras._tf_keras.keras.models import load_model
from keras._tf_keras.keras.preprocessing.image import img_to_array


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

MODEL_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "Models"
)

MODELS = [
    "Model EfficientNet.keras",
    "Model DenseNet.keras",
    "Model ResNet.keras"
]

CLASS_NAMES = [
    "Brown spot",
    "Healthy",
    "Hispa",
    "Leaf blast",
    "Neck blast"
]

IMAGE_SIZE = (224, 224)

_loaded_models = {}


def get_model(modelNo):

    if modelNo not in range(len(MODELS)):
        raise ValueError(
            f"Invalid model number: {modelNo}"
        )

    if modelNo in _loaded_models:
        return _loaded_models[modelNo]

    model_path = os.path.join(
        MODEL_FOLDER,
        MODELS[modelNo]
    )

    print("=" * 60)
    print("Loading model...")
    print("Model number :", modelNo)
    print("Model name   :", MODELS[modelNo])
    print("Model path   :", model_path)
    print("=" * 60)

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found:\n{model_path}"
        )

    try:
        model = load_model(
            model_path,
            compile=False
        )

    except Exception as e:
        print("MODEL LOADING ERROR:")
        print(str(e))

        raise RuntimeError(
            f"Unable to load model '{MODELS[modelNo]}'.\n"
            f"Error: {str(e)}"
        )

    _loaded_models[modelNo] = model

    print("Model loaded successfully.")

    return model


def prepare_image(image_data, modelNo):

    if isinstance(image_data, str):
        image = Image.open(image_data)
    else:
        image = image_data

    image = image.convert("RGB")

    image = image.resize(
        IMAGE_SIZE
    )

    image_array = img_to_array(
        image
    )

    image_array = image_array.astype(
        "float32"
    )


    # ========================================================
    # EFFICIENTNET
    # ========================================================

    if modelNo == 0:

        # EfficientNetV2B0 has built-in preprocessing.
        # Keep pixel values in the original 0-255 range.

        pass


    # ========================================================
    # DENSENET / RESNET
    # ========================================================

    else:

        # Original DenseNet and ResNet models
        # were trained using 0.1 / 256.

        image_array = image_array * (
            0.1 / 256.0
        )


    # ========================================================
    # ADD BATCH DIMENSION
    # ========================================================

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    return image_array


def predict(image_data, modelNo):

    print("\n")
    print("=" * 60)
    print("STARTING PREDICTION")
    print("=" * 60)

    try:

        # ====================================================
        # LOAD MODEL
        # ====================================================

        model = get_model(
            modelNo
        )

        print("Model ready.")


        # ====================================================
        # PREPARE IMAGE
        # ====================================================

        image_array = prepare_image(
            image_data,
            modelNo
        )

        print(
            "Image shape:",
            image_array.shape
        )

        print(
            "Image dtype:",
            image_array.dtype
        )

        print(
            "Image min:",
            np.min(image_array)
        )

        print(
            "Image max:",
            np.max(image_array)
        )


        # ====================================================
        # PREDICTION
        # ====================================================

        prediction = model.predict(
            image_array,
            verbose=0
        )

        print(
            "Raw prediction:",
            prediction
        )


        # ====================================================
        # VALIDATE PREDICTION
        # ====================================================

        if prediction is None:

            raise RuntimeError(
                "Model returned None."
            )

        prediction = np.asarray(
            prediction
        )

        print(
            "Prediction shape:",
            prediction.shape
        )

        if prediction.size == 0:

            raise RuntimeError(
                "Model returned an empty prediction."
            )


        # ====================================================
        # GET PROBABILITIES
        # ====================================================

        probabilities = prediction[0]


        # ====================================================
        # EFFICIENTNET
        # ====================================================

        if modelNo == 0:

            # EfficientNet uses softmax.
            # Values are already probabilities.

            probabilities = np.asarray(
                probabilities,
                dtype="float32"
            )


        # ====================================================
        # DENSENET / RESNET
        # ====================================================

        else:

            # Original models use sigmoid.
            # Normalize values for display.

            probabilities = np.asarray(
                probabilities,
                dtype="float32"
            )

            total = np.sum(
                probabilities
            )

            if total > 0:

                probabilities = (
                    probabilities / total
                )


        # ====================================================
        # FIND PREDICTED CLASS
        # ====================================================

        predicted_index = int(
            np.argmax(
                probabilities
            )
        )

        confidence = float(
            probabilities[
                predicted_index
            ]
        )


        # ====================================================
        # CHECK CLASS INDEX
        # ====================================================

        if predicted_index >= len(
            CLASS_NAMES
        ):

            raise RuntimeError(
                f"Model returned class index "
                f"{predicted_index}, but only "
                f"{len(CLASS_NAMES)} classes are configured."
            )


        predicted_class = CLASS_NAMES[
            predicted_index
        ]


        # ====================================================
        # DISPLAY RESULT
        # ====================================================

        print("=" * 60)
        print("PREDICTION SUCCESS")
        print("Class      :", predicted_class)
        print("Index      :", predicted_index)
        print(
            "Confidence :",
            f"{confidence * 100:.2f}%"
        )
        print("=" * 60)


        # ====================================================
        # RETURN RESULT
        # ====================================================

        return {

            "class": predicted_class,

            "class_index": predicted_index,

            "confidence": confidence,

            "confidence_percent": round(
                confidence * 100,
                2
            ),

            "probabilities":
                probabilities.tolist(),

            "raw_prediction":
                prediction.tolist()
        }


    except Exception as e:

        print("\n")
        print("=" * 60)
        print("PREDICTION ERROR")
        print("=" * 60)
        print(str(e))
        print("=" * 60)

        raise