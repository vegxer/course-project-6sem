from sklearn.model_selection import train_test_split
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.layers.embeddings import Embedding
from keras import metrics
from keras import models
from datetime import datetime
from keras.callbacks import ModelCheckpoint

from reviews_processor import load_dataset, write_to_file, get_model_accuracy

if __name__ == "__main__":
    print("Time of start: " + datetime.now().strftime("%H:%M:%S"))

    X_dataset, y_dataset = load_dataset("processed_dataset.txt")
    X_train, X_test, y_train, y_test = train_test_split(X_dataset, y_dataset, random_state=11, test_size=0.25)

    words_per_review = 300

    X_train = pad_sequences(X_train, maxlen=words_per_review)
    X_test = pad_sequences(X_test, maxlen=words_per_review)
    X_test, X_val, y_test, y_val = train_test_split(X_test, y_test, random_state=11, test_size=0.30)
    rnn = Sequential()
    rnn.add(Embedding(input_dim=28704, output_dim=128, input_length=words_per_review))
    rnn.add(LSTM(units=128, dropout=0.2, recurrent_dropout=0.2))
    rnn.add(Dense(units=5, activation='sigmoid'))
    rnn.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=[metrics.Accuracy(), metrics.Precision(), metrics.Recall(), metrics.CategoricalAccuracy(),
                         metrics.CategoricalCrossentropy(), metrics.MeanSquaredError()])
    rnn.summary()
    chkpt = ModelCheckpoint('best_model',
                            monitor='val_loss',
                            verbose=1,
                            save_best_only=True,
                            mode='auto')
    rnn.fit(X_train, y_train, epochs=25, batch_size=32, validation_data=(X_val, y_val), callbacks=[chkpt])
    rnn.save('model')
    try:
        write_to_file(X_test, y_test, "training_test_set.txt")
    except:
        print("Ошибка записи тестового датасета")
    results = rnn.evaluate(X_test, y_test)
    print("Results: ")
    print(results)

    print("Точность: " + str(get_model_accuracy(models.load_model("model"), X_test, y_test)))

    print("Time of end: " + datetime.now().strftime("%H:%M:%S"))
