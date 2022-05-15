import json
from threading import Thread

from keras import models
from numpy import ndarray
from numpy.typing import NDArray
from reviews_processor import read_dictionary, index_of_max, load_reviews_dataset

# Переменные окружения
path_to_reviews = "text_reviews/test.json"
path_to_dictionary = "dictionary.txt"
threads_num = 4
grade_scale = 5
res_path = "res2.json"


def predict_aspect(reviews: NDArray[NDArray[int]], aspect: str, pred_res: list):
    pred_res.append(models.load_model(f"grade_{grade_scale}/models/{aspect}_best")
                    .predict(reviews))


# Функция предсказания аспектов отзывов
def predict(reviews: NDArray[NDArray[int]]) -> list[dict[str, int]]:
    plot_predictions = []
    music_predictions = []
    actors_predictions = []
    originality_predictions = []
    spectacularity_predictions = []
    plot_thread = Thread(target=predict_aspect, args=[reviews, "plot", plot_predictions])
    music_thread = Thread(target=predict_aspect, args=[reviews, "music", music_predictions])
    actors_thread = Thread(target=predict_aspect, args=[reviews, "actors", actors_predictions])
    originality_thread = Thread(target=predict_aspect, args=[reviews, "originality", originality_predictions])
    spectacularity_thread = Thread(target=predict_aspect, args=[reviews, "spectacularity", spectacularity_predictions])
    plot_thread.start()
    music_thread.start()
    actors_thread.start()
    originality_thread.start()
    spectacularity_thread.start()
    plot_thread.join()
    music_thread.join()
    actors_thread.join()
    originality_thread.join()
    spectacularity_thread.join()

    res = []
    for i in range(len(plot_predictions[0])):
        res.append({
            "plot": index_of_max(plot_predictions[0][i]) + 1,
            "music": index_of_max(music_predictions[0][i]) + 1,
            "actors": index_of_max(actors_predictions[0][i]) + 1,
            "originality": index_of_max(originality_predictions[0][i]) + 1,
            "spectacularity": index_of_max(spectacularity_predictions[0][i]) + 1,
        })

    return res


def main():
    dictionary = read_dictionary(path_to_dictionary)
    dataset = load_reviews_dataset(path_to_reviews, dictionary, 250, threads_num)
    with open(res_path, "w", encoding="utf-8") as file:
        json.dump(predict(dataset), file)


if __name__ == "__main__":
    main()
