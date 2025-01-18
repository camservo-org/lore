import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from llama_index.core import (
    Document,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.NPC import NPC

load_dotenv()
PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Initialize Flask app

app = Flask(__name__)

# --- DATABASE SETUP ---
DATABASE_URL = "sqlite:///mud_game.db"  # Replace with PostgreSQL URL if needed
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# --- VECTOR INDEX SETUP ---
PERSIST_DIR = "./storage"
if os.path.exists(PERSIST_DIR):
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    vector_index = load_index_from_storage(storage_context)
else:
    vector_index = VectorStoreIndex([])

# --- API ROUTES ---


@app.route("/generate_lore", methods=["POST"])
def generate_lore():
    print("TESTS")
    """Generate lore using ChatGPT and save it locally."""
    data = request.json
    prompt = data.get("prompt", "Describe a new region in the MUD world.")

    # Call ChatGPT (mocked here)
    lore = f"Generated lore for prompt: {prompt}"

    doc = Document(text=lore)

    vector_index.insert(doc)
    vector_index.storage_context.persist(persist_dir="./storage")

    return jsonify({"message": "Lore generated and saved.", "lore": lore})


@app.route("/query_lore", methods=["GET"])
def query_lore():
    """Query the vector index for lore."""
    query = "What regions exists and what can you tell me about them?"
    query_engine = vector_index.as_query_engine()
    response = query_engine.query(query)
    return jsonify({"query": query, "response": response.response})


@app.route("/add_npc", methods=["POST"])
def add_npc():
    """Add an NPC to the database."""
    data = request.json
    name = data.get("name")
    description = data.get("description", "")
    location = data.get("location", "")
    backstory = data.get("backstory", None)
    generate_backstory = data.get("generate_backstory", False)
    session = SessionLocal()
    try:
        npc = NPC(
            name=name,
            description=description,
            location=location,
            api_key=OPENAI_API_KEY,
            backstory=backstory,
            generate_backstory=generate_backstory,
        )
        session.add(npc)
        session.commit()
        return jsonify({f"message": "NPC {npc.name} added successfully."})
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()


@app.route("/get_npcs", methods=["GET"])
def get_npcs():
    """Retrieve all NPCs."""
    session = SessionLocal()
    npcs = session.query(NPC).all()
    return jsonify(
        {
            "npcs": [
                {
                    "id": npc.id,
                    "name": npc.name,
                    "description": npc.description,
                    "location": npc.location,
                    "backstory": npc.backstory,
                }
                for npc in npcs
            ]
        }
    )


# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    app.run(debug=True)
