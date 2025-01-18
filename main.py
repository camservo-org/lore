import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from llama_index.core import (Document, StorageContext, VectorStoreIndex,
                              load_index_from_storage)
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.LoreManager import LoreManager
from app.NPC import NPC

load_dotenv()
PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# --- DATABASE SETUP ---
## TODO: Run migrations if database hasn't been used before.
## TODO: Allow for remote connections.
DATABASE_URL = "sqlite:///mud_game.db"  # Replace with PostgreSQL URL if needed
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


@app.route("/create_region", methods=["POST"])
def create_region():
    data = request.json
    description = data.get("description", "")
    manager = LoreManager("./storage", api_key=OPENAI_API_KEY)
    manager.create_region(description)
    return jsonify({})


@app.route("/query_lore", methods=["GET"])
def query_lore():
    ## TODO: Make this an actual query passed in.
    manager = LoreManager("./storage", api_key=OPENAI_API_KEY)
    response = manager.query_lore("Can you describe some of the regions?")
    print(type(response))
    return jsonify({"response": response})


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


if __name__ == "__main__":
    app.run(debug=True)
