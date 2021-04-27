import os
import random

import cv2
import keras
from PIL import Image
from keras_preprocessing.image import ImageDataGenerator
from numpy import array, ndarray
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K, layers
# from keras.utils import print_summary
from typing import List

from tensorflow.python.debug.examples.debug_mnist import tf
from tensorflow.python.keras.utils.layer_utils import print_summary

from config import Config
import matplotlib.pyplot as plt
import numpy as np

from lib.decorators import singleton


@singleton
class CNN:
    def train(self, save_name: str = None):
        x_train, y_train = self.__load_data(f"{Config.BASE_DIR}/dataset_augmented_2/")
        x_test, y_test, _ = self.__load_test_data(f"{Config.BASE_DIR}/test_data")

        batch_size = 32
        self.num_classes = 10
        epochs = 30

        img_rows, img_cols = 28, 28

        if K.image_data_format() == 'channels_first':
            x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
            x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
            self.input_shape = (1, img_rows, img_cols)
        else:
            x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
            x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
            self.input_shape = (img_rows, img_cols, 1)

        x_train = x_train.astype('float32')
        x_test = x_test.astype('float32')

        x_train /= 255
        x_test /= 255

        print('x_train shape:', x_train.shape)
        print(x_train.shape[0], 'train samples')

        y_train = keras.utils.to_categorical(y_train, self.num_classes)
        y_test = keras.utils.to_categorical(y_test, self.num_classes)

        model = self.__create_model()

        print_summary(model)

        # return

        aug = ImageDataGenerator(
            rotation_range=20,
            width_shift_range=0.1,
            height_shift_range=0.1,
            shear_range=0.2,
            zoom_range=0.2,
            # horizontal_flip=True,
            # vertical_flip=True,
            fill_mode="nearest"
        )

        h = model.fit(x=x_train, y=y_train, epochs=epochs, batch_size=batch_size)
        # h = model.fit_generator(aug.flow(x_train, y_train, batch_size=batch_size),
        #                         epochs=epochs,
        #                         steps_per_epoch=len(x_train) // batch_size)

        # score = model.evaluate(x_test, y_test, verbose=0)

        # print('Test loss:', score[0])
        # print('Test accuracy:', score[1])

        # if save_name is not None:
        # model.save("/Users/a1/univ/S1/diploma/cnn/models/4.h5")

        score = model.evaluate(x_test, y_test, verbose=0)
        print('Test loss:', score[0])
        print('Test accuracy:', score[1])

        # print_summary(model)

        plt.plot(h.history['acc'])
        plt.title('Model accuracy')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        plt.legend(['Train'], loc='upper left')
        plt.show()

        # Plot training & validation loss values
        plt.plot(h.history['loss'])
        plt.title('Model loss')
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        plt.legend(['Train'], loc='upper left')
        plt.show()

    def load(self, model_name: str):
        self.model = load_model(Config.BASE_DIR + '/cnn/models/' + model_name)

    def predict(self, file_path: str):
        img_data = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        img_data = cv2.resize(img_data, (28, 28))
        # img_data = np.invert(img_data)

        img_data = img_data.reshape(1, 28, 28, 1)

        img_data = img_data.astype('float32')

        img_data /= 255

        f = self.model.predict(img_data)

        return f

    def predict_concrete_number(self, data) -> int:
        # plt.imshow(data, interpolation='nearest')
        # plt.show()

        img_data = cv2.resize(data, (28, 28))
        # img_data = np.invert(img_data)

        plt.imshow(img_data, interpolation='nearest')
        plt.show()

        img_data_r = img_data.reshape(1, 28, 28, 1)

        img_data_r = img_data_r.astype('float32')

        img_data_r /= 255

        f = self.model.predict(img_data_r)

        max_v, d = 0, 0
        for i, v in enumerate(f[0]):
            if v > max_v:
                max_v = v
                d = i

        # img_data = np.invert(img_data)
        data = Image.fromarray(img_data)
        data.save(f"{Config.BASE_DIR}/test_data/{d}_{random.randint(100000, 999999)}.png")

        return d

    def test_model(self):
        x_test, y_test, labels = self.__load_test_data(f"{Config.BASE_DIR}/test_data")

        count = 0
        for x, y, label in zip(x_test, y_test, labels):
            img_data = cv2.resize(x, (28, 28))
            # img_data = np.invert(img_data)

            # plt.imshow(img_data, interpolation='nearest')
            # plt.show()

            img_data_r = img_data.reshape(1, 28, 28, 1)

            img_data_r = img_data_r.astype('float32')

            img_data_r /= 255

            f = self.model.predict(img_data_r)

            max_v, d = 0, 0
            for i, v in enumerate(f[0]):
                if v > max_v:
                    max_v = v
                    d = i

            if not d == y:
                print(f"{label}: returned {d}")
            else:
                count += 1

        print('Test accuracy:', count / len(x_test))

        # if K.image_data_format() == 'channels_first':
        #     x_test = x_test.reshape(x_test.shape[0], 1, 28, 28)
        # else:
        #     x_test = x_test.reshape(x_test.shape[0], 28, 28, 1)
        # x_test = x_test.astype('float32')
        # x_test /= 255
        # y_test = keras.utils.to_categorical(y_test, 10)
        # score = self.model.evaluate(x_test, y_test, verbose=0)
        # print('Test loss:', score[0])
        # print('Test accuracy:', score[1])

    def __create_model(self):
        model = Sequential()
        model.add(Conv2D(32, kernel_size=(3, 3), input_shape=self.input_shape))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(64, kernel_size=(3, 3)))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Flatten())  # Flattening the 2D arrays for fully connected layers
        model.add(Dropout(0.2))
        model.add(Dense(128, activation="relu"))
        model.add(Dropout(0.6))
        model.add(Dense(10, activation="softmax"))

        model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["acc"])

        return model
        model = keras.Sequential(
            [
                keras.Input(shape=self.input_shape),
                layers.Conv2D(32, kernel_size=(3, 3), activation="relu"),
                layers.MaxPooling2D(pool_size=(2, 2)),
                layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
                layers.MaxPooling2D(pool_size=(2, 2)),
                layers.Flatten(),
                layers.Dropout(0.5),
                layers.Dense(self.num_classes, activation="softmax"),
            ]
        )
        model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
        return model

        model.add(Conv2D(8, kernel_size=(3, 3),
                         activation='relu',
                         input_shape=self.input_shape))

        # model.add(Conv2D(16, (3, 3),
        #                  activation='relu'
        #                  ))
        # model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Conv2D(32, (3, 3),
                         activation='relu'
                         ))
        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Conv2D(64, (3, 3),
                         activation='relu'
                         ))

        # model.add(Conv2D(128, (3, 3),
        #                  activation='relu'
        #                  ))
        #
        # model.add(Conv2D(128, (3, 3),
        #                  activation='relu'
        #                  ))
        # model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Flatten())

        # model.add(Dense(1024,
        #                 activation='relu'
        #                 ))
        # model.add(Dense(512,
        #                 activation='relu'
        #                 ))
        model.add(Dense(128,
                        activation='relu'
                        ))
        model.add(Dropout(0.5))
        model.add(Dense(32,
                        activation='relu'
                        ))
        model.add(Dense(self.num_classes, activation='softmax'))

        model.compile(loss=keras.losses.categorical_crossentropy,
                      optimizer=keras.optimizers.Adam(learning_rate=0.0001),
                      metrics=['acc'])

        return model

    def __load_data(self, path):
        k = 0
        for x in range(0, 10):
            k += len(os.listdir(path + f"{x}"))

        train_x, train_y = ndarray(shape=(k, 28, 28), dtype=float), array([0 for _ in range(k)])
        m = 0
        for n in range(0, 10):
            train_pic = os.listdir(path + f"{n}")

            for i, x in enumerate(train_pic):
                img_data = cv2.imread(path + f"/{n}/" + x, cv2.IMREAD_GRAYSCALE)
                img_data = cv2.resize(img_data, (28, 28))

                train_x[m] = array(img_data)
                train_y[m] = n

                m += 1

        return train_x, train_y

    def __load_test_data(self, path):
        k = len(os.listdir(path))

        train_x, train_y = ndarray(shape=(k, 28, 28), dtype=float), array([0 for _ in range(k)])
        m = 0

        train_pic = os.listdir(path)

        for i, x in enumerate(train_pic):
            if not x.endswith(".png"):
                continue
            img_data = cv2.imread(path + "/" + x, cv2.IMREAD_GRAYSCALE)
            # img_data = np.invert(img_data)

            train_x[m] = array(img_data)
            train_y[m] = int(x[0])

            m += 1

        return train_x, train_y, train_pic
