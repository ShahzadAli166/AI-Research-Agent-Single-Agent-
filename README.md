# AI Research Agent

A beginner-friendly research app built with Streamlit, CrewAI, DuckDuckGo search, and Groq using `openai/gpt-oss-120b`.

## Files

```text
AI-Research-Agent/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Deploy directly from GitHub (no local setup)

1. Create a GitHub repository named `AI-Research-Agent`.
2. Upload `app.py`, `requirements.txt`, `README.md`, and `.gitignore` to the repository root.
3. Open https://share.streamlit.io/ and sign in with GitHub.
4. Click **Create app** → **Yup, I have an app**.
5. Select your repository, branch `main`, and main file `app.py`.
6. Open **Advanced settings** → **Secrets**, and paste:

   ```toml
   GROQ_API_KEY = "your_real_groq_api_key"
   ```

7. Choose Python **3.12** if available and click **Deploy**.

Never commit your real API key to GitHub. Store it only in Streamlit Secrets.

## Get a Groq API key

Create a key at https://console.groq.com/keys and keep it private.

## Use the app

1. Enter a research topic.
2. Select Brief, Standard, or Detailed.
3. Click **Research topic**.
4. Review the report and its source links, then download it as Markdown or a Word document (`.docx`).

## Notes

- DuckDuckGo results and availability can vary.
- Open the linked sources and verify important claims.
- The app uses one CrewAI agent, not a multi-agent crew.
- Streamlit Community Cloud installs dependencies from `requirements.txt`.
- The Word download converts report headings, paragraphs, bullet lists, and numbered lists from the generated Markdown.
