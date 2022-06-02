from sklearn.model_selection import train_test_split, StratifiedKFold
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, LSTM, Bidirectional, Dropout, GlobalMaxPool1D
from keras.layers.embeddings import Embedding
from keras import metrics, Input
from datetime import datetime
from keras.callbacks import ModelCheckpoint, EarlyStopping
from numpy import asarray, zeros

from reviews_processor import load_dataset, get_statistics


def sublist(target: list, indexes: list[int]) -> list:
    res = []
    for index in indexes:
        res.append(target[index])
    return res


if __name__ == "__main__":
    print("Time of start: " + datetime.now().strftime("%H:%M:%S"))

    aspects = ["plot", "music", "actors", "originality", "spectacularity"]
    scales = ["2", "3", "5"]

    for aspect in aspects:
        for scale in scales:
            X_dataset, y_dataset = load_dataset(f"grade_{scale}/digit_datasets/{aspect}.txt")

            split = 1
            results = []
            kFold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            for train, test in kFold.split([0] * len(X_dataset), [0] * len(X_dataset)):
                X_train = asarray(sublist(X_dataset, train))
                y_train = asarray(sublist(y_dataset, train))
                X_test = asarray(sublist(X_dataset, test))
                y_test = asarray(sublist(y_dataset, test))
                get_statistics(y_train, y_test, f"stats_{aspect}_{scale}_{split}.json")
                split += 1

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

                metric = [metrics.CategoricalAccuracy(), metrics.Precision(), metrics.Recall()]
                for i in range(int(scale)):
                    metric.append(metrics.Precision(class_id=i))
                    metric.append(metrics.Recall(class_id=i))

                rnn.compile(optimizer='adam',
                            loss='categorical_crossentropy',
                            metrics=metric)
                rnn.summary()
                chkpt = ModelCheckpoint(f'grade_{scale}/models/{aspect}_{split}_best',
                                        monitor='val_categorical_accuracy',
                                        verbose=1,
                                        save_best_only=True,
                                        mode='auto')

                rnn.fit(X_train, y_train, epochs=20, batch_size=32, chkpt=[chkpt])
                rnn.save(f'grade_{scale}/models/{aspect}_{split}')

                results.append(rnn.evaluate(X_test, y_test))

            print(results)

    print("Time of end: " + datetime.now().strftime("%H:%M:%S"))
