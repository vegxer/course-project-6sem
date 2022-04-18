from keras import models

from reviews_loader import generate_dataset, load_dataset
from keras.preprocessing.sequence import pad_sequences

if __name__ == "__main__":
    model = models.load_model("best_model")
    generate_dataset("test.json", "1.txt")
    X_train, y_train = load_dataset("1.txt")
    words_per_review = 300
    X_train = pad_sequences(X_train, maxlen=words_per_review)
    print(model.predict(X_train))
