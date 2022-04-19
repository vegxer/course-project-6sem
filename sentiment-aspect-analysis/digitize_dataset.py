from reviews_processor import generate_dataset

if __name__ == "__main__":
    path = input("Введите путь к текстовому датасету: ")
    digitized_path = input("Введите путь для сохранения оцифрованного датасета")
    generate_dataset(path, digitized_path, 10)
