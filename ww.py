# West Watch website

# Flask setup from pset 9: Finance
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helper import notification, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///west.db")


# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget existing user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("email"):
            return notification("Must provide email.")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return notification("Must provide password.")

        # Query users database for email
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return notification("Invalid email and or password.")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Redirect logout to login page
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# Register Page
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST
    if request.method == "POST":

        # Set name
        name = request.form.get("name")

        # Set email
        email = request.form.get("email")

        # Set password
        password = request.form.get("password")

        # Set grade
        grade = request.form.get("grade")

        # Ensure name was submitted
        if not name:
            return notification("Must provide name.")

        # Ensure email was submitted
        if not email:
            return notification("Must provide email.")

        # Ensure email ends with "bentonvillek12.org"
        if not email.endswith('@bentonvillek12.org'):
            return notification("Must use a valid Bentonville Schools email.")

        # Ensure grade was submitted
        if grade == None:
            return notification("Must select grade.")

        # Ensure password was submitted and confirmed
        elif not password:
            return notification("Must provide password.")

        elif password != request.form.get("confirmation"):
            return notification("Passwords do not match.")

        # Ensure email has not been registered
        registered = db.execute("SELECT email FROM users WHERE email = ?", email)
        if len(registered) != 0:
            return notification("Email already registered.")

        # If everything is entered correctly
        else:
            # Hash password
            password_hash = generate_password_hash(password)

            # Add user to database
            db.execute("INSERT INTO users (email, hash, name, diploma, grade) VALUES(?, ?, ?, ?, ?)", email, password_hash, name, diploma, grade)

            # Redirect user to home page
            return redirect("/")

    # User reached route via GET
    else:
        return render_template("register.html")


# Home Page
@app.route("/", methods=["GET"])
@login_required
def index():
    """Welcome User"""

    name = db.execute("SELECT name FROM users WHERE id = ?", session["user_id"])

    # Render the homepage to display name on index.html
    return render_template("index.html", name=name[0])


