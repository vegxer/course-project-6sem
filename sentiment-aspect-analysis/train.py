import keras.layers
from keras.optimizer_v2.adam import Adam
from sklearn.model_selection import train_test_split
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, LSTM, SimpleRNN, GRU, Bidirectional, GlobalMaxPool1D, Dropout, Conv1D, MaxPooling1D, \
    Flatten, GlobalMaxPool2D, BatchNormalization
from keras.layers.embeddings import Embedding
from keras import metrics, Input
from keras import models
from datetime import datetime
from keras.callbacks import ModelCheckpoint

from reviews_processor import load_dataset, write_to_file, get_model_accuracy

if __name__ == "__main__":
    print("Time of start: " + datetime.now().strftime("%H:%M:%S"))

    # X_train, y_train = load_dataset("reviewsTrainDigit2.txt")
    # X_test, y_test = load_dataset("reviewsTestDigit2.txt")
    X_dataset, y_dataset = load_dataset("grade_three/digit_datasets/plot.txt")
    X_train, X_test, y_train, y_test = train_test_split(X_dataset, y_dataset, random_state=42, test_size=0.2)

    words_per_review = 250

    X_train = pad_sequences(X_train, maxlen=words_per_review)
    X_test = pad_sequences(X_test, maxlen=words_per_review)
    # X_test, X_val, y_test, y_val = train_test_split(X_test, y_test, random_state=42, test_size=0.30)
    rnn = Sequential()
    rnn.add(Input(shape=(250,)))
    rnn.add(Embedding(input_dim=39731, output_dim=250, input_length=words_per_review))
    rnn.add(Bidirectional(LSTM(units=250, return_sequences=True)))
    rnn.add(GlobalMaxPool1D())
    rnn.add(Dense(units=250, activation='tanh'))
    rnn.add(Dropout(0.5))
    rnn.add(Dense(units=3, activation='sigmoid'))

    rnn.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=[metrics.Accuracy(), metrics.Precision(), metrics.Recall(), metrics.CategoricalAccuracy(),
                         metrics.CategoricalCrossentropy(), metrics.MeanSquaredError()])
    rnn.summary()
    chkpt = ModelCheckpoint('grade_three/models/plot_model_best',
                            monitor='val_loss',
                            verbose=1,
                            save_best_only=True,
                            mode='auto')
    rnn.fit(X_train, y_train, epochs=2, batch_size=32, validation_data=(X_test, y_test), callbacks=[chkpt])
    rnn.save('grade_three/models/plot_model')
    try:
        write_to_file(X_test, y_test, "test_set.txt")
    except Exception:
        print("Ошибка записи тестового датасета")
    results = rnn.evaluate(X_test, y_test)
    print("Результаты: ")
    print("loss: " + str(results[0]))
    print("accuracy: " + str(results[1]))
    precision = float(results[2])
    recall = float(results[3])
    print("precision: " + str(precision))
    print("recall: " + str(recall))
    print("F1: " + str((2 * precision * recall) / (precision + recall)))
    print("categorical accuracy: " + str(results[4]))
    print("categorical crossentropy: " + str(results[5]))
    print("mean squared error: " + str(results[6]))

    # print("Точность: " + str(get_model_accuracy(models.load_model("plot_model2"), X_test, y_test)))

    print("Time of end: " + datetime.now().strftime("%H:%M:%S"))
