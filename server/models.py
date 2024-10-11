from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # Relationship
    hero_powers = db.relationship('HeroPower', back_populates='hero', cascade='all, delete-orphan')
    powers = association_proxy('hero_powers', 'power')

    # Serialization rules so that we can serialize the related Heroes and Powers
    serialize_rules = ('-hero_powers.hero', '-powers.heroes')

    def __repr__(self):
        return f'<Hero {self.id}>'

class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # Relationship to HeroPower
    hero_powers = db.relationship('HeroPower', back_populates='power', cascade='all, delete-orphan')
    heroes = association_proxy('hero_powers', 'hero')

    # Serialization rules so that we can serialize the related Heroes
    serialize_rules = ('-hero_powers.power', '-heroes.powers')

    # Validation rules
    @validates('description')
    def validate_description(self, key, description):
        if not description or len(description) < 20:
            raise ValueError("Description must be present and at least 20 characters long.")
        return description

    def __repr__(self):
        return f'<Power {self.id}>'

class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # Relationships to Hero and Power
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'))

    hero = db.relationship('Hero', back_populates='hero_powers')
    power = db.relationship('Power', back_populates='hero_powers')

    # Serialization rules so that we can serialize the related Hero and Power
    serialize_rules = ('-hero.hero_powers', '-power.hero_powers')

    # Validation rules
    @validates('strength')
    def validate_strength(self, key, strength):
        valid_strengths = ['Strong', 'Weak', 'Average']
        if strength not in valid_strengths:
            raise ValueError("Strength must be one of: Strong, Weak, Average")
        return strength

    # custom __repr__ method
    def __repr__(self):
        return f'<HeroPower {self.id}>'