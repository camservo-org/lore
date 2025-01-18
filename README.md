# lore
Not much to this yet.  The idea is that I'd like to use a SQL DB for storing objects with specific details (HP, equipment, etc..) and llama index for more esoteric things like lore and history about the realm.

If anyone is interested in helping me, or setting me straight about how to work on this, please feel free to reach out to me at camservo@gmail.com

## Getting set up
### Set up your venv
1. Set up venv: `python -m venv venv`
2. Activate your venv `source venv/bin/activate`
3. Install requirements `pip install -r requirements.txt`

### Seed the DB
1. Install alembic `pip install alembic`
2. Run migrations `alembic upgrade head`

## API Endpoints
- Create Regions: `curl -X POST http://127.0.0.1:5000/create_region -H "Content-Type: application/json" -d '{"description": "Describe a new region in a fantasy world.  Make it be themed high fantasy.  Somewhat tolkienish.  Be creative."}''`
- Create NPC: `curl -X POST http://127.0.0.1:5000/add_npc -H "Content-Type: application/json" -d '{"description": "The local merchant.  Hes kinda weird and shady.", "location": "Mystic Tower", "generate_backstory": true}'`
- Query NPC: `curl -X GET http://127.0.0.1:5000/get_npcs`
- Query realm lore: `curl -X GET "http://127.0.0.1:5000/query_lore?query=what%20regions%20are%20there"`