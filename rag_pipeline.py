from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


def analyze_resume(resume_path, jd_path):

    # --------------------------------------------------
    # LOAD RESUME
    # --------------------------------------------------

    resume_loader = PyPDFLoader(resume_path)
    resume_documents = resume_loader.load()


    # --------------------------------------------------
    # SPLIT RESUME INTO CHUNKS
    # --------------------------------------------------

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    resume_chunks = text_splitter.split_documents(
        resume_documents
    )


    # --------------------------------------------------
    # CREATE EMBEDDINGS
    # --------------------------------------------------

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )


    # --------------------------------------------------
    # CREATE FAISS VECTOR STORE
    # --------------------------------------------------

    vector_store = FAISS.from_documents(
        resume_chunks,
        embeddings
    )


    # --------------------------------------------------
    # CREATE RETRIEVER
    # --------------------------------------------------

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 5}
    )


    # --------------------------------------------------
    # LOAD JOB DESCRIPTION
    # --------------------------------------------------

    jd_loader = PyPDFLoader(jd_path)
    jd_documents = jd_loader.load()

    jd_text = "\n".join(
        document.page_content
        for document in jd_documents
    )


    # --------------------------------------------------
    # RETRIEVE RELEVANT RESUME EVIDENCE
    # --------------------------------------------------

    query = f"""
    Identify the important skills, technologies,
    experience requirements and qualifications from
    this job description.

    Retrieve the resume sections that provide the
    strongest evidence related to those requirements.

    JOB DESCRIPTION:

    {jd_text}
    """

    retrieved_documents = retriever.invoke(query)


    # Combine retrieved resume chunks
    context = "\n\n".join(
        document.page_content
        for document in retrieved_documents
    )


    # --------------------------------------------------
    # LLM PROMPT
    # --------------------------------------------------

    prompt = ChatPromptTemplate.from_template(
        """
You are an AI recruiting assistant helping a recruiter
evaluate a candidate against a specific job description.

Analyze the job description using ONLY the retrieved
resume evidence provided below.

Return EXACTLY these five sections:

## STRONG MATCHES

Select UP TO 3 strongest matches.

Format:

✓ Requirement — Evidence

Only include a match if it is clearly relevant to an
important JD requirement.

Mention the specific project, internship or experience
where the candidate demonstrated the skill.

Example:

✓ Generative AI & LLMs — Candidate developed LLM-powered
agentic workflows using LangChain and LangGraph during
the ARSoft internship.

## GAPS

Select UP TO 3 meaningful gaps.

Format:

⚠ Requirement — No supporting evidence found

Do not assume the candidate lacks a skill simply because
it was not retrieved.

Do not create gaps just to reach 3 items.

## RECRUITER TAKEAWAY

Write EXACTLY ONE sentence.

Maximum 25 words.

Mention the strongest alignment and the main area the
recruiter should verify.

## INTERVIEW QUESTIONS

Generate EXACTLY 3 short questions.

Questions should help verify:

- an important demonstrated skill
- an important gap
- an unclear JD requirement

## EVIDENCE BEHIND ANALYSIS

Provide UP TO 3 concise evidence statements.

These should explain WHERE the candidate demonstrated
the relevant requirement.

Format:

**Requirement**
Candidate demonstrated this through [specific project,
internship or experience].

For example:

**LangGraph**
Candidate demonstrated LangGraph experience through the
BHRAMAN AI project, where they built a multi-agent travel
planner using LangGraph and LangChain.

**LLMs**
Candidate gained hands-on LLM experience during the ARSoft
internship through LLM-powered agentic workflows.

IMPORTANT RULES:

- Be concise.
- Do not rewrite the entire resume.
- Do not repeat the same evidence unnecessarily.
- Do not assign a numerical score.
- Do not make a hiring decision.
- Do not invent skills or experience.
- Do not treat absence from retrieved evidence as proof
  that the candidate lacks a skill.
- Prioritize important JD requirements.
- Prefer technical evidence over generic soft skills.
- Use ONLY the provided JD and retrieved resume evidence.
- Keep the entire response under 250 words.

JOB DESCRIPTION:

{job_description}


RETRIEVED RESUME EVIDENCE:

{context}
"""
    )


    # --------------------------------------------------
    # CALL LLM
    # --------------------------------------------------

    llm = ChatOpenAI(
        model="gpt-4.1",
        temperature=0
    )

    final_prompt = prompt.invoke({
        "job_description": jd_text,
        "context": context
    })

    response = llm.invoke(final_prompt)


    # --------------------------------------------------
    # RETURN ANALYSIS + RETRIEVED DOCUMENTS
    # --------------------------------------------------

    return {
        "analysis": response.content,
        "retrieved_documents": retrieved_documents
    }