import tensorflow as tf
import numpy as np
import os

MODEL_PATH = r"D:\RiceLeafXNet\static\Models\Model EfficientNet_new.keras"
TEST_DIR = r"D:\RiceLeafXNet\datasets\Plant Diseases\Rice\test"

model = tf.keras.models.load_model(MODEL_PATH, compile=False)

test_ds = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    image_size=(224, 224),
    batch_size=16,
    label_mode="int",
    shuffle=False
)

class_names = test_ds.class_names

file_paths = test_ds.file_paths

wrong_count = 0
index = 0

for images, labels in test_ds:
    predictions = model.predict(images, verbose=0)

    predicted_classes = np.argmax(predictions, axis=1)
    confidences = np.max(predictions, axis=1)

    for i in range(len(labels)):
        actual = int(labels[i].numpy())
        predicted = int(predicted_classes[i])

        if actual != predicted:
            print("\n" + "=" * 60)
            print("WRONG PREDICTION")
            print("=" * 60)

            print("Image      :", file_paths[index])
            print("Actual     :", class_names[actual])
            print("Predicted  :", class_names[predicted])
            print("Confidence :", f"{confidences[i] * 100:.2f}%")

            wrong_count += 1

        index += 1

print("\n" + "=" * 60)
print(f"TOTAL WRONG: {wrong_count}/25")
print("=" * 60)