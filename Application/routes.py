import secrets
import os
from flask import render_template, url_for, flash, redirect, request, abort
from Application.models import User, Post
from Application.forms import RegForm, LogForm, UpdateAccForm, PostForm
from Application import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    pos = Post.query.filter_by(post_id=None).paginate(page=page, per_page=5)

    return render_template("home.html", pos=pos)

@app.route('/about')
def about():

    return render_template("about.html")

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegForm()
    if form.validate_on_submit():
        hash_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hash_pass)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login',  methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LogForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_pg = request.args.get('next')
            return redirect(next_pg) if next_pg else redirect(url_for('home'))
        else:
            flash('Login failed', 'danger')
    return render_template('login.html', title='login', form=form)

@app.route('/logout',)
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    randam_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = randam_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static\\profil_pics', picture_fn)
    output_size=(125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn



@app.route('/account', methods=['GET','POST'] )
@login_required
def account():
    form = UpdateAccForm()
    if form.validate_on_submit():
        if form.picture.data:
            os.remove(os.path.join(app.root_path, 'static\\profil_pics', current_user.img))
            picture_file = save_picture(form.picture.data)

            current_user.img = picture_file

        current_user.username = form.username.data
        current_user.emil = form.email.data
        db.session.commit()
        flash('Account info updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    img_file = url_for('static', filename='profil_pics/' + current_user.img)
    return render_template('account.html', title='account', img_file=img_file, form=form)

@app.route('/post/new', methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, autor=current_user, up_votes=0, down_votes=0)
        db.session.add(post)
        db.session.commit()
        flash('Post created', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='new post', form=form,  legend='New post')

@app.route('/comment/new<post_id>', methods=['GET','POST'])
@login_required
def new_comment(post_id):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, autor=current_user, post_id=post_id)
        db.session.add(post)
        db.session.commit()
        flash('Comment created', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='new post', form=form, legend='New post')

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)

    pos = Post.query.filter_by(post_id=post_id).all()
    print(pos)

    return render_template('post.html', title=post.title, p=post, pos=pos)

@app.route('/post/<int:post_id>/update', methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.autor != current_user:
        abort(403)
    else:
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash("Post updated", 'success')
            return redirect(url_for('post', post_id=post.id))
        elif request.method == 'GET':
            form.title.data = post.title
            form.content.data = post.content
        return render_template('create_post.html', title='update post', form=form, legend='Update post')

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.autor != current_user:
        abort(403)
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post Deleted', 'success')
        return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    pos = Post.query.filter_by(autor=user)\
        .order_by(Post.date.desc())\
        .paginate(page=page, per_page=5)
    return render_template("user_posts.html", pos=pos, user=user)
