
import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import numpy as np
from bs4 import BeautifulSoup
import time
import os

# Lightweight embedding using Hugging Face API (free)
from sentence_transformers import SentenceTransformer


st.set_page_config(
    page_title="Free RAG News Summarizer",
    page_icon="🗞️",
    layout="wide",
    initial_sidebar_state="expanded"
)




def get_api_keys():

    try:
        newsapi_key = st.secrets.get("NEWSAPI_KEY", os.getenv("NEWSAPI_KEY"))
        hf_token = st.secrets.get("HUGGINGFACE_TOKEN", os.getenv("HUGGINGFACE_TOKEN"))
        return newsapi_key, hf_token
    except:
        return None, None


NEWSAPI_KEY, HUGGINGFACE_TOKEN = get_api_keys()




@st.cache_resource
def load_embedding_model():
    """Load lightweight embedding model (cached)"""
    with st.spinner("Loading embedding model (first time only)..."):
        # Use smallest model for Streamlit Cloud
        model = SentenceTransformer('paraphrase-MiniLM-L3-v2')  # Only 61MB!
    return model


@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_news_newsapi(topic, days=7):
    """Fetch news from NewsAPI (cached)"""
    if not NEWSAPI_KEY:
        return None, "Please add NEWSAPI_KEY to Streamlit Secrets"

    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)

    url = "https://newsapi.org/v2/everything"
    params = {
        'q': topic,
        'from': from_date.strftime('%Y-%m-%d'),
        'to': to_date.strftime('%Y-%m-%d'),
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 50,
        'apiKey': NEWSAPI_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get('status') == 'ok':
            return data['articles'], None
        else:
            return None, data.get('message', 'Unknown error')
    except Exception as e:
        return None, str(e)


@st.cache_data(ttl=3600)
def fetch_news_rss(topic):

    print(f"\n🔍 Fetching news about '{topic}' from RSS feeds (100% FREE)...")

    # Free RSS feeds from major news sources
    rss_feeds = [
        f"https://news.google.com/rss/search?q={topic}&hl=en-US&gl=US&ceid=US:en",
    ]

    articles = []
    for feed_url in tqdm(rss_feeds, desc="Fetching from RSS feeds"):
        try:
            response = requests.get(feed_url, timeout=10)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            # Find all items (articles)
            for item in root.findall('.//item'):
                title_elem = item.find('title')
                link_elem = item.find('link')
                desc_elem = item.find('description')
                pub_elem = item.find('pubDate')

                article = {
                    'title': title_elem.text if title_elem is not None else '',
                    'description': desc_elem.text if desc_elem is not None else '',
                    'url': link_elem.text if link_elem is not None else '',
                    'publishedAt': pub_elem.text if pub_elem is not None else '',
                    'source': {'name': 'Google News'}
                }

                if article['title']:  # Only add if has title
                    articles.append(article)

            time.sleep(1)  # Be polite
        except Exception as e:
            print(f"⚠️ Error with feed: {e}")
            continue

    print(f"✅ Found {len(articles)} articles from RSS feeds")
    return articles, None

def summarize_with_huggingface(text, max_length=130):
    if not HUGGINGFACE_TOKEN:
        sentences = text.split('.')[:3]
        return '. '.join(sentences) + '.'

    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": text[:1024], "parameters": {"max_length": max_length}},
            timeout=30
        )
        result = response.json()

        if isinstance(result, list) and len(result) > 0:
            return result[0].get('summary_text', 'Summary generation failed')
        elif isinstance(result, dict) and 'error' in result:
            # Model loading, retry
            time.sleep(2)
            return summarize_with_huggingface(text, max_length)
        else:
            return 'Summary generation failed'
    except Exception as e:
        sentences = text.split('.')[:3]
        return '. '.join(sentences) + '.'



