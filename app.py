from threading import local
from tkinter import messagebox
from turtle import delay
from wsgiref.validate import InputWrapper
from flask import Flask, redirect, render_template, request,url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import  InputRequired, length
import mysql.connector as sql_db
import MySQLdb as sql_db 

db = sql_db.connect(host="127.0.0.1", port=3306, user="root", passwd="root",db="pagina_web")


app = Flask(__name__)
app.config['SECRET_KEY'] = 'root'

#AQUI PREPARÉ LA PARTE INICIAL
#---------------------------------------------------------
@app.route("/")
def index():
    return render_template ("index.html")

@app.route("/contactos")
def contactos():
    return render_template ("contactos.html")

#AQUI PREPARÉ EL LOGIN
#---------------------------------------------------------
@app.route("/login", methods= ['GET','POST'])
def login():
    
    if 'loggedin' in session:
        
        return redirect(url_for('dashboard'))

    return render_template ("login.html")

@app.route("/user_login",methods= ['GET','POST'])
def user_login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        db_user_login = sql_db.connect(host="127.0.0.1", port=3306, user="root", passwd="root",db="pagina_web")
        cursor_user_login =db_user_login.cursor(sql_db.cursors.DictCursor)
        cursor_user_login.execute("SELECT * FROM usuarios WHERE username=%s and password=%s", (username,password))
        cuenta = cursor_user_login.fetchone()
    if cuenta:
        session['loggedin'] = True
        session['id'] = cuenta['id']
        session['username'] = cuenta['username']
        return render_template('index.html')
    
    else:
        db_user_login.commit()
        db_user_login.close()
    
        return render_template('login.html')

#AQUI PREPARÉ EL REGISTRO
#---------------------------------------------------------
@app.route("/registrar")
def registrar():
    if 'loggedin' in session:
        
        return render_template('registrar.html', username=session['username'])

    return redirect(url_for('login'))

@app.route("/user_done",methods= ['POST'])
def user_done():
    if request.method == "POST":
        username=request.form['usuario_txt']
        nombre=request.form['nombre_txt']
        apellido=request.form['apellido_txt']
        correo=request.form['correo_txt']
        password=request.form['clave_txt']
    db_user_done = sql_db.connect(host="127.0.0.1", port=3306, user="root", passwd="root",db="pagina_web")
    cursor_user_done =db_user_done.cursor(sql_db.cursors.DictCursor)
    cursor_user_done.execute("SELECT * FROM usuarios WHERE username=%s", (username))
    info_registro = cursor_user_done.fetchone()
    if info_registro is not None:
        return "ERROR: ESTE USUARIO YA EXISTE!!!... REDIRECCIONANDO AUTOMATICAMENTE" ,  {"Refresh": "2; url=/registrar"} 
    
    elif info_registro is None:
        cursor_user_done.execute ("INSERT INTO usuarios(username,nombre,apellido,password,correo) VALUES (%s,%s,%s,%s,%s)",(username,nombre,apellido,password,correo))    
    db_user_done.commit()
    db_user_done.close()
    return "USUARIO REGISTRADO CORRECTAMENTE!!!... REDIRECCIONANDO AUTOMATICAMENTE",  {"Refresh": "2; url=/dashboard"} 


#AQUI PREPARÉ EL DASHBOARD Y EL LOGOUT
#---------------------------------------------------------
@app.route("/dashboard")
def dashboard():
    if 'loggedin' in session:
        
        return render_template('dashboard.html', username=session['username'])

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login')) 


#AQUI PREPARÉ EL REGISTRO DE ENTRADA Y SALIDA DE PRODUCTOS
#---------------------------------------------------------
@app.route("/registro_entrada")
def reg_entrada():
    return render_template ("registro_entrada.html")

@app.route("/registro_salida")
def reg_salida():
    return render_template ("registro_salida.html")


@app.route('/almacen', methods= ["GET", "POST"])
def almacen():
    
    cursor =db.cursor(sql_db.cursors.DictCursor)
    if request.method=="POST" and 'text_buscar' in request.form:
        sql = "SELECT * FROM productos where nombre_pro like '%" + request.form['text_buscar'] + "%'"
    
    else:
        sql = "SELECT * FROM productos"
    cursor.execute(sql)
    db.commit()
    pro_almacen = cursor.fetchall()
    return render_template ("almacen.html",pro_almacenes = pro_almacen)
    


if __name__=="__main__":
    app.run(debug=True)