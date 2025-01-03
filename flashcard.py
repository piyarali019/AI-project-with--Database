from flask import render_template, redirect, request, flash, url_for,jsonify,session
from models import User, db,Question
from forms import login_form, register_form, admin_edit_user_form
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from main import app,api
import sqlite3

from sqlalchemy.orm import joinedload

from api import UserAPI
api.add_resource(UserAPI,"/api/user","/api/user/login")


# DATABASE = 'database.sqlite3.db'
import os
DATABASE = r'C:\Users\User\OneDrive\Desktop\piyaraliapp\instance\database.sqlite3'
@app.route('/', methods=['GET', 'POST'])
def home_page():
    form = login_form()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            return redirect(url_for('dashboard'))
        else:
            flash('Username and password are not match! Please try again', category='danger')
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user.username)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = register_form()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              password=form.password.data)
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('login_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = login_form()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            return redirect(url_for('dashboard'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    return redirect(url_for("home_page"))



@app.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('home_page'))  # Ensure the current user is an admin

    users = User.query.all()

    user_edit_form = admin_edit_user_form()

    if user_edit_form.validate_on_submit():
        user_to_edit = User.query.filter_by(username=user_edit_form.username.data).first()
        if user_to_edit:
            user_to_edit.is_admin = user_edit_form.is_admin.data == 'True'  # Update admin status
            db.session.commit()


        db.session.commit()

    return render_template('admin_dashboard.html', users=users,  user_edit_form=user_edit_form)


from werkzeug.security import generate_password_hash


from werkzeug.security import generate_password_hash

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_users():
    if not current_user.is_admin:
        flash("Access denied! Admins only.", category='danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')

        if action == 'delete' and user_id:
            # Handle deleting a user
            user_to_delete = User.query.get(user_id)
            if user_to_delete:
                db.session.delete(user_to_delete)
                db.session.commit()
                flash(f"User {user_to_delete.username} has been deleted.", category='success')
            else:
                flash("User not found.", category='danger')

        elif action == 'edit' and user_id:
            # Handle editing a user
            user_to_edit = User.query.get(user_id)
            if user_to_edit:
                new_username = request.form.get('username')
                is_admin = request.form.get('is_admin') == 'True'
                new_password = request.form.get('password')

                user_to_edit.username = new_username
                user_to_edit.is_admin = is_admin

                if new_password.strip():
                    user_to_edit.password = generate_password_hash(new_password)

                db.session.commit()
                flash(f"User {user_to_edit.username} has been updated.", category='success')
            else:
                flash("User not found.", category='danger')

        return redirect(url_for('admin_users'))  # Redirect to avoid form resubmission

    # Fetch all users
    users = User.query.all()
    return render_template('admin_users.html', users=users)




@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.is_admin:  # Ensure only admins can add users
        form = register_form()
        if form.validate_on_submit():  # When the form is submitted and valid
            # Create a new user object
            user_to_create = User(username=form.username.data, password=form.password.data)
            db.session.add(user_to_create)  # Add the new user to the session
            db.session.commit()  # Commit the transaction to the database
            flash(f'User {form.username.data} has been created!', 'success')
            return redirect(url_for('admin_users'))  # Redirect to admin user management page
        return render_template('admin_add_user.html', form=form)  # Render the form if not submitted
    else:
        flash("You don't have permission to access this page.", 'danger')
        return redirect(url_for('dashboard'))  # Redirect to dashboard if not admin





@app.route('/admin/analytics', methods=['GET'])
@login_required
def admin_analytics():
    if not current_user.is_admin:
        flash("Access denied! Admins only.", category='danger')
        return redirect(url_for('dashboard'))

    # Analytics data
    total_users = User.query.count()

    # Fetch total test questions from the Questions table
    total_test_questions = db.session.query(Question).count()  # This is the correct query for the Questions table

    # Fetch the usernames and scores of users who have a non-null score
    users_scores = User.query.filter(User.score != None).with_entities(User.username, User.score).all()

    return render_template('admin_analytics.html',
                           total_users=total_users,
                           total_test_questions=total_test_questions,  # Total test questions
                           users_scores=users_scores)  # Pass users' names and scores


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("Access denied! Admins only.", category='danger')
        return redirect(url_for('admin_dashboard'))

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully.", category='success')
    else:
        flash("User not found.", category='danger')

    return redirect(url_for('admin_users'))



@app.route('/start_test')
def start_test():
    return render_template('test_page.html')



def fetch_quiz():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Fetch all questions
        cursor.execute("SELECT * FROM Questions")
        questions = cursor.fetchall()

        # Fetch all answers
        cursor.execute("SELECT * FROM Answers")
        answers = cursor.fetchall()

    # Prepare quiz data
    quiz = []
    for question in questions:
        question_id, question_text = question
        question_answers = [
            {
                "answer_id": answer[0],
                "answer_text": answer[2],
                "is_correct": answer[3]
            }
            for answer in answers if answer[1] == question_id
        ]
        quiz.append({
            "question_id": question_id,
            "question": question_text,
            "options": [answer["answer_text"] for answer in question_answers],
            "correct": next((index for index, answer in enumerate(question_answers) if answer["is_correct"]), None)
        })
    return quiz


def get_db_connection():
    conn = sqlite3.connect(DATABASE, check_same_thread=False) # Use your actual database name
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/get_quiz')
def get_quiz():
    quiz_data = fetch_quiz()
    return jsonify(quiz_data)



@app.route('/update_score', methods=['POST'])
@login_required
def update_score():
    score = request.json.get('score')  # Assuming score is sent in the request body

    if not score:
        return jsonify({'status': 'error', 'message': 'No score provided'}), 400

    try:
        # Update the current user's score in the database
        user = current_user  # Flask-Login's current_user is automatically populated
        user.score = score  # Update the score field (make sure the User model has a 'score' field)
        db.session.commit()  # Commit the change to the database

        return jsonify({'status': 'success', 'message': 'Score updated successfully!'}), 200
    except Exception as e:
        db.session.rollback()  # Rollback in case of any error
        print(f"Error updating score: {e}")
        return jsonify({'status': 'error', 'message': 'Database error occurred'}), 500





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

