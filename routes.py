


@app.route('/')
def index():
    return render_template('index.html', title='Home')


@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route ('/login', methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user:
        if check_password_hash(user.password_hash, password):
            flash('Logged in successfully.', category='success')
            login_user(user, remember=True)
            return redirect(url_for('home'))
        else:
            flash('Incorrect password, try again.', category='error')

    return render_template('login.html', title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
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
            flash('Email already exists.')
            return redirect(url_for('register', category='error'))
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
    return redirect(url_for('home')) 