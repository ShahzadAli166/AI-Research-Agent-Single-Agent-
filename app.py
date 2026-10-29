import os
import streamlit as st
from crewai import Agent, Crew, Process, Task, LLM
from crewai.tools import tool
from ddgs import DDGS

MODEL_NAME = "groq/openai/gpt-oss-120b"

st.set_page_config(page_title="AI Research Agent", page_icon="🔎", layout="wide")
st.markdown("""
<style>
.block-container {max-width: 1050px; padding-top: 2rem;}
.hero {padding: 1.6rem; border-radius: 18px; background: linear-gradient(120deg,#10243a,#245b78); color:white; margin-bottom:1rem;}
.hero h1 {margin:0 0 .4rem 0;} .hero p {margin:0;color:#e2edf5;}
</style>
<div class="hero"><h1>🔎 AI Research Agent</h1>
<p>Research a topic, search the web, and generate a structured report with source links.</p></div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.subheader("Research settings")
    depth = st.selectbox("Report depth", ["Brief", "Standard", "Detailed"], index=1)
    result_count = st.slider("Search results per query", 4, 10, 6)
    st.caption("One CrewAI agent • DuckDuckGo • Groq")

try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    groq_api_key = os.getenv("GROQ_API_KEY", "")

if not groq_api_key:
    st.error('GROQ_API_KEY is missing. In Streamlit app settings → Secrets, add: GROQ_API_KEY = "your_groq_api_key"')
    st.stop()

@tool("DuckDuckGo web search")
def web_search(query: str) -> str:
    """Search the public web. Return source titles, URLs, and snippets for a focused query."""
    try:
        with DDGS() as client:
            results = list(client.text(query, max_results=result_count))
        if not results:
            return f"No search results found for: {query}"
        return "\n\n".join(
            f"{i}. {item.get('title', 'Untitled')}\nURL: {item.get('href') or item.get('url', '')}\nSnippet: {item.get('body', '')}"
            for i, item in enumerate(results, 1)
        )
    except Exception as exc:
        return f"Search failed: {type(exc).__name__}: {exc}"

def build_crew(topic: str, depth_choice: str):
    word_guidance = {
        "Brief": "Write about 700–1,000 words.",
        "Standard": "Write about 1,200–1,800 words.",
        "Detailed": "Write about 2,000–2,500 words.",
    }
    llm = LLM(model=MODEL_NAME, api_key=groq_api_key, temperature=0.2)
    agent = Agent(
        role="Research Analyst",
        goal="Research the topic with web search and produce a clear, evidence-based report.",
        backstory="You are careful and skeptical. Prefer primary and reputable sources, cross-check important claims, never invent citations, and state uncertainty.",
        tools=[web_search],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=8,
    )
    task = Task(
        description=(
            "Research this topic: {topic}\n\n"
            "Use the DuckDuckGo search tool multiple times with focused queries. Prefer official documentation, primary sources, academic papers, and reputable organizations. "
            "Cross-check important claims. Do not fabricate URLs, authors, dates, statistics, quotations, or references.\n\n"
            "Write a Markdown report with: 1. Title 2. Executive Summary 3. Introduction and Scope "
            "4. Key Findings 5. Evidence and Analysis 6. Limitations/Uncertainties 7. Conclusion "
            "8. References. Cite web claims inline with numbered references such as [1], matching the reference list. "
            "If evidence is limited, say so. " + word_guidance[depth_choice]
        ),
        expected_output="A structured Markdown research report with evidence-based analysis, inline numbered citations, source URLs, and explicit limitations.",
        agent=agent,
    )
    return Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)

with st.form("research_form"):
    topic = st.text_area("What topic should I research?", placeholder="Example: Current applications of AI agents in manufacturing quality control", height=110)
    submitted = st.form_submit_button("🔍 Research topic", type="primary", use_container_width=True)

if submitted:
    if not topic.strip():
        st.warning("Enter a research topic first.")
    elif len(topic.strip()) > 500:
        st.warning("Please keep the topic under 500 characters.")
    else:
        with st.status("Searching the web and preparing your report…", expanded=True) as status:
            try:
                result = build_crew(topic.strip(), depth).kickoff(inputs={"topic": topic.strip()})
                report = getattr(result, "raw", str(result))
                st.session_state["last_topic"] = topic.strip()
                st.session_state["last_report"] = report
                status.update(label="Research report ready", state="complete", expanded=False)
            except Exception as exc:
                status.update(label="Research failed", state="error", expanded=True)
                st.error(f"Research failed: {type(exc).__name__}: {exc}")
                st.info("Check your Streamlit Secrets, Groq account/model access, and deployment logs.")

if st.session_state.get("last_report"):
    st.divider()
    st.subheader("Research report")
    st.caption(f"Topic: {st.session_state.get('last_topic', '')}")
    st.markdown(st.session_state["last_report"])
    st.download_button("⬇️ Download report (.md)", data=st.session_state["last_report"], file_name="research_report.md", mime="text/markdown")

st.divider()
st.caption("AI-generated research can contain errors. Verify important claims against the linked original sources.")
