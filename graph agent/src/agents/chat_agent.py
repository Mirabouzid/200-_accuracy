from typing import Optional, Dict, List
import re

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.groq import Groq

from config import Config


def get_chat_agent() -> Agent:
    """Create and return the Agno Agent configured for graph Q&A.
    Uses Groq LLM and persists chat history to a local SQLite DB.
    """
    # Model id requested by user
    chat_model = Groq(id="openai/gpt-oss-120b")
    return Agent(
        name="Graph Chat Agent",
        model=chat_model,
        db=SqliteDb(db_file="agno_chat.db"),
        description="Answer user questions by querying the Neo4j graph when needed.",
        instructions=[
            "You are a Cypher-savvy assistant for a blockchain wallet graph.",
            "Schema:",
            "(w:Wallet {address, balance, transaction_count, is_top_holder, pagerank, is_mixer})",
            "(t:Token {address})",
            "(w1)-[:TRANSFERRED {amount, count, weight}]->(w2)",
            "(w)-[:HOLDS]->(t)",
            "Use lowercase addresses. Prefer concise JSON tables in answers.",
            "When data is needed, produce a Cypher query wrapped in triple backticks.",
        ],
        markdown=True,
        add_history_to_context=True,
    )


def extract_cypher(text: str) -> Optional[str]:
    """Extract a Cypher query from a fenced code block, if present."""
    if not text:
        return None
    # Look for ```cypher ... ``` or generic ``` ... ``` blocks
    match = re.search(r"```(?:cypher\n)?([\s\S]*?)```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def run_cypher(query: str, params: Optional[Dict] = None) -> List[Dict]:
    """Execute Cypher against the configured Neo4j and return rows as dicts."""
    from neo4j import GraphDatabase
    neo4j_uri = getattr(Config, "NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = getattr(Config, "NEO4J_USER", "neo4j")
    neo4j_password = getattr(Config, "NEO4J_PASSWORD", "neo4j")
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    try:
        with driver.session() as session:
            result = session.run(query, **(params or {}))
            return [r.data() for r in result]
    finally:
        driver.close()