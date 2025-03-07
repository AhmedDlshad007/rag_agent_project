
# Movie Research Assistant (RAG Agent)

## Overview
This project is a **Retrieval Augmented Generation (RAG) Agent** designed to assist users in researching movies and TV shows. It integrates with external APIs (Google Search, YouTube, TMDb, and OMDb) to fetch movie details, ratings, release dates, and trailers, presenting the information in a clean and user-friendly GUI built with Python's `tkinter`.

The application was developed as part of the Junior Developer application process for **blackcode SA**, showcasing my ability to build AI-powered tools with a focus on usability and functionality.

---

## Key Features
1. **Movie Information Retrieval**:
   - Fetches movie details such as title, release date, IMDb rating, director, and cast from **TMDb** and **OMDb APIs**.
   - Displays a summary of the movie, including a brief overview and genre information.

2. **YouTube Trailer Integration**:
   - Searches for and retrieves the official movie trailer using **YouTube's API**.
   - Provides a clickable link to the trailer within the GUI.

3. **Poster Display**:
   - Fetches and displays the movie poster using the **OMDb API**.
   - The poster is dynamically resized and displayed in the GUI.

4. **Session Log**:
   - Maintains a log of user interactions, including search queries, API responses, and errors.
   - Provides transparency into how the information is retrieved and processed.

5. **Simple GUI**:
   - Built using Python's `tkinter` framework, the GUI is intuitive and easy to use.
   - Includes input fields, a results display area, and a session log for tracking actions.

---

## How It Works
1. **User Input**:
   - The user enters a movie name in the search bar.
   
2. **API Integration**:
   - The application queries **TMDb** and **OMDb** for movie details and poster URLs.
   - It also searches **YouTube** for the official trailer.

3. **Data Processing**:
   - The retrieved data is formatted and displayed in the GUI.
   - The session log is updated with each step of the process.

4. **Output**:
   - The user sees a summary of the movie, including:
     - Title, release date, and IMDb rating.
     - Director and main cast.
     - A brief overview and genre information.
     - A link to the official trailer.
     - The movie poster.

---

## Implementation Details
### Tools and Technologies
- **Python**: Core programming language.
- **Tkinter**: Used for building the GUI.
- **Requests**: For making HTTP requests to external APIs.
- **Pillow (PIL)**: For handling and displaying movie posters.
- **TMDb API**: For fetching movie details.
- **OMDb API**: For fetching additional movie information and posters.
- **YouTube API**: For searching and retrieving movie trailers.

### Challenges Faced

1. **API Integration**:
   - Integrating multiple APIs (TMDb, OMDb, YouTube) was one of the most challenging parts of the project. At first, I struggled with understanding how to structure API requests and handle responses. For example, some APIs returned nested JSON data, and I had to figure out how to extract the specific information I needed. I also ran into issues with rate limits, especially with the OMDb API, which forced me to implement retries and fallback mechanisms. This taught me the importance of error handling and graceful degradation in real-world applications.

2. **GUI Design**:
   - Designing a clean and intuitive GUI was harder than I expected. I wanted the interface to be simple yet functional, but balancing all the elements (input fields, results display, session log, and poster display) took a lot of trial and error. One specific challenge was dynamically resizing the movie poster while maintaining its aspect ratio. I spent a lot of time experimenting with the `Pillow` library to get it right. This part of the project really pushed me to think about user experience and how to present information in a way that’s easy to understand.

3. **Session Log Implementation**:
   - Implementing the session log was a learning curve. I wanted it to update in real-time with user interactions and API responses, but I didn’t realize how tricky it would be to manage the `tkinter` text widget. At first, the log would either overwrite itself or not update at all. I had to research how to properly append text and ensure the log stayed readable. This taught me a lot about managing state in a GUI application and how to make the system more transparent to the user.

4. **Debugging and Testing**:
   - Debugging was a big part of this project. There were times when the application would crash unexpectedly, and I had to dig through logs and print statements to figure out why. For example, I initially didn’t account for cases where a movie might not have a poster or trailer, which caused errors. This taught me the importance of writing robust code that can handle edge cases gracefully. I also learned how to use debugging tools more effectively, which will definitely help me in future projects.

5. **Learning While Building**:
   - This project was a huge learning experience for me. I had never worked with some of these APIs or libraries before, so I spent a lot of time reading documentation and experimenting. For example, I had to learn how to use `Pillow` for image processing and `tkinter` for GUI development, both of which were new to me. There were moments of frustration, but every challenge I overcame made me feel more confident in my abilities. I realized that building something from scratch is the best way to learn, even if it means making mistakes along the way.

---

## How to Run the Project
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/movie-research-assistant.git
   cd movie-research-assistant
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up API Keys**:
   - Obtain API keys for **TMDb**, **OMDb**, and **YouTube**.
   - Add the keys to the `main.py` file.

4. **Run the Application**:
   ```bash
   python gui.py
   ```

---


### Future Improvements

1. **Enhanced Error Handling**:
   - Improve error messages and fallback options for failed API requests. For example, if a movie poster or trailer isn’t available, the application could suggest similar movies or provide a default image/placeholder.

2. **Advanced Search**:
   - Expand the search functionality to include TV shows, actors, and directors. This would make the tool more versatile and useful for a wider range of entertainment research.

3. **Offline Mode**:
   - Add a caching mechanism to store frequently searched movie data locally. This would allow users to access basic information even when offline, improving the app’s reliability.

4. **Export Options**:
   - Allow users to export their session logs or favorite movies to a file (e.g., CSV or JSON). This could be useful for users who want to keep a record of their research.

5. **Multi-Language Support**:
   - Add support for multiple languages, both in the GUI and in the movie data retrieval. This would make the application accessible to a broader audience.

6. **Performance Optimization**:
   - Optimize the app’s performance, especially when handling large amounts of data or multiple API calls. This could include asynchronous requests or better resource management.

7. **User Feedback Integration**:
   - Add a feature for users to provide feedback on the app’s functionality or suggest improvements. This could help guide future updates and make the tool more user-centric.


---

## Conclusion
This project demonstrates my ability to build a functional and user-friendly application using Python and external APIs. It highlights my problem-solving skills, attention to detail, and ability to deliver a polished product within a limited timeframe. I look forward to contributing to **blackcode SA's** innovative projects and continuing to grow as a developer.

