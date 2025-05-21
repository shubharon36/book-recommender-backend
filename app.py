from flask import Flask, request, jsonify
from flask_cors import CORS  # Import Flask-CORS
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import process, fuzz
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes in your Flask app

# Load data and preprocessing (DO THIS ONCE!)
try:
    books = pd.read_csv('data/Books.csv')  # Relative path within backend/
    ratings = pd.read_csv('data/Ratings.csv')
    user = pd.read_csv('data/Users.csv')

    # --- Popularity-Based Top 50 ---
    ratings_with_name = ratings.merge(books, on='ISBN')
    num_rating_df = ratings_with_name.groupby('Book-Title').count()['Book-Rating'].reset_index()
    num_rating_df.rename(columns={'Book-Rating': 'num_ratings'}, inplace=True)
    avg_rating_df = ratings_with_name.groupby('Book-Title')['Book-Rating'].mean().reset_index(name='avg_rating')
    popular_df = num_rating_df.merge(avg_rating_df, on='Book-Title')
    popular_books = popular_df[popular_df['num_ratings'] >= 250].sort_values('avg_rating', ascending=False).head(50)

    # --- Collaborative Filtering ---
    x = ratings_with_name.groupby('User-ID').count()['Book-Rating'] > 200
    users_who_read = x[x].index
    filtered_ratings = ratings_with_name[ratings_with_name['User-ID'].isin(users_who_read)]
    y = filtered_ratings.groupby('Book-Title').count()['Book-Rating'] > 50
    famous_books = y[y].index
    final_ratings = filtered_ratings[filtered_ratings['Book-Title'].isin(famous_books)]
    pt = final_ratings.pivot_table(index='Book-Title', columns='User-ID', values='Book-Rating')
    pt.fillna(0, inplace=True)
    similarity = cosine_similarity(pt)

except FileNotFoundError as e:
    print(f"Error: Could not load data files. Ensure they are in the correct location. {e}")
    exit()

def get_top_50_books():
 # Merge, then drop duplicates by Book-Title, then take head(50)
    # This ensures that even if 'books' has multiple entries for the same title,
    # we only pick one for the top 50 list.
    top_50_books_df = books.merge(popular_books, on='Book-Title')[['Book-Title', 'Book-Author', 'Image-URL-L', 'num_ratings', 'avg_rating']]
    
    # Drop duplicates based on 'Book-Title' to ensure uniqueness
    # Keep the first occurrence, which should correspond to the highest-rated/most popular
    top_50_books_df = top_50_books_df.drop_duplicates(subset=['Book-Title'])
    
    # Ensure we still only have 50 books after dropping duplicates
    top_50_books_df = top_50_books_df.head(50) 
    
    return top_50_books_df.to_dict(orient='records')
def get_recommendations_from_matrix(book_name, pt, books):
    match = process.extractOne(book_name, pt.index, scorer=fuzz.token_sort_ratio)

    if match[1] > 75:  # Adjust threshold as needed
        book_index = pt.index.get_loc(match[0])
        similarity_scores = cosine_similarity(pt)
        similar_books = sorted(list(enumerate(similarity_scores[book_index])), key=lambda x: x[1], reverse=True)[1:6]

        recommended_books = []
        for i, score in similar_books:
            recommended_book_index = i  # The 'i' from enumerate is the index in pt.index
            recommended_title = pt.index[recommended_book_index]
            book_details = books[books['Book-Title'] == recommended_title]
            if not book_details.empty:
                book_details = book_details.iloc[0]
                recommended_books.append({
                    'Title': book_details['Book-Title'],
                    'Author': book_details['Book-Author'],
                    'Image-URL-L': book_details['Image-URL-L']
                })
            else:
                print(f"Book title '{recommended_title}' not found in books data.")
        return recommended_books
    else:
        print("No close match found in the pivot table. Try again.")
        return []

# --- API Endpoints ---
@app.route('/api/top-50', methods=['GET'])
def top_50():
    return jsonify(get_top_50_books())

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    book_title = data['title']
    recommendations = get_recommendations_from_matrix(book_title, pt, books)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)