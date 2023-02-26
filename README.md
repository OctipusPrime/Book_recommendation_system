# Book_recommendation_system

## Purpose
This is a script to answer the question: 
"Is possible to find similar books by analysing book reviews on Goodreads?"
It uses data that was already gathered from the Goodreads API and accessible
at https://sites.google.com/eng.ucsd.edu/ucsdbookgraph/home?pli=1

## Overview of the script:
1. Select relevant information from the dataset and transform it into dictionaries for speed of access
2. Lemmatize reviews and create a dictionary of all 1 and 2-grams with list of books in the reviews of which they occurred
3. Given a query, find books, the reviews of which shared the same keywords
4. Return book titles in order of the highest number of shared keywords
5. Evaluate compared to the list of recommended/similar books that Goodreads provides

## Example of an output given 250,000 books and 1,000,000 full text reviews: 

ID to entry created.

Word frequencies saved.

Words selected.

Preprocessing total: hours: 5, minutes: 15, seconds: 44, milliseconds: 971 
- Creating book_id to entries dictionary: hours 0, minutes: 0, seconds: 27, milliseconds: 155 
- Creating a keyword to occurrence dictionary: hours 5, minutes: 15, seconds: 17, milliseconds: 55 
- Limiting to books in reviews: hours 0, minutes: 0, seconds: 0, milliseconds: 761 

Closest book in our library: The Fellowship of the Ring (The Lord of the Rings, #1)

Similar books:
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

Found 17 out of 17 similar books (as per Goodreads recommendation).

Look-up time total: hours 0, minutes: 0, seconds: 0, milliseconds: 277 
- Search: hours 0, minutes: 0, seconds: 0, milliseconds: 11 
- Lookup: hours 0, minutes: 0, seconds: 0, milliseconds: 196 
- Sorting: hours 0, minutes: 0, seconds: 0, milliseconds: 63 

## Limitations:
- Only Fantasy and Supernatural data subset is used to limit the size of used data.
- Preprocessing is quite slow, but only needs to be done once. All the resulting files are saved and the actual lookup 
    takes less than half a second. 
- query is a fuzzy search, but would benefit from letting a user select from matches. Given a catalogue of 
    258,000 books, there is a good chance we find a different book than the user intended.
- decision of which reviews to consider for books with large number of them is very simplistic
- if this application were to be further worked on, the book lookup should be a database instead of a dictionary
- there is no algorithm to take into the account a book's rating when selecting results to print, there
    could be some tradeoff between valuing shared keywords and average_rating
- search for similar books to the query is book based and does not recognize series
- given that there are multiple entries of the same title but different id, the script is not merging them in any way

## Future prospects
- a functionality to allow the user to ban certain tags could be easily implemented, 
    a little harder would be them promoting certain tags
- we could be learning people's tag or keyword preferences by recording what they are 
    typing in and then "retraining" the model with those keywords added and maybe
    given a preference. 
