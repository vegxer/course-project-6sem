from keras import models

from keras.preprocessing.sequence import pad_sequences

from reviews_processor import generate_dataset, load_dataset, get_model_accuracy


if __name__ == "__main__":
    model = models.load_model("model")
    choice = input("1 - Текстовый датасет\n2 - Оцифрованный датасет\nВаш выбор: ")
    path = input("Введите путь датасета: ")
    if choice == 1:
        generate_dataset(path, "1.txt", 8)
        X_test, y_test = load_dataset("1.txt")
    else:
        X_test, y_test = load_dataset(path)
    words_per_review = 300
    X_test = pad_sequences(X_test, maxlen=words_per_review)
    print("Точность модели: " + str(get_model_accuracy(model, X_test, y_test)))
