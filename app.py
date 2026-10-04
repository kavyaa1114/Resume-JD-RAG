import streamlit as st
import tempfile
import os
import re

from rag_pipeline import analyze_resume


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="TalentLens | Resume-JD Analyzer",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    .stApp {
        background-color: #f7f8fc;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 4rem;
        padding-bottom: 4rem;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    [data-testid="stSidebar"] {
        background-color: #f0f2f7;
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: #30333d;
    }


    /* ======================================================
       MAIN TITLE
       ====================================================== */

    .hero-title {
        font-size: 42px;
        font-weight: 750;
        color: #181a23;
        line-height: 1.1;
        margin-top: 4px;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 16px;
        color: #707583;
        margin-bottom: 30px;
    }


    /* ======================================================
       UPLOADERS
       ====================================================== */

    [data-testid="stFileUploader"] {
        background-color: white;
        border: 1px solid #e2e4ea;
        border-radius: 12px;
        padding: 8px;
    }


    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button {
        border-radius: 9px;
        min-height: 46px;
        font-size: 15px;
        font-weight: 650;
    }


    /* ======================================================
       RESULT CARDS
       ====================================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white;
        border-radius: 12px;
    }


    /* ======================================================
       DIVIDER
       ====================================================== */

    .soft-divider {
        margin-top: 32px;
        margin-bottom: 30px;
        border-top: 1px solid #e2e4ea;
    }


    /* ======================================================
       RESULT HEADINGS
       ====================================================== */

    .result-heading {
        font-size: 26px;
        font-weight: 720;
        color: #20222d;
        margin-bottom: 5px;
    }

    .result-subheading {
        color: #777d8b;
        font-size: 14px;
        margin-bottom: 20px;
    }


    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("◈ TalentLens")

    st.caption(
        "A RAG-powered recruiter assistant that retrieves "
        "relevant candidate evidence and generates concise "
        "job-specific analysis."
    )

    st.divider()

    st.subheader("How it works")

    st.info("① Upload candidate resume")

    st.info("② Upload job description")

    st.info("③ Retrieve relevant resume evidence")

    st.info("④ Generate recruiter analysis")

    st.divider()

    st.subheader("Technology")

    st.caption(
        "RAG  •  FAISS  •  OpenAI  •  LangChain  •  Streamlit"
    )

    st.divider()

    st.caption(
        "Decision-support tool — does not make hiring decisions."
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    "##### AI RECRUITING INTELLIGENCE"
)

st.markdown(
    '<div class="hero-title">Resume-JD Analyzer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-subtitle">'
    "Understand how a candidate's experience aligns with a job description."
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# DOCUMENT UPLOAD SECTION
# ============================================================

resume_col, jd_col = st.columns(
    2,
    gap="large"
)


# ------------------------------------------------------------
# RESUME
# ------------------------------------------------------------

with resume_col:

    with st.container(border=True):

        st.subheader("👤 Candidate Resume")

        st.caption(
            "Upload the candidate's resume in PDF format."
        )

        resume_file = st.file_uploader(
            "Resume PDF",
            type=["pdf"],
            key="resume",
            label_visibility="collapsed"
        )

        if resume_file:

            st.success(
                f"✓ {resume_file.name}"
            )


# ------------------------------------------------------------
# JOB DESCRIPTION
# ------------------------------------------------------------

with jd_col:

    with st.container(border=True):

        st.subheader("💼 Job Description")

        st.caption(
            "Upload the job description you want to evaluate against."
        )

        jd_file = st.file_uploader(
            "Job Description PDF",
            type=["pdf"],
            key="jd",
            label_visibility="collapsed"
        )

        if jd_file:

            st.success(
                f"✓ {jd_file.name}"
            )


# ============================================================
# ANALYZE BUTTON
# ============================================================

st.write("")

button_left, button_center, button_right = st.columns(
    [1, 2, 1]
)

with button_center:

    analyze_button = st.button(
        "🔍 Analyze Candidate",
        type="primary",
        use_container_width=True
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def extract_section(text, section_name, next_sections=None):
    """
    Extract one section from the LLM response.
    """

    if not text:
        return ""

    if next_sections:

        next_pattern = "|".join(
            re.escape(section)
            for section in next_sections
        )

        pattern = (
            rf"##\s*{re.escape(section_name)}\s*"
            rf"(.*?)(?=\n##\s*(?:{next_pattern})|\Z)"
        )

    else:

        pattern = (
            rf"##\s*{re.escape(section_name)}\s*"
            rf"(.*?)(?=\Z)"
        )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        return match.group(1).strip()

    return ""


def parse_items(section_text):
    """
    Extract bullet and numbered items.
    """

    if not section_text:
        return []

    lines = section_text.splitlines()

    items = []

    current = ""

    for line in lines:

        line = line.strip()

        if not line:
            continue

        is_new_item = (
            line.startswith("✓")
            or line.startswith("⚠")
            or re.match(r"^\d+\.", line)
        )

        if is_new_item:

            if current:
                items.append(current.strip())

            current = line

        else:

            if current:
                current += " " + line

    if current:
        items.append(current.strip())

    return items


def split_requirement(item):
    """
    Split:

    Requirement — Evidence

    into:

    Requirement
    Evidence
    """

    item = item.replace("✓", "", 1)
    item = item.replace("⚠", "", 1)
    item = item.strip()

    if "—" in item:

        title, description = item.split(
            "—",
            1
        )

        return (
            title.strip(),
            description.strip()
        )

    return item, ""


def clean_text(text):
    """
    Remove accidental HTML/code formatting if an LLM
    response ever contains it.
    """

    if not text:
        return ""

    text = text.replace(
        "```html",
        ""
    )

    text = text.replace(
        "```markdown",
        ""
    )

    text = text.replace(
        "```",
        ""
    )

    # Remove HTML tags if they somehow appear.
    text = re.sub(
        r"<[^>]+>",
        "",
        text
    )

    return text.strip()


def parse_evidence(evidence_text):
    """
    Parse evidence formatted as:

    **Requirement**
    Candidate demonstrated this through...
    """

    if not evidence_text:
        return []

    evidence_text = clean_text(
        evidence_text
    )

    pattern = r"\*\*(.*?)\*\*"

    matches = list(
        re.finditer(
            pattern,
            evidence_text
        )
    )

    evidence = []

    for i, match in enumerate(matches):

        title = match.group(1).strip()

        start = match.end()

        if i + 1 < len(matches):

            end = matches[i + 1].start()

        else:

            end = len(evidence_text)

        description = evidence_text[
            start:end
        ].strip()

        if description:

            evidence.append(
                (
                    title,
                    description
                )
            )

    return evidence


# ============================================================
# RUN ANALYSIS
# ============================================================

if analyze_button:

    if resume_file is None or jd_file is None:

        st.warning(
            "Please upload both a candidate resume "
            "and a job description."
        )

    else:

        with st.spinner(
            "Retrieving candidate evidence and generating analysis..."
        ):

            resume_path = None
            jd_path = None

            try:

                # ------------------------------------------------
                # TEMPORARY RESUME FILE
                # ------------------------------------------------

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as resume_temp:

                    resume_temp.write(
                        resume_file.getbuffer()
                    )

                    resume_path = resume_temp.name


                # ------------------------------------------------
                # TEMPORARY JD FILE
                # ------------------------------------------------

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as jd_temp:

                    jd_temp.write(
                        jd_file.getbuffer()
                    )

                    jd_path = jd_temp.name


                # ------------------------------------------------
                # RUN RAG PIPELINE
                # ------------------------------------------------

                result = analyze_resume(
                    resume_path,
                    jd_path
                )

                st.session_state.analysis_result = result


            except Exception as e:

                st.error(
                    "Something went wrong while analyzing "
                    "the documents."
                )

                st.exception(e)


            finally:

                # ------------------------------------------------
                # CLEAN UP TEMPORARY FILES
                # ------------------------------------------------

                if (
                    resume_path
                    and os.path.exists(resume_path)
                ):

                    os.remove(
                        resume_path
                    )

                if (
                    jd_path
                    and os.path.exists(jd_path)
                ):

                    os.remove(
                        jd_path
                    )


# ============================================================
# DISPLAY RESULTS
# ============================================================

if st.session_state.analysis_result:

    result = st.session_state.analysis_result

    analysis = result["analysis"]


    # ========================================================
    # EXTRACT SECTIONS
    # ========================================================

    sections = [
        "STRONG MATCHES",
        "GAPS",
        "RECRUITER TAKEAWAY",
        "INTERVIEW QUESTIONS",
        "EVIDENCE BEHIND ANALYSIS"
    ]

    matches_text = extract_section(
        analysis,
        "STRONG MATCHES",
        sections[1:]
    )

    gaps_text = extract_section(
        analysis,
        "GAPS",
        sections[2:]
    )

    takeaway_text = extract_section(
        analysis,
        "RECRUITER TAKEAWAY",
        sections[3:]
    )

    questions_text = extract_section(
        analysis,
        "INTERVIEW QUESTIONS",
        sections[4:]
    )

    evidence_text = extract_section(
        analysis,
        "EVIDENCE BEHIND ANALYSIS"
    )


    # ========================================================
    # RESULTS HEADER
    # ========================================================

    st.markdown(
        '<div class="soft-divider"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="result-heading">'
        '🎯 Recruiter Analysis'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="result-subheading">'
        'Grounded analysis generated from the job description '
        'and relevant resume evidence.'
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # STRONG MATCHES
    # ========================================================

    if matches_text:

        st.markdown(
            "### 🟢 Strong Matches"
        )

        matches = parse_items(
            matches_text
        )

        for item in matches:

            title, description = split_requirement(
                item
            )

            with st.container(
                border=True
            ):

                st.markdown(
                    f"**✓ {title}**"
                )

                if description:

                    st.write(
                        description
                    )


    # ========================================================
    # GAPS
    # ========================================================

    if gaps_text:

        st.markdown(
            "### 🔴 Areas to Verify"
        )

        gaps = parse_items(
            gaps_text
        )

        for item in gaps:

            title, description = split_requirement(
                item
            )

            with st.container(
                border=True
            ):

                st.markdown(
                    f"**⚠ {title}**"
                )

                if description:

                    st.caption(
                        description
                    )


    # ========================================================
    # RECRUITER TAKEAWAY
    # ========================================================

    if takeaway_text:

        takeaway_text = clean_text(
            takeaway_text
        )

        st.markdown(
            "### 🎯 Recruiter Takeaway"
        )

        st.info(
            takeaway_text
        )


    # ========================================================
    # INTERVIEW QUESTIONS
    # ========================================================

    if questions_text:

        st.markdown(
            "### 💬 Suggested Interview Questions"
        )

        questions = parse_items(
            questions_text
        )

        for number, question in enumerate(
            questions,
            start=1
        ):

            question = re.sub(
                r"^\d+\.\s*",
                "",
                question
            ).strip()

            with st.container(
                border=True
            ):

                st.markdown(
                    f"**{number}.** {question}"
                )


    # ========================================================
    # EVIDENCE BEHIND ANALYSIS
    # ========================================================

    if evidence_text:

        st.markdown(
            '<div class="soft-divider"></div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="result-heading">'
            '🔎 Evidence Behind Analysis'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="result-subheading">'
            'Relevant candidate experience retrieved from the '
            'resume and used to ground the analysis.'
            '</div>',
            unsafe_allow_html=True
        )

        evidence_items = parse_evidence(
            evidence_text
        )

        for title, description in evidence_items:

            with st.container(
                border=True
            ):

                st.markdown(
                    f"**{title}**"
                )

                st.write(
                    description
                )


# ============================================================
# FOOTER
# ============================================================

if st.session_state.analysis_result:

    st.divider()

    st.caption(
        "TalentLens uses retrieval-augmented generation to "
        "ground recruiter analysis in candidate-specific evidence."
    )