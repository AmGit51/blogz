from flask import Flask, request, redirect, render_template,session,flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:ytdcne24!@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'G$*R`YA4m5nar9L!'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(240))
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120),unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Loggged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect or user does not exist', 'error')
    return render_template('/login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    username_error = ''
    password_error = ''
    verifypassword_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verifypassword = request.form['verifypassword']
	
        if " " in username or len(username) == 0 or len(username) > 20 or len(username) < 3:
            username_error = 'This is not a vaild username.'

        if " " in password or len(password) == 0 or len(password) > 20 or len(password) < 3:
            password_error = 'This is not a valid password.'
            password = ''

        if " " in verifypassword or len(verifypassword) == 0 or len(verifypassword) > 20 or len(verifypassword) < 3:
            verifypassword_error = 'Re-enter a valid password.'
            verifypassword = ''

        if password != verifypassword:
            if " " in password or len(password) == 0 or len(password) > 20 or len(password) < 3:
                password_error = 'This is not a valid password.'
                password = ''
            elif " " in verifypassword or len(verifypassword) == 0 or len(verifypassword) > 20 or len(verifypassword) < 3:
                verifypassword_error = 'Re-enter a valid password.'
                verifypassword = ''
            else:
                password_error = 'Passwords do not match.'
                verifypassword_error = 'Passwords do not match.'
                password = ''
                verifypassword = ''

        if not username_error and not password_error and not verifypassword_error:
            existing_user = User.query.filter_by(username=username).first()

            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')

            if existing_user:
                flash('User already exists', 'error')
                return render_template('signup.html')

        else:
            return render_template('signup.html',
            username = username,
            username_error = username_error,
            password_error = password_error,
            verifypassword_error = verifypassword_error)

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/blog', methods=['GET'])
def blog():

    
    blog_id = request.args.get('id')
    blog_user = request.args.get('user')

    if blog_id:
        blog_post = Blog.query.get(blog_id)
        return render_template('display.html', blog_post=blog_post)

    if blog_user:
        user = User.query.filter_by(username=blog_user).first()
        blog_post = Blog.query.filter_by(owner=user).all()
        return render_template('singleUser.html', username=blog_user, blog_post=blog_post)

    else:
        posts = Blog.query.all()
        return render_template('blog.html', title="Build a Blog", posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()

    title_error = ""
    body_error = ""

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']


        if len(blog_title) == 0:
            title_error = 'Please fill in the title'

        if len(blog_body) == 0:
            body_error = 'Please fill in the body'

        if len(blog_title) == 0 and len(blog_body) == 0:
            title_error = 'Please fill in the title'
            body_error = 'Please fill in the body'

        if len(blog_title) != 0 and len(blog_body) != 0:
            blog_post = Blog(blog_title, blog_body, owner)
            db.session.add(blog_post)
            db.session.commit()
            id = blog_post.id
            return redirect('http://127.0.0.1:5000/blog?id={0}'.format(id))

        else:
            return render_template('newpost.html',
            blog_title=blog_title,
            blog_body=blog_body,
            title_error=title_error,
            body_error=body_error)

    return render_template('newpost.html')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', title="HOME", users=users)

if __name__ == '__main__':
    app.run()