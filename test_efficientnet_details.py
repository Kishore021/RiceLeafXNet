import tensorflow as tf
import numpy as np

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

y_true = []
y_pred = []

for images, labels in test_ds:
    predictions = model.predict(images, verbose=0)
    predicted_classes = np.argmax(predictions, axis=1)

    y_true.extend(labels.numpy())
    y_pred.extend(predicted_classes)

y_true = np.array(y_true)
y_pred = np.array(y_pred)

print("\n" + "=" * 60)
print("CLASS RESULTS")
print("=" * 60)

total_correct = 0

for i, class_name in enumerate(class_names):

    actual = np.sum(y_true == i)
    correct = np.sum((y_true == i) & (y_pred == i))
    wrong = actual - correct

    total_correct += correct

    print(f"\n{class_name}")
    print(f"  Correct : {correct}/{actual}")
    print(f"  Wrong   : {wrong}/{actual}")
    print(f"  Accuracy: {correct / actual * 100:.2f}%")

print("\n" + "=" * 60)
print("OVERALL RESULT")
print("=" * 60)

total = len(y_true)

print(f"Correct predictions : {total_correct}/{total}")
print(f"Wrong predictions   : {total - total_correct}/{total}")
print(f"Test Accuracy       : {total_correct / total * 100:.2f}%")

print("\n" + "=" * 60)
print("CONFUSION MATRIX")
print("=" * 60)

matrix = np.zeros((len(class_names), len(class_names)), dtype=int)

for actual, predicted in zip(y_true, y_pred):
    matrix[actual][predicted] += 1

print("\nRows = Actual")
print("Columns = Predicted\n")

print("             ", end="")

for name in class_names:
    print(f"{name[:12]:>14}", end="")

print()

for i, name in enumerate(class_names):
    print(f"{name[:12]:12}", end="")

    for j in range(len(class_names)):
        print(f"{matrix[i][j]:14}", end="")

    print()

print("\nClass order:")
for i, name in enumerate(class_names):
    print(f"{i} = {name}")