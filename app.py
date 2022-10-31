from importlib.resources import path
import os
from flask import Flask, render_template, request, redirect, session
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory

app = Flask(__name__)

app.secret_key='YOUR_SECRET_KEY'

mysql=MySQL()

    app.config['MYSQL_DATABASE_HOST'] = 'YOUR_HOST_NAME'
app.config['MYSQL_DATABASE_USER'] = 'YOUR_USER_NAME'
app.config['MYSQL_DATABASE_PASSWORD'] = 'YOUR_DATABASE_PASSWORD'
app.config['MYSQL_DATABASE_DB'] = 'YUOR_DATABASE_NAME'
mysql.init_app(app)


@app.route('/')
def inicio():
    return render_template('sitio/index.html')

@app.route('/img/<imagen>')
def imagenes(imagen):
    return send_from_directory(os.path.join('templates/sitio/img'),imagen)

@app.route('/libros')
def libros():

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute('SELECT * FROM `libros`')
    lista_libros = cursor.fetchall()
    conexion.commit()

    return render_template('sitio/libros.html', libros=lista_libros)

@app.route('/about')
def about():
    return render_template('sitio/about.html')

@app.route('/admin/')
def admin_index():
    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _usuario = request.form['txtUsuario']
    _password = request.form['txtPassword']

    print(_usuario)
    print(_password)

    if _usuario=="admin" and _password=="123":
        session["login"]=True
        session["usuario"]="Administrador"
        return redirect("/admin")

    return render_template('admin/login.html')

@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect('/admin/login')

@app.route('/admin/libros')
def admin_libros():
    
    if not 'login' in session:
        return redirect('/admin/login')

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute('SELECT * FROM `libros`')
    lista_libros = cursor.fetchall()
    conexion.commit()
    
    return render_template('admin/libros.html', libros=lista_libros)

@app.route('/admin/libros/guardar', methods=['POST'])
def admin_libros_guardar():

    if not 'login' in session:
        return redirect('/admin/login')

    _nombre = request.form['txtNombre']
    _url =request.form['txtURL']
    _imagen = request.files['txtImagen']

    tiempo = datetime.now()
    horaActual = tiempo.strftime('%Y%H%M%S')

    if _imagen.filename!="":
        nuevoNombre = horaActual+'_'+_imagen.filename
        _imagen.save('templates/sitio/img/'+nuevoNombre)

    sql="INSERT INTO `libros` (`id`, `nombre`, `imagen`, `url`) VALUES (NULL,%s,%s,%s);"
    datos=(_nombre,nuevoNombre,_url)

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()

    return redirect('/admin/libros')

@app.route('/admin/libros/borrar', methods=['POST'])
def admin_libros_borrar():

    if not 'login' in session:
        return redirect('/admin/login')
        
    _id=request.form['txtID']

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute('SELECT imagen FROM `libros` WHERE id=%s', (_id))
    lista_libros = cursor.fetchall()
    conexion.commit()

    if os.path.exists('templates/sitio/img/'+str(lista_libros[0][0])):
        os.unlink('templates/sitio/img/'+str(lista_libros[0][0]))

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute('DELETE FROM `libros` WHERE id=%s', (_id))
    conexion.commit()

    return redirect('/admin/libros')


if __name__ == '__main__':
    app.run(debug=True)
