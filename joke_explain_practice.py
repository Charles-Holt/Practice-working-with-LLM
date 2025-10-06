import os
import requests
import streamlit as st

API_BASE = "https://models.github.ai"
INFERENCE_PATH = "/inference/chat/completions"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_MODELS_TOKEN")

st.set_page_config(page_title="Joke Explanation (GitHub Models)", page_icon="😂")
st.title("Joke Explanation App 😂")
st.caption("Powered by GitHub Models free tier")

# Model picker (these IDs come from the GitHub Models catalog)
# You can list models at: https://models.github.ai/catalog/models
model = st.sidebar.selectbox(
    "Model",
    ["openai/gpt-4.1-mini", "openai/gpt-4.1", "openai/gpt-4o-mini"],
    index=0,
    help="Models are hosted by GitHub Models."
)

with st.expander("Debug"):
    st.write({
        "has_github_token": bool(GITHUB_TOKEN),
        "model": model,
    })

if not GITHUB_TOKEN:
    st.error(
        "No GitHub token found.\n\n"
        "Create a fine-grained token with **Models: Read** and set it in your shell:\n"
        "   export GITHUB_TOKEN=github_pat_your_token\n\n"
        "Then run:  streamlit run joke_explain_app.py"
    )
    st.stop()

joke = st.text_area("Enter a joke to explain:", height=140,
                    placeholder="e.g., Why did the scarecrow win an award? Because he was outstanding in his field!")

if st.button("Explain Joke"):
    if not joke.strip():
        st.warning("Please enter a joke first.")
    else:
        with st.spinner("Explaining…"):
            try:
                url = f"{API_BASE}{INFERENCE_PATH}"
                headers = {
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {GITHUB_TOKEN}",
                    "X-GitHub-Api-Version": "2022-11-28",
                    "Content-Type": "application/json",
                }
                body = {
                    "model": model,
                    "messages": [
                        {"role": "system",
                         "content": "You explain jokes clearly for beginners in 2–3 sentences. Identify the wordplay or reference and why it’s funny."},
                        {"role": "user", "content": joke}
                    ],
                    "max_tokens": 180,
                    "temperature": 0.4
                }
                r = requests.post(url, headers=headers, json=body, timeout=60)
                if r.status_code != 200:
                    st.error(f"GitHub Models API error {r.status_code}: {r.text}")
                else:
                    data = r.json()
                    # Response schema: { choices: [ { message: { role, content } } ] }
                    content = data["choices"][0]["message"]["content"]
                    st.subheader("Explanation")
                    st.write(content)
            except Exception as e:
                st.error(f"Request failed: {e}")
