import json

import pandas as pd
# nltk.download('stopwords')
from nltk.corpus import stopwords
import yake

from main import NUMBER_OF_REVIEWS_TO_CONSIDER

stop_words = set(stopwords.words('english'))
from langdetect import detect
from textblob import TextBlob
from nltk.tokenize import word_tokenize
from fuzzywuzzy import fuzz



def downsize_book_entries(id_to_title_score_location, books_info_location):
    # Open the output file in write mode
    with open(id_to_title_score_location, "w") as destination:
        id_to_entry_dic = {}
        # Iterate over the JSON data in chunks using pandas
        df_reader = pd.read_json(books_info_location, orient="records", lines=True, chunksize=3000)
        for chunk in df_reader:
            # Convert the chunk to a list of dictionaries and write it to the output file in JSON format
            chunk_data = chunk[['book_id', 'title', 'average_rating', 'similar_books']].to_dict(orient="records")
            for entry in chunk_data:
                id = str(entry['book_id'])
                entry.pop('book_id')
                id_to_entry_dic[id] = entry
        json.dump(id_to_entry_dic, destination)
    return id_to_entry_dic


def identify_keywords(keywords_location, reviews_location, id_to_entry, language, max_ngram_size, deduplication_threshold,
                      deduplication_algo, windowSize, numOfKeywords, review_count_threshold):
    with open(keywords_location, "w") as destination:
        df_reader = pd.read_json(reviews_location, orient="records", lines=True, chunksize=1000)
        custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold,
                                                    dedupFunc=deduplication_algo, windowsSize=windowSize,
                                                    top=numOfKeywords, features=None)
        chunk_counter = 0
        keywords = {}
        book_frequency = {}
        for chunk in df_reader:
            chunk_counter += 1
            # Convert the chunk to a list of dictionaries and write it to the output file in JSON format
            chunk_data = chunk[['book_id', 'review_text']].to_dict(orient="records")
            for entry in chunk_data:
                entry['book_id'] = str(entry['book_id'])
                # Increase count of this book in book_frequency
                if entry['book_id'] in book_frequency.keys():
                    book_frequency[entry['book_id']] += 1
                else:
                    book_frequency[entry['book_id']] = 1
                # Check if the book is in the database
                if entry['book_id'] in id_to_entry.keys() and book_frequency[entry['book_id']] < review_count_threshold:
                    # Check if it isn't empty string
                    if len(entry['review_text']) == 0:
                        continue

                    # Check if entry is written in English
                    try:
                        if detect(entry['review_text']) != 'en':
                            continue
                    except:
                        continue
                    # Join into a string separated by spaces after lemmatization
                    lemm_chunk = " ".join(lemmatize(entry['review_text']))
                    #lemm_chunk = entry['review_text']
                    # Extract keywords
                    keywords_list = custom_kw_extractor.extract_keywords(lemm_chunk)
                    for keyword, score in keywords_list:
                        # Add keyword to dictionary in format 'keyword':[list of books it occurred in]
                        if keyword not in keywords.keys():
                            keywords[keyword] = [str(entry['book_id'])]
                        else:
                            keywords[keyword].append(str(entry['book_id']))
            # Stop after a certain number of chunks
            if chunk_counter == NUMBER_OF_REVIEWS_TO_CONSIDER:
                break
        return keywords


def limit_id_to_entry_to_review_matches(id_to_book_original, keywords):
    id_to_book_new = {}
    for word in keywords:
        for book in keywords[word]:
            if book not in id_to_book_new.keys():
                try:
                    id_to_book_new[book] = id_to_book_original[book]
                except:
                    continue
    return id_to_book_new

def load_dictionary(location):
    with open(location, "r") as source:
        return json.load(source)


def save_dictionary(location, dictionary):
    with open(location, 'w') as dic_file:
        json.dump(dictionary, dic_file)

def tokenize(cleaned_file):
    words = []
    for sentence in cleaned_file.split():
        word = word_tokenize(sentence)
        words.extend(word)
    return words

