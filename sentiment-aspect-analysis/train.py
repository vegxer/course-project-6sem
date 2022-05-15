from sklearn.model_selection import train_test_split
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, LSTM, Bidirectional, Dropout, GlobalMaxPool1D
from keras.layers.embeddings import Embedding
from keras import metrics, Input
from datetime import datetime
from keras.callbacks import ModelCheckpoint, EarlyStopping
from numpy import asarray

from reviews_processor import load_dataset

if __name__ == "__main__":
    print("Time of start: " + datetime.now().strftime("%H:%M:%S"))
    aspect = "plot"
    scale = "3"
    X_dataset, y_dataset = load_dataset(f"grade_{scale}/digit_datasets/{aspect}_body.txt")
    X_train, X_test, y_train, y_test = train_test_split(asarray(X_dataset), asarray(y_dataset),
                                                        random_state=42,
                                                        test_size=0.2)

    words_per_review = 250

    X_train = pad_sequences(X_train, maxlen=words_per_review)
    X_test = pad_sequences(X_test, maxlen=words_per_review)
    rnn = Sequential()
    rnn.add(Input(shape=(250,)))
    rnn.add(Embedding(input_dim=39731, output_dim=words_per_review, input_length=words_per_review))
    rnn.add(Bidirectional(LSTM(units=words_per_review // 2, return_sequences=True)))
    rnn.add(GlobalMaxPool1D())
    rnn.add(Dense(units=words_per_review // 5, activation='tanh'))
    rnn.add(Dropout(0.5))
    rnn.add(Dense(units=int(scale), activation='sigmoid'))

    rnn.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=[metrics.CategoricalAccuracy(),
                         metrics.Precision(class_id=0),
                         metrics.Precision(class_id=1),
                         metrics.Precision(class_id=2),
                         metrics.Precision(),
                         metrics.Recall(class_id=0),
                         metrics.Recall(class_id=1),
                         metrics.Recall(class_id=2),
                         metrics.Recall(),
                         ])
    rnn.summary()
    chkpt = ModelCheckpoint(f'grade_{scale}/models/{aspect}_best',
                            monitor='val_categorical_accuracy',
                            verbose=1,
                            save_best_only=True,
                            mode='auto')
    early_stop = EarlyStopping(monitor='val_categorical_accuracy', min_delta=0.0001,
                               patience=3, verbose=1, mode='auto')
    rnn.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test), callbacks=[chkpt])
    rnn.save(f'grade_{scale}/models/{aspect}')

    results = rnn.evaluate(X_test, y_test)
    print(results)

print("Time of end: " + datetime.now().strftime("%H:%M:%S"))
