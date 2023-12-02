import os 
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from tables import *
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
#lo tenia con os.getenv("DATABASE_URL") pero no me funcionó xd
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://happytails_a803_user:1T65MjFgdAoHkm13SfzsYiMPUfEa2t6d@dpg-clkbg76g1b2c73e8gtq0-a.oregon-postgres.render.com/happytails_a803"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def main():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        main()