from keras import models

from reviews_loader import load_dataset
from keras.preprocessing.sequence import pad_sequences

if __name__ == "__main__":
    model = models.load_model("best_model")
    X_train, y_train = load_dataset("test.json")
    words_per_review = 350
    X_train = pad_sequences(X_train, maxlen=words_per_review)
    print(model.predict(X_train))
