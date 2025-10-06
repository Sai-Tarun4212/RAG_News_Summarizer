# 🗞️ RAG News Summarizer

A free, AI-powered news summarization app using Retrieval-Augmented Generation (RAG). Get instant summaries of the latest news on any topic!

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Features

- 🔍 **Search Latest News** - Fetch articles from multiple sources
- 🤖 **AI-Powered Summaries** - Get concise summaries using state-of-the-art models
- 💬 **Interactive Q&A** - Ask questions about the news
- 🆓 **100% Free** - Uses free APIs and lightweight models
- ⚡ **Fast & Efficient** - Optimized for Streamlit Cloud
- 📱 **Mobile Friendly** - Works on all devices.

## 🚀 Live Demo

**Try it now:** [https://your-app.streamlit.app](https://your-app.streamlit.app)

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Embeddings**: Sentence Transformers (paraphrase-MiniLM-L3-v2)
- **Summarization**: Hugging Face API (BART)
- **Vector Search**: NumPy + Cosine Similarity
- **News Sources**: NewsAPI / RSS Feeds

## 📋 Prerequisites

- Python 3.8 or higher
- NewsAPI key (optional, [get it free here](https://newsapi.org/register))
- Hugging Face token (optional, [get it free here](https://huggingface.co/settings/tokens))

## 🔧 Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/rag-news-summarizer.git
   cd rag-news-summarizer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up secrets** (optional but recommended)
   ```bash
   mkdir .streamlit
   cp secrets.toml.example .streamlit/secrets.toml
   ```
   
   Edit `.streamlit/secrets.toml` and add your API keys:
   ```toml
   NEWSAPI_KEY = "your-newsapi-key-here"
   HUGGINGFACE_TOKEN = "your-huggingface-token-here"
   ```

5. **Run the app**
   ```bash
   streamlit run streamlit_app.py
   ```

6. **Open browser** at `http://localhost:8501`

## 🌐 Deploy to Streamlit Cloud

### Quick Deploy (5 minutes)

1. **Fork this repository** (click Fork button)

2. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**

3. **Sign in with GitHub**

4. **Click "New app"** and select:
   - Repository: `YOUR_USERNAME/rag-news-summarizer`
   - Branch: `main`
   - Main file: `streamlit_app.py`

5. **Add secrets** (click Advanced settings):
   ```toml
   NEWSAPI_KEY = "your-newsapi-key-here"
   HUGGINGFACE_TOKEN = "your-huggingface-token-here"
   ```

6. **Click Deploy!** 🚀

Your app will be live at `https://your-app.streamlit.app` in ~5-10 minutes!

## 🔑 Getting Free API Keys.

### NewsAPI (Recommended)
1. Go to https://newsapi.org/register
2. Sign up with email (free)
3. Copy your API key
4. **Free tier**: 100 requests/day

### Hugging Face (Optional)
1. Go to https://huggingface.co/join
2. Create free account
3. Go to Settings → Access Tokens
4. Create new token
5. **Free tier**: 30,000 characters/month

### No API Keys?
The app works without any API keys using RSS feeds! Just choose "RSS Feeds" option when running.

## 💡 Usage

### Basic Usage

1. **Enter a topic** (e.g., "artificial intelligence", "climate change")
2. **Click "Search & Analyze"**
3. **Wait for articles to load** (~30 seconds)
4. **Ask questions** about the news
5. **Get AI-generated summaries**

### Example Queries

```
Topic: "space exploration"
Question: "What are the latest Mars missions?"

Topic: "cryptocurrency"
Question: "What's happening with Bitcoin?"

Topic: "climate change"
Question: "What are recent policy changes?"
```

## 🎨 Customization

### Change Appearance

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
```

### Add More News Sources

Edit `streamlit_app.py`:
```python
feeds = [
    f"https://news.google.com/rss/search?q={topic}",
    f"https://www.reddit.com/search.rss?q={topic}",
    # Add more RSS feeds here
]
```

### Use Different Models

```python
# For better embeddings (requires more memory)
model = SentenceTransformer('all-MiniLM-L6-v2')

# For multilingual support
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
```

## 📊 Performance

| Metric | Value |
|--------|-------|
| Average response time | ~3-5 seconds |
| Articles processed | Up to 50 per query |
| Memory usage | ~300MB |
| Model size | 61MB (embedding) |
| Works on free tier | ✅ Yes |

## 🐛 Troubleshooting

### "No articles found"
- Try different search terms
- Switch between NewsAPI and RSS feeds
- Check API key is valid

### "Out of memory"
- Reduce number of articles in settings
- Use smaller embedding model
- Clear cache (Settings → Clear cache)

### "API rate limit exceeded"
- Switch to RSS feeds (no limit)
- Wait 24 hours for NewsAPI reset
- Use Hugging Face local models

### App is slow
- First run downloads models (~1 min)
- Subsequent runs are cached
- Check your internet connection

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contributions
- [ ] Add more news sources
- [ ] Implement article saving/bookmarking
- [ ] Add sentiment analysis
- [ ] Multi-language support
- [ ] Export summaries to PDF
- [ ] Email notifications
- [ ] Dark mode toggle

## 📈 Roadmap

- [x] Basic RAG implementation
- [x] Streamlit interface
- [x] Free API integration
- [ ] User authentication
- [ ] Save favorite articles
- [ ] Historical search
- [ ] Share summaries
- [ ] Mobile app version

## 📝 Project Structure

```
rag-news-summarizer/
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt           # Python dependencies
├── .streamlit/
│   ├── config.toml           # Streamlit configuration
│   └── secrets.toml          # API keys (not in repo)
├── .gitignore                # Git ignore file
├── secrets.toml.example      # Template for secrets
└── README.md                 # This file
```

## 🔬 How It Works

### RAG Pipeline

1. **Retrieval**: Fetch latest news articles from NewsAPI or RSS feeds
2. **Processing**: Create embeddings using Sentence Transformers
3. **Search**: Find relevant articles using cosine similarity
4. **Generation**: Summarize with Hugging Face BART model
5. **Display**: Show results in interactive interface

### Architecture

```
User Query → Fetch News → Create Embeddings → Vector Search
                ↓              ↓                  ↓
         NewsAPI/RSS    Sentence-BERT      Similarity Match
                                                  ↓
                                         AI Summarization
                                                  ↓
                                         Display Results
```

## 💰 Cost Breakdown

| Service | Cost | Limit |
|---------|------|-------|
| Streamlit Cloud | **Free** | 1 public app |
| NewsAPI | **Free** | 100 req/day |
| Hugging Face | **Free** | 30k chars/month |
| Sentence Transformers | **Free** | Unlimited (local) |
| **Total** | **$0/month** | Perfect for personal use |

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - Amazing web framework
- [Hugging Face](https://huggingface.co/) - Free AI models
- [NewsAPI](https://newsapi.org/) - News aggregation
- [Sentence Transformers](https://www.sbert.net/) - Embedding models

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

