from flask import Flask,render_template,redirect,request,flash,url_for,session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'todolistkey'
db = SQLAlchemy(app)

class User (db.Model):
    id=db.Column(db.Integer,primary_key = True)
    userName = db.Column(db.String(150),unique=True,nullable=False)
    password = db.Column(db.String(150),nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean,default=False)
    due_date = db.Column(db.Date)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

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

@app.route('/dashboard',methods = ['GET','POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description','')
        due_date = request.form.get('due_date')
        due_date = datetime.strptime(due_date,'%Y-%m-%d') if due_date else None
        new_task = Task(name=name,description=description,due_date=due_date,user_id=user_id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('dashboard'))
    tasks = Task.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html',tasks=tasks)

@app.route('/complete/<int:task_id>',methods= ['POST'])
def complete(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != session['user_id'] :
        return "Unauthorized", 403
    task.completed = not task.completed
    db.session.commit()
    return redirect('/dashboard')

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != session['user_id'] :
        return "Unauthorized", 403
    db.session.delete(task)
    db.session.commit()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)