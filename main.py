from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:blogz@localhost:3306/blogz"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = "y337kGcys&zP3B"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200))
    password = db.Column(db.String(20))
    blogs = db.relationship("Blog", backref="owner")

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.before_request
def required_login():
    allowed_routes = ["login", "signup", "blog", "index"]
    if request.endpoint not in allowed_routes and "email" not in session:
        flash("You must be logged in to do that.")
        return redirect("/login")

@app.route("/")
def index():
    userlist = User.query.all()
    authorid = request.args.get("id")
    if authorid is not None:
        user = User.query.get(authorid)
        blog = Blog.query.filter_by(owner_id=authorid)
        return render_template("singleUser.html", user=user, blog=blog)
    return render_template("index.html", userlist=userlist)

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        verify = request.form["verify"]

        if email == "":
            flash("Please fill out your email.")
            return redirect("/signup")
        
        if password == "" or verify == "":
            flash("Please fill out the password fields.")
            return reidrect("/signup")

        if pwver(password, verify) == False:
            flash("Your passwords do not match.")
            return redirect("/signup")

        existing_user = User.query.filter_by(email=email).first()

        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session["email"] = email
            return redirect("/newpost")

        if existing_user:
            flash("That email has already been assigned to an account.")
            return redirect("/signup")

    return render_template("signup.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session["email"] = email
            flash("Logged in")
            return redirect("/newpost")
        if not user:
            flash("Email is not in our database.")
            return redirect("/login")
        if pwver(password, user.password) == False:
            flash("User password incorrect.")
            return redirect("/login")
    return render_template("login.html")

def pwver(pw, ver):
    if pw == ver:
        return True
    else:
        return False

@app.route("/logout")
def logout():
    del session["email"]
    return redirect("/blog")

@app.route("/blog", methods=["GET"])
def blog():
    blog = Blog.query.all()
    idname = request.args.get("id")
    if idname is not None:
        entry = Blog.query.get(idname)
        return render_template("test.html", entry=entry)
    return render_template("blog.html", blog=blog)

@app.route("/newpost", methods=["POST", "GET"])
def newpost():
    owner = User.query.filter_by(email=session["email"]).first()
    entry = ""
    if request.method == "POST":
        title_name = request.form["titlename"]
        entry_name = request.form["entryname"]
        if title_name == "":
            flash("Please fill out a title.")
            return render_template("new_post.html", entryname=entry_name, titlename=title_name)
        if entry_name == "":
            flash("Please fill out the body of your entry.")
            return render_template("new_post.html", entryname=entry_name, titlename=title_name)
        else: 
            new_entry = Blog(title_name, entry_name, owner)
            db.session.add(new_entry)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_entry.id))
    return render_template("new_post.html", entry=entry)

if __name__ == "__main__":
    app.run()