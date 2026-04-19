"""
audit_chain.py  —  LangChain + Groq logic
  1. generate_document(topic)   → writes an AI doc on a topic
  2. audit_document(text)       → extracts claims, verifies each, returns list of results
"""

import os, json, re
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# ── LLM Setup ─────────────────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",     # free tier model
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY"),
)

parser = StrOutputParser()


# ─────────────────────────────────────────────────────────────────────────────
# 1.  GENERATE DOCUMENT
# ─────────────────────────────────────────────────────────────────────────────
gen_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI assistant that writes short factual research briefs.
Write a 150-200 word research brief on the given topic.
Include specific facts: dates, numbers, names, statistics, events.
Do NOT use markdown. Write in plain paragraphs."""),
    ("human", "Write a research brief about: {topic}")
])

gen_chain = gen_prompt | llm | parser


def generate_document(topic: str) -> str:
    return gen_chain.invoke({"topic": topic})


# ─────────────────────────────────────────────────────────────────────────────
# 2.  EXTRACT CLAIMS
# ─────────────────────────────────────────────────────────────────────────────
extract_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a fact-checking assistant.
Extract every specific factual claim from the given text.
A claim is any sentence or phrase that states a verifiable fact:
  - dates, years, numbers, statistics
  - names of people, places, organizations
  - events, achievements, records

Return ONLY a JSON array of strings. No explanation. No markdown. Example:
["Claim one here.", "Claim two here."]"""),
    ("human", "Text:\n{text}")
])

extract_chain = extract_prompt | llm | parser


def extract_claims(text: str) -> list[str]:
    raw = extract_chain.invoke({"text": text})
    try:
        # strip any accidental markdown code fences
        clean = re.sub(r"```[a-z]*", "", raw).strip().strip("`").strip()
        claims = json.loads(clean)
        return [c for c in claims if isinstance(c, str) and len(c) > 10]
    except Exception:
        # fallback: split by newline
        lines = [l.strip().strip('"').strip("'") for l in raw.split("\n") if len(l.strip()) > 10]
        return lines[:15]


# ─────────────────────────────────────────────────────────────────────────────
# 3.  VERIFY EACH CLAIM
# ─────────────────────────────────────────────────────────────────────────────
verify_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a strict fact-checker.
Given a factual claim, determine if it is:
  - VERIFIED   : The claim is accurate and widely established
  - UNVERIFIED : The claim may be true but cannot be confirmed or is ambiguous
  - HALLUCINATION : The claim is factually wrong, impossible, or invented

You must respond ONLY with a JSON object. No markdown. No explanation outside JSON.
Format:
{{
  "verdict": "VERIFIED" | "UNVERIFIED" | "HALLUCINATION",
  "confidence": <integer 0-100>,
  "reasoning": "<one sentence explanation>",
  "source": "<a real URL or empty string if none>"
}}"""),
    ("human", "Claim: {claim}")
])

verify_chain = verify_prompt | llm | parser


def verify_claim(claim: str) -> dict:
    raw = verify_chain.invoke({"claim": claim})
    try:
        clean = re.sub(r"```[a-z]*", "", raw).strip().strip("`").strip()
        result = json.loads(clean)
        # sanitize
        verdict = result.get("verdict", "UNVERIFIED").upper()
        if verdict not in ("VERIFIED", "UNVERIFIED", "HALLUCINATION"):
            verdict = "UNVERIFIED"
        return {
            "claim": claim,
            "verdict": verdict,
            "confidence": int(result.get("confidence", 50)),
            "reasoning": result.get("reasoning", ""),
            "source": result.get("source", ""),
        }
    except Exception:
        return {
            "claim": claim,
            "verdict": "UNVERIFIED",
            "confidence": 40,
            "reasoning": "Could not parse verification response.",
            "source": "",
        }


# ─────────────────────────────────────────────────────────────────────────────
# 4.  FULL AUDIT PIPELINE
# ─────────────────────────────────────────────────────────────────────────────
def audit_document(text: str) -> list[dict]:
    claims = extract_claims(text)
    results = []
    for claim in claims[:12]:          # limit to 12 claims to avoid rate limits
        result = verify_claim(claim)
        results.append(result)
    return results
