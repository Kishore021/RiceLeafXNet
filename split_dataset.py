import os
import shutil
import random

BASE_DIR = r"D:\RiceLeafXNet\datasets\Plant Diseases\Rice"

RAW_DIR = os.path.join(BASE_DIR, "raw")
TRAIN_DIR = os.path.join(BASE_DIR, "train")
VAL_DIR = os.path.join(BASE_DIR, "validation")
TEST_DIR = os.path.join(BASE_DIR, "test")

CLASSES = [
    "Brown spot",
    "Healthy",
    "Hispa",
    "Leaf blast",
    "Neck blast"
]

# 40 train + 5 validation + 5 test = 50 per class
TRAIN_COUNT = 40
VAL_COUNT = 5
TEST_COUNT = 5

random.seed(42)

# Create output folders
for class_name in CLASSES:
    os.makedirs(os.path.join(TRAIN_DIR, class_name), exist_ok=True)
    os.makedirs(os.path.join(VAL_DIR, class_name), exist_ok=True)
    os.makedirs(os.path.join(TEST_DIR, class_name), exist_ok=True)

for class_name in CLASSES:

    source_dir = os.path.join(RAW_DIR, class_name)

    files = [
        f for f in os.listdir(source_dir)
        if os.path.isfile(os.path.join(source_dir, f))
    ]

    random.shuffle(files)

    required = TRAIN_COUNT + VAL_COUNT + TEST_COUNT

    if len(files) < required:
        raise ValueError(
            f"{class_name} has only {len(files)} files. "
            f"Need at least {required}."
        )

    train_files = files[:TRAIN_COUNT]
    val_files = files[TRAIN_COUNT:TRAIN_COUNT + VAL_COUNT]
    test_files = files[TRAIN_COUNT + VAL_COUNT:required]

    for filename in train_files:
        shutil.copy2(
            os.path.join(source_dir, filename),
            os.path.join(TRAIN_DIR, class_name, filename)
        )

    for filename in val_files:
        shutil.copy2(
            os.path.join(source_dir, filename),
            os.path.join(VAL_DIR, class_name, filename)
        )

    for filename in test_files:
        shutil.copy2(
            os.path.join(source_dir, filename),
            os.path.join(TEST_DIR, class_name, filename)
        )

    print(f"{class_name}:")
    print(f"  Train      : {len(train_files)}")
    print(f"  Validation : {len(val_files)}")
    print(f"  Test       : {len(test_files)}")
    print()

print("=" * 50)
print("DATASET SPLIT COMPLETED")
print("=" * 50)
print("Train      : 200 images")
print("Validation : 25 images")
print("Test       : 25 images")
print("Total      : 250 images")