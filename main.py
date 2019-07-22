from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash
from app import app, db
from models import User, Blog

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', title='Blogz', users=users)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)

        if users.count() == 1:
            user = users.first()
        
            if user and check_pw_hash(password, user.pw_hash):
                session['username'] = username
                flash("Welcome back, " + username)
                return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
        
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
      
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already in use')
            return redirect('/signup')
        if username == '':
            flash('Please enter a username')
        if len(username) < 3:
            flash('Username must be at least 3 characters')
            return redirect('/signup')
        if len(password) < 3:
            flash('Password must be at least 3 characters')
            return redirect('/signup')
        if password != verify:
            flash('passwords do not match')
            return redirect('/signup')
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash("Welcome, " + username)
            return redirect('/newpost')
    
    return render_template('signup.html')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    posts = Blog.query.all()
    title = Blog.query.get('title')

    if blog_id:
        post = Blog.query.get(blog_id)
        return render_template('singleUser.html', post=post, header="User Posts")
    
    if user_id:
        posts = Blog.query.filter_by(owner_id=user_id)
        return render_template('blog.html', posts=posts)

    return render_template('blog.html', posts=posts, header = 'All Blog Posts' )
    

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        owner = User.query.filter_by(username=session['username']).first()
        blog_title = request.form['blogtitle']
        blog_body = request.form['blogbody']
        title_error = ''
        body_error = ''
        
        if not blog_title:
            title_error = "Please enter a blog title"
        if not blog_body:
            body_error = "Please enter a blog entry"

        if not body_error and not title_error:
            new_entry = Blog(blog_title, blog_body, owner=owner)     
            db.session.add(new_entry)
            db.session.commit()
            post_id = "/blog?id=" + str(new_entry.id)       
            return redirect(post_id)
        else:
            return render_template('newpost.html', title='New Entry', title_error=title_error, body_error=body_error, blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newpost.html', title='New Entry')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

if  __name__ == "__main__":
    app.run()