#импорты
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os


#создаем приложение
app = Flask(__name__)
app.config['SECRET_KEY'] = 'very_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads/images'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app) #связываем наше приложение 'app' с SQLAlchemy

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True) #connection with Post

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image = db.Column(db.String(250))
    user_number = db.Column(db.String(250))


@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if 'user_id' not in session:
        flash('Please log in to create a post.', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        category = request.form['category']
        title = request.form['title']
        title = title.lower()
        content = request.form['content']
        content = content.lower()
        price = request.form['price']
        image = request.files['file']
        user_number = request.form['number']
        if image:
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
            photo = image.filename  
        else:
            photo = 'static/uploads/images/no_image.png'
        new_post = Post(category=category, title=title, content=content, price=price, user_id=session['user_id'], image=photo, user_number=user_number)
        db.session.add(new_post)
        db.session.commit()
        flash('Пост успешно создан!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html')

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if 'user_id' not in session or session['user_id'] != post.user_id:
        flash('You do not have permission to edit this post.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        post.category = request.form['category']
        post.title = request.form['title']
        post.title = post.title.lower()
        post.content = request.form['content']
        post.content = post.content.lower()
        post.price = request.form['price']
        post.image = request.files['file']
        post.user_number = request.form['number']
        if post.image:
            post.image.save(os.path.join(app.config['UPLOAD_FOLDER'], post.image.filename))
            post.image = post.image.filename
        else:
            post.image = 'static/uploads/images/no_image.png'
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('edit_post.html', post=post)

@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if 'user_id' not in session or session['user_id'] != post.user_id:
        flash('You do not have permission to delete this post.', 'danger')
        return redirect(url_for('home'))

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/more_details/<int:post_id>', methods=['GET', 'POST'])
def more_details(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('more_details.html', post=post)

@app.route('/filter', methods=['GET', 'POST'])
def filter():
    if request.method == 'POST':
        category = request.form['category']
        filtered_posts = Post.query.filter_by(category=category).all()
        return render_template('home.html', posts=filtered_posts, category=category)

    return redirect(url_for('home'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search = request.form['search']
        search = search.lower()
        search_post = []
        filtered_posts = Post.query.all()
        for fil_post in filtered_posts:
            if search in fil_post.content or search in fil_post.title:
                search_post.append(fil_post)
        return render_template('home.html', posts=search_post, category=search)

    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host=('0.0.0.0'))
