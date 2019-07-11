from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = "y337kGcys&zP3B"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(2000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

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
            new_entry = Blog(title_name, entry_name)
            db.session.add(new_entry)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_entry.id))
    return render_template("new_post.html", entry=entry)

if __name__ == "__main__":
    app.run()