import os
import tensorflow as tf
from keras._tf_keras.keras import layers
from keras._tf_keras.keras.models import Sequential
from keras._tf_keras.keras.layers import Dense, Flatten, Dropout, BatchNormalization
from keras._tf_keras.keras.applications.efficientnet_v2 import EfficientNetV2B0


# ============================================================
# Paths
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OLD_MODEL = os.path.join(
    BASE_DIR,
    "static",
    "Models",
    "Model EfficientNet.keras"
)

NEW_MODEL = os.path.join(
    BASE_DIR,
    "static",
    "Models",
    "Model EfficientNet_fixed.keras"
)


# ============================================================
# Check model file
# ============================================================

print("=" * 60)
print("RiceLeafXNet - EfficientNet Model Repair Test")
print("=" * 60)

print("Old model:")
print(OLD_MODEL)

if not os.path.exists(OLD_MODEL):
    print("\nERROR: Model file does not exist.")
    raise FileNotFoundError(OLD_MODEL)

print("\nOld model found.")


# ============================================================
# Create the SAME EfficientNet architecture
# used in the training notebook
# ============================================================

print("\nCreating EfficientNetV2B0...")

base_eff = EfficientNetV2B0(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)

base_eff.trainable = False


# ============================================================
# Create model
# ============================================================

model_eff = Sequential()

model_eff.add(base_eff)

model_eff.add(
    Flatten()
)

model_eff.add(
    Dense(
        256,
        activation="relu"
    )
)

model_eff.add(
    Dropout(0.5)
)

model_eff.add(
    BatchNormalization()
)

model_eff.add(
    Dense(
        5,
        activation="sigmoid"
    )
)


# ============================================================
# Build model
# ============================================================

model_eff.build(
    input_shape=(None, 224, 224, 3)
)


print("\nNew model architecture created.")

model_eff.summary()


# ============================================================
# Load existing trained weights
# ============================================================

print("\n")
print("=" * 60)
print("Loading existing trained weights...")
print("=" * 60)

try:

    model_eff.load_weights(
        OLD_MODEL
    )

    print("\nSUCCESS!")
    print("Existing trained weights loaded.")

except Exception as e:

    print("\n")
    print("=" * 60)
    print("WEIGHT LOADING FAILED")
    print("=" * 60)

    print(type(e).__name__)
    print(str(e))

    raise


# ============================================================
# Test prediction
# ============================================================

print("\n")
print("=" * 60)
print("Testing prediction with dummy image...")
print("=" * 60)

import numpy as np

dummy_image = np.zeros(
    (1, 224, 224, 3),
    dtype=np.float32
)

prediction = model_eff.predict(
    dummy_image,
    verbose=0
)

print("\nPrediction:")
print(prediction)

print("\nPrediction shape:")
print(prediction.shape)


# ============================================================
# Save repaired model
# ============================================================

print("\n")
print("=" * 60)
print("Saving repaired model...")
print("=" * 60)

model_eff.save(
    NEW_MODEL
)

print("\nSUCCESS!")
print("New model saved:")
print(NEW_MODEL)

print("\n")
print("=" * 60)
print("TEST COMPLETED")
print("=" * 60)