from flask import Flask, render_template,flash,url_for,redirect,request
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message

import os

UPLOAD_fOLDER='static/imagen/'
ALLOWEB_EXTENSIONS=set(['png','jpg','jpeg'])

app = Flask(__name__)

# Configuracion email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL']= False
app.config['MAIL_USERNAME'] = 'anfinalweb@gmail.com'
app.config['MAIL_PASSWORD'] = 'Amayadopta'

mail=Mail(app)




#Coneccion de la base de datos
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='anfinal'
mysql=MySQL(app)

app.config['UPLOAD_fOLDER']=UPLOAD_fOLDER

#configuraciones


#utilizado para el manejo de for e if en el html
app.secret_key='mysecretkey'

@app.route('/')
@app.route('/<string:perfil>')
def index(perfil='Perfil'):
	return render_template('menu.html' , perfil=perfil)

@app.route('/perfil')
@app.route('/perfil/<string:perfil>')
def perfil(perfil='Perfil'):
	return render_template('inicioSesion.html', perfil=perfil)

@app.route('/darEnAdopcion')
@app.route('/darEnAdopcion/<string:perfil>')
def darEnAdopcion(perfil='Perfil'):
	if perfil != 'Perfil':
			return render_template('DarEnAdopcion.html', perfil=perfil)
	else:
			return render_template('registrarse.html')

@app.route('/recuperara_Contraseña')
def recuperara_Contraseña():
	return render_template('recuperar_Contraseña.html')


@app.route('/envioContraseñaCorreo', methods=['POST'])
def envioContraseñaCorreo():
	if request.method=='POST':
		usuario=request.form['usuario']
		print(usuario)
		cur=mysql.connection.cursor()
		cur.execute('SELECT contraseña FROM usuarios WHERE email=%s',(usuario,))
		data=cur.fetchall()

		if len(data)==0:
			flash("No hay ningun usuario registrado")

		if len(data)==1:
			msg=Message('Recuperacion de Contraseña',
				recipients=[usuario],sender='anfinalweb@gmail.com')
			msg.html=render_template('email.html' , data=data[0][0])
			mail.send(msg)
			flash("Mira el correo se le envio su contraseña ")

	return render_template('inicioSesion.html')


@app.route('/adoptar')
@app.route('/adoptar/<string:perfil>')
def adoptar(perfil='Perfil'):
		if perfil != 'Perfil':
			cur=mysql.connection.cursor()
			cur.execute('SELECT * FROM mascotas WHERE 1')
			data=cur.fetchall()
			return render_template('adoptar.html', perfil=perfil ,mascotas=data)
		else:
			return render_template('registrarse.html')


@app.route('/formulario/<string:perfil>/<int:id>')
def formulario(perfil,id):

	cur=mysql.connection.cursor()
	cur.execute('SELECT * FROM mascotas WHERE id=%s',(id,))
	data=cur.fetchall()
	return render_template('FormularioAdopcion.html', perfil=perfil ,contact=data[0])

@app.route('/registro')
def registro():
	return render_template('registrarse.html', perfil="Perfil")


@app.route('/login', methods=['POST'])
def login():
	if request.method=='POST':
		usuario=request.form['usuario']
		contraseña=request.form['contraseña']
		cur=mysql.connection.cursor()
		cur.execute('SELECT nombre FROM usuarios WHERE contraseña=%s and email=%s',(contraseña,usuario))
		data=cur.fetchall()
		print(data)

	if len(data) == 1:
		flash("Sesion abierta satisfactoriamente")
		return redirect(url_for('index' , perfil=data[0]))

	if len(data) == 0:
		flash("Usuario o contraseña incorrectas ")
		return redirect(url_for('login'))

@app.route('/mascotas/<string:perfil>', methods=['POST'])
def mascotas(perfil):
	if request.method=='POST':
		cedula=request.form['cedula']
		contraseña=request.form['contraseña']
		cur=mysql.connection.cursor()
		cur.execute('SELECT nombre FROM usuarios WHERE contraseña=%s and cedula=%s and nombre=%s',(contraseña,cedula,perfil))
		data=cur.fetchall()

	if len(data) == 1:
		cur=mysql.connection.cursor()
		cur.execute('SELECT * FROM mascotas WHERE representante={0}'.format(cedula))
		data=cur.fetchall()
		return render_template('mostrarmascotas.html',contacts=data, perfil=perfil)

	if len(data) == 0:
		flash("Usuario o contraseña incorrectas ")
		return render_template('menu.html', perfil=perfil)

@app.route('/add_contact', methods=['POST'])
def add_contact():
	if request.method=='POST':
		nombres=request.form['nombres']
		apellidos=request.form['apellidos']
		direccion=request.form['direccion']
		cedula=request.form['cedula']
		email=request.form['email']
		telefono=request.form['telefono']
		contraseña=request.form['contraseña']
		cur=mysql.connection.cursor()
		cur.execute('INSERT INTO usuarios(nombre,apellido,direccion,email,telefono,contraseña,cedula) VALUES (%s,%s,%s,%s,%s,%s,%s)',(nombres,apellidos,direccion,email,telefono,contraseña,cedula))
		mysql.connection.commit()
		flash("Registro completado")
	return redirect(url_for('index', perfil=nombres))

@app.route('/solicitud/<int:id>', methods=['POST'])
def solicitud(id):
	if request.method=='POST':
		nombres=request.form['nombres']
		apellidos=request.form['apellidos']
		direccion=request.form['direccion']
		email=request.form['email']
		telefono=request.form['telefono']
		razon=request.form['razon']
		persona=[nombres,apellidos,direccion,email,telefono,razon]
		cur=mysql.connection.cursor()
		cur.execute('SELECT * FROM mascotas WHERE id={0}'.format(id))
		data=cur.fetchall()

		msg=Message('Recuperacion de Contraseña',
				recipients=['idaga30@hotmail.com'],sender='anfinalweb@gmail.com')
		msg.html=render_template('emailAdopcion.html' , data=data[0], persona=persona)
		mail.send(msg)
		flash("Registro completado")
	return redirect(url_for('index', perfil=nombres))



@app.route('/add_mascota/<string:perfil>', methods=['POST'])
def add_mascota(perfil):
	if request.method=='POST':

		file=request.files['archivo']
		imagen=secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_fOLDER'],imagen))
		
		nombre=request.form['nombre']
		vacunas=request.form['vacunas']
		edad=request.form['edad']
		genero=request.form['genero']
		raza=request.form['raza']
		representante=request.form['representante']
		direccion=request.form['direccion']
		descripcion=request.form['descripcion']
		telefono=request.form['telefono']
		cur=mysql.connection.cursor()
		cur.execute('INSERT INTO mascotas(nombre,genero,edad,vacunas,telefono,raza,direccion,descripcion,imagen,representante) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(nombre,genero,edad,vacunas,telefono,raza,direccion,descripcion,imagen,representante))
		mysql.connection.commit()
		flash("Registro de mascota completado")

	return redirect(url_for('index', perfil=perfil))



if __name__=='__main__':
	app.run(debug=True)