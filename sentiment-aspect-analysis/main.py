from sklearn.model_selection import train_test_split
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.layers.embeddings import Embedding

from reviews_loader import load_dataset

if __name__ == "__main__":
    X_train, y_train = load_dataset("../reviewsTrain.json")
    X_test, y_test = load_dataset("../reviewsTest.json")

    words_per_review = 350

    X_train = pad_sequences(X_train, maxlen=words_per_review)
    X_test = pad_sequences(X_test, maxlen=words_per_review)
    X_test, X_val, y_test, y_val = train_test_split(
        X_test, y_test, random_state=11, test_size=0.20)
    rnn = Sequential()
    rnn.add(Embedding(input_dim=15000, output_dim=128,
                      input_length=words_per_review))
    rnn.add(LSTM(units=128, dropout=0.2, recurrent_dropout=0.2))
    rnn.add(Dense(units=5, activation='sigmoid'))
    rnn.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy'])
    rnn.summary()
    rnn.fit(X_train, y_train, epochs=10, batch_size=32,
            validation_data=(X_val, y_val))
    results = rnn.evaluate(X_test, y_test)
    print("Results: ")
    print(results)
