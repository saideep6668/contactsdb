from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_mysqldb import MySQL
import os
import uuid

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'saideep'

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'saideep1234'
app.config['MYSQL_DB'] = 'contacts_app'

mysql = MySQL(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def generate_filename(filename):
    extension = filename.rsplit('.', 1)[1]
    unique_filename = f'{uuid.uuid4()}.{extension}'
    return os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

@app.route('/')
def index():
        cur = mysql.connection.cursor()
        cur.execute("SELECT  id, first_name, last_name, email, mobile, profile_photo FROM contacts")
        contacts = [{'id': row[0], 'first_name': row[1], 'last_name': row[2], 'email': row[3],'mobile': row[4], 'image_url': row[5]} for row in cur.fetchall()]
        cur.close()

        return render_template('index.html', contacts=contacts)


@app.route('/search')
def search():
    search_query = request.args.get("q")

    if search_query:
        cur = mysql.connection.cursor()
        query = "SELECT  id, first_name, last_name, email, mobile, profile_photo FROM contacts WHERE first_name LIKE %s"
        cur.execute(query, ("%" + search_query + "%",))
        contacts = [{'id': row[0], 'first_name': row[1], 'last_name': row[2], 'email': row[3],'mobile': row[4], 'image_url': row[5]} for row in cur.fetchall()]
        cur.close()
        if contacts:
            return render_template('index.html', contacts=contacts)
        else:
             return render_template('loader.html')

    else:
        contacts = []
       


@app.route("/details/<int:id>")
def details(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM contacts WHERE id = %s", (id,))
    contacts = cur.fetchone()
    cur.close()
    # print(contacts)

    if contacts:
        return render_template("details.html", contacts=contacts)
    else:
        return render_template("error.html")



@app.route("/add", methods=["GET", "POST"])
def add_contact():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                filename = generate_filename(image.filename)
                image.save(filename)
                profile_photo = url_for('uploaded_file', filename=os.path.basename(filename))
            else:
                profile_photo = None
        else:
            profile_photo = None

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO contacts (first_name,last_name, email, mobile, profile_photo) VALUES (%s, %s, %s, %s, %s)",
            (first_name, last_name, email, mobile, profile_photo)
        )
        mysql.connection.commit()
        cur.close()

        return redirect(url_for("index"))
    return render_template("add.html")



@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_contact(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM contacts WHERE id = %s", (id,))
    contact = cur.fetchone()
    cur.close()

    if not contact:
        return render_template("error.html")

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        

        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE contacts SET first_name = %s, last_name= %s, email = %s, mobile = %s  WHERE id = %s",
            (first_name, last_name, email, mobile,  id)
        )
        mysql.connection.commit()
        cur.close()

        return redirect(url_for("index"))

    return render_template("edit.html", contact=contact)




@app.route("/delete/<int:id>")
def delete_contact(id):
    return render_template("confirm_delete.html", contact_id=id)

@app.route("/delete_confirm/<int:id>")
def delete_confirm_contact(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM contacts WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for("index"))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    app.run(debug=True)
