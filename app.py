#Importing the required libraries
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2,ResNet50
import pandas
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Conv2D
from keras.layers import MaxPooling2D,GlobalAveragePooling2D   
from keras.layers import Flatten
from keras.layers import Dropout

#Reading the Covid-19 Dataset
train_data_path="C:/Users/nilch/Desktop/Computer Vision/X-ray images -Covid Prediction/Computer-Vision/Covid19-dataset/train"
test_data_path="C:/Users/nilch/Desktop/Computer Vision/X-ray images -Covid Prediction/Computer-Vision/Covid19-dataset/test"
IMG_SIZE=(224,224)
BATCH_SIZE=32

#Creating the dataset directly from directory
train_dataset=tf.keras.preprocessing.image_dataset_from_directory(
    train_data_path,
    label_mode='categorical',
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

test_dataset=tf.keras.preprocessing.image_dataset_from_directory(
    test_data_path,
    label_mode='categorical'
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

#Applying data augmentation and normalization
normalization_layer=tf.keras.layers.Rescaling(1./255)

data_augmentation=keras.Sequential([
    tf.keras.layers.RandomFlip("vertical"),
    tf.keras.layers.RandomRotation(0.1),
    tf.keras.layers.RandomZoom(0.1),
    tf.keras.layers.RandomContrast(0.9)
])

train_dataset=train_dataset.map(lambda x,y:(data_augmentation(x,training=True),y))

train_dataset=train_dataset.map(lambda x,y:(normalization_layer(x),y))
test_dataset=test_dataset.map(lambda x,y:(normalization_layer(x),y))

#Keeping the data in memory for faster processing and prefetching the data
AUTOTUNE=tf.data.experimental.AUTOTUNE
train_dataset=train_dataset.cache().prefetch(buffer_size=AUTOTUNE)  
test_dataset=test_dataset.cache().prefetch(buffer_size=AUTOTUNE)


#Importing transfer model
base_model=ResNet50(input_shape=(224,224,3),include_top=False,weights='imagenet')
#base_model.trainable=False

for layer in base_model.layers[-30:]:
    layer.trainable=False

#Defining the model architecture
model=tf.keras.Sequential([base_model,                     
    Conv2D(filters=32,kernel_size=(3,3),activation='relu',padding='same',input_shape=(224,224,3)),
    MaxPooling2D(pool_size=(2,2),padding='same'),
    Dropout(0.2),
    Conv2D(filters=64,kernel_size=(3,3),activation='relu',padding='same'),
    MaxPooling2D(pool_size=(2,2),padding='same'),
    Conv2D(filters=128,kernel_size=(3,3),activation='relu',padding='same'),
    MaxPooling2D(pool_size=(2,2)),
    Flatten(),
    Dense(units=128,activation='relu'),
    Dense(units=3,activation='softmax')
])

#Compiling and training the model
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),loss='categorical_crossentropy',metrics=['accuracy'])
history=model.fit(train_dataset,epochs=20,validation_data=test_dataset)

#Evaluating the model
test_loss, test_acc = model.evaluate(test_dataset)
print(f"Test Accuracy: {test_acc:.4f}")

