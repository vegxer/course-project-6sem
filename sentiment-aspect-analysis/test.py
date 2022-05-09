from keras import models
from keras_preprocessing.sequence import pad_sequences

from reviews_processor import load_dataset, get_model_accuracy, load_text_dataset, read_dictionary

if __name__ == "__main__":
    model = models.load_model("grade_5/models/plot_best")
    choice = input("1 - Текстовый датасет\n2 - Оцифрованный датасет\nВаш выбор: ")
    path = input("Введите путь датасета: ")
    if choice == '1':
        dic_path = input("Введите путь к словарю: ")
        dicti = read_dictionary(dic_path)
        aspect = input("Введите аспект, оценку которого нужно определить: ")
        grade_scale = int(input("Введите шкалу оценивания (2, 3, 5): "))
        X_test, y_test = load_text_dataset(path, dicti, 250, aspect, grade_scale, 10)
    else:
        X_test, y_test = load_dataset(path)
    X_test = pad_sequences(X_test, maxlen=250)
    print("Точность модели: " + str(get_model_accuracy(model, X_test, y_test)))
