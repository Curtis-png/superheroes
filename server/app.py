from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Heroes(Resource):
    def get(self):
        heroes = [hero.to_dict(only=('id', 'name', 'super_name')) for hero in Hero.query.all()]
        return heroes, 200

class HeroById(Resource):
    def get(self, id):
        hero = db.session.get(Hero, id)  
        if hero:
            return hero.to_dict(rules=('-hero_powers.hero',)), 200
        return {"error": "Hero not found"}, 404

class Powers(Resource):
    def get(self):
        powers = [power.to_dict(only=('id', 'name', 'description')) for power in Power.query.all()]
        return powers, 200

class PowerById(Resource):
    def get(self, id):
        power = db.session.get(Power, id)  
        if power:
            return power.to_dict(only=('id', 'name', 'description')), 200
        return {"error": "Power not found"}, 404

    def patch(self, id):
        power = db.session.get(Power, id) 
        if not power:
            return {"error": "Power not found"}, 404
        data = request.get_json()
        if 'description' in data:
            if len(data['description']) < 20:
                return {"errors": ["validation errors"]}, 400
            power.description = data['description']
            db.session.commit()
            return power.to_dict(only=('id', 'name', 'description')), 200
        return {"errors": ["validation errors"]}, 400

class HeroPowers(Resource):
    def post(self):
        data = request.get_json()
        required_fields = ['strength', 'hero_id', 'power_id']
        missing_fields = [field for field in required_fields if field not in data]

        # validate presence of required fields
        if missing_fields:
            return {"errors": [f"Missing field: {field}" for field in missing_fields]}, 400

        # validate 'strength' value
        if data['strength'] not in ['Strong', 'Weak', 'Average']:
            return {"errors": ["validation errors"]}, 400

        try:
            # Validate existence of Hero and Power
            hero = db.session.get(Hero, data['hero_id']) 
            power = db.session.get(Power, data['power_id'])  

            if not hero or not power:
                return {"errors": ["Invalid 'hero_id' or 'power_id'"]}, 400

            # creation of new HeroPower
            new_hero_power = HeroPower(
                strength=data['strength'],
                hero_id=data['hero_id'],
                power_id=data['power_id']
            )
            db.session.add(new_hero_power)
            db.session.commit()

            # serialize the new HeroPower along with related Hero and Power
            response_data = {
                'id': new_hero_power.id,
                'strength': new_hero_power.strength,
                'hero_id': new_hero_power.hero_id,
                'power_id': new_hero_power.power_id,
                'hero': hero.to_dict(rules=('-hero_powers.hero',)),
                'power': power.to_dict(rules=('-hero_powers.power',))
            }

            return response_data, 200 

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating HeroPower: {e}")
            return {"errors": ["validation errors"]}, 400

api.add_resource(Heroes, '/heroes')
api.add_resource(HeroById, '/heroes/<int:id>')
api.add_resource(Powers, '/powers')
api.add_resource(PowerById, '/powers/<int:id>')
api.add_resource(HeroPowers, '/hero_powers')

@app.route('/')
def index():
    return 'Code challenge'

if __name__ == '__main__':
    app.run(port=5555, debug=True)