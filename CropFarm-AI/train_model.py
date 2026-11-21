
import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models

# Project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dataset directory
DATASET_DIR = os.path.join(
    BASE_DIR, "static", "dataset", "PlantVillage"
)

# Model settings
IMAGE_SIZE = (128, 128)
BATCH_SIZE = 16
EPOCHS = 10

print("===================================")
print("cropFarm AI - CNN Model Training")
print("===================================")

# Load dataset
datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    validation_split=0.2
)

train_data = datagen.flow_from_directory(
    DATASET_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    subset="training",
    seed=42
)

validation_data = datagen.flow_from_directory(
    DATASET_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="categorical",
    subset="validation",
    seed=42
)

# Build CNN model
model = models.Sequential([
    layers.Input(shape=(128, 128, 3)),

    layers.Conv2D(32, (3, 3), activation="relu"),
    layers.MaxPooling2D((2, 2)),

    layers.Conv2D(64, (3, 3), activation="relu"),
    layers.MaxPooling2D((2, 2)),

    layers.Conv2D(128, (3, 3), activation="relu"),
    layers.MaxPooling2D((2, 2)),

    layers.Flatten(),

    layers.Dense(128, activation="relu"),
    layers.Dropout(0.5),

    layers.Dense(train_data.num_classes, activation="softmax")
])

# Compile model
model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# Display model structure
model.summary()

# Train model
history = model.fit(
    train_data,
    validation_data=validation_data,
    epochs=EPOCHS
)

# Save trained model
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

model.save(os.path.join(MODEL_DIR, "crop_disease_model.keras"))

# Save class names
import json

class_indices = train_data.class_indices

with open(os.path.join(MODEL_DIR, "class_indices.json"), "w") as file:
    json.dump(class_indices, file)

print("===================================")
print("cropFarm AI Model Training Complete!")
print("Model saved successfully!")
print("===================================")
