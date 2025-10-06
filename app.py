import streamlit as st
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
import os
import xml.etree.ElementTree as ET
import re

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




def calculate_similarity(query, text):
    """Calculate simple keyword-based similarity"""
    query_words = set(re.findall(r'\w+', query.lower()))
    text_words = set(re.findall(r'\w+', text.lower()))

    if not query_words or not text_words:
        return 0.0

    intersection = query_words.intersection(text_words)
    return len(intersection) / len(query_words)


def simple_summarize(text, max_sentences=3):
    """Simple extractive summarization"""
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:max_sentences]
    return '. '.join(sentences) + '.'


 
# FETCH NEWS
 

@st.cache_data(ttl=3600)
def fetch_news_newsapi(topic, days=7):
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
    """Fetch from RSS feeds - Python 3.13 compatible"""
    feeds = [
        f"https://news.google.com/rss/search?q={topic}&hl=en-US&gl=US&ceid=US:en",
    ]

    articles = []
    for feed_url in feeds:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(feed_url, headers=headers, timeout=10)
            response.raise_for_status()

            root = ET.fromstring(response.content)

            items = root.findall('.//item')

            for item in items[:30]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                desc_elem = item.find('description')

                title = title_elem.text if title_elem is not None else ''
                link_text = link_elem.text if link_elem is not None else ''
                description = desc_elem.text if desc_elem is not None else ''

                if description:
                    try:
                        soup = BeautifulSoup(description, 'html.parser')
                        description = soup.get_text()
                    except:
                        pass

                article = {
                    'title': title,
                    'description': description,
                    'url': link_text,
                    'publishedAt': '',
                    'source': {'name': 'Google News'}
                }

                if article['title']:
                    articles.append(article)

        except Exception as e:
            continue

    return articles, None


def summarize_with_api(text):
    """Try HuggingFace API, fallback to simple summary"""
    if not HUGGINGFACE_TOKEN:
        return simple_summarize(text)

    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": text[:1024]},
            timeout=30
        )
        result = response.json()

        if isinstance(result, list) and len(result) > 0:
            return result[0].get('summary_text', simple_summarize(text))
        else:
            return simple_summarize(text)
    except:
        return simple_summarize(text)


 
# MAIN APP
 

def main():
    st.title("🗞️ Free RAG News Summarizer")


    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        st.subheader("🔑 API Status")
        if NEWSAPI_KEY:
            st.success("✅ NewsAPI Connected")
        else:
            st.warning("⚠️ Using RSS feeds")

        if HUGGINGFACE_TOKEN:
            st.success("✅ HuggingFace Connected")
        else:
            st.info("ℹ️ Using simple summarization")

        st.markdown("---")

        st.subheader("📊 Settings")
        news_source = st.radio(
            "News Source:",
            ["RSS Feeds (Free)", "NewsAPI"],
            index=0 if not NEWSAPI_KEY else 1
        )

        days = st.slider("Days to search:", 1, 30, 7)
        top_k = st.slider("Articles to show:", 1, 10, 5)

    # Main content
    topic = st.text_input(
        "🔍 Enter news topic:",
        placeholder="e.g., artificial intelligence, climate change"
    )

    if st.button("🚀 Search & Analyze", type="primary"):
        if not topic:
            st.warning("Please enter a topic")
            return

        with st.spinner("Fetching news..."):
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

    if st.session_state.get('articles'):
        st.markdown("---")
        st.subheader("💬 Ask Questions About the News")

        query = st.text_input(
            "Enter your question:",
            placeholder="What are the latest developments?"
        )

        if st.button("🔎 Get Answer") and query:
            articles = st.session_state.articles

            # Calculate similarity for each article
            scored_articles = []
            for article in articles:
                text = f"{article['title']}. {article.get('description', '')}"
                score = calculate_similarity(query, text)
                scored_articles.append((score, article))

            # Sort by score and get top results
            scored_articles.sort(reverse=True, key=lambda x: x[0])
            relevant_articles = [art for score, art in scored_articles[:top_k] if score > 0]

            if not relevant_articles:
                st.warning("No relevant articles found for your question.")
                return

            # Combine text
            combined_text = "\n\n".join([
                f"{a['title']}. {a.get('description', '')}"
                for a in relevant_articles[:3]
            ])

            # Generate summary
            with st.spinner("Generating summary..."):
                summary = summarize_with_api(combined_text)

            st.markdown("### 📝 Summary")


            st.markdown(f"""
            <div style="
                padding: 1.5rem;
                border-radius: 8px;
                border-left: 4px solid #FF4B4B;
                background-color: rgba(240, 242, 246, 0.5);
                backdrop-filter: blur(10px);
                font-family: 'Source Serif Pro', serif;
                font-size: 1.1rem;
                line-height: 1.8;
            ">
                {summary}
            </div>
            """, unsafe_allow_html=True)


            st.markdown("### 📰 Relevant Articles")
            for i, article in enumerate(relevant_articles, 1):
                with st.expander(f"{i}. {article['title']}"):
                    if article.get('description'):
                        st.write(article['description'])
                    if article.get('url'):
                        st.markdown(f"[Read More]({article['url']})")

    st.markdown("---")
    st.markdown("*By Tarun*")


if __name__ == "__main__":
    main()