import os
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetV2B0
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# =========================
# 1. Paths
# =========================

BASE_DIR = r"D:\RiceLeafXNet\datasets\Plant Diseases\Rice"

TRAIN_DIR = os.path.join(BASE_DIR, "train")
VAL_DIR = os.path.join(BASE_DIR, "validation")

# =========================
# 2. Settings
# =========================

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16
NUM_CLASSES = 5
EPOCHS = 30

# =========================
# 3. Load datasets
# =========================

train_ds = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="int",
    shuffle=True,
    seed=42
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    VAL_DIR,
    image_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="int",
    shuffle=False
)

print("Classes:")
print(train_ds.class_names)

# =========================
# 4. Data augmentation
# =========================

data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.15),
    layers.RandomZoom(0.15),
    layers.RandomContrast(0.10)
])

# =========================
# 5. EfficientNetV2B0
# =========================

base_model = EfficientNetV2B0(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)

base_model.trainable = False

# =========================
# 6. Build model
# =========================

inputs = layers.Input(shape=(224, 224, 3))

x = data_augmentation(inputs)

x = base_model(x, training=False)

x = layers.GlobalAveragePooling2D()(x)

x = layers.Dense(256, activation="relu")(x)

x = layers.Dropout(0.4)(x)

outputs = layers.Dense(
    NUM_CLASSES,
    activation="softmax"
)(x)

model = models.Model(inputs, outputs)

# =========================
# 7. Compile
# =========================

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# =========================
# 8. Callbacks
# =========================

MODEL_PATH = r"D:\RiceLeafXNet\static\Models\Model EfficientNet_new.keras"

checkpoint = ModelCheckpoint(
    MODEL_PATH,
    monitor="val_accuracy",
    save_best_only=True,
    mode="max",
    verbose=1
)

early_stop = EarlyStopping(
    monitor="val_accuracy",
    patience=7,
    mode="max",
    restore_best_weights=True,
    verbose=1
)

# =========================
# 9. Train
# =========================

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    callbacks=[checkpoint, early_stop]
)

print("=" * 60)
print("TRAINING COMPLETED")
print("=" * 60)
print("Best model saved to:")
print(MODEL_PATH)

# =========================
# 10. Final validation result
# =========================

loss, accuracy = model.evaluate(val_ds, verbose=1)

print("=" * 60)
print(f"Validation Accuracy: {accuracy * 100:.2f}%")
print("=" * 60)