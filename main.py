import time
import functions as f

# No need for an exact match, the script uses fuzzy search to find the best match.
query = "The Fellowship of the Ring (The Lord of the Rings #1)"

reviews_location = './goodreads_reviews_fantasy_paranormal.json.gz'
books_info_location = './goodreads_books_fantasy_paranormal.json.gz'
id_to_title_score_location = './id_to_title.json'
word_to_id_location = './words_to_id.json'
keywords_location = './keywords.json'
create_id_to_entry_dictionary = False
create_keyword_dictionary = False
limit_ids_to_those_in_reviews = True  # Turns out that there are multiple ids for the same title
lookup_query = True
TOP_X = 10  # maximum number of  hits to print
NUMBER_OF_REVIEWS_TO_CONSIDER = 1000  # a thousand for every one

# maximum number of reviews of a particular books is taken into account
# done to reduce bias toward books with large number of reviews -> words
review_count_threshold = 10

# yake (Yet Another Keyword Extractor) settings
language = "en"
max_ngram_size = 1
deduplication_threshold = 0.9
deduplication_algo = 'seqm'
windowSize = 1
numOfKeywords = 8

if __name__ == "__main__":
    start_time = time.time()
    # In order to avoid looping through every book when looking for
    # a pointer to the title, I transformed the books json into
    # a dictionary which will make it faster to look up the title
    if create_id_to_entry_dictionary:
        id_to_book_entry = f.downsize_book_entries(id_to_title_score_location, books_info_location)
    else:
        id_to_book_entry = f.load_dictionary(id_to_title_score_location)
    id_to_book_entry_lookup = time.time()
    print("ID to entry created.")

    if create_keyword_dictionary:
        keywords = f.identify_keywords(keywords_location, reviews_location, id_to_book_entry, language, max_ngram_size,
                                     deduplication_threshold, deduplication_algo, windowSize, numOfKeywords, review_count_threshold)
        print("Word frequencies saved.")
        f.save_dictionary(keywords_location, keywords)
    else:
        keywords = f.load_dictionary(keywords_location)
    keywords_lookup = time.time()
    print("Words selected.")

    if limit_ids_to_those_in_reviews:
        id_to_book_entry = f.limit_id_to_entry_to_review_matches(id_to_book_entry, keywords)
    limiting_to_books_in_reviews = time.time()
    preprocessing = time.time()
    print(f"Preprocessing total: {f.time_conversion(preprocessing - start_time)} \n "
          f"\t Creating book_id to entries dictionary: {f.time_conversion(id_to_book_entry_lookup - start_time)} \n"
          f"\t Creating a keyword to occurence dictionary: {f.time_conversion(keywords_lookup - id_to_book_entry_lookup)} \n"
          f"\t Limiting to books in reviews: {f.time_conversion(limiting_to_books_in_reviews - keywords_lookup)} \n")

    if lookup_query:
        id_queried_book = f.search(query, id_to_book_entry)
        search_time = time.time()
        print(f"Closest book in our library: {id_to_book_entry[id_queried_book]['title']}")
        id_to_match_count, max_count, min_count = f.get_books_sharing_keywords(keywords, id_queried_book)
        book_with_shared_keyword_lookup = time.time()
        selected_books = f.select_books(id_to_match_count)
        books_in_top_x = f.print_top_books(selected_books, TOP_X, id_to_book_entry)
        sorting_of_hits = time.time()
        hits, out_of = f.evaluate_finds(selected_books, id_to_book_entry, id_queried_book, id_to_book_entry)
        print(f"We found {hits} out of {out_of} similar books.")
        finish = time.time()

        print(f"Look-up time total: {f.time_conversion(finish - preprocessing)} \n "
              f"\t Search: {f.time_conversion(search_time - preprocessing)} \n "
              f"\t Lookup: {f.time_conversion(book_with_shared_keyword_lookup - search_time)} \n "
              f"\t Sorting: {f.time_conversion(sorting_of_hits - book_with_shared_keyword_lookup)} ")
