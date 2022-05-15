import json
import random
import re
import spacy
from joblib import Parallel, delayed
from keras.preprocessing.sequence import pad_sequences
from keras.utils.np_utils import to_categorical
from nltk import SnowballStemmer

nlp = spacy.load("ru_core_news_sm")
stemmer = SnowballStemmer("russian")


def num_to_text(num):
    if num == 1:
        return 'oneStar'
    if num == 2:
        return 'twoStar'
    if num == 3:
        return 'threeStar'
    if num == 4:
        return 'fourStar'
    return 'fiveStar'


def get_statistics(path, save_path):
    with open(path, "r", encoding="utf-8") as dataset:
        reviews = json.load(dataset)
    statistics = {}
    statistics['count'] = 0
    statistics['plot'] = {}
    statistics['plot']['oneStar'] = 0
    statistics['plot']['twoStar'] = 0
    statistics['plot']['threeStar'] = 0
    statistics['plot']['fourStar'] = 0
    statistics['plot']['fiveStar'] = 0

    statistics['music'] = {}
    statistics['music']['oneStar'] = 0
    statistics['music']['twoStar'] = 0
    statistics['music']['threeStar'] = 0
    statistics['music']['fourStar'] = 0
    statistics['music']['fiveStar'] = 0

    statistics['originality'] = {}
    statistics['originality']['oneStar'] = 0
    statistics['originality']['twoStar'] = 0
    statistics['originality']['threeStar'] = 0
    statistics['originality']['fourStar'] = 0
    statistics['originality']['fiveStar'] = 0

    statistics['spectacularity'] = {}
    statistics['spectacularity']['oneStar'] = 0
    statistics['spectacularity']['twoStar'] = 0
    statistics['spectacularity']['threeStar'] = 0
    statistics['spectacularity']['fourStar'] = 0
    statistics['spectacularity']['fiveStar'] = 0

    statistics['actors'] = {}
    statistics['actors']['oneStar'] = 0
    statistics['actors']['twoStar'] = 0
    statistics['actors']['threeStar'] = 0
    statistics['actors']['fourStar'] = 0
    statistics['actors']['fiveStar'] = 0

    statistics['rating'] = {}
    statistics['rating']['oneStar'] = 0
    statistics['rating']['twoStar'] = 0
    statistics['rating']['threeStar'] = 0
    statistics['rating']['fourStar'] = 0
    statistics['rating']['fiveStar'] = 0

    for review in reviews:
        if review['plot'] is not None and review['music'] is not None and review['actors'] is not None and review['originality'] is not None and review['spectacularity'] is not None:
            statistics['count'] += 1
            try:
                statistics['rating'][num_to_text(review['rating'])] += 1
            except Exception:
                print("err")
            statistics['plot'][num_to_text(review['plot'])] += 1
            statistics['music'][num_to_text(review['music'])] += 1
            statistics['actors'][num_to_text(review['actors'])] += 1
            statistics['originality'][num_to_text(review['originality'])] += 1
            statistics['spectacularity'][num_to_text(review['spectacularity'])] += 1

    with open(save_path, "w", encoding="utf-8") as file:
        json.dump(statistics, file)


def scale_to_five_grade(grade):
    return to_categorical(grade - 1, num_classes=5)


def scale_to_three_grade(grade):
    grades = [0, 0, 0]
    if grade < 3:
        grades[0] = 1
    elif grade == 3:
        grades[1] = 1
    else:
        grades[2] = 1
    return grades


def scale_to_two_grade(grade):
    grades = [0, 0]
    if grade < 3:
        grades[0] = 1
    else:
        grades[1] = 1
    return grades


def get_list_of_reviews_and_y_res(reviews, aspect, grade_scale):
    scale_func = scale_to_five_grade if grade_scale == 5 else scale_to_three_grade if grade_scale == 3 else scale_to_two_grade
    y_res = []
    processed_reviews = []
    corrupted_reviews = 0
    for review in reviews:
        try:
            review_text = 'оценка: ' + str(review['rating']) + "\n\n" + \
                          'рекомендация: ' + review['recommend'] + "\n\n" + \
                          "достоинства: " + review['plus'].lower() + "\n\n" + \
                          "недостатки: " + review['minus'].lower() + "\n\n" + \
                          "отзыв: " + review['body'].lower()
            y_res.append(scale_func(review[aspect]))
            processed_reviews.append(review_text)
        except Exception:
            corrupted_reviews += 1
    print("Повреждённых отзывов: " + str(corrupted_reviews))
    return processed_reviews, y_res


