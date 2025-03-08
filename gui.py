import tkinter as tk
from tkinter import scrolledtext, font
import requests
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
from youtubesearchpython import VideosSearch
import json
import re
from PIL import Image, ImageTk
import io


# Theme colors
LIGHT_THEME = {
    "bg": "#f0f0f0",  # Light gray background
    "fg": "#333333",  # Dark gray text
    "button_bg": "#4CAF50",  # Green button
    "button_fg": "white",  # White button text
    "text_bg": "#ffffff",  # White text area background
    "text_fg": "#333333",  # Dark gray text area text
}

DARK_THEME = {
    "bg": "#333333",  # Dark gray background
    "fg": "#f0f0f0",  # Light gray text
    "button_bg": "#2196F3",  # Blue button
    "button_fg": "white",  # White button text
    "text_bg": "#1e1e1e",  # Dark text area background
    "text_fg": "#f0f0f0",  # Light gray text area text
}


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

# Search for movie info
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
                tmdb_details = fetch_tmdb_details(movie_name)
                omdb_details = fetch_omdb_details(movie_name)
                trailer_url = search_youtube_trailer(movie_name)

                # Fetch poster URL from OMDb API
                poster_url = fetch_movie_poster(movie_name)  
                print(f"Poster URL in search_movie_info: {poster_url}")  # Debug: Print poster URL

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
                return output, poster_url  # Now returning two values

        return "No valid IMDb page found in search results.", None
    else:
        return "No results found.", None


# Extract IMDb details
def extract_imdb_details(imdb_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(imdb_url, headers=headers)

    if response.status_code == 200:
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

        return result_text
    else:
        return f"Failed to fetch IMDb page. Status code: {response.status_code}\n"

# Fetch TMDb details
def fetch_tmdb_details(movie_name):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            movie = data["results"][0]  # Get the first result
            result_text = "\nTMDb Details:\n"
            result_text += f"Overview: {movie.get('overview', 'No overview available')}\n"
            
            # Map genre IDs to genre names
            genre_names = [GENRE_MAPPING.get(genre_id, "Unknown") for genre_id in movie.get('genre_ids', [])]
            result_text += f"Genres: {', '.join(genre_names)}\n"
            
            result_text += f"Popularity: {movie.get('popularity', 'N/A')}\n"
            return result_text
        else:
            return "No results found on TMDb.\n"
    else:
        return f"Failed to fetch TMDb data. Status code: {response.status_code}\n"

# Fetch OMDb details
def fetch_omdb_details(movie_name):
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie_name}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get("Response") == "True":
            result_text = "\nOMDb Details:\n"
            result_text += f"Rotten Tomatoes Rating: {data.get('Ratings', [{}])[1].get('Value', 'N/A')}\n"
            result_text += f"Box Office: {data.get('BoxOffice', 'N/A')}\n"
            result_text += f"Awards: {data.get('Awards', 'N/A')}\n"
            return result_text
        else:
            return "No results found on OMDb.\n"
    else:
        return f"Failed to fetch OMDb data. Status code: {response.status_code}\n"


import requests

