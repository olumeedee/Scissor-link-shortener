
from flask import render_template, request, redirect, url_for, flash
from . import app, db, cache, limiter
from .models import User,Url
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .utils import generate_short_url,generate_qr_code,link_analytics,get_location
import requests




@app.route('/', methods=['GET', 'POST'])
@limiter.limit('10/minutes')
def index():
    if request.method == 'POST':
        long_url = request.form['long_url']
        custom_url = request.form['custom_url'] or None
        long_url_exists = Url.query.filter_by(user_id=current_user.id).filter_by(long_url=long_url).first()

        if requests.get(long_url).status_code != 200:
            return render_template('404.html')

        elif long_url_exists:
            flash ('This link has already been shortened.')
            return redirect(url_for('dashboard'))

        elif custom_url:
            url_exists = Url.query.filter_by(custom_url=custom_url).first()
            if url_exists:
                flash ('That custom path is taken. Please try another.')
                return redirect(url_for('index'))
            short_url = custom_url

        elif long_url[:4] != 'http':
            long_url = 'http://' + long_url
        
        else:
            while True:
                short_url = generate_short_url()
                short_url_exists = Url.query.filter_by(short_url=short_url).first()
                if not short_url_exists:
                    break
        
        link = Url(long_url=long_url, short_url=short_url, custom_url=custom_url, user_id=current_user.id)
        db.session.add(link)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('index.html', title='Home')


@app.route('/dashboard')
@login_required
def dashboard():
    links = Url.query.filter_by(user_id=current_user.id).order_by(Url.created_at.desc()).all()
    host = request.host_url
    return render_template('dashboard.html', links=links, host=host)



@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/history')
@login_required
def history():
    links = Url.query.filter_by(user_id=current_user.id).order_by(Url.created_at.desc()).all()
    host = request.host_url
    return render_template('history.html', links=links, host=host)




@app.route('/<short_url>')
@cache.cached(timeout=30)
def redirect_link(short_url):
    link = Url.query.filter_by(short_url=short_url).first()
    if link:
        link.clicks += 1
        db.session.commit()
        return redirect(link.long_url)
    else:
        return render_template('404.html')
    
    
@app.route('/<short_url>/qr_code')
@login_required
@cache.cached(timeout=30)
@limiter.limit('10/minutes')
def generate_qr_code_link(short_url):
    link = Url.query.filter_by(user_id=current_user.id).filter_by(short_url=short_url).first()

    if link:
        image_io = generate_qr_code(request.host_url + link.short_url)
        return image_io.getvalue(), 200, {'Content-Type': 'image/png'}
    
    return render_template('404.html')


@app.route('/<short_url>/delete')
@login_required
def delete(short_url):
    link = Url.query.filter_by(user_id=current_user.id).filter_by(short_url=short_url).first()

    if link:
        db.session.delete(link)
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('404.html')



@app.route('/<short_url>/edit', methods=['GET', 'POST'])
@login_required
@limiter.limit('10/minutes')
def update(short_url):
    link = Url.query.filter_by(user_id=current_user.id).filter_by(short_url=short_url).first()
    host = request.host_url
    if link:
        if request.method == 'POST':
            custom_url = request.form['custom_url']
            if custom_url:
                link_exists = Url.query.filter_by(custom_url=custom_url).first()
                if link_exists:
                    flash('That custom path already exists. Please try another.', category='error')
                    return redirect(url_for('update', short_url=short_url))
                if not custom_url.isalnum() and '-' not in custom_url:
                    flash('Custom path can only contain alphanumeric characters and hyphens.', category='error')
                    return redirect(url_for('update', short_url=short_url))
                link.custom_url = custom_url
                link.short_url = custom_url
                db.session.commit()
                flash('Custom path updated successfully.', category='success')
                return redirect(url_for('dashboard'))
        return render_template('edit.html', link=link, host=host)
    flash('Link does not exist.', category='error')
    return redirect(url_for('dashboard'))


@app.route('/<short_url>/analytics')
@login_required
def analytics(short_url):
    link = Url.query.filter_by(user_id=current_user.id).filter_by(short_url=short_url).first()
    host = request.host_url
    if link:
        return render_template('analytics.html', link=link, host=host)
    return render_template('404.html')
    

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username_email = request.form.get('username_email')
        password = request.form.get('password')

        user = User.query.filter((User.email == username_email) | (User.username == username_email)).first()

        if user:
        
            if check_password_hash(user.password_hash, password):
                flash('Logged in successfully.', category='success')
                login_user(user, remember=True)
                return redirect(url_for('index'))
            else:
                flash('Please provide valid credentials.', category='error')
                return redirect(url_for('login'))
            
        else:
            flash('Account not found. Please sign up to continue.', category='error')
            return redirect(url_for('register'))
    return render_template('login.html', title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()

        if user_exists:
            flash('Username already exists.', category='error')
            return redirect(url_for('register'))
        if email_exists:
            flash('Email already exists.', category='error')
            return redirect(url_for('register'))
        if len(username) < 4:
            flash('Username must be at least 4 characters.', category='error')
            return redirect(url_for('register'))
        if len(first_name) < 2:
            flash('First name must be at least 2 characters.', category='error')
            return redirect(url_for('register'))
        if len(last_name) < 2:
            flash('Last name must be at least 2 characters.', category='error')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash('Password must be at least 6 characters.', category='error')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwords do not match.', category='error')
            return redirect(url_for('register'))
        else:
            new_user = User(username=username, first_name=first_name, last_name=last_name, email=email, password_hash=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully.', category='success')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', category='success')
    return redirect(url_for('index')) 