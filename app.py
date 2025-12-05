from flask import Flask, request, render_template, redirect, url_for
import pickle
import requests
import random

app = Flask(__name__)

API_KEY = "65963bfd1439d6718d9fc840b144b8e6"

movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# --- TMDB Fetch Functions ---
def fetch_tmdb_movie(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US&append_to_response=credits,videos"
    r = requests.get(url)
    if r.status_code != 200:
        return {}
    data = r.json()
    trailer_key = None
    for v in data.get("videos", {}).get("results", []):
        if v["type"] == "Trailer" and v["site"] == "YouTube":
            trailer_key = v["key"]
            break
    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "overview": data.get("overview"),
        "rating": data.get("vote_average"),
        "poster": f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get("poster_path") else "https://via.placeholder.com/500x750?text=No+Image",
        "backdrop": f"https://image.tmdb.org/t/p/w1280{data.get('backdrop_path')}" if data.get("backdrop_path") else "https://via.placeholder.com/1280x720?text=No+Image",
        "genres": [g["name"] for g in data.get("genres", [])],
        "release_date": data.get("release_date"),
        "runtime": data.get("runtime"),
        "trailer": trailer_key,
        "cast": data.get("credits", {}).get("cast", [])[:10],
        "crew": data.get("credits", {}).get("crew", [])
    }

def fetch_tmdb_category(category="trending", limit=10000):
    if category == "trending":
        url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={API_KEY}"
    elif category == "top_rated":
        url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}&language=en-US&page=1"
    
    else:
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_genres={category}&language=en-US&page=1"
    
    r = requests.get(url)
    if r.status_code != 200:
        return []
    return [
        {
            "id": m["id"],
            "title": m["title"],
            "rating": m.get("vote_average"),
            "poster": f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get("poster_path") else "https://via.placeholder.com/500x750?text=No+Image"
        }
        for m in r.json().get("results", [])[:limit]
    ]
    

def recommend(movie):
    if movie not in movies["title"].values:
        return []
    index = movies[movies["title"] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended = []
    for i in distances[1:6]:
        m_id = movies.iloc[i[0]].movie_id
        m_data = fetch_tmdb_movie(m_id)
        recommended.append({
            "id": m_id,
            "title": m_data.get("title"),
            "rating": m_data.get("rating"),
            "poster": m_data.get("poster"),
            "trailer": m_data.get("trailer")
        })
    return recommended

# --- Routes ---
@app.route("/")
def home():
    trending = fetch_tmdb_category("trending", 100)
    top_rated = fetch_tmdb_category("top_rated", 100)
    top_five = trending[:10]
    anime = fetch_tmdb_category("anime", limit=20)

    hero_movies = []
    for m in top_five:
        details = fetch_tmdb_movie(m["id"])
        hero_movies.append({
            "title": details.get("title"),
            "rating": details.get("rating"),
            "backdrop": details.get("backdrop")
        })

    # Additional categories example
    categories = {
        "Action": 28,
        
        "Comedy": 35,
        "Horror": 27,
        "Romance": 10749,
        "Sci-Fi": 878
    }

    additional_categories = {}
    for cat_name, cat_id in categories.items():
        additional_categories[cat_name] = fetch_tmdb_category(cat_id, 100)

    return render_template(
        "index.html",
        trending=trending,
        top_rated=top_rated,
        top_five=top_five,
        hero_movies=hero_movies,
        additional_categories=additional_categories,
        movies=movies["title"].tolist()
    )

@app.route("/recommend", methods=["POST"])
def recommend_route():
    movie_name = request.form.get("movie")
    recommendations = recommend(movie_name)
    return render_template("recommend.html", movie=movie_name, recommendations=recommendations)

@app.route("/movie/<int:movie_id>")
def movie_page(movie_id):
    details = fetch_tmdb_movie(movie_id)
    similar = recommend(details["title"]) if details else []
    return render_template("movie.html", movie=details, similar=similar)

@app.route("/actor/<int:actor_id>")
def actor_page(actor_id):
    url = f"https://api.themoviedb.org/3/person/{actor_id}/movie_credits?api_key={API_KEY}&language=en-US"
    r = requests.get(url)
    movies_list = []
    if r.status_code == 200:
        for m in r.json().get("cast", [])[:15]:
            movies_list.append({
                "id": m["id"],
                "title": m["title"],
                "poster": f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get("poster_path") else "https://via.placeholder.com/500x750?text=No+Image",
                "rating": m.get("vote_average")
            })
    return render_template("actor.html", movies=movies_list)

@app.route("/surprise")
def surprise():
    random_movie_id = random.choice(movies["movie_id"].tolist())
    return redirect(url_for("movie_page", movie_id=random_movie_id))

if __name__ == "__main__":
    app.run(debug=True)
