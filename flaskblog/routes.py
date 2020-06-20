import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm, PostForm, DetailsForm,
                             RequestResetForm, ResetPasswordForm)
from flaskblog.models import User, Post, Details
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.calcs import main_calc
import pandas as pd
import datetime
from flask_mail import Message


@app.route("/")
@app.route("/home")
def home():
    page=request.args.get('page', 1, type=int) #1 is default
    posts=Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5) #before Post.query.all()
    return render_template('home.html', posts=posts)

@app.route("/user/<string:username>")
def user_posts(username):
    page=request.args.get('page', 1, type=int) #1 is default
    user=User.query.filter_by(username=username).first_or_404()
    posts=Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page,per_page=5) #before Post.query.all()
    return render_template('user_posts.html', posts=posts, user=user)

@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your Account has been created! You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user,remember=form.remember.data)
            next_page=request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))  #redirect to next page if next page exists
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com', recipients=[user.email])
    msg.body = f''' To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, ignore this email and no changes will be made
    '''
    mail.send(msg)

@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RequestResetForm
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info') #info is class
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user=User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form=ResetPasswordForm
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static\profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
def new_post():
    form=PostForm()
   #form_details=DetailsForm()
    if form.validate_on_submit():
        post=Post(title=form.title.data, content=form.content.data, start_year=form.start_year.data,
                  start_month=form.start_month.data, inflation=form.inflation.data,
                  withdrawal_rate=form.withdrawal_rate.data,start_age=form.start_age.data,
                  retirement_age=form.retirement_age.data, author=current_user) #added here
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!','success')
        #how do i figure out what the post_id was and route to update post?
        return redirect(url_for('home'))


    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')

#@app.route("/post/<int:post_id>")
#def post(post_id):
#    post=Post.query.get_or_404(post_id)
#    return render_template('post.html', title=post.title, post=post)

# This page will be where
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)   #post_id is a given variable so i can update the new details table ith this
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.start_year=form.start_year.data
        post.start_month=form.start_month.data
        post.inflation=form.inflation.data
        post.withdrawal_rate=form.withdrawal_rate.data
        post.start_age=form.start_age.data
        post.retirement_age=form.retirement_age.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
  # GET is not working and leading to error for label related to integer
  #  elif request.method == 'GET':
  #      form.title.data = post.title
  #      form.content.data = post.content
  #      form.start_year=post.start_year
  #      form.start_month=post.start_month
  #      form.inflation=post.inflation
  #      form.withdrawal_rate=post.withdrawal_rate
  #      form.start_age=post.start_age
  #      form.retirement_age=post.retirement_age

    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))



###################33

labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]

values = [
    967.67, 1190.89, 1079.75, 1349.19,
    2328.91, 2504.28, 2873.83, 4764.87,
    4349.29, 6458.30, 9907, 16297
]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]



@app.route('/line')
def line():
    line_labels=labels
    line_values=values
    return render_template('line_chart.html', title='Bitcoin Monthly Price in USD', max=17000, labels=line_labels, values=line_values)


@app.route("/post/<int:post_id>")
def post(post_id):
    line_labels = labels
    line_values = values
    post=Post.query.get_or_404(post_id) # this pulls from post and feeds to values in html file
    details=Details.query.filter_by(post_id=post_id).all()
    if not details:
        line_labels = labels
        line_values = values
    else:
        start_year=post.start_year
        start_month=post.start_month
        inflation=post.inflation
        withdrawal_rate=post.withdrawal_rate
        start_age=post.start_age
        retirement_age=post.retirement_age

        df = pd.DataFrame([(d.details_id, d.category, d.date_entry_year, d.date_entry_month, d.entry_name,
                            d.value, d.perc_change, d.contrib) for d in details],
                          columns=['item_id', 'category', 'date_entry_year', 'date_entry_month',
                                   'entry_name', 'value', 'perc_change', 'contrib'])

        df_accounts=main_calc(start_year, start_month, inflation, withdrawal_rate, start_age, retirement_age, df)

        line_labels=df_accounts['Dates'].astype(str).values.tolist()
        line_values=df_accounts['Net Worth'].astype(int).values.tolist()

     #date_list=df_accounts['Dates'].values.tolist()
     #net_worth_list=df_accounts['Net_Worth'].values.tolist()

#    df = sample_calc(starting_year, starting_value)
#    year_list=df['year'].values.tolist()
#    values_list=df['values'].values.tolist()

#    line_labels=date_list
#    line_values=net_worth_list

#    items=df.to_dict()    had items=items in there before when using this
    return render_template('post_line.html',  title=post.title+' '+'Line Chart', post=post, max=max(line_values), labels=line_labels, values=line_values)


@app.route("/post/<int:post_id>/add_details", methods=['GET', 'POST'])
@login_required
def add_details(post_id):
    post = Post.query.get_or_404(post_id)   #post_id is a given variable so i can update the new details table ith this
    if post.author != current_user:
        abort(403)
    form = DetailsForm()
    if form.validate_on_submit():
        details=Details(category=form.category.data, date_entry_year=form.date_entry_year.data, date_entry_month=form.date_entry_month.data,
                  entry_name=form.entry_name.data,
                  value=form.value.data,perc_change=form.perc_change.data,
                  contrib=form.contrib.data, post_id=post_id) #added here
        db.session.add(details)
        db.session.commit()

        flash('Your detail has been added!', 'success')
        return redirect(url_for('post', post_id=post.id))

    return render_template('add_details.html', title='New Post',
                           form=form, legend='New Post')