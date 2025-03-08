import requests
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
from youtubesearchpython import VideosSearch
import json
import re

# API Keys
TMDB_API_KEY = "876262812143a500c36b773ee79778dc"  
OMDB_API_KEY = "4e61bc43"  

# Fetch genre list from TMDb
def fetch_tmdb_genres():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return {genre["id"]: genre["name"] for genre in response.json()["genres"]}
    return {}

# Genre mapping
GENRE_MAPPING = fetch_tmdb_genres()

def search_movie_info(movie_name):
    params = {
        "q": f"{movie_name} movie IMDb page",
        "hl": "en",
        "gl": "us",
        "api_key": "0818658513070eceb6a18e7df7e462715694ca06a229b8a95f83290e503c6b93" 
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if "organic_results" in results:
        for result in results["organic_results"]:
            link = result.get("link", "")
            if "imdb.com/title/" in link:
                title = result.get("title", "No title found")
                imdb_details = extract_imdb_details(link)
                tmdb_details, poster_url = fetch_tmdb_details(movie_name)
                omdb_details = fetch_omdb_details(movie_name)
                trailer_url = search_youtube_trailer(movie_name)

                # Format the output
                output = f"""
                Title: {title}
                IMDb Link: {link}

                IMDb Details:
                {imdb_details}

                TMDb Details:
                {tmdb_details}

                OMDb Details:
                {omdb_details}

                YouTube Trailer: {trailer_url if trailer_url else "No trailer found"}
                """

                return output, poster_url

        return "No valid IMDb page found in search results.", None
    else:
        return "No results found.", None



def extract_imdb_details(imdb_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(imdb_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        soup = BeautifulSoup(response.text, "html.parser")
        result_text = ""

        # Extract release date
        release_date = soup.find("a", {"class": "ipc-link ipc-link--baseAlt ipc-link--inherit-color", "href": lambda x: x and "releaseinfo" in x})
        if release_date:
            result_text += f"Release Date: {release_date.text.strip()}\n"

        # Extract IMDb rating
        rating = soup.find("span", {"class": "sc-bde20123-1 iZlgcd"})
        if rating:
            result_text += f"IMDb Rating: {rating.text}\n"

        # Extract director
        director = soup.find("a", {"class": "ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link"})
        if director:
            result_text += f"Director: {director.text.strip()}\n"

        # Extract cast (first 3 actors)
        cast = soup.find_all("a", {"data-testid": "title-cast-item__actor"})
        if cast:
            result_text += "Cast:\n"
            for actor in cast[:3]:  # Print first 3 actors
                result_text += f"- {actor.text.strip()}\n"

        return result_text if result_text else "No details found on IMDb."
    except requests.exceptions.RequestException as e:
        return f"Failed to fetch IMDb page: {str(e)}"
    except Exception as e:
        return f"An error occurred while extracting IMDb details: {str(e)}"


def fetch_tmdb_details(movie_name):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            movie = data["results"][0]  # Get the first result
            poster_path = movie.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            
            result_text = "\nTMDb Details:\n"
            result_text += f"Overview: {movie.get('overview', 'No overview available')}\n"

            # Map genre IDs to genre names
            genre_names = [GENRE_MAPPING.get(genre_id, "Unknown") for genre_id in movie.get('genre_ids', [])]
            result_text += f"Genres: {', '.join(genre_names)}\n"
            result_text += f"Popularity: {movie.get('popularity', 'N/A')}\n"

            return result_text, poster_url  # Return poster URL
        else:
            return "No results found on TMDb.\n", None
    else:
        return f"Failed to fetch TMDb data. Status code: {response.status_code}\n", None


def fetch_omdb_details(movie_name):
    try:
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie_name}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        if data.get("Response") == "False":
            return "No results found on OMDb."

        result_text = "\nOMDb Details:\n"
        result_text += f"Rotten Tomatoes Rating: {data.get('Ratings', [{}])[1].get('Value', 'N/A')}\n"
        result_text += f"Box Office: {data.get('BoxOffice', 'N/A')}\n"
        result_text += f"Awards: {data.get('Awards', 'N/A')}\n"
        return result_text
    except requests.exceptions.RequestException as e:
        return f"Failed to fetch OMDb data: {str(e)}"
    except Exception as e:
        return f"An error occurred while fetching OMDb details: {str(e)}"


def fetch_similar_movies(self, movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={TMDB_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        if not data.get("results"):
            return "No similar movies found."

        similar_movies = data["results"][:5]  # Get top 5 similar movies
        recommendations = "\nRecommended Movies:\n"
        for movie in similar_movies:
            recommendations += f"- {movie['title']} ({movie.get('release_date', 'N/A')})\n"
        return recommendations
    except requests.exceptions.RequestException as e:
        return f"Failed to fetch recommendations: {str(e)}"



import requests
import re
import json

def search_youtube_trailer(movie_name):
    try:
        # Construct the YouTube search URL
        query = f"{movie_name} official trailer"
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"

        # Set headers to mimic a browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Send a GET request to YouTube
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            # Extract JSON data from the response
            html = response.text
            json_data = re.search(r'var ytInitialData = ({.*?});', html, re.DOTALL).group(1)
            data = json.loads(json_data)

            # Debug: Print the JSON data structure
            with open("youtube_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print("YouTube JSON data saved to 'youtube_data.json'.")

            # Find the first video result
            video_results = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]

            for result in video_results:
                if "videoRenderer" in result:
                    video_id = result["videoRenderer"]["videoId"]
                    trailer_url = f"https://www.youtube.com/watch?v={video_id}"
                    print(f"\nYouTube Trailer: {trailer_url}")
                    return trailer_url

            print("No trailer found on YouTube.")
            return None
        else:
            print(f"Failed to fetch YouTube search results. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error searching for YouTube trailer: {e}")
        return None


def save_to_favorites(movie_name, details):
    try:
        # Load existing favorites
        try:
            with open("favorites.json", "r") as file:
                favorites = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            favorites = {}

        # Add new favorite
        favorites[movie_name] = details

        # Save back to file
        with open("favorites.json", "w") as file:
            json.dump(favorites, file, indent=4)

        print(f"\n{movie_name} has been added to favorites!")

    except Exception as e:
        print(f"Error saving to favorites: {str(e)}")



if __name__ == "__main__":
    movie_name = input("Enter a movie name: ")
    search_movie_info(movie_name)