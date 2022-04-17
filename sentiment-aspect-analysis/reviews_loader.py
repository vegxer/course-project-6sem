import json

from joblib import Parallel, delayed
import multiprocessing

import spacy
import random
import numpy
from keras.preprocessing.text import one_hot
from keras.preprocessing.text import text_to_word_sequence
from keras.utils.np_utils import to_categorical

from nltk.corpus import PlaintextCorpusReader
from nltk.stem.snowball import SnowballStemmer
from nltk.probability import FreqDist
from nltk.tokenize import RegexpTokenizer
from nltk import bigrams
from nltk import pos_tag
from collections import OrderedDict
from sklearn.metrics import classification_report, accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import GridSearchCV
from sklearn.utils import shuffle
from multiprocessing import Pool
import numpy as np
from scipy.sparse import csr_matrix

nlp = spacy.load("ru_core_news_sm")
stemmer = SnowballStemmer("russian")


def get_list_of_reviews_and_y_res(reviews):
    y_res = []
    processed_reviews = []
    for review in reviews:
        review_text = "достоинства: " + review['plus'].lower() + "\n\n" + \
                      "недостатки: " + review['minus'].lower() + "\n\n" + \
                      "отзыв: " + review['body'].lower()
        processed_reviews.append(text_to_word_sequence(review_text))
        y_res.append(to_categorical(review['plot'] - 1, num_classes=5))
    return processed_reviews, y_res


def pos_tag_review(review):
    return pos_tag(review, lang='rus')


def pos_tag_reviews(reviews):
    return Parallel(n_jobs=1)(delayed(pos_tag_review)(review) for review in reviews)


def clean_review(review):
    cleaned_review = []
    for word in review:
        cleaned_review.append(nlp(word)[0].lemma_)
    return cleaned_review


def clean_reviews(reviews):
    return Parallel(n_jobs=1)(delayed(clean_review)(review) for review in reviews)


def load_dataset(path_to_dataset):
    X_res = []
    y_res = []
    # result = one_hot(
    #     review_text,
    #     round(len(
    #         set(text_to_word_sequence(review_text))
    #     ))
    # )
    with open(path_to_dataset, "r", encoding="utf-8") as dataset:
        processed_reviews, y_res = get_list_of_reviews_and_y_res(json.load(dataset))
        # processed_reviews = pos_tag_reviews(processed_reviews)
        processed_reviews = clean_reviews(processed_reviews)
        cleaned_words = []
        # for i in words:
        #     if i[1] in ['S', 'A', 'V', 'ADV']:
        #         cleaned_words.append(stemmer.stem(i[0]))
        # return cleaned_words
        print(1)

    zipped = list(zip(X_res, y_res))
    random.shuffle(zipped)
    X_res, y_res = zip(*zipped)
    return numpy.asarray(X_res), numpy.asarray(y_res)
