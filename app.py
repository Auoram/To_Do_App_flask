from flask import Flask,render_template,redirect,request,flash,url_for,session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'todolistkey'
db = SQLAlchemy(app)

class User (db.Model):
    id=db.Column(db.Integer,primary_key = True)
    userName = db.Column(db.String(150),unique=True,nullable=False)
    password = db.Column(db.String(150),nullable=False)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        userName = request.form['userName']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(userName=userName).first():
            flash("This username already exists !")
            return redirect(url_for('register'))
        new_user = User(userName=userName,password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Your account was created successfully ! Please login now.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        user=User.query.filter_by(userName=request.form['userName']).first()
        if user and check_password_hash(user.password,request.form['password']):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        flash('Incorrect username or password')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return f"welcome, user ID: {session['user_id']}"

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)