def lemmatize(cleaned_file):
    lemmatized_list = []
    word_list = tokenize(cleaned_file)
    for word in word_list:
        sent = TextBlob(str.lower(word))
        tag_dict = {"J": 'a',
                    "N": 'n',
                    "V": 'v',
                    "R": 'r'}
        words_and_tags = [(w, tag_dict.get(pos[0], 'n')) for w, pos in sent.tags]
        lemmatized_list.append([wd.lemmatize(tag) for wd, tag in words_and_tags])
    # ugly but it works
    return [item for sublist in lemmatized_list for item in sublist]


def transform_books(books):
    dictionary = {}
    for entry in books:
        dictionary[entry['book_id']] = [entry['title'], entry['average_rating']]
    return dictionary

def downsize_to_reviews(reviews, id_to_title_score):
    downsized_id_lookup = {}
    i = 0  # Counter for index of current entry
    while i < len(reviews):
        entry = reviews[i]
        if entry['book_id'] in id_to_title_score.keys():
            downsized_id_lookup[entry['book_id']] = id_to_title_score[entry['book_id']]
            i += 1
        else:
            # Remove current entry from list and return it
            reviews.pop(i)
    return downsized_id_lookup, reviews


def search(query, id_title_score):
    max_score = 0
    max_key = None
    for key in id_title_score.keys():
        title = id_title_score[key]['title']
        score = fuzz.ratio(title, query)
        if score > max_score:
            max_score = score
            max_key = key
        if score > 95:
            # In case the title is near exact,
            # there is no need to go through the whole list
            return key
    return max_key


def get_books_sharing_keywords(keywords, queried_book):
    books_sharing_keywords = {}
    max_count = 0
    min_count = 0
    queried_book = str(queried_book)
    for word in keywords.keys():
        if queried_book in keywords[word]:
            #keywords[word].remove(queried_book)
            for book in keywords[word]:
                try:
                    books_sharing_keywords[book] += 1
                    current_count = books_sharing_keywords[book]
                    max_count = current_count if current_count > max_count else max_count
                    min_count = current_count if current_count < min_count else min_count
                except:
                    books_sharing_keywords[book] = 1
    return books_sharing_keywords, max_count, min_count


def select_books(books_sharing_keywords):
    sorted_items = sorted(books_sharing_keywords.items(), key=lambda item: item[1], reverse=True)
    books_sharing_keywords.clear()
    books_sharing_keywords.update(sorted_items)
    return list(books_sharing_keywords.keys())

def print_top_books(selected_books, TOP_X, id_to_book_entry):
    selected_size = len(selected_books)
    books_in_top_x = []
    # ensure you don't run out of books if ther are only a few found
    top_x = selected_size if selected_size < TOP_X else TOP_X
    for position in range(1, top_x):
        books_in_top_x.append(selected_books[position])
        print(f"{position+1}. {id_to_book_entry[selected_books[position]]['title']} "
              f"with rating: {id_to_book_entry[selected_books[position]]['average_rating']}")
    return books_in_top_x


def evaluate_finds(selected_books, id_to_book_entry, query_id, id_to_title_score):
    number_of_hits = 0
    recommended_in_review = 0
    for book in id_to_book_entry.keys():
        if book == query_id:
            goodreads_similar = id_to_book_entry[book]['similar_books']
            for recommended in goodreads_similar:
                if recommended in id_to_title_score.keys():
                    recommended_in_review += 1
            for similar in goodreads_similar:
                if similar in selected_books:
                    number_of_hits += 1

    return number_of_hits, recommended_in_review


def time_conversion(elapsed_time):
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    seconds, milliseconds = divmod(seconds, 1)
    milliseconds = round(milliseconds * 1000)
    return f"hours {int(hours)}, minutes: {int(minutes)}, seconds: {int(seconds)}, miliseonds: {int(milliseconds)}"

