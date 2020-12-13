from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import  secure_filename
from algorithm import Algorithm

import os

UPLOAD_Folder = os.path.abspath('./uploads/')
ALLOWED_EXTENSIONS = set(["csv"])

#*
# @filename es el nombre del archivo
# *#
def allowed_file(filename):
    #comparamos en primer lugar si el nombre tiene un punto
    #luego con la funcion rsplit dividimos la cadena es 2
    #y seleccionamos la parte de la derecha del arreglo
    #luego verificamos si está en nuestro arreglo de extensiones
    #ejemplo nom_archivo.csv -> [nom_archivo, csv]
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)

#Inicializar Sesión
app.secret_key = 'mysecretkey'

#ruta para subir archivos
app.config["UPLOAD_FOLDER"] = UPLOAD_Folder

app.config["solucion"] = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_Model', methods=['POST'])
def generate_Model():
    if request.method == 'POST':
        if "filepath" not in request.files:
            flash('The form has no file part')
            return redirect(url_for('index'))

        file_ = request.files['filepath']
        if file_.filename=='':
            flash('No file selected')
            return redirect(url_for('index'))
        
        if file_ and allowed_file(file_.filename):
            #secure_filename evitará que la ruta del archivo ...
            filename = secure_filename(file_.filename)
            file_.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            criterio = request.form['criterio']
            seleccion = request.form['selectparents']

            #return redirect(url_for('get_file', filename=filename))
            name = app.config['UPLOAD_FOLDER'] + '/' + filename
            algoritmo = Algorithm(name, int(criterio), int(seleccion))
            solucion = algoritmo.execute()
            app.config['solucion'] = solucion.solucion

            algoritmo.escribirArchivo(solucion.solucion)

            flash("Modelo Generado Correctamente")
        else:
            flash('File extension no permited')
        
        return redirect(url_for('index'))

@app.route('/calc_Note', methods=['POST'])
def calc_Note():
    if request.method == 'POST':
        n1 = request.form['note1']
        n2 = request.form['note2']
        n3 = request.form['note3']
        n4 = request.form['note4']

        nc = int(n1)*app.config['solucion'][0] + int(n2)*app.config['solucion'][1] + int(n3)*app.config['solucion'][2] + int(n4)*app.config['solucion'][3]

        flash("Nota Calculada " +  str(nc))
        
        return redirect(url_for('index'))

#Ruta que me permite ver si se cargó correctamente el archivo
@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(port=5000, debug=True)