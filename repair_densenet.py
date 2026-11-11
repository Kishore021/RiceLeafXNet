import os
import numpy as np
import tensorflow as tf

from keras._tf_keras.keras.layers import (
    Dense,
    Flatten,
    Dropout,
    BatchNormalization
)
from keras._tf_keras.keras.models import Sequential
from keras._tf_keras.keras.applications.densenet import DenseNet121


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OLD_MODEL = os.path.join(
    BASE_DIR,
    "static",
    "Models",
    "Model DenseNet.keras"
)

NEW_MODEL = os.path.join(
    BASE_DIR,
    "static",
    "Models",
    "Model DenseNet_fixed.keras"
)


# ============================================================
# CHECK OLD MODEL
# ============================================================

print("=" * 60)
print("DENSENET MODEL REPAIR")
print("=" * 60)

if not os.path.exists(OLD_MODEL):
    raise FileNotFoundError(
        f"Original DenseNet model not found:\n{OLD_MODEL}"
    )

print("Old model found:")
print(OLD_MODEL)


# ============================================================
# CREATE ORIGINAL DENSENET121 BACKBONE
# ============================================================

print("\nCreating DenseNet121...")

base_model = DenseNet121(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)

base_model.trainable = False

print("DenseNet121 created.")
print("Backbone output shape:", base_model.output_shape)


# ============================================================
# RECREATE THE SAME MODEL FROM YOUR NOTEBOOK
# ============================================================

print("\nCreating original model architecture...")

model_dense = Sequential()

model_dense.add(base_model)
model_dense.add(Flatten())
model_dense.add(Dense(256, activation="relu"))
model_dense.add(Dropout(0.5))
model_dense.add(BatchNormalization())
model_dense.add(Dense(5, activation="sigmoid"))

model_dense.build(input_shape=(None, 224, 224, 3))

print("New model architecture created.")

model_dense.summary()


# ============================================================
# LOAD EXISTING TRAINED WEIGHTS
# ============================================================

print("\nLoading existing trained weights...")
print("Please wait...")

model_dense.load_weights(OLD_MODEL)

print("\nSUCCESS!")
print("Existing DenseNet trained weights loaded.")


# ============================================================
# TEST PREDICTION
# ============================================================

print("\nTesting prediction with dummy image...")

dummy_image = np.zeros(
    (1, 224, 224, 3),
    dtype=np.float32
)

prediction = model_dense.predict(
    dummy_image,
    verbose=0
)

print("Prediction:")
print(prediction)

print("Prediction shape:")
print(prediction.shape)


# ============================================================
# SAVE REPAIRED MODEL
# ============================================================

print("\nSaving repaired DenseNet model...")

model_dense.save(NEW_MODEL)

print("\nSUCCESS!")
print("New model saved:")
print(NEW_MODEL)

print("\n" + "=" * 60)
print("DENSENET REPAIR COMPLETED")
print("=" * 60)