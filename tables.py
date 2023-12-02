from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from flask_sqlalchemy import  SQLAlchemy
from flask import Flask
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://happytails_a803_user:1T65MjFgdAoHkm13SfzsYiMPUfEa2t6d@dpg-clkbg76g1b2c73e8gtq0-a.oregon-postgres.render.com/happytails_a803"
db = SQLAlchemy(app)


class City(db.Model):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    locations = relationship('Location', back_populates='city')

    def __str__(self) -> str:
        return f"City(id={self.id}, name={self.name})"

class Country(db.Model):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    locations = relationship('Location', back_populates='country')

    def __str__(self) -> str:
        return f"Country(id={self.id}, name={self.name})"

class Species(db.Model):
    __tablename__ = 'species'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    breeds = relationship('Breed', back_populates='species')
    pets = relationship('Pet', back_populates='species')

    def __str__(self) -> str:
        return f"Species(id={self.id}, name={self.name})"

class Breed(db.Model):
    __tablename__ = 'breeds'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    species_id = Column(Integer, ForeignKey('species.id'))
    species = relationship('Species', back_populates='breeds')
    pets = relationship('Pet', back_populates='breed')

    def __str__(self) -> str:
        return f"Breed(id={self.id}, name={self.name}, species_id={self.species_id})"

class Location(db.Model):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    city_id = Column(Integer, ForeignKey('cities.id'))
    country_id = Column(Integer, ForeignKey('countries.id'))
    city = relationship('City', back_populates='locations')
    country = relationship('Country', back_populates='locations')
    pets = relationship('Pet', back_populates='location')

    def __str__(self) -> str:
        return f"Location(id={self.id}, name={self.name}, latitude={self.latitude}, longitude={self.longitude}, city_id={self.city_id}, country_id={self.country_id})"

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)  # Make email unique
    username = Column(String, unique=True, nullable=False)  # Make username unique
    password = Column(String, nullable=False)
    description = Column(String)
    pets = relationship('Pet', back_populates='user')
    links = relationship('UserLink', back_populates='user')
    
    def __str__(self) -> str:
        return f"User(id={self.id}, email={self.email}, username={self.username}, password={self.password}, description={self.description})"


class Pet(db.Model):
    __tablename__ = 'pets'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    species_id = Column(Integer, ForeignKey('species.id'))
    breed_id = Column(Integer, ForeignKey('breeds.id'))
    age = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    ip = Column(String)
    user = relationship('User', back_populates='pets')
    location = relationship('Location', back_populates='pets')
    species = relationship('Species', back_populates='pets')
    breed = relationship('Breed', back_populates='pets')
    environmental_measurements = relationship('EnvironmentalMeasurement', back_populates='pet')
    stored_food_amounts = relationship('StoredFoodAmount', back_populates='pet')
    food_in_bowls = relationship('FoodInBowl', back_populates='pet')
    alerts = relationship('Alert', back_populates='pet')
    cameras = relationship('Camera', back_populates='pet')

    def __str__(self) -> str:
        return f"Pet(id={self.id}, name={self.name}, species_id={self.species_id}, breed_id={self.breed_id}, age={self.age}, user_id={self.user_id}, location_id={self.location_id}, ip={self.ip})"

class EnvironmentalMeasurement(db.Model):
    __tablename__ = 'environmental_measurements'
    id = Column(Integer, primary_key=True)
    temperature = Column(Float)
    humidity = Column(Float)
    thermal_sensation = Column(Float)
    date_time = Column(String)
    pet_id = Column(Integer, ForeignKey('pets.id'))
    pet = relationship('Pet', back_populates='environmental_measurements')

    def __str__(self) -> str:
        return f"EnvironmentalMeasurement(id={self.id}, temperature={self.temperature}, humidity={self.humidity}, thermal_sensation={self.thermal_sensation}, date_time={self.date_time}, pet_id={self.pet_id})"

class StoredFoodAmount(db.Model):
    __tablename__ = 'stored_food_amounts'
    id = Column(Integer, primary_key=True)
    food_amount = Column(Float)
    date_time = Column(String)
    pet_id = Column(Integer, ForeignKey('pets.id'))
    pet = relationship('Pet', back_populates='stored_food_amounts')

    def __str__(self) -> str:
        return f"StoredFoodAmount(id={self.id}, food_amount={self.food_amount}, date_time={self.date_time}, pet_id={self.pet_id})"

class FoodInBowl(db.Model):
    __tablename__ = 'food_in_bowls'
    id = Column(Integer, primary_key=True)
    food_in_bowl = Column(Boolean)
    date_time = Column(String)
    pet_id = Column(Integer, ForeignKey('pets.id'))
    pet = relationship('Pet', back_populates='food_in_bowls')
    

    def __str__(self) -> str:
        return f"FoodInBowl(id={self.id}, food_in_bowl={self.food_in_bowl}, date_time={self.date_time}, pet_id={self.pet_id})"

class Alert(db.Model):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True)
    mechanical_failure = Column(Boolean)
    no_food_in_storage = Column(Boolean)
    date_time = Column(String)
    pet_id = Column(Integer, ForeignKey('pets.id'))
    pet = relationship('Pet', back_populates='alerts')

    def __str__(self) -> str:
        return f"Alert(id={self.id}, mechanical_failure={self.mechanical_failure}, no_food_in_storage={self.no_food_in_storage}, date_time={self.date_time}, pet_id={self.pet_id})"

class Camera(db.Model):
    __tablename__ = 'cameras'
    id = Column(Integer, primary_key=True)
    image_url = Column(String)
    pet_id = Column(Integer, ForeignKey('pets.id'))
    pet = relationship('Pet', back_populates='cameras')
    

    def __str__(self) -> str:
        return f"Camera(id={self.id}, image_url={self.image_url}, pet_id={self.pet_id})"

class UserLink(db.Model):
    __tablename__ = 'user_links'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    profile_picture = Column(String)  # Puedes almacenar la ruta o nombre del archivo de la imagen
    twitter_link = Column(String)
    facebook_link = Column(String)

    user = relationship('User', back_populates='links')
    
    def __str__(self):
        return f"UserLink(id={self.id}, user_id={self.user_id}, profile_picture={self.profile_picture}, twitter_link={self.twitter_link}, facebook_link={self.facebook_link})"