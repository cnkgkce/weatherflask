from enum import unique
from logging import debug
from flask import Flask,url_for,render_template,request,session,flash
from werkzeug.utils import redirect
import requests
from flask_wtf import FlaskForm
from wtforms import StringField,validators
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from functools import wraps


app = Flask(__name__,static_folder="static",template_folder="templates")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

#config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/cenkg/OneDrive/Masaüstü/weatherapp/weather.db'

db = SQLAlchemy(app)


API_KEY = "<SECRET>"

BASE_API_URL = "https://api.openweathermap.org/data/2.5/weather?q=" #Bu sabit 


def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if "username" in session:
            return f(*args,**kwargs)
        else:
            redirect(url_for("login"))
    return decorated_function


@app.route("/")
def home():
    form = SearchForm(request.form)
    if "username" in session:
            
        return render_template("index.html",form=form)

    return redirect(url_for("login"))



@app.route("/search",methods=["POST","GET"])
def search():
    if request.method == "POST":
            
        form = SearchForm(request.form)  #formdan veri almıyor dolayısıyla aşağıda nonetype geliyor 
        if form.validate:
            city = str(form.name.data)
            extension = BASE_API_URL+city+"&appid="+API_KEY
            response = requests.get(extension)
            if response.ok:
                resp_data = response.json() #Elimizde json datası var
                Main = resp_data["main"]
                temp = Main["temp"]
                pressure = Main["pressure"]
                name = resp_data["name"]

                return render_template("result.html",temp=temp,pressure=pressure,name=name,form=form)

            else:
                return redirect(url_for("home"))
        else:
            return redirect(url_for("home"))

    else:
        return redirect(url_for("home"))




@app.route("/login",methods=["POST","GET"])
def login():
    form = LoginForm(request.form)
    if request.method == "GET":
        return render_template("login.html",form=form)
    else:
        username = form.username.data
        password  = form.password.data
        user = User.query.filter_by(username=username).first()
        if user.password == password:
            session["username"] = username
            flash("Welcome","success")
            return redirect(url_for("home"))
    
    flash("Invalid username or password","error")
    return redirect(url_for("login"))



@app.route("/register",methods=["POST","GET"])
def register():
    form = RegisterForm(request.form)
    if request.method == "GET":
        return render_template("register.html",form=form)
    else:
        username = form.username.data
        password = form.password.data

        user = User(username=username,password=password)
        db.session.add(user)
        db.session.commit()

    return redirect(url_for("login"))




@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

class SearchForm(FlaskForm):
    name = StringField("Aratmak istediğiniz şehiri yazınız",validators=[DataRequired("Veri giriniz")])

#Login-Register ile kullanıcı kayıt işlemi yap & sqlite kullan 

class LoginForm(FlaskForm):
    username = StringField("Kullanıcı Adı",[validators.Length(min=3)])
    password = PasswordField("Parola",[validators.Length(min=6)])


class RegisterForm(FlaskForm):
    username = StringField("Kullanıcı Adı",[validators.Length(min=3,max=10)])
    password = PasswordField("Parola",[validators.Length(min=6,max=20)])



class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(80),unique=True,nullable=False)
    password = db.Column(db.String(10),nullable=False)



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
