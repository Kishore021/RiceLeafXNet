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
from keras._tf_keras.keras.applications import ResNet152


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OLD_MODEL = os.path.join(
    BASE_DIR,
    "static",
    "Models",
    "Model ResNet.keras"
)

NEW_MODEL = os.path.join(
    BASE_DIR,
    "static",
    "Models",
    "Model ResNet_fixed.keras"
)


# ============================================================
# START
# ============================================================

print("=" * 60)
print("RESNET152 MODEL REPAIR")
print("=" * 60)


# ============================================================
# CHECK ORIGINAL MODEL
# ============================================================

if not os.path.exists(OLD_MODEL):
    raise FileNotFoundError(
        f"Original ResNet model not found:\n{OLD_MODEL}"
    )

print("Old model found:")
print(OLD_MODEL)


# ============================================================
# CREATE EXACT RESNET152 BACKBONE
# ============================================================

print("\nCreating ResNet152...")

conv_base = ResNet152(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)

conv_base.trainable = False

print("ResNet152 created.")
print("Backbone output shape:", conv_base.output_shape)


# ============================================================
# RECREATE MODEL FROM NOTEBOOK
# ============================================================

print("\nCreating original model architecture...")

model_res = Sequential()

model_res.add(conv_base)
model_res.add(Flatten())
model_res.add(Dense(256, activation="relu"))
model_res.add(Dropout(0.5))
model_res.add(BatchNormalization())
model_res.add(Dense(5, activation="sigmoid"))

model_res.build(input_shape=(None, 224, 224, 3))

print("New model architecture created.")

model_res.summary()


# ============================================================
# LOAD EXISTING TRAINED WEIGHTS
# ============================================================

print("\nLoading existing trained weights...")
print("Please wait...")

model_res.load_weights(OLD_MODEL)

print("\nSUCCESS!")
print("Existing ResNet152 trained weights loaded.")


# ============================================================
# TEST PREDICTION
# ============================================================

print("\nTesting prediction with dummy image...")

dummy_image = np.zeros(
    (1, 224, 224, 3),
    dtype=np.float32
)

prediction = model_res.predict(
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

print("\nSaving repaired ResNet model...")

model_res.save(NEW_MODEL)

print("\nSUCCESS!")
print("New model saved:")
print(NEW_MODEL)

print("\n" + "=" * 60)
print("RESNET152 REPAIR COMPLETED")
print("=" * 60)