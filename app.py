from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
from flask_socketio import SocketIO, send, emit
from flask_mail import Mail, Message
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash
from colorama import Fore, Style
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from serial import Serial, SerialException
from serial.tools.list_ports import comports
from flask_uploads import UploadSet, configure_uploads, IMAGES
import threading
import schedule
import time
import json
import sys  
import os

from helpers import login_required, is_email,bytes_to_dict, tiempo_a_segundos

from models_form import DispenserForm, LoginForm, RegissterForm, UserLinksForm
from tables import db, City, Country, Species, Location, Pet, User, Breed, Location, User, Pet,EnvironmentalMeasurement, StoredFoodAmount, FoodInBowl, Alert, Camera, UserLink
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24);
socketio = SocketIO(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv("GMAIL")
app.config['MAIL_PASSWORD'] = os.getenv("PASS_WORD")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/uploads/profile_pictures'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://happytails_a803_user:1T65MjFgdAoHkm13SfzsYiMPUfEa2t6d@dpg-clkbg76g1b2c73e8gtq0-a.oregon-postgres.render.com/happytails_a803"
db.init_app(app)
csrf = CSRFProtect(app)

arduino = None
background_task_running = False

@app.route('/home')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    csrf.protect() 
    session.clear()
    
    form = LoginForm()
     
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        query = text("SELECT * FROM users WHERE username = :username or email = :username")
        
        if not username:
            return render_template("login.html", error="Username is required")
        if not password:
            return render_template("login.html", error="Password is required")
        
        if db.session.execute(query, {"username": username}).rowcount == 0:
            return render_template("login.html", error="Username does not exist")
        
        user = db.session.execute(query, {"username": username}).fetchone()
        
        if  not check_password_hash(user.password, password):
            return render_template("login.html", error="Incorrect password")
        
        session["user_id"] = user.id
        session["username"] = user.username
        return redirect("/dashboard")
    else:
        return render_template("login.html", form=form)
                
    

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegissterForm()
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirm_password")
        email = request.form.get("mail")
        
        if not username or len(username) < 3:
            return render_template("register.html", error="Invalid username \n The username cannot be longer than 20 characters, and cannot contain any symbols. ")
        if not password or not confirmation:
            return render_template("register.html", error="Password is required")
        if password != confirmation:
            return render_template("register.html", error="Passwords do not match")
        if not email:
            return render_template("register.html", error="Email is required")
        if not is_email(email):
            return render_template("register.html", error="Invalid email")
        if len(password) < 4:
            return render_template("register.html", error="Password must be at least 8 characters long")
        
        user_exist = text("SELECT * FROM users WHERE username = :username")
        if db.session.execute( user_exist, {"username": username}).rowcount != 0: 
            return render_template("register.html", error="Username already exists")
        
        query = text("INSERT INTO users (username, password, email) VALUES (:username, :password, :email)") 
        db.session.execute(query, {"username": username, "password": generate_password_hash(password), "email": email})
        db.session.commit()
        
        msg = Message("Welcome to Happy Tails", sender="dknauth@code-fu.net.ni", recipients=[email])
        message = f'Welcome to Happy Tails, {username}! \n Estamos encantados de darte la bienvenida a nuestra comunidad amente de los animales.'
        msg.body = message
        
        try:
            mail.send(msg)
            print(Fore.GREEN + "Email sent" + Style.RESET_ALL)
        except Exception as e:
            print(e)
            return render_template("register.html", error="Error sending welcome email")
            
        if request.form.get("autologin") is not None:
            query = text("SELECT * FROM users WHERE username = :username")
            user = db.session.execute(query, {"username": username}).fetchone()
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect("/")
        else:
            return redirect('/login')
    else:
        return render_template('register.html', form=form)
    

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route("/stream")
@login_required
def stream():
    return render_template('stream.html')

@app.route("/user/<string:username>")
def user(username):
    if request.method == "GET":
        form = DispenserForm()
        
        form.city.choices = [(city.id, city.name) for city in City.query.all()]
        form.country.choices = [(country.id, country.name) for country in Country.query.all()]
        form.breed.choices = [(breed.id, breed.name) for breed in Breed.query.all()]
        form.species.choices = [(species.id, species.name) for species in Species.query.all()]
        
        query = text("SELECT * FROM user_links WHERE user_id = :user")
        links = db.session.execute(query, {"user": session["user_id"]}).fetchone()
        
        pets = [ (pet.name, pet.age, pet.location_id, pet.breed_id) for pet in Pet.query.filter_by(user_id=session["user_id"]).all()] 
        
        location = []
        i = []
        
        for pet in pets:
            i.append((Location.query.filter_by(id=pet[2]).first()))     
            location.append(i[0].name)  
            print(location)
        
        query = text("SELECT * FROM users WHERE username = :user")
        user = db.session.execute(query, {"user": username}).fetchone()
        if user is None:
            return redirect("/")
        return render_template("user.html", form=form, user=user, links=links, pets=pets, location=location)
   

@app.route('/submit_dispenser', methods=['POST'])
def submit_dispenser():
    form = DispenserForm()
    
    form.city.choices = [(city.id, city.name) for city in City.query.all()]
    form.country.choices = [(country.id, country.name) for country in Country.query.all()]
    form.breed.choices = [(breed.id, breed.name) for breed in Breed.query.all()]
    form.species.choices = [(species.id, species.name) for species in Species.query.all()]

    if form.validate_on_submit():
        # Obtener los datos del formulario
        name = form.name.data
        age = form.age.data
        species_id = form.species.data
        breed_id = form.breed.data
        location_name = form.location_name.data
        latitude = form.latitude.data
        longitude = form.longitude.data
        city_id = form.city.data
        country_id = form.country.data
        code = form.code.data

        species = Species.query.get(species_id)
        breed = Breed.query.get(breed_id)
        city = City.query.get(city_id)
        country = Country.query.get(country_id)

        location = Location(
            name=location_name,
            latitude=latitude,
            longitude=longitude,
            city=city,
            country=country
        )

        user = User.query.filter_by(username=f'{session["username"]}').first()  

        pet = Pet(
            name=name,
            age=age,
            species=species,
            breed=breed,
            location=location,
            user=user,
            ip=code
        )

        db.session.add(location)
        print(location)
        db.session.add(pet)
        print(pet)
        db.session.commit()
        
    else: 
        print(form.errors)

    return redirect(f'/user/{session["username"]}')
    
    
    
@app.route('/settings')
@login_required
def settings():
    form = UserLinksForm()
    
    return render_template('settings.html', form=form)

@app.route('/submit_links', methods=['POST'])
def submit_links():
    form = UserLinksForm()
    
    if form.validate_on_submit():   
        user_link = UserLink.query.filter_by(user_id=session["user_id"]).first()
        
        filename_base = secure_filename(form.profile_picture.data.filename) if form.profile_picture.data else None

        if user_link:
            user_link.profile_picture = filename_base
            user_link.twitter_link = form.twitter_link.data
            user_link.facebook_link = form.facebook_link.data
        else:
            user_link = UserLink(
                user_id= session["user_id"],
                profile_picture= filename_base,
                twitter_link=form.twitter_link.data,
                facebook_link=form.facebook_link.data
            )
            db.session.add(user_link)

        db.session.commit()
        
        if form.profile_picture.data:
            filename_base = secure_filename(form.profile_picture.data.filename)
            _, file_extension = os.path.splitext(filename_base)
            form.profile_picture.data.filename = "user" + f"{session['user_id']}" + f"{file_extension}"
            filename = photos.save(form.profile_picture.data)
            user_link.profile_picture = filename
            db.session.commit()
        else:
            print("Invalid file extension")
        
    return redirect('/settings')



@socketio.on('contact')
def handle_form_contact(data):
    print(data)
    body = f"{data['name']} queire contactarse contigo, dice: {data['msg']}"
    send_mail(os.getenv("GMAIL"), f"Happy Tails contact from:  {data['name']}!", body)
    
    emit('contact', {'status': 'Send mail'})

@socketio.on('start_background_task')
def start_background_task():
    global background_task_running
    if not background_task_running:
        background_task_running = True
        socketio.start_background_task(target=read_serial_data)  

@socketio.on('stop_background_task')
def stop_background_task():
    global background_task_running
    background_task_running = False    
    
    
def send_mail(reciver, title, body):
    msg = Message(title, sender='dknauth@code-fu.net.ni', recipients=[reciver])
    msg.body = body
    
    try:
        mail.send(msg)
        print(Fore.GREEN + "Email sent" + Style.RESET_ALL)
    except Exception as e:
        print(e)
        
        
def connect_to_arduino():
    global arduino
    try:
        arduino = Serial('COM5', 9600, timeout=2)
        time.sleep(2)
        print('Connection to Arduino successful')
    except SerialException as e:
        print(f"Failed to connect to Arduino: {e}")

def close_arduino_connection():
    global arduino
    if arduino and arduino.is_open:
        arduino.close()
        print('Connection to Arduino closed')

def read_serial_data():
    global arduino
    
    if not arduino or not arduino.is_open:
        print('Arduino not connected. Exiting read_serial_data.')
        return

    print(f'Connection to serial port {arduino.port} is opened')

    while background_task_running:
        data = arduino.readline().decode('utf-8').strip()
        try:
            if len(data) == 0:
                print("Data none")
                msg = {"status": "error", "message": "No device connected"}
                socketio.emit('disconnect', msg)
            else:
                print(data)
                data_json = json.loads(data)
                data_json['time'] = tiempo_a_segundos(data_json['time'])
                socketio.emit('show_data', data_json)
                    
        except ValueError:
            msg = {"status": "error", "message": "Invalid data received"}
            socketio.emit('disconnect', msg)
            print(f'Invalid data received: {msg}')

        
def job():
    global arduino
    action = "food\n"
    print(Fore.GREEN + f"{action}" + Style.RESET_ALL)
    
    try: 
        if arduino and arduino.is_open:
            arduino.write(action.encode())
            print(Fore.GREEN + f"Send action {action}" + Style.RESET_ALL)
    except SerialException as e:
        print(Fore.RED + f"Serial port error: {e}" + Style.RESET_ALL) 
        
     
def schedule_jobs():
    schedule.every().day.at("09:15").do(job)
    schedule.every().day.at("09:16").do(job)
    schedule.every().day.at("09:17").do(job)
        
if __name__ == '__main__':
    sys.stdout = sys.__stdout__
    
    connect_to_arduino()
    
    try:
        socketio.run(app, debug=True, host='0.0.0.0', port=8000)
    finally:
        close_arduino_connection()