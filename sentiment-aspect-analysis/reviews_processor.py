import json
import random
import re
import numpy
import spacy
from joblib import Parallel, delayed
from keras.utils.np_utils import to_categorical


def get_list_of_reviews_and_y_res(reviews):
    y_res = []
    processed_reviews = []
    for review in reviews:
        review_text = "достоинства: " + review['plus'].lower() + "\n" + \
                      "недостатки: " + review['minus'].lower() + "\n" + \
                      "отзыв: " + review['body'].lower()
        processed_reviews.append(review_text)
        y_res.append(to_categorical(review['rating'] - 1, num_classes=5))
    return processed_reviews, y_res


def pos_tag_review(review):
    nlp = spacy.load("ru_core_news_sm")
    tagged = []
    tokens = nlp(review)
    for token in tokens:
        tagged.append([token.lemma_, token.pos_])
    return tagged


def pos_tag_reviews(reviews, threads_num):
    return Parallel(n_jobs=threads_num)(delayed(pos_tag_review)(review) for review in reviews)


def clean_review(review):
    cleaned_review = []
    for word in review:
        if len(word[0]) > 1 and word[1] in ['PROPN', 'ADJ', 'VERB', 'NOUN']:
            cleaned_review.append(word[0])
    return cleaned_review


def clean_reviews(reviews, threads_num):
    return Parallel(n_jobs=threads_num)(delayed(clean_review)(review) for review in reviews)


def cut_reviews(reviews, length):
    for i in range(len(reviews)):
        if len(reviews[i]) > length:
            reviews[i] = reviews[i][:length]
    return reviews


def create_sorted_dictionary(reviews):
    dictionary = {}
    for review in reviews:
        for word in review:
            if word not in dictionary:
                dictionary[word] = 1
            else:
                dictionary[word] += 1
    dictionary = dict([item for item in dictionary.items() if item[1] > 3])
    sorted_dict = list(sorted(dictionary.items(), key=lambda item: item[1]))
    dict_len = len(sorted_dict)
    tuples = []
    for i in range(dict_len):
        tuples.append((sorted_dict[i][0], dict_len - i))
    return dict(tuples)


def parallel_encode(review, dictionary):
    encoded = []
    for word in review:
        if word in dictionary:
            encoded.append(dictionary[word])
    return encoded


def encode_frequent(reviews, threads_num):
    dictionary = create_sorted_dictionary(reviews)
    encoded_reviews = Parallel(n_jobs=threads_num)(delayed(parallel_encode)(review, dictionary) for review in reviews)
    return len(dictionary), encoded_reviews


def write_to_file(X_res, y_res, save_path):
    with open(save_path, "w", encoding="utf-8") as save_file:
        for x in X_res:
            for el in x:
                save_file.write(str(el))
                save_file.write(" ")
            save_file.write("\n")
        save_file.write("\n")
        for y in y_res:
            for star in y:
                save_file.write(str(star))
                save_file.write(" ")
            save_file.write("\n")


def generate_dataset(path_to_text_dataset, path_to_save_numeric_dataset, threads_num, review_length=300):
    with open(path_to_text_dataset, "r", encoding="utf-8") as dataset:
        processed_reviews, y_res = get_list_of_reviews_and_y_res(json.load(dataset))
    processed_reviews = pos_tag_reviews(processed_reviews, threads_num)
    processed_reviews = clean_reviews(processed_reviews, threads_num)
    processed_reviews = cut_reviews(processed_reviews, review_length)
    vocabulary_size, X_res = encode_frequent(processed_reviews, threads_num)
    print("Vocab size: " + str(vocabulary_size))

    zipped = list(zip(X_res, y_res))
    random.shuffle(zipped)
    X_res, y_res = zip(*zipped)

    write_to_file(X_res, y_res, path_to_save_numeric_dataset)


def load_dataset(path_to_numeric_dataset):
    X_res = []
    y_res = []
    x = True
    with open(path_to_numeric_dataset, "r", encoding="utf-8") as dataset:
        for line in dataset:
            if line == '\n':
                if not x:
                    print("Ошибка чтения файла")
                x = False
                continue
            if x:
                X_res.append([int(element) for element in re.findall('\\d+', line)])
            else:
                y_res.append([int(element[0]) for element in re.findall('\\d\\.\\d', line)])
    return numpy.asarray(X_res), numpy.asarray(y_res)


def index_of_max(predicts):
    index = 0
    for k in range(len(predicts)):
        if predicts[k] > predicts[index]:
            index = k
    return index


def get_model_accuracy(model, X_test, y_test):
    predictions = model.predict(X_test)
    correct_count = 0
    for i in range(len(predictions)):
        if index_of_max(predictions[i]) == index_of_max(y_test[i]):
            correct_count += 1
    return correct_count / len(X_test)
