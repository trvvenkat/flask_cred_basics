from flask import Flask, render_template, url_for, flash, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager, login_user, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = "this_is_a_secret_key"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ex.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@localhost/ex'
db = SQLAlchemy(app)



class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(50), nullable = False)
    lastname = db.Column(db.String(50), nullable = False)
    phone = db.Column(db.Integer, unique = True)
    email = db.Column(db.String(100), nullable = False, unique = True)
    password = db.Column(db.String(50), nullable = False)

    def __repr__(self):
        return '<User %r>'%self.id


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/', methods = ['POST', 'GET'])
def index():
    return render_template('index.html')


@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')

        if (not firstname) or (not lastname) or (not phone) or (not email) or (not password):
            flash("Enter all details to SignUP", "error")
            return redirect('/signup')


        usere = Users.query.filter_by(email=email).first()
        userp = Users.query.filter_by(phone=phone).first()

        if userp:
            flash("Phone Number already Exist | add different Phone Number", "error")
            return redirect('/signup')
        
        elif usere:
            flash("e-Mail ID already Exist | add different e-Mail", "error")
            return redirect('/signup')
        
        else:
            new_user = Users(firstname=firstname, lastname=lastname, phone=phone, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            
            flash("You are successfully signed up", "success")
            return redirect('/')
    
    else:
        return render_template('signup.html')




@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        usere = Users.query.filter_by(email=email).first()
        userp = Users.query.filter_by(phone=email).first()
        print(usere)
        print(userp)

        if (usere) and (usere.password == password): 
            login_user(usere)
            flash("You are logged in", "success")
            return redirect('/profile')
        
        if (userp) and (userp.password == password):
            login_user(userp)
            flash("You are logged in", "success")
            return redirect('/profile')
        
        else:
            flash("Please Check Your login details", "error")
            return redirect('/')


@app.route('/profile', methods = ['POST', 'GET'])
@login_required
def profile():
    #name = current_user.firstname
    return render_template('profile.html', user=current_user)


@app.route('/users', methods = ['POST', 'GET'])
@login_required
def users():
    users = Users.query.order_by(Users.firstname).all()
    return render_template('users.html', users=users)


@app.route('/edituser/<int:userid>', methods = ['POST', 'GET'])
@login_required
def edituser(userid):
    userdetails = Users.query.get_or_404(userid)
    #ud = Users.query.filter(userid).first()
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        phone = request.form.get('phone')
        email = request.form.get('email')

        if (not firstname) or (not lastname) or (not phone) or (not email):
            flash("Enter all details to Update", "error")
            return render_template("updateuser.html", userdetails=userdetails)
        
        usere = Users.query.filter_by(email=email).first()
        userp = Users.query.filter_by(phone=phone).first()
        print(userp, userdetails)

        if (usere is not userdetails) and usere is not None:
            flash("e-Mail ID already Exist | add different e-Mail", "error")
            return render_template("updateuser.html", userdetails=userdetails)
        
        elif (userp is not userdetails) and userp is not None:
            flash("Phone Number already Exist | add different Phone Number", "error")
            return render_template("updateuser.html", userdetails=userdetails)
        
        else:
            userdetails.firstname = firstname
            userdetails.lastname = lastname
            userdetails.email = email
            userdetails.phone = phone

            db.session.commit()
            return redirect('/profile')
    

    else:
        return render_template("updateuser.html",userdetails=userdetails)


@app.route('/deletes/<int:userid>', methods = ['POST', 'GET'])
@login_required
def deletes(userid):
    deleteuser = Users.query.get_or_404(userid)
    if request.method == "POST":
        logout_user()
        db.session.delete(deleteuser)
        db.session.commit()
        flash("Account Deleted Successfully", "success")
        return redirect('/')
    
    else:
        return render_template("delete.html")


@app.route('/delete/<int:userid>', methods = ['POST', 'GET'])
def delete(userid):
    deleteuser = Users.query.get_or_404(userid)
    logout_user()
    db.session.delete(deleteuser)
    db.session.commit()
    flash("Account Deleted Successfully", "success")
    return redirect('/')








@app.route('/logout', methods = ['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)