# Courses Page
@app.route("/courses", methods=["GET", "POST"])
@login_required
def courses():
    """Display Courses by Department"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Find course title
        course_selection = request.form.get("selection")

        # Query details about course
        course_details = db.execute("SELECT * FROM courses WHERE title = ?", course_selection)

        # Find all evaluations of the course
        evaluations = db.execute("SELECT Overall, Difficulty, Materials, Assignments, Instruction, Feedback, Time FROM evaluate WHERE course_code = (SELECT code FROM courses WHERE title = ?)", course_selection)

        # Only return evaluations if they exist
        if len(evaluations) != 0:
            # Find rounded averages for all evaluation measures
            eval_means = db.execute("SELECT ROUND(AVG(Overall), 2) AS Overall, ROUND(AVG(Difficulty), 2) AS Difficulty, ROUND(AVG(Materials), 2) AS Materials, ROUND(AVG(Assignments), 2) AS Assignments, ROUND(AVG(Instruction), 2) AS Instruction, ROUND(AVG(Feedback), 2) AS Feedback, ROUND(AVG(Time), 2) AS Time FROM evaluate WHERE course_code = (SELECT code FROM courses WHERE title = ?)", course_selection)
            evaluations = evaluations[0]

            # Create data list of all evaluation means for d3 visualization
            data = []
            for evaluation in evaluations:
                for mean in eval_means:
                    course = { "evaluation": evaluation, "rating": mean["" + evaluation + ""] }
                    data.append(course)

            # Return comments if there are any
            comments = db.execute("SELECT comments FROM evaluate WHERE comments != 'None' AND course_code = (SELECT code FROM courses WHERE title = ?)", course_selection)


            return render_template("course.html", course_details=course_details, data=data, comments=comments)

        # If no evaluations, return only course details
        else:
            return render_template("course.html", course_details=course_details)

    # Return list of courses by departments to display
    else:

        departments = db.execute("SELECT DISTINCT department FROM courses")

        courses = db.execute("SELECT title, department FROM courses")

        # Render the page to display courses in dropdown
        return render_template("courses.html", departments=departments, courses=courses)


# Evaluate Code Page
@app.route("/evalcode", methods=["GET", "POST"])
@login_required
def evalcode():
    """Enter Evaluation Code to Evaluate a Course"""

    #User reached route via POST
    if request.method == "POST":

        # Find code entered
        code = request.form.get("code")

        # Find course title associated with code entered
        course = db.execute("SELECT title FROM courses WHERE code = ?", code)

        # Ensure code was submitted correctly
        if not code or len(course) == 0:
            return notification("Must provide valid code.")

        # Get list of overall evaluation measures
        evaluations = db.execute("SELECT Overall, Difficulty, Materials, Assignments, Time FROM evaluate")

        # Get list of teacher evaluation measures
        teacher_evaluations = db.execute("SELECT Instruction, Feedback FROM evaluate")

        # Return template with evaluation measure headings, course title, and course code
        return render_template("evaluate.html", course=course, evaluations=evaluations[0], teacherEval=teacher_evaluations[0], code=code)

    else:

        # Render the page to display courses in dropdown
        return render_template("evalcode.html")


# Evaluate Page
@app.route("/evaluate", methods=["GET", "POST"])
@login_required
def evaluate():
    """Submit Evaluation for Course"""

    #User reached route via POST
    if request.method == "POST":

        # Get values submitted for each evaluation measure
        code = request.form.get("code")
        overall = request.form.get("Overall")
        difficulty = request.form.get("Difficulty")
        materials = request.form.get("Materials")
        assignments = request.form.get("Assignments")
        time = request.form.get("Time")
        instruction = request.form.get("Instruction")
        feedback = request.form.get("Feedback")
        comment = request.form.get("comments")

        # Only add comment if included
        if not comment:
            db.execute("INSERT INTO evaluate (course_code, Overall, Difficulty, Materials, Assignments, Time, Instruction, Feedback) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", code, overall, difficulty, materials, assignments, time, instruction, feedback)

        else:
            db.execute("INSERT INTO evaluate (course_code, Overall, Difficulty, Materials, Assignments, Time, Instruction, Feedback, Comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", code, overall, difficulty, materials, assignments, time, instruction, feedback, comment)

        # redirect user to home page
        return redirect("/")

    # User reached route via GET
    else:

        # Render the page to display the evaluation form
        return render_template("evaluate.html")

# Add Favorites
@app.route("/addfavorite", methods=["POST"])
@login_required
def addfavorite():
    """Add Course to Favorites"""

    # Get code of course being added to favorites
    code = request.form.get("favorite")

    # Check if course has already been added to favorites
    added = db.execute("SELECT course_code FROM favorites WHERE user_id=? AND course_code=?", session["user_id"], code)

    if len(added) != 0:
        return notification("You have already added this course to favorites.")

    # Add course to favorites
    db.execute("INSERT INTO favorites (user_id, course_code) VALUES (?, ?)", session["user_id"], code)

    # Take user back to list of courses
    return redirect("/courses")


# Favorites Page
@app.route("/favorites", methods=["GET", "POST"])
@login_required
def favorites():
    """View Favorite Courses"""

    # User reached route via POST
    if request.method == "POST":

        # Get code of course being deleted from favorites
        code = request.form.get("delete")

        # Delete course from favorites
        db.execute("DELETE FROM favorites WHERE user_id=? AND course_code=?", session["user_id"], code)

    # Find all courses in favorites database
    favorites = db.execute("SELECT title, code FROM courses WHERE code IN (SELECT course_code FROM favorites WHERE user_id = ?)", session["user_id"])

    # Render favorites courses template
    return render_template("favorites.html", favorites=favorites)


# My Schedule Page
@app.route("/myschedule", methods=["GET", "POST"])
@login_required
def schedule():
    """Display and Edit Schedule"""

    # User reached route via POST
    if request.method == "POST":

        # Find title of course being deleted from schedule
        delete_course = request.form.get("delete")

        # Identify if random generate button has been pressed
        random = request.form.get("random")

        # If user wants to delete a course form schedule, delete course from schedule database
        if delete_course:
            delete_code = db.execute("SELECT code FROM courses WHERE title = ?", delete_course)
            db.execute("DELETE FROM schedule WHERE user_id=? AND course_code=?", session["user_id"], delete_code[0]["code"])

        # If user wants to generate a random schedule, clear current schedule entries
        elif random:
            db.execute("DELETE FROM schedule WHERE user_id = ?", session["user_id"])

            # Find 28 courses to fill the schedule
            code = db.execute("SELECT DISTINCT code FROM courses WHERE credit = 1 ORDER BY RANDOM() LIMIT 28")

            # Add generated courses to each grade
            # Set range values to 0 and 7 since there are 7 courses in each year
            range_from = 0
            range_to = 7
            # Go through each of the four years of high school
            for grade in range (9, 13):
                # Assigning 7 courses to each year
                for i in range(range_from, range_to):
                    db.execute("INSERT INTO schedule (user_id, course_code, grade) VALUES (?, ?, ?)", session["user_id"], code[i]["code"], grade)
                # Add 7 to range variables to enter new courses for the next year
                range_from += 7
                range_to += 7

        # If user wants to add a course to their schedule, then...
        else:

            # Identify grade where course is being added
            grade = request.form.get("schedule")

            # Identify course code of course being added
            code = request.form.get("course")

            # Identify credit value of course being added
            credit = db.execute("SELECT credit FROM courses WHERE code = ?", code)

            # Check if course has already been added
            added = db.execute("SELECT course_code FROM schedule WHERE course_code = ?", code)
            if len(added) != 0:
                return notification("You have already added this course to your schedule.")

            # Check total credits for grade where course is being added
            grade_credits = db.execute("SELECT SUM(credit) AS credit FROM courses WHERE code IN (SELECT course_code FROM schedule WHERE user_id = ? AND grade = ?)", session["user_id"], grade)

            # Get value of credit sum
            grade_credits = grade_credits[0]["credit"]

            # Set grade_credits equal to 0 if NoneType
            if grade_credits is None:
                grade_credits = 0

            # Add course credit to total credits for the grade
            grade_credits += credit[0]["credit"]

            # Check if total grade credits exceed maximum value of 7.0 credits per year
            if grade_credits > 7.0:
                return notification("You have reached the maximum number of credits for this year. There is not enough space in your schedule for this course. Try adding this course to another year.")

            # Add course to schedule database
            db.execute("INSERT INTO schedule (user_id, course_code, grade) VALUES (?, ?, ?)", session["user_id"], code, grade)

    # Find credit sum of schedule for each grade
    credits9 = db.execute("SELECT SUM(credit) AS credit, grade FROM courses INNER JOIN schedule ON courses.code = schedule.course_code WHERE code IN (SELECT course_code FROM schedule WHERE user_id = ? AND grade = 9)", session["user_id"] )
    credits10 = db.execute("SELECT SUM(credit) AS credit, grade FROM courses INNER JOIN schedule ON courses.code = schedule.course_code WHERE code IN (SELECT course_code FROM schedule WHERE user_id = ? AND grade = 10)", session["user_id"] )
    credits11 = db.execute("SELECT SUM(credit) AS credit, grade FROM courses INNER JOIN schedule ON courses.code = schedule.course_code WHERE code IN (SELECT course_code FROM schedule WHERE user_id = ? AND grade = 11)", session["user_id"] )
    credits12 = db.execute("SELECT SUM(credit) AS credit, grade FROM courses INNER JOIN schedule ON courses.code = schedule.course_code WHERE code IN (SELECT course_code FROM schedule WHERE user_id = ? AND grade = 12)", session["user_id"] )

    # Select all courses added to schedule for user
    courses = db.execute("SELECT courses.title, courses.credit, schedule.grade FROM courses INNER JOIN schedule ON courses.code = schedule.course_code WHERE courses.code IN (SELECT course_code FROM schedule WHERE user_id = ?)", session["user_id"])

    # Create list of grades to use in html for loop
    grades = [9, 10, 11, 12]

    # Return template to display courses, grades, and credit totals for each year
    return render_template("schedule.html", courses=courses, grades=grades, credits9=credits9, credits10=credits10, credits11=credits11, credits12=credits12)