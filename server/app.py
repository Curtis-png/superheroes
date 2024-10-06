from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

# Set up the database connection
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Create the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return '<h1>Code Challenge</h1>'

# Define Resource classes
class HeroListResource(Resource):
    def get(self):
        heroes = Hero.query.all()
        return [hero.to_dict() for hero in heroes]

class HeroResource(Resource):
    def get(self, id):
        hero = db.session.get(Hero, id)
        if hero:
            return hero.to_dict()
        return {"error": "Hero not found"}, 404

class PowerListResource(Resource):
    def get(self):
        powers = Power.query.all()
        return [power.to_dict() for power in powers]

class PowerResource(Resource):
    def get(self, id):
        power = db.session.get(Power, id)
        if power:
            return power.to_dict()
        return {"error": "Power not found"}, 404

    def patch(self, id):
        power = db.session.get(Power, id)
        if not power:
            return {"error": "Power not found"}, 404

        data = request.get_json()
        description = data.get('description')

        if description is None:
            return {"errors": ["Description is required"]}, 400

        if len(description) < 20:
            return {"errors": ["Description must be at least 20 characters long"]}, 400

        power.description = description

        try:
            db.session.commit()
            return power.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 500

class HeroPowerResource(Resource):
    def post(self):
        data = request.get_json()
        strength = data.get('strength')
        hero_id = data.get('hero_id')
        power_id = data.get('power_id')

        if strength not in ['Strong', 'Weak', 'Average']:
            return {"errors": ["Strength must be one of 'Strong', 'Weak', 'Average'"]}, 400

        hero = db.session.get(Hero, hero_id)
        power = db.session.get(Power, power_id)

        if not hero:
            return {"errors": ["Hero not found"]}, 404
        if not power:
            return {"errors": ["Power not found"]}, 404

        try:
            new_hero_power = HeroPower(strength=strength, hero=hero, power=power)
            db.session.add(new_hero_power)
            db.session.commit()
            return new_hero_power.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 500

# Add routes to the API
api.add_resource(HeroListResource, '/heroes')
api.add_resource(HeroResource, '/heroes/<int:id>')
api.add_resource(PowerListResource, '/powers')
api.add_resource(PowerResource, '/powers/<int:id>')
api.add_resource(HeroPowerResource, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
