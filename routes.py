



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