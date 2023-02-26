import time
import functions as f
'''
This is a script to answer the question: 
"Is possible to find similar books by analysing book reviews on Goodreads?"
It uses data that was already gathered from the Goodreads API and accessible
at https://sites.google.com/eng.ucsd.edu/ucsdbookgraph/home?pli=1

# Overview of the script:
1. Select relevant information from the dataset and transform it into dictionaries for speed of access
2. Lemmatize reviews and create a dictionary of all 1 and 2-grams with list of books in the reviews of which they occurred
3. Given a query, find books, the reviews of which shared the same keywords
4. Return book titles in order of the highest number of shared keywords
5. Evaluate compared to the list of recommended/similar books that Goodreads provides

# Example of an output given 250,000 books and 1,000,000 full text reviews: 

ID to entry created.
Word frequencies saved.
Words selected.
Preprocessing total: hours 5, minutes: 15, seconds: 44, milliseconds: 971 
_Creating book_id to entries dictionary: hours 0, minutes: 0, seconds: 27, milliseconds: 155 
_Creating a keyword to occurrence dictionary: hours 5, minutes: 15, seconds: 17, milliseconds: 55 
_Limiting to books in reviews: hours 0, minutes: 0, seconds: 0, milliseconds: 761 

## Closest book in our library: The Fellowship of the Ring (The Lord of the Rings, #1)

## Similar books:
1. Oath of Servitude (The Punishment Sequence, #1) with rating: 3.79
2. The Hobbit with rating: 4.25
3. Children Shouldn't Play with Dead Things (Dead Things, #1) with rating: 4.33
4. A Crown for Cold Silver (The Crimson Empire, #1) with rating: 3.65
5. The Hobbit: Or There and Back Again with rating: 4.25
6. Fields of Elysium (Fields of Elysium, #1) with rating: 3.78
7. No Ordinary Star (No Ordinary Star, #1) with rating: 4.15
8. Our Souls to Keep (Our Souls to Keep, #1) with rating: 4.08
9. The Undead Heart (Blood Thirst, #1) with rating: 3.92
10. Eden Forest with rating: 4.16
11. Switch (New World, #1) with rating: 3.89
12. Shadows of the Realm (The Circle of Talia, #1) with rating: 3.88
13. Throne of Glass (Throne of Glass, #1) with rating: 4.23
14. Dawn of Wonder (The Wakening, #1) with rating: 4.35
15. The Hobbit with rating: 4.25
16. See How She Runs (The Chronicles of Izzy, #1) with rating: 3.84
17. Aire with rating: 3.72
18. The Name of the Wind (The Kingkiller Chronicle, #1) with rating: 4.55
19. Fantasy of Frost (The Tainted Accords, #1) with rating: 4.21
20. Senlin Ascends (The Books of Babel, #1) with rating: 4.37

We found 17 out of 17 similar books (as per Goodreads recommendation).

Look-up time total: hours 0, minutes: 0, seconds: 0, milliseconds: 277 
_Search: hours 0, minutes: 0, seconds: 0, milliseconds: 11 
_Lookup: hours 0, minutes: 0, seconds: 0, milliseconds: 196 
_Sorting: hours 0, minutes: 0, seconds: 0, milliseconds: 63 

Limitations:
- Preprocessing is very slow, but only needs to be done once. All the resulting files are saved and the actual lookup 
    takes less than half a second. 
- query is a fuzzy search, but would benefit from letting a user select from matches. Given a catalogue of 
    258,000 books, there is a good chance we find a different book than the user intended.
- decision of which reviews to consider for books with large number of them is very simplistic
- if this application were to be further worked on, the book lookup should be a database instead of a dictionary
- there is no algorithm to take into the account a book's rating when selecting results to print, there
    could be some tradeoff between valuing shared keywords and average_rating
- search for similar books to the query is book based and does not recognize series
- given that there are multiple entries of the same title but different id, the script is not merging them in any way

Future prospects
- a functionality to allow the user to ban certain tags could be easily implemented, 
    a little harder would be them promoting certain tags
- we could be learning people's tag or keyword preferences by recording what they are 
    typing in and then "retraining" the model with those keywords added and maybe
    given a preference. 
'''
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
