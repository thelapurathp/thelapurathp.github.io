# Q-GUIDE WORLD TOUR: WEST WATCH User Manual/Documentation

I created a Flask website in the CS50 IDE for my final project. Utilizing the Jinja web template engine, I coded the "ww.py" document as the application containing all of my page routes.
My Python code references various html pages, found in the "templates" folder. The document also references the "helpers.py" document, which provides code for the "notification" message as well as login required code.
My project can be compiled and run using the "export FLASK_APP=ww.py" command in the terminal, followed by "flask run" in which the IDE creates a web server that access the West Watch website.
This is very similar to the way in which pset 9: Finance was compiled and run, as I use similar elements from that pset in this final project.

All of the data referenced throughout "ww.py" is stored in the SQL database "west.db" through phpliteadmin. There are currently a set of sample evaluations and users to test the project's code.
The "ww.py" document begins by importing necessary aspects for Flask to work alongside SQL and outside documents, including render_template, notification, redirect, and session.
Once the application is configured and the "west.db" SQL database is linked to the document through the CS50 Library, the login page is coded. This is the first page the user will see when the web server is opened right after running Flask.
The login page clears the session of any past logins, and renders the "login.html" page with a form to login with an email and a password. Once this information is submitted by the user, "login()" ensures that an email and password was submitted
and that the user exists. If any of these conditions are not met, a message is returned indicating the error that occured. If all the information is inputted correctly and the user is in the system, then the user is redirected to the home page and
their session user id is stored in the "users" database table.

Next, the "logout()" function logs the user out, clears the session, and redirects the user to the main page.
From there, we have the "/register" page. When this page is reached via GET, the register form is displayed using render_template. If this route is reached via POST, then a user is trying to register for a West Watch account. If any part of the
registration information is incorrect or unanswered (name, email (within the Bentonville Schools domain), grade, password (confirmed)), then a notification message is sent to the user indicating the issue.
If all of the information is accurately provided, the user's password is hashed and added to the "users" database table, along with all of the other information that was inputted.

The home page is displayed next within "ww.py", and it simply takes the name of the user to send to the "index.html" template. This gives the user a personalized greeting as well as a rundown of the site's characteristics and general purpose.
The courses page is coded next. This page, when reached via GET, displays all of the courses in the "courses" database table, grouped by department. When a user clicks on a particular course, they are taken to a page with details about the course
and any inputted evaluations for the course. The title of the course is received through the "courses.html" form and is used to query information about the course. A data list containing all of the evaluation measures and their average values is
sent to "course.html" to create a d3 visualization.

In order to evaluate a course, the user must include the course's code. This is in place to prevent students from evaluating courses that they have not been approved to evaluate. If the user has been giving the course code, then they have the option
to evaluate the course based on different measures on a scale of 1 to 5: Overall, Difficulty, Materials, Assignments, Instruction, and Feedback. Time is evaluated from 1 to 20 as it is a measure of hours/week spent on the course.
Once the evaluation is completed and submitted, it is stored in the "evaluate" database table through "evaluate()". This code saves the information from the form and inputs it into the database.

Then, the "addfavorite()" function allows a user to add a course to favorites from the "course.html" page. This code inputs that course code into the "favorites" database table and displays these entries on the "/favorites" web page.
Finally, the "schedule()" function takes three different POST forms. One allows a user to delete the course from their schedule page ("/myschedule"). Another allows the user to randomly generate a set of 7 different courses for each grade year.
The last POST form allows the user to add a course to their schedule, specifying which grade they plan to take the course, on the "course.html" page. This is similar to the favorites page.

YOUTUBE VIDEO URL: https://youtu.be/yE3mlpcxFt4.