def get_list_of_reviews(reviews):
    processed_reviews = []
    corrupted_reviews = 0
    for review in reviews:
        try:
            review_text = (('оценка: ' + str(review['rating']) + "\n\n") if 'rating' in review else '') + \
                          (('рекомендация: ' + review['recommend'] + "\n\n") if 'recommend' in review else '') + \
                          (("достоинства: " + review['plus'].lower() + "\n\n") if 'plus' in review else '') + \
                          (("недостатки: " + review['minus'].lower() + "\n\n") if 'minus' in review else '') + \
                          "отзыв: " + review['body'].lower()
            processed_reviews.append(review_text)
        except Exception:
            corrupted_reviews += 1
    print("Некорректных отзывов: " + str(corrupted_reviews))
    return processed_reviews


def pos_tag_review(review):
    tagged = []
    tokens = nlp(review)
    for token in tokens:
        tagged.append([token.lemma_, token.pos_])
    return tagged


def pos_tag_reviews(reviews, threads_num):
    return Parallel(n_jobs=threads_num)(delayed(pos_tag_review)(review) for review in reviews)


def pos_tag_review_unpossed(review):
    tagged = []
    tokens = nlp(review)
    for token in tokens:
        tagged.append(stemmer.stem(token.lemma_))
    return tagged


def pos_tag_reviews_unpossed(reviews, threads_num):
    return Parallel(n_jobs=threads_num)(delayed(pos_tag_review_unpossed)(review) for review in reviews)


def clean_review(review):
    cleaned_review = []
    for word in review:
        if (len(word[0]) == 1 and word[0].isdigit()) or (len(word[0]) > 1 and word[1] in ['PROPN', 'ADJ', 'VERB', 'NOUN']):
            cleaned_review.append(stemmer.stem(word[0]))
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
    dictionary = dict([item for item in dictionary.items() if item[1] > 2])
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
    return dictionary, encoded_reviews


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
                save_file.write(str(float(star)))
                save_file.write(" ")
            save_file.write("\n")


def save_dictionary(save_path, dictionary):
    with open(save_path, "w", encoding="utf-8") as save_file:
        for item in dictionary.items():
            save_file.write(item[0] + " " + str(item[1]))
            save_file.write("\n")


def generate_dataset(path_to_text_dataset, path_to_save_numeric_dataset, aspect, grade_scale, threads_num, review_length=250):
    with open(path_to_text_dataset, "r", encoding="utf-8") as dataset:
        processed_reviews, y_res = get_list_of_reviews_and_y_res(json.load(dataset), aspect, grade_scale)
    processed_reviews = pos_tag_reviews(processed_reviews, threads_num)
    processed_reviews = clean_reviews(processed_reviews, threads_num)
    processed_reviews = cut_reviews(processed_reviews, review_length)
    dictionary, X_res = encode_frequent(processed_reviews, threads_num)
    print("Vocab size: " + str(len(dictionary)))

    zipped = list(zip(X_res, y_res))
    random.shuffle(zipped)
    X_res, y_res = zip(*zipped)

    write_to_file(X_res, y_res, path_to_save_numeric_dataset)
    save_dictionary("dictionary.txt", dictionary)


def digitize_reviews(reviews, dictionary):
    digitized = []
    for i in range(len(reviews)):
        digitized.append([])
        for word in reviews[i]:
            if word in dictionary:
                digitized[i].append(dictionary[word])
    return digitized


def load_text_dataset(path_to_text_dataset, dictionary, review_length, aspect, grade_scale, threads_num):
    with open(path_to_text_dataset, "r", encoding="utf-8") as dataset:
        processed_reviews, y_res = get_list_of_reviews_and_y_res(json.load(dataset), aspect, grade_scale)
    processed_reviews = pos_tag_reviews_unpossed(processed_reviews, threads_num)
    processed_reviews = digitize_reviews(processed_reviews, dictionary)
    processed_reviews = cut_reviews(processed_reviews, review_length)
    return processed_reviews, y_res


def load_reviews_dataset(path_to_text_dataset: str, dictionary: dict, review_length: int, threads_num: int):
    with open(path_to_text_dataset, "r", encoding="utf-8") as dataset:
        processed_reviews = get_list_of_reviews(json.load(dataset))
    processed_reviews = pos_tag_reviews_unpossed(processed_reviews, threads_num)
    processed_reviews = digitize_reviews(processed_reviews, dictionary)
    processed_reviews = cut_reviews(processed_reviews, review_length)
    processed_reviews = pad_sequences(processed_reviews, maxlen=review_length)
    return processed_reviews


def read_dictionary(path):
    dictionary = {}
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            item = line.split(' ')
            dictionary[item[0]] = int(item[1])
    return dictionary


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
    return X_res, y_res


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
