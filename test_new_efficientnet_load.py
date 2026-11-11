import tensorflow as tf

MODEL_PATH = r"D:\RiceLeafXNet\static\Models\Model EfficientNet_new.keras"

print("Loading new EfficientNet model...")

model = tf.keras.models.load_model(
    MODEL_PATH,
    compile=False
)

print("\nMODEL LOAD SUCCESS")
print("Input shape :", model.input_shape)
print("Output shape:", model.output_shape)
print("Model name  :", model.name)