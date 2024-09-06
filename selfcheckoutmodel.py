import os 
import cv2 
import numpy as np
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from keras.utils import to_categorical

training_data = [
    "V:/VIT/Project/Self checkout machine virtual keyboard with opencv/TrainingDataforSelfCheckoutMachine/TrainingData/1001",
    "V:/VIT/Project/Self checkout machine virtual keyboard with opencv/TrainingDataforSelfCheckoutMachine/TrainingData/1002",
    "V:/VIT/Project/Self checkout machine virtual keyboard with opencv/TrainingDataforSelfCheckoutMachine/TrainingData/1003" 
]

def load_image(training_data):
    images = []
    labels = []
    label_map = {folder: i for i, folder in enumerate(training_data)}
    for folder_path in training_data:
        label = label_map[folder_path]
        for filename in os.listdir(folder_path):
            if filename.endswith('.jpg'):
                try:
                    img = cv2.imread(os.path.join(folder_path, filename))
                    img = cv2.resize(img, (150,150))
                    images.append(img)
                    labels.append(label)
                except Exception as e:
                    print(f"Error loading image {os.path.join(folder_path, filename)}: {e}")
    return np.array(images), np.array(labels)

images, labels = load_image(training_data)
X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)
X_train = X_train.astype('float32') / 255
X_test = X_test.astype('float32') / 255
num_classes = len(training_data)
y_train = to_categorical(y_train, num_classes=num_classes)
y_test = to_categorical(y_test, num_classes=num_classes)
model = Sequential()
model.add(Conv2D(32, kernel_size=(3,3), activation='relu', input_shape=(150,150,3)))
model.add(Conv2D(64, kernel_size=(3,3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(3, activation='softmax'))
model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
model.fit(X_train, y_train, batch_size=32, epochs=50, verbose=1, validation_data=(X_test, y_test))
model.save("self_checkout_model.h5")
