import os
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from ela_preprocess import convert_to_ela_image

# Dataset paths
real_path = "dataset/real"
fake_path = "dataset/fake"

IMG_SIZE = (128, 128)

def load_dataset():
    X = []
    y = []
    
    for label, folder in enumerate([real_path, fake_path]):  # 0=real, 1=fake
        for file in os.listdir(folder):
            try:
                path = os.path.join(folder, file)
                ela_img = convert_to_ela_image(path)
                ela_img = np.array(ela_img)
                ela_img = np.resize(ela_img, (IMG_SIZE[0], IMG_SIZE[1], 3))
                X.append(ela_img)
                y.append(label)
            except Exception as e:
                print(f"Error with {file}: {e}")
    
    return np.array(X), np.array(y)

print("📂 Loading dataset...")
X, y = load_dataset()
print("✅ Dataset loaded:", X.shape, y.shape)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# CNN Model
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3)),
    MaxPooling2D(2,2),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer=Adam(learning_rate=0.0001), loss='binary_crossentropy', metrics=['accuracy'])

print("🚀 Training model...")
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=10, batch_size=16)

# Ensure model directory exists
os.makedirs("model", exist_ok=True)

# Save full model (architecture + weights)
model.save("model/model.h5")
print("💾 Full model saved as model/model.h5")
