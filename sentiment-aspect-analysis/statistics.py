from reviews_processor import get_statistics

if __name__ == "__main__":
    dataset_path = input("Введите путь к датасету: ")
    statistics_path = input("Введите путь для сохранения статистики: ")
    get_statistics(dataset_path, statistics_path)
