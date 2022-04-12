import json

import random
import numpy
from keras.preprocessing.text import one_hot
from keras.preprocessing.text import text_to_word_sequence


def load_dataset(path_to_dataset):
    X_res = []
    y_res = []
    with open(path_to_dataset, "r", encoding="ISO-8859-5") as dataset:
        reviews = json.load(dataset)
        for review in reviews:
            review_text = "Достоинства: " + review['plus'] + "\n\n" + \
                          "Недостатки: " + review['minus'] + "\n\n" + \
                          "Отзыв: " + review['body']
            result = one_hot(review_text, round(len(set(text_to_word_sequence(review_text)))))
            X_res.append(result)

            y_res.append([review['plot'], review['actors'], review['music'], review['spectacularity'], review['originality']])

    zipped = list(zip(X_res, y_res))
    random.shuffle(zipped)
    X_res, y_res = zip(*zipped)
    return numpy.asarray(X_res), numpy.asarray(y_res)
