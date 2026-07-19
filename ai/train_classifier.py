"""
Saves the model to ai/exercise_model.keras
"""
import os
import glob
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras import layers

DATA_DIR   = os.path.join(os.path.dirname(__file__), "training_data")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "exercise_model.keras")

# Load all CSV files
all_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
if not all_files:
    print("No training data found. Run collect_training_data.py first.")
    exit()

df = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)
print(f"Loaded {len(df)} frames across {len(all_files)} files")
print(df["label"].value_counts())

# Features and labels
X = df.drop("label", axis=1).values.astype(np.float32)
y = df["label"].values

# Encode labels
encoder = LabelEncoder()
y_enc   = encoder.fit_transform(y)
print(f"Classes: {encoder.classes_}")

# Save label order so classifier uses same mapping
np.save(os.path.join(os.path.dirname(__file__), "label_classes.npy"),
        encoder.classes_)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
)

# Build model
model = keras.Sequential([
    keras.layers.Input(shape=(51,)),
    keras.layers.Dense(256, activation="relu"),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(128, activation="relu"),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(64,  activation="relu"),
    keras.layers.Dense(len(encoder.classes_), activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# Train
history = model.fit(
    X_train, y_train,
    epochs          = 50,
    batch_size      = 32,
    validation_data = (X_test, y_test),
    callbacks=[
        keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)
    ]
)

import numpy as np, os
np.save(os.path.join(os.path.dirname(__file__), "training_history.npy"), history.history)

# Evaluate
loss, acc = model.evaluate(X_test, y_test)
print(f"\nTest accuracy: {acc:.2%}")

# Save
model.save(MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")

from sklearn.metrics import classification_report, accuracy_score
import numpy as np

y_pred = np.argmax(model.predict(X_test, verbose=0), axis=1)
print("Overall accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=encoder.classes_))