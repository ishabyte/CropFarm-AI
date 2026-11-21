
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

DATASET_DIR = "static/dataset/PlantVillage"
MODEL_PATH = "models/crop_disease_model.keras"

model = tf.keras.models.load_model(MODEL_PATH)

datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    validation_split=0.2
)

validation_data = datagen.flow_from_directory(
    DATASET_DIR,
    target_size=(128, 128),
    batch_size=16,
    class_mode="categorical",
    subset="validation",
    seed=42,
    shuffle=False
)

loss, accuracy = model.evaluate(validation_data)

print("\n===== MODEL EVALUATION =====")
print(f"Validation Loss: {loss:.4f}")
print(f"Validation Accuracy: {accuracy * 100:.2f}%")
