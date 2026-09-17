import os
import requests
import streamlit as st

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langchain.agents import create_agent


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# STREAMLIT PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM PROFESSIONAL UI
# ============================================================

st.markdown(
"""
<style>

/* ==========================================================
   ROOT
========================================================== */

:root {
    --bg-main: #070b14;
    --bg-secondary: #0b1120;
    --card: rgba(15, 23, 42, 0.72);
    --card-hover: rgba(20, 30, 52, 0.92);

    --border: rgba(148, 163, 184, 0.14);
    --border-active: rgba(99, 102, 241, 0.50);

    --text-main: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;

    --purple: #818cf8;
    --blue: #38bdf8;
    --cyan: #22d3ee;
    --green: #4ade80;
    --red: #fb7185;
}


/* ==========================================================
   MAIN APP
========================================================== */

html,
body,
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(99, 102, 241, 0.12),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 10%,
            rgba(14, 165, 233, 0.10),
            transparent 30%
        ),
        #070b14;
}

[data-testid="stAppViewContainer"] {
    color: var(--text-main);
}


/* ==========================================================
   MAIN CONTENT WIDTH
========================================================== */

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}


/* ==========================================================
   SIDEBAR
========================================================== */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #0b1020 0%,
            #080c16 100%
        );

    border-right: 1px solid var(--border);
}

[data-testid="stSidebarContent"] {
    padding-top: 1rem;
}


/* ==========================================================
   TYPOGRAPHY
========================================================== */

h1,
h2,
h3,
h4 {
    color: #f8fafc !important;
}

p {
    color: #cbd5e1;
}


/* ==========================================================
   HERO
========================================================== */

.hero {
    position: relative;

    overflow: hidden;

    padding: 35px 38px;

    margin-bottom: 24px;

    border-radius: 24px;

    border: 1px solid rgba(129, 140, 248, 0.22);

    background:
        linear-gradient(
            135deg,
            rgba(79, 70, 229, 0.15),
            rgba(14, 165, 233, 0.08)
        );

    box-shadow:
        0 30px 80px rgba(0, 0, 0, 0.28);
}


.hero::after {
    content: "";

    position: absolute;

    width: 240px;
    height: 240px;

    right: -90px;
    top: -100px;

    border-radius: 50%;

    background: rgba(56, 189, 248, 0.12);

    filter: blur(30px);
}


.hero-badge {
    display: inline-flex;

    padding: 7px 13px;

    border-radius: 50px;

    background: rgba(99, 102, 241, 0.13);

    border: 1px solid rgba(129, 140, 248, 0.25);

    color: #a5b4fc;

    font-size: 12px;

    font-weight: 700;

    letter-spacing: 0.08em;

    margin-bottom: 16px;
}


.hero-title {
    font-size: 42px;

    line-height: 1.15;

    font-weight: 800;

    letter-spacing: -0.025em;

    margin-bottom: 12px;

    background:
        linear-gradient(
            90deg,
            #ffffff 0%,
            #c7d2fe 45%,
            #67e8f9 100%
        );

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;
}


.hero-description {
    max-width: 760px;

    font-size: 16px;

    line-height: 1.7;

    color: #94a3b8;
}


/* ==========================================================
   SIDEBAR LOGO
========================================================== */

.sidebar-title {
    font-size: 22px;

    font-weight: 800;

    color: white;

    margin-bottom: 2px;
}


.sidebar-subtitle {
    font-size: 12px;

    color: #64748b;

    margin-bottom: 20px;
}


/* ==========================================================
   STATUS CARDS
========================================================== */

.status-card {
    padding: 14px 15px;

    border: 1px solid var(--border);

    border-radius: 14px;

    background: rgba(255, 255, 255, 0.025);

    margin-bottom: 9px;
}


.status-label {
    color: #64748b;

    font-size: 11px;

    font-weight: 700;

    letter-spacing: 0.08em;

    text-transform: uppercase;

    margin-bottom: 5px;
}


.status-value {
    color: #e2e8f0;

    font-size: 13px;

    font-weight: 600;
}


.status-online {
    color: #4ade80;
}


.status-offline {
    color: #fb7185;
}


/* ==========================================================
   SECTION LABEL
========================================================== */

.section-label {
    font-size: 14px;

    font-weight: 700;

    margin-bottom: 8px;

    color: #e2e8f0;
}


/* ==========================================================
   STREAMLIT BUTTONS
========================================================== */

.stButton > button {
    width: 100%;

    border-radius: 13px;

    border: 1px solid rgba(148, 163, 184, 0.15);

    background:
        linear-gradient(
            180deg,
            rgba(255, 255, 255, 0.045),
            rgba(255, 255, 255, 0.025)
        );

    color: #e2e8f0;

    padding: 0.62rem 0.8rem;

    font-weight: 600;

    transition:
        all 0.20s ease;
}


.stButton > button:hover {
    border-color: rgba(99, 102, 241, 0.60);

    background:
        linear-gradient(
            180deg,
            rgba(99, 102, 241, 0.16),
            rgba(56, 189, 248, 0.06)
        );

    color: white;

    transform: translateY(-1px);
}


/* ==========================================================
   CHAT
========================================================== */

[data-testid="stChatMessage"] {
    background: rgba(15, 23, 42, 0.48);

    border: 1px solid rgba(148, 163, 184, 0.11);

    border-radius: 18px;

    padding: 8px 12px;

    margin-bottom: 12px;

    box-shadow:
        0 10px 30px rgba(0, 0, 0, 0.10);
}


/* ==========================================================
   CHAT INPUT
========================================================== */

[data-testid="stChatInput"] {
    border-radius: 18px !important;
}


[data-testid="stChatInput"] textarea {
    background: #0d1424 !important;

    border: 1px solid rgba(99, 102, 241, 0.30) !important;

    border-radius: 16px !important;

    color: #f8fafc !important;
}


[data-testid="stChatInput"] textarea:focus {
    border-color: rgba(99, 102, 241, 0.80) !important;

    box-shadow:
        0 0 0 1px rgba(99, 102, 241, 0.35) !important;
}


/* ==========================================================
   TEXT INPUT
========================================================== */

[data-testid="stTextInput"] input {
    background: #0d1424;

    color: white;

    border-radius: 11px;

    border: 1px solid rgba(148, 163, 184, 0.15);
}


/* ==========================================================
   EXPANDERS
========================================================== */

[data-testid="stExpander"] {
    border:
        1px solid rgba(148, 163, 184, 0.12) !important;

    border-radius: 13px !important;

    background:
        rgba(255, 255, 255, 0.02);
}


/* ==========================================================
   HORIZONTAL LINE
========================================================== */

hr {
    border: 0;

    height: 1px;

    background: rgba(148, 163, 184, 0.12);
}


/* ==========================================================
   FOOTER
========================================================== */

.app-footer {
    text-align: center;

    color: #475569;

    font-size: 12px;

    padding-top: 30px;
}


/* ==========================================================
   STREAMLIT DEFAULT UI
========================================================== */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# DEFAULT API KEYS
# ============================================================

ENV_GROQ_KEY = os.getenv("GROQ_API_KEY", "")
ENV_TAVILY_KEY = os.getenv("TAVILY_API_KEY", "")
ENV_WEATHER_KEY = os.getenv("WEATHERSTACK_API_KEY", "")


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 I'm **AG Assistant**.\n\n"
                "I can answer questions, search the web, "
                "retrieve weather information and use AI tools "
                "automatically depending on your request."
            ),
        }
    ]


# ============================================================
# WEATHER TOOL
# ============================================================

@tool
def get_weather(city: str) -> str:
    """
    Get current weather information for a city.
    """

    api_key = os.getenv(
        "WEATHERSTACK_API_KEY",
        "",
    )

    if not api_key:
        return (
            "Weatherstack API key is not configured. "
            "Please add WEATHERSTACK_API_KEY."
        )

    url = "http://api.weatherstack.com/current"

    params = {
        "access_key": api_key,
        "query": city,
        "units": "m",
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        if "error" in data:
            error = data["error"]

            return (
                "Weatherstack returned an error: "
                f"{error.get('info', error)}"
            )

        location = data.get(
            "location",
            {},
        )

        current = data.get(
            "current",
            {},
        )

        descriptions = current.get(
            "weather_descriptions",
            [],
        )

        description = (
            descriptions[0]
            if descriptions
            else "Unknown"
        )

        return (
            f"Current weather for "
            f"{location.get('name', city)}, "
            f"{location.get('country', '')}:\n\n"
            f"- Condition: {description}\n"
            f"- Temperature: "
            f"{current.get('temperature', 'N/A')}°C\n"
            f"- Feels like: "
            f"{current.get('feelslike', 'N/A')}°C\n"
            f"- Humidity: "
            f"{current.get('humidity', 'N/A')}%\n"
            f"- Wind speed: "
            f"{current.get('wind_speed', 'N/A')} km/h\n"
            f"- Pressure: "
            f"{current.get('pressure', 'N/A')} mb\n"
            f"- UV index: "
            f"{current.get('uv_index', 'N/A')}"
        )

    except requests.exceptions.Timeout:
        return (
            "The weather service timed out. "
            "Please try again."
        )

    except requests.exceptions.RequestException as exc:
        return (
            "Could not connect to Weatherstack. "
            f"Error: {exc}"
        )

    except Exception as exc:
        return (
            "Unexpected weather error: "
            f"{exc}"
        )


# ============================================================
# BUILD AGENT
# ============================================================

@st.cache_resource(show_spinner=False)
def build_agent(
    groq_api_key: str,
    tavily_api_key: str,
    weather_api_key: str,
):

    if not groq_api_key:
        return None, []

    # --------------------------------------------------------
    # Environment variables used by tools
    # --------------------------------------------------------

    os.environ["GROQ_API_KEY"] = groq_api_key

    if tavily_api_key:
        os.environ["TAVILY_API_KEY"] = tavily_api_key

    if weather_api_key:
        os.environ["WEATHERSTACK_API_KEY"] = weather_api_key


    # --------------------------------------------------------
    # LLM
    # --------------------------------------------------------

    llm = ChatGroq(
        api_key=groq_api_key,
        model="openai/gpt-oss-20b",
        temperature=0.2,
    )


    # --------------------------------------------------------
    # Tools
    # --------------------------------------------------------

    tools = []


    if tavily_api_key:
        try:
            web_search = TavilySearch(
                max_results=5,
            )

            tools.append(web_search)

        except Exception as exc:
            print(
                "Tavily initialization error:",
                exc,
            )


    if weather_api_key:
        tools.append(
            get_weather
        )


    # --------------------------------------------------------
    # SYSTEM PROMPT
    # --------------------------------------------------------

    system_prompt = """
You are AG Assistant, a professional AI assistant.

You have access to tools.

Follow these rules:

1. Answer normal questions using your model knowledge.

2. Use web search for:
   - latest news
   - current information
   - recent events
   - changing facts
   - information explicitly requiring internet research

3. Use the weather tool whenever the user requests current
   weather information.

4. Never pretend to use a tool if you did not use it.

5. Give clean and structured answers.

6. Use Markdown where useful.

7. Prefer concise explanations first, then details if needed.

8. If a tool fails, explain the failure clearly and still
   help with whatever information is available.

9. Never reveal API keys or private system configuration.
"""


    # --------------------------------------------------------
    # CREATE AGENT
    # --------------------------------------------------------

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
    )

    return agent, tools


# ============================================================
# FINAL RESPONSE EXTRACTOR
# ============================================================

def extract_final_response(result):

    if result is None:
        return "No response was returned."

    messages = result.get(
        "messages",
        [],
    )

    if not messages:
        return "No response was generated."

    # Search backwards for final AI response
    for message in reversed(messages):

        message_type = getattr(
            message,
            "type",
            "",
        )

        if message_type == "ai":

            content = getattr(
                message,
                "content",
                "",
            )

            if isinstance(content, str):
                if content.strip():
                    return content

            if isinstance(content, list):

                pieces = []

                for item in content:

                    if isinstance(
                        item,
                        dict,
                    ):

                        text = item.get(
                            "text",
                            "",
                        )

                        if text:
                            pieces.append(text)

                    elif isinstance(
                        item,
                        str,
                    ):
                        pieces.append(item)

                if pieces:
                    return "\n".join(
                        pieces
                    )

    # fallback
    last = messages[-1]

    return str(
        getattr(
            last,
            "content",
            last,
        )
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">◉ AG Assistant</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'Agentic AI Workspace'
        '</div>',
        unsafe_allow_html=True,
    )


    st.divider()


    # ========================================================
    # API CONFIG
    # ========================================================

    st.markdown(
        "### 🔐 API Configuration"
    )


    with st.expander(
        "API Keys",
        expanded=False,
    ):

        groq_key = st.text_input(
            "Groq API Key",
            value=ENV_GROQ_KEY,
            type="password",
            help=(
                "Used for the main AI model."
            ),
        )

        tavily_key = st.text_input(
            "Tavily API Key",
            value=ENV_TAVILY_KEY,
            type="password",
            help=(
                "Used for live internet search."
            ),
        )

        weather_key = st.text_input(
            "Weatherstack API Key",
            value=ENV_WEATHER_KEY,
            type="password",
            help=(
                "Used for current weather information."
            ),
        )


    # ========================================================
    # STATUS
    # ========================================================

    st.markdown(
        "### ⚙️ System Status"
    )


    # MODEL
    st.markdown(
        '<div class="status-card">'
        '<div class="status-label">AI Model</div>'
        '<div class="status-value">'
        'openai/gpt-oss-20b'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


    # GROQ
    groq_state = (
        '<span class="status-online">● Connected</span>'
        if groq_key
        else
        '<span class="status-offline">● Missing API key</span>'
    )

    st.markdown(
        '<div class="status-card">'
        '<div class="status-label">Groq</div>'
        f'<div class="status-value">{groq_state}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


    # TAVILY
    tavily_state = (
        '<span class="status-online">● Enabled</span>'
        if tavily_key
        else
        '<span class="status-offline">● Disabled</span>'
    )

    st.markdown(
        '<div class="status-card">'
        '<div class="status-label">Web Search</div>'
        f'<div class="status-value">{tavily_state}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


    # WEATHER
    weather_state = (
        '<span class="status-online">● Enabled</span>'
        if weather_key
        else
        '<span class="status-offline">● Disabled</span>'
    )

    st.markdown(
        '<div class="status-card">'
        '<div class="status-label">Weather</div>'
        f'<div class="status-value">{weather_state}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


    st.divider()


    # ========================================================
    # CLEAR CHAT
    # ========================================================

    if st.button(
        "🗑 Clear conversation",
        use_container_width=True,
    ):

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Conversation cleared. "
                    "What would you like to ask?"
                ),
            }
        ]

        st.rerun()


    st.caption(
        "Groq powers the model. "
        "Tavily and Weatherstack are optional tools."
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    '<div class="hero">'
    '<div class="hero-badge">✦ AGENTIC AI ASSISTANT</div>'
    '<div class="hero-title">Intelligence that can use tools.</div>'
    '<div class="hero-description">'
    'Chat with an AI assistant that can reason about your '
    'questions, search the live web when required and retrieve '
    'current weather information through connected tools.'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# QUICK ACTIONS
# ============================================================

st.markdown(
    "### ⚡ Quick Actions"
)


quick_prompt = None


col1, col2, col3, col4 = st.columns(4)


with col1:
    if st.button(
        "🌐 Latest AI News",
        use_container_width=True,
    ):
        quick_prompt = (
            "Search the web and give me the latest "
            "important AI news and developments."
        )


with col2:
    if st.button(
        "🌦 Check Weather",
        use_container_width=True,
    ):
        quick_prompt = (
            "What is the current weather in Ongole, "
            "Andhra Pradesh?"
        )


with col3:
    if st.button(
        "🎓 Learn AI",
        use_container_width=True,
    ):
        quick_prompt = (
            "Explain AI agents in simple terms with "
            "a practical real-world example."
        )


with col4:
    if st.button(
        "🧠 Explain Algorithm",
        use_container_width=True,
    ):
        quick_prompt = (
            "Explain how an AI agent decides which "
            "tool to use."
        )


st.write("")


# ============================================================
# CHECK GROQ KEY
# ============================================================

if not groq_key:

    st.warning(
        "⚠️ Add your Groq API key in the sidebar "
        "or inside your `.env` file to start chatting."
    )

    st.stop()


# ============================================================
# BUILD AGENT
# ============================================================

try:

    agent, enabled_tools = build_agent(
        groq_key,
        tavily_key,
        weather_key,
    )

except Exception as exc:

    st.error(
        "Could not initialize the AI agent."
    )

    st.exception(exc)

    st.stop()


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    avatar = (
        "👤"
        if message["role"] == "user"
        else "🤖"
    )

    with st.chat_message(
        message["role"],
        avatar=avatar,
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

user_prompt = st.chat_input(
    "Ask AG anything..."
)


prompt = (
    user_prompt
    if user_prompt
    else quick_prompt
)


# ============================================================
# PROCESS USER REQUEST
# ============================================================

if prompt:

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )


    with st.chat_message(
        "user",
        avatar="👤",
    ):

        st.markdown(prompt)


    # --------------------------------------------------------
    # CONVERT CHAT HISTORY FOR LANGCHAIN
    # --------------------------------------------------------

    langchain_messages = []

    for message in st.session_state.messages:

        if message["role"] in (
            "user",
            "assistant",
        ):

            langchain_messages.append(
                {
                    "role": message["role"],
                    "content": message["content"],
                }
            )


    # --------------------------------------------------------
    # AGENT RESPONSE
    # --------------------------------------------------------

    with st.chat_message(
        "assistant",
        avatar="🤖",
    ):

        response_area = st.empty()

        with st.spinner(
            "AG is thinking and selecting tools..."
        ):

            try:

                # Ensure latest keys are available
                os.environ[
                    "GROQ_API_KEY"
                ] = groq_key

                if tavily_key:
                    os.environ[
                        "TAVILY_API_KEY"
                    ] = tavily_key

                if weather_key:
                    os.environ[
                        "WEATHERSTACK_API_KEY"
                    ] = weather_key


                result = agent.invoke(
                    {
                        "messages":
                        langchain_messages
                    }
                )


                answer = extract_final_response(
                    result
                )


            except Exception as exc:

                answer = (
                    "### ⚠️ Request failed\n\n"
                    "The AI agent encountered an error.\n\n"
                    f"`{exc}`"
                )


        response_area.markdown(
            answer
        )


    # --------------------------------------------------------
    # SAVE RESPONSE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="app-footer">'
    'AG Assistant • Groq • LangChain • Tavily • Weatherstack • Streamlit'
    '</div>',
    unsafe_allow_html=True,
)