def main():
    # Header
    st.title("🗞️ Free RAG News Summarizer")
    st.markdown("*Powered by Sentence Transformers & Hugging Face*")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Key status
        st.subheader("🔑 API Status")
        if NEWSAPI_KEY:
            st.success("✅ NewsAPI Connected")
        else:
            st.warning("⚠️ NewsAPI not configured (using RSS)")
            with st.expander("How to add NewsAPI"):
                st.markdown("""
                1. Get free key: https://newsapi.org/register
                2. Go to Streamlit Cloud Settings
                3. Add to Secrets:
                ```
                NEWSAPI_KEY = "your-key-here"
                ```
                """)

        if HUGGINGFACE_TOKEN:
            st.success("✅ Hugging Face Connected")
        else:
            st.info("ℹ️ Using basic summarization")
            with st.expander("How to add Hugging Face"):
                st.markdown("""
                1. Get free token: https://huggingface.co/settings/tokens
                2. Add to Streamlit Secrets:
                ```
                HUGGINGFACE_TOKEN = "your-token-here"
                ```
                """)

        st.markdown("---")

        # Settings
        st.subheader("📊 Settings")
        news_source = st.radio(
            "News Source:",
            ["RSS Feeds (Free, No Key)", "NewsAPI (Requires Key)"],
            index=0 if not NEWSAPI_KEY else 1
        )

        days = st.slider("Days to search:", 1, 30, 7)
        top_k = st.slider("Articles to analyze:", 1, 5, 3)




    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        topic = st.text_input(
            "🔍 Enter news topic:",
            placeholder="e.g., artificial intelligence, climate change, space exploration"
        )

    with col2:
        search_button = st.button("🚀 Search & Analyze", type="primary", use_container_width=True)

    # Search logic
    if search_button and topic:
        # Initialize session state
        if 'articles' not in st.session_state:
            st.session_state.articles = []
        if 'embeddings' not in st.session_state:
            st.session_state.embeddings = None

        # Progress
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Step 1: Fetch news
        status_text.text("📰 Fetching news articles...")
        progress_bar.progress(20)

        if "RSS" in news_source:
            articles, error = fetch_news_rss(topic)
        else:
            articles, error = fetch_news_newsapi(topic, days)

        if error:
            st.error(f"❌ Error: {error}")
            return

        if not articles:
            st.warning("No articles found. Try a different topic.")
            return

        st.session_state.articles = articles
        st.success(f"✅ Found {len(articles)} articles")
        progress_bar.progress(50)

        # Step 2: Create embeddings
        status_text.text("🧠 Creating embeddings...")

        try:
            model = load_embedding_model()

            texts = [f"{a['title']}. {a.get('description', '')}" for a in articles]
            embeddings = model.encode(texts, show_progress_bar=False)
            st.session_state.embeddings = embeddings

            progress_bar.progress(100)
            status_text.text("✅ Ready for questions!")
            time.sleep(1)
            status_text.empty()
            progress_bar.empty()

        except Exception as e:
            st.error(f"❌ Error creating embeddings: {e}")
            return

    # Query interface
    if st.session_state.get('articles') and st.session_state.get('embeddings') is not None:
        st.markdown("---")
        st.subheader("💬 Ask Questions About the News")

        query = st.text_input(
            "Enter your question:",
            placeholder="e.g., What are the latest developments? Who are the key players?"
        )

        if st.button("🔎 Get Answer") and query:
            with st.spinner("Analyzing articles..."):
                # Load model
                model = load_embedding_model()
                query_embedding = model.encode([query])
                similarities = np.dot(st.session_state.embeddings, query_embedding.T).flatten()
                top_indices = np.argsort(similarities)[-top_k:][::-1]
                relevant_articles = [st.session_state.articles[i] for i in top_indices]

                # Create combined text
                combined_text = "\n\n".join([
                    f"{a['title']}. {a.get('description', '')}"
                    for a in relevant_articles
                ])

                # Generate summary
                with st.spinner("Generating summary..."):
                    summary = summarize_with_huggingface(combined_text)

                # Display results
                st.markdown("### 📝 Summary")
                st.info(summary)

                st.markdown("### 📰 Top Relevant Articles")
                for i, article in enumerate(relevant_articles, 1):
                    with st.expander(f"{i}. {article['title']}"):
                        st.markdown(f"**Source:** {article['source']['name']}")
                        if article.get('description'):
                            st.markdown(f"**Description:** {article['description']}")
                        if article.get('url'):
                            st.markdown(f"**[Read More]({article['url']})**")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p>Made by Tarun| 
        <a href='https://github.com/yourusername/rag-news-summarizer'>GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()