def fetch_movie_poster(movie_name):
    omdb_api_key = "4e61bc43"  # Replace with your actual OMDb API key
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={omdb_api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        data = response.json()

        if "Poster" in data and data["Poster"] != "N/A":
            print(f"Poster URL: {data['Poster']}")  # Debug: Print the poster URL
            return data["Poster"]  # Return poster image URL
        else:
            print("No poster found in OMDb response.")  # Debug: No poster available
    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster: {e}")
    
    return None  # Return None if there's an error



# Search for YouTube trailer
from pytube import Search
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
def search_youtube_trailer(movie_name):
    try:
        query = f"{movie_name} official trailer"
        print(f"Searching YouTube for: {query}")  # Debugging
        search = Search(query)
        results = search.results
        print("YouTube Search Results:", results)  # Debugging

        if results:
            trailer_url = results[0].watch_url
            print(f"Found YouTube Trailer: {trailer_url}")  # Debugging
            return trailer_url
        else:
            print("No YouTube trailer found.")  # Debugging
            return None
    except Exception as e:
        print(f"Error searching for YouTube trailer: {e}")  # Debugging
        return None

# GUI Application
class MovieSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Search RAG Agent")
        self.root.geometry("1400x950")  # Slightly larger window
        self.root.configure(bg="#f0f0f0")  # Light gray background

        # Custom Fonts
        self.title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.label_font = font.Font(family="Helvetica", size=12)
        self.button_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.text_font = font.Font(family="Courier", size=11)

        # Input Frame
        self.input_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.input_frame.pack(pady=20)

        self.movie_label = tk.Label(self.input_frame, text="Enter Movie Name:", font=self.label_font, bg="#f0f0f0")
        self.movie_label.grid(row=0, column=0, padx=10)

        self.movie_entry = tk.Entry(self.input_frame, width=50, font=self.text_font)
        self.movie_entry.grid(row=0, column=1, padx=10)

        self.search_button = tk.Button(self.input_frame, text="Search", font=self.button_font, bg="#4CAF50", fg="white", command=self.search_movie)
        self.search_button.grid(row=0, column=2, padx=10)

        # Save to Favorites Button
        self.favorites_button = tk.Button(self.input_frame, text="Save to Favorites", font=self.button_font, bg="#2196F3", fg="white", command=self.save_to_favorites)
        self.favorites_button.grid(row=0, column=3, padx=10)

        # View Favorites Button
        self.view_favorites_button = tk.Button(self.input_frame, text="View Favorites", font=self.button_font, bg="#FF9800", fg="white", command=self.view_favorites)
        self.view_favorites_button.grid(row=0, column=4, padx=10)

        # Get Recommendations Button
        self.recommendations_button = tk.Button(self.input_frame, text="Get Recommendations", font=self.button_font, bg="#9C27B0", fg="white", command=self.get_recommendations)
        self.recommendations_button.grid(row=0, column=5, padx=10)

        # Add a "Toggle Theme" button
        self.theme_button = tk.Button(self.input_frame, text="Toggle Theme", font=self.button_font, bg="#9C27B0", fg="white", command=self.toggle_theme)
        self.theme_button.grid(row=0, column=6, padx=10)

        # Results Display
        self.results_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=120, height=20, font=self.text_font, bg="#ffffff", fg="#333333")
        self.results_text.pack(pady=10, padx=20)

        # Session Log
        self.session_log = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=120, height=10, font=self.text_font, bg="#ffffff", fg="#333333")
        self.session_log.pack(pady=10, padx=20)
        self.session_log.insert(tk.END, "Session Log:\n")  # Initialize with a header

        # Favorites List
        self.favorites = self.load_favorites()

        # Load theme preference and apply theme
        self.current_theme = self.load_settings()
        self.apply_theme(LIGHT_THEME if self.current_theme == "light" else DARK_THEME)

        # Add an image label
        self.poster_label = tk.Label(self.root, bg="#f0f0f0")
        self.poster_label.pack(pady=10)


    import requests
    from PIL import Image, ImageTk
    import io

    def search_movie(self):
        movie_name = self.movie_entry.get().strip()  

        if not movie_name:
            self.session_log.insert(tk.END, "Please enter a movie name.\n")
            return

        # Log the search action
        self.session_log.insert(tk.END, f"Searching for movie: {movie_name}\n")

        # Fetch movie details
        output, poster_url = search_movie_info(movie_name)  
        print(f"Poster URL in search_movie: {poster_url}")  # Debug: Print poster URL

        # Display movie details in the results text area
        self.results_text.delete(1.0, tk.END)  # Clear previous results
        self.results_text.insert(tk.END, output)

        # Log the result
        self.session_log.insert(tk.END, f"Movie details fetched for: {movie_name}\n")

        # Load and display the poster if available
        if poster_url:
            try:
                response = requests.get(poster_url)
                response.raise_for_status()  # Ensure the request was successful
                print(f"Poster response status code: {response.status_code}")  # Debug: Print status code

                image_data = response.content  # Get image data
                print(f"Image data length: {len(image_data)}")  # Debug: Print image data length

                image = Image.open(io.BytesIO(image_data))  # Open image from bytes
                print(f"Image format: {image.format}, Image size: {image.size}")  # Debug: Print image details

                image = image.resize((200, 300), Image.Resampling.LANCZOS)  # Use LANCZOS instead of ANTIALIAS
                photo = ImageTk.PhotoImage(image)

                self.poster_label.config(image=photo)
                self.poster_label.image = photo  # Keep reference to avoid garbage collection
                print("Poster displayed successfully.")  # Debug: Confirm poster display

                # Log poster success
                self.session_log.insert(tk.END, f"Poster loaded for: {movie_name}\n")
            except requests.exceptions.RequestException as e:
                print(f"Error loading poster: {e}")
                self.session_log.insert(tk.END, f"Error loading poster for: {movie_name}\n")
                self.poster_label.config(image='', text="No poster available")
            except Exception as e:
                print(f"Unexpected error loading poster: {e}")
                self.session_log.insert(tk.END, f"Unexpected error loading poster for: {movie_name}\n")
                self.poster_label.config(image='', text="No poster available")
        else:
            self.session_log.insert(tk.END, f"No poster available for: {movie_name}\n")
            self.poster_label.config(image='', text="No poster available")


    def save_to_favorites(self):
        movie_name = self.movie_entry.get()
        if not movie_name:
            self.session_log.insert(tk.END, "Error: No movie to save. Please search for a movie first.\n")
            return

        # Get the current movie details from the results text
        movie_details = self.results_text.get(1.0, tk.END).strip()
        if not movie_details:
            self.session_log.insert(tk.END, "Error: No movie details to save.\n")
            return

        # Save to favorites
        self.favorites[movie_name] = movie_details
        self.save_favorites()
        self.session_log.insert(tk.END, f"Saved to favorites: {movie_name}\n")

    def save_favorites(self):
        try:
            with open("favorites.json", "w") as file:
                json.dump(self.favorites, file, indent=4)
        except Exception as e:
            self.session_log.insert(tk.END, f"Error saving favorites: {str(e)}\n")

    def load_favorites(self):
        try:
            with open("favorites.json", "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def view_favorites(self):
        if not self.favorites:
            self.session_log.insert(tk.END, "No favorites saved.\n")
            return

        # Display favorites in a new window
        favorites_window = tk.Toplevel(self.root)
        favorites_window.title("Favorites")
        favorites_window.geometry("900x600")
        favorites_window.configure(bg="#f0f0f0")

        favorites_text = scrolledtext.ScrolledText(favorites_window, wrap=tk.WORD, width=100, height=25, font=self.text_font, bg="#ffffff", fg="#333333")
        favorites_text.pack(pady=20, padx=20)

        #"Delete Favorite" button
        delete_button = tk.Button(favorites_window, text="Delete Selected Favorite", font=self.button_font, bg="#FF5252", fg="white", command=lambda: self.delete_favorite(favorites_window, favorites_text))
        delete_button.pack(pady=10)

        # Display favorites
        for movie_name, details in self.favorites.items():
            favorites_text.insert(tk.END, f"Movie: {movie_name}\n")
            favorites_text.insert(tk.END, f"Details:\n{details}\n")
            favorites_text.insert(tk.END, "-" * 80 + "\n")

    def get_tmdb_movie_id(self, movie_name):
        try:
            url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            data = response.json()
            if not data.get("results"):
                return None

            return data["results"][0]["id"]  # Return the ID of the first result
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch TMDb movie ID: {str(e)}")
            return None

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

    def get_recommendations(self):
        movie_name = self.movie_entry.get()
        if not movie_name:
            self.session_log.insert(tk.END, "Error: No movie selected. Please search for a movie first.\n")
            return

        # Get TMDb movie ID
        movie_id = self.get_tmdb_movie_id(movie_name)
        if not movie_id:
            self.session_log.insert(tk.END, "Error: Could not find TMDb ID for the movie.\n")
            return

        # Fetch similar movies
        recommendations = self.fetch_similar_movies(movie_id)
        if not recommendations:
            self.session_log.insert(tk.END, "No recommendations found.\n")
            return

        # Display recommendations in a new window
        recommendations_window = tk.Toplevel(self.root)
        recommendations_window.title("Movie Recommendations")
        recommendations_window.geometry("600x400")
        recommendations_window.configure(bg="#f0f0f0")

        recommendations_text = scrolledtext.ScrolledText(recommendations_window, wrap=tk.WORD, width=70, height=20, font=self.text_font, bg="#ffffff", fg="#333333")
        recommendations_text.pack(pady=20, padx=20)

        recommendations_text.insert(tk.END, recommendations)
    
    def delete_favorite(self, favorites_window, favorites_text):
        try:
        # Check if any text is selected
            selected_text = favorites_text.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
        except tk.TclError:
        # No text is selected
            self.session_log.insert(tk.END, "Error: No favorite selected. Please select a movie to delete.\n")
            return

    # Extract the movie name from the selected text
        movie_name = selected_text.split("\n")[0].replace("Movie: ", "").strip()
        if movie_name not in self.favorites:
            self.session_log.insert(tk.END, f"Error: '{movie_name}' not found in favorites.\n")
            return

    # Delete the favorite
        del self.favorites[movie_name]
        self.save_favorites()
        self.session_log.insert(tk.END, f"Deleted favorite: {movie_name}\n")

    # Refresh the favorites window
        favorites_text.delete(1.0, tk.END)
        for movie_name, details in self.favorites.items():
            favorites_text.insert(tk.END, f"Movie: {movie_name}\n")
            favorites_text.insert(tk.END, f"Details:\n{details}\n")
            favorites_text.insert(tk.END, "-" * 80 + "\n")
    
    def toggle_theme(self):
        # Toggle between light and dark themes
        if self.current_theme == "light":
            self.apply_theme(DARK_THEME)
            self.current_theme = "dark"
        else:
            self.apply_theme(LIGHT_THEME)
            self.current_theme = "light"

        # Save the theme preference
        self.save_settings()
    
    def apply_theme(self, theme):
    # Apply theme to the root window
        self.root.configure(bg=theme["bg"])

    # Apply theme to the input frame
        self.input_frame.configure(bg=theme["bg"])
        self.movie_label.configure(bg=theme["bg"], fg=theme["fg"])
        self.movie_entry.configure(bg=theme["text_bg"], fg=theme["text_fg"])

    # Apply theme to buttons
        self.search_button.configure(bg=theme["button_bg"], fg=theme["button_fg"])
        self.favorites_button.configure(bg=theme["button_bg"], fg=theme["button_fg"])
        self.view_favorites_button.configure(bg=theme["button_bg"], fg=theme["button_fg"])
        self.recommendations_button.configure(bg=theme["button_bg"], fg=theme["button_fg"])
        self.theme_button.configure(bg=theme["button_bg"], fg=theme["button_fg"])

    # Apply theme to text areas
        self.results_text.configure(bg=theme["text_bg"], fg=theme["text_fg"])
        self.session_log.configure(bg=theme["text_bg"], fg=theme["text_fg"])
    

    def save_settings(self):
        settings = {
            "theme": self.current_theme
    }
        try:
            with open("settings.json", "w") as file:
                json.dump(settings, file, indent=4)
        except Exception as e:
            print(f"Error saving settings: {str(e)}")

    def load_settings(self):
        try:
            with open("settings.json", "r") as file:
                settings = json.load(file)
                return settings.get("theme", "light")
        except (FileNotFoundError, json.JSONDecodeError):
            return "light"
    
   

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = MovieSearchApp(root)
    root.mainloop()