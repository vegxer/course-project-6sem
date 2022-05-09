from keras import models
from joblib import Parallel, delayed
from reviews_processor import read_dictionary, digitize_reviews_to_predict, index_of_max

path_to_reviews = "text_reviews/test.json"
path_to_dictionary = "dictionary.txt"
threads_num = 10
grade_scale = 3

plot_model = models.load_model("grade_{grade_scale}/models/plot_best".format(grade_scale=grade_scale))
music_model = models.load_model("grade_{grade_scale}/models/music_best".format(grade_scale=grade_scale))
actors_model = models.load_model("grade_{grade_scale}/models/actors_best".format(grade_scale=grade_scale))
originality_model = models.load_model("grade_{grade_scale}/models/originality_best".format(grade_scale=grade_scale))
spectacularity_model = models.load_model("grade_{grade_scale}/models/spectacularity_best".format(grade_scale=grade_scale))


def predict(reviews):
    plot_predictions = plot_model.predict(reviews)
    music_predictions = music_model.predict(reviews)
    actors_predictions = actors_model.predict(reviews)
    originality_predictions = originality_model.predict(reviews)
    spectacularity_predictions = spectacularity_model.predict(reviews)

    res = []
    for i in range(len(plot_predictions)):
        res.append({
            "plot": index_of_max(plot_predictions[i]) + 1,
            "music": index_of_max(music_predictions[i]) + 1,
            "actors": index_of_max(actors_predictions[i]) + 1,
            "originality": index_of_max(originality_predictions[i]) + 1,
            "spectacularity": index_of_max(spectacularity_predictions[i]) + 1,
        })

    return res


if __name__ == "__main__":
    dictionary = read_dictionary(path_to_dictionary)
    dataset = digitize_reviews_to_predict(path_to_reviews, dictionary, 250, threads_num)
    print(predict(dataset))
