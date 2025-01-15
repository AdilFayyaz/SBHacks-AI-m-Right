# AI’m Right

AI’m Right simplifies the study process by providing tools for quiz generation, lecture handouts, and video content search using cutting-edge AI technologies. This project was submitted during SBHacksIX.

![gallery](https://github.com/user-attachments/assets/a41738de-c75b-4023-8936-2aa32254d79f)

- [Youtube Demo](https://www.youtube.com/watch?v=MnOdexX39SU)
- [DevPost Link](https://devpost.com/software/ai-m-right)


---

## Features
- **Smart Quiz Generation**: Generate customized quizzes based on your lecture content.
- **Handout Creation**: Summarize lecture materials into concise and easy-to-digest handouts.
- **Lecture Video Search**: Quickly locate specific topics or concepts in large video archives.

---

## Tech Stack
- **Frontend**: [Streamlit](https://streamlit.io/) for a user-friendly interface.
- **Backend**: [Flask](https://flask.palletsprojects.com/) for robust server-side operations.
- **APIs**: Claude, Pinecone, Aryn, Twelve Labs for advanced processing and data management.
- **Database**: Pinecone Vector Database for scalable data retrieval.

![pipeline](https://github.com/user-attachments/assets/1e61aa32-e393-4788-8982-a035f551e0be)

---

## Installation

### Prerequisites
- Python 3.8 or higher.
- Install dependencies with pip:
  ```bash
  pip install -r requirements.txt
  ```

### Setting up Environment Variables
1. Create a `.env` file in the root directory of the project.
2. Add the following API keys:
   ```env
   CLAUDE_API="<your-claude-api-key>"
   ARYN_API_KEY="<your-aryn-api-key>"
   PINECONE_API_KEY="<your-pinecone-api-key>"
   TWELVE_LABS_KEY="<your-twelve-labs-key>"
   INDEX_ID="<your-index-id>"
   ```

---

## Running the Application

### Backend
Start the Flask server:
   ```bash
   python server.py
   ```

### Frontend
Start the Streamlit app:
   ```bash
   streamlit run main.py
   ```

---

## Usage
1. Open your browser and navigate to `http://localhost:8501` (Streamlit default port).
2. Use the following features:
   - **Quiz Generation**: Upload lecture materials or paste content to generate quizzes.
   - **Handout Creation**: Provide lecture notes to generate summarized handouts.
   - **Video Search**: Upload video files to search for specific topics or concepts.

---

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

---

## License
This project is licensed under the [MIT License](LICENSE).

---

