from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from flask_sqlalchemy import  SQLAlchemy
from sqlalchemy.orm import relationship
from flask import Flask, redirect, render_template, request
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()

app = Flask(__name__)
#lo tenia con os.getenv("DATABASE_URL") pero no me funcionó xd
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://happytails_a803_user:1T65MjFgdAoHkm13SfzsYiMPUfEa2t6d@dpg-clkbg76g1b2c73e8gtq0-a.oregon-postgres.render.com/happytails_a803"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


class Species(db.Model):
    __tablename__ = 'species'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    breeds = relationship('Breed', back_populates='species')

    def __str__(self) -> str:
        return f"Species(id={self.id}, name={self.name})"

class Breed(db.Model):
    __tablename__ = 'breeds'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    species_id = Column(Integer, ForeignKey('species.id'))
    species = relationship('Species', back_populates='breeds')

    def __str__(self) -> str:
        return f"Breed(id={self.id}, name={self.name}, species_id={self.species_id})"


cat_species = Species(name="Cat")
dog_species = Species(name="Dog")

cat_breeds = [
        Breed(name="Persian", species=cat_species),
        Breed(name="Siamese", species=cat_species),
        Breed(name="Maine Coon", species=cat_species),
        Breed(name="Ragdoll", species=cat_species),
        Breed(name="Bengal", species=cat_species),
        Breed(name="Sphynx", species=cat_species),
        Breed(name="British Shorthair", species=cat_species),
        Breed(name="Scottish Fold", species=cat_species),
        Breed(name="Abyssinian", species=cat_species),
        Breed(name="Russian Blue", species=cat_species),
        Breed(name="Birman", species=cat_species),
        Breed(name="Norwegian Forest", species=cat_species),
    ]

dog_breeds = [
        Breed(name="Labrador Retriever", species=dog_species),
        Breed(name="German Shepherd", species=dog_species),
        Breed(name="Golden Retriever", species=dog_species),
        Breed(name="Beagle", species=dog_species),
        Breed(name="Dachshund", species=dog_species),
        Breed(name="Bulldog", species=dog_species),
        Breed(name="Poodle", species=dog_species),
        Breed(name="Boxer", species=dog_species),
        Breed(name="Chihuahua", species=dog_species),
        Breed(name="Pomeranian", species=dog_species),
        Breed(name="Shih Tzu", species=dog_species),
        Breed(name="Husky", species=dog_species),
        
    ]

def main():
    db.session.add(cat_species)
    db.session.add(dog_species)
    
    db.session.commit()
    # Add data to the database
    for dog in dog_breeds:
        db.session.add(dog)

    for cat in cat_breeds:
        db.session.add(cat)

    # Commit the changes
    db.session.commit()



if __name__ == "__main__":
    with app.app_context():
        main()