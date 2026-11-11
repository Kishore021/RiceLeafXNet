from flask import Flask, render_template, request, redirect, session, url_for, flash
import os
import re
import secrets
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

import classify
from PIL import Image
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import bcrypt


# ============================================================
# APP CONFIGURATION
# ============================================================

app = Flask(__name__)

port = int(os.getenv("PORT", 5000))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Model.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = os.getenv(
    "SECRET_KEY",
    "1A2bc4s"
)

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    minutes=30
)

db = SQLAlchemy(app)


# ============================================================
# FOLDERS
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

STATIC_FOLDER = os.path.join(
    BASE_DIR,
    "static"
)

TEST_IMAGE_FOLDER = os.path.join(
    STATIC_FOLDER,
    "images",
    "test"
)

PROFILE_IMAGE_FOLDER = os.path.join(
    STATIC_FOLDER,
    "images",
    "users"
)

os.makedirs(
    TEST_IMAGE_FOLDER,
    exist_ok=True
)

os.makedirs(
    PROFILE_IMAGE_FOLDER,
    exist_ok=True
)


# ============================================================
# ADMIN CONFIGURATION
# ============================================================

ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME",
    "admin"
)

ADMIN_EMAIL = os.getenv(
    "ADMIN_EMAIL",
    "admin@localhost"
)

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    ""
)


# ============================================================
# SECURITY VERIFICATION CONFIGURATION
# ============================================================

SECURITY_MAX_ATTEMPTS = 5

SECURITY_QUESTIONS = [
    "What was the name of your first school?",
    "What is your favorite food?",
    "What was the name of your first pet?",
    "What is your favorite color?",
    "What city were you born in?"
]


# ============================================================
# CLASS NAMES
# ============================================================

class_names = [
    "Brown spot",
    "Healthy",
    "Hispa",
    "Leaf blast",
    "Neck blast"
]


# ============================================================
# USER MODEL
# ============================================================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(128),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(128),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(128),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="user"
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    profile_image = db.Column(
        db.String(255),
        nullable=True
    )

    security_question = db.Column(
        db.String(255),
        nullable=True
    )

    security_answer = db.Column(
        db.String(128),
        nullable=True
    )


    def __repr__(self):

        return f"<User {self.username}>"

    def to_dict(self):

        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "profile_image": self.profile_image,
            "security_question": self.security_question
        }


# ============================================================
# HISTORY MODEL
# ============================================================

class History(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    userId = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    image = db.Column(
        db.String(255),
        nullable=False
    )

    result = db.Column(
        db.String(255),
        nullable=False
    )

    date_created = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):

        return (
            f"<Result {self.result} - "
            f"{self.userId}>"
        )

    def to_dict(self):

        return {
            "id": self.id,
            "userId": self.userId,
            "image": self.image,
            "result": self.result,
            "date_created": self.date_created
        }


# ============================================================
# DATABASE MIGRATION
# ============================================================

def migrate_database():

    """
    Adds new columns to an existing Model.db
    without deleting existing users/history.
    """

    inspector = db.inspect(
        db.engine
    )

    user_columns = [
        column["name"]
        for column in inspector.get_columns(
            "user"
        )
    ]

    migration_queries = []

    if "role" not in user_columns:

        migration_queries.append(
            """
            ALTER TABLE user
            ADD COLUMN role VARCHAR(20)
            NOT NULL DEFAULT 'user'
            """
        )

    if "is_active" not in user_columns:

        migration_queries.append(
            """
            ALTER TABLE user
            ADD COLUMN is_active BOOLEAN
            NOT NULL DEFAULT 1
            """
        )

    if "profile_image" not in user_columns:

        migration_queries.append(
            """
            ALTER TABLE user
            ADD COLUMN profile_image VARCHAR(255)
            """
        )

    if "security_question" not in user_columns:

        migration_queries.append(
            """
            ALTER TABLE user
            ADD COLUMN security_question VARCHAR(255)
            """
        )

    if "security_answer" not in user_columns:

        migration_queries.append(
            """
            ALTER TABLE user
            ADD COLUMN security_answer VARCHAR(128)
            """
        )

    for query in migration_queries:

        try:

            db.session.execute(
                db.text(query)
            )

        except Exception as error:

            print(
                "Migration warning:",
                error
            )

    try:

        history_columns = [
            column["name"]
            for column in inspector.get_columns(
                "history"
            )
        ]

        if "image" in history_columns:
            pass

    except Exception as error:

        print(
            "History migration warning:",
            error
        )

    db.session.commit()


# ============================================================
# CREATE / MIGRATE DATABASE
# ============================================================

with app.app_context():

    db.create_all()

    migrate_database()


# ============================================================
# ADMIN CREATION
# ============================================================

def create_default_admin():

    """
    Creates the admin account if ADMIN_PASSWORD
    is configured.

    Existing admin accounts are not overwritten.
    """

    if not ADMIN_PASSWORD:

        print(
            "\nADMIN_PASSWORD is not configured."
        )

        print(
            "Admin account will not be created automatically."
        )

        return

    existing_admin = User.query.filter_by(
        username=ADMIN_USERNAME
    ).first()

    if existing_admin:

        if existing_admin.role != "admin":

            existing_admin.role = "admin"

            db.session.commit()

        return

    password_hash = bcrypt.hashpw(
        ADMIN_PASSWORD.encode("utf-8"),
        bcrypt.gensalt()
    )

    admin = User(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password=password_hash,
        role="admin",
        is_active=True
    )

    try:

        db.session.add(
            admin
        )

        db.session.commit()

        print(
            "\n=========================================="
        )

        print(
            "ADMIN ACCOUNT CREATED"
        )

        print(
            "Username:",
            ADMIN_USERNAME
        )

        print(
            "Email:",
            ADMIN_EMAIL
        )

        print(
            "=========================================="
        )

    except IntegrityError:

        db.session.rollback()

        print(
            "Admin username/email already exists."
        )


with app.app_context():

    create_default_admin()


# ============================================================
# HELPERS
# ============================================================

def get_current_user():

    if "userId" not in session:

        return None

    return User.query.get(
        session["userId"]
    )


def getUser():

    user = get_current_user()

    if user is None:

        return None, []

    history = History.query.filter(
        History.userId == user.id
    ).order_by(
        History.date_created.desc()
    ).all()

    return user.to_dict(), history


def password_matches(
    password,
    stored_password
):

    try:

        return bcrypt.checkpw(
            password.encode("utf-8"),
            stored_password
        )

    except Exception:

        return False


def hash_password(password):

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )


def valid_email(email):

    pattern = (
        r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    )

    return bool(
        re.match(
            pattern,
            email
        )
    )


# ============================================================
# SECURITY VERIFICATION HELPERS
# ============================================================

def normalize_security_answer(answer):

    return " ".join(
        answer.strip().lower().split()
    )


def hash_security_answer(answer):

    normalized = normalize_security_answer(
        answer
    )

    return bcrypt.hashpw(
        normalized.encode("utf-8"),
        bcrypt.gensalt()
    )


def security_answer_matches(
    answer,
    stored_answer
):

    if not answer or not stored_answer:
        return False

    try:

        normalized = normalize_security_answer(
            answer
        )

        return bcrypt.checkpw(
            normalized.encode("utf-8"),
            stored_answer
        )

    except Exception:

        return False


def clear_security_session():

    session.pop(
        "security_attempts",
        None
    )

    session.pop(
        "security_reset_user_id",
        None
    )


# ============================================================
# LOGIN PROTECTION
# ============================================================

PUBLIC_ENDPOINTS = {
    "index",
    "home",
    "model",
    "about",
    "result",
    "remedies",
    "login",
    "register",
    "forgot",
    "reset",
    "verifySecurity",
    "admin_login",
    "static"
}


USER_PROTECTED_ENDPOINTS = {
    "output",
    "profile",
    "update",
    "editProfile",
    "changePassword",
    "resetHistory",
    "securitySettings",
    "verifySecurity",
    "logout"
}


ADMIN_PROTECTED_ENDPOINTS = {
    "admin_logout",
    "admin_dashboard",
    "admin_users",
    "admin_user_details",
    "admin_toggle_user",
    "admin_delete_user",
    "admin_scans",
    "admin_profile",
    "admin_change_password"
}


@app.before_request
def check_login_session():

    endpoint = request.endpoint

    if endpoint == "static":

        return

    if endpoint in PUBLIC_ENDPOINTS:

        return

    if endpoint in ADMIN_PROTECTED_ENDPOINTS:

        if (
            "adminId" not in session
            or session.get("admin_logged")
            is not True
        ):

            return redirect(
                url_for("admin_login")
            )

        admin = User.query.get(
            session["adminId"]
        )

        if (
            admin is None
            or admin.role != "admin"
            or not admin.is_active
        ):

            session.clear()

            return redirect(
                url_for("admin_login")
            )

        return

    if endpoint in USER_PROTECTED_ENDPOINTS:

        if "userId" not in session:

            return redirect(
                url_for("login")
            )

        user = get_current_user()

        if user is None:

            session.clear()

            return redirect(
                url_for("login")
            )

        if not user.is_active:

            session.clear()

            flash(
                "Your account has been disabled.",
                "danger"
            )

            return redirect(
                url_for("login")
            )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# ============================================================
# HOME COMPATIBILITY ENDPOINT
# ============================================================
# Existing templates may use url_for("home").
# The real home function is index().
# Both endpoints open the same page.
# ============================================================

app.add_url_rule(
    "/",
    endpoint="home",
    view_func=index
)


# ============================================================
# MODEL
# ============================================================

@app.route("/model")
def model():

    return render_template(
        "model.html"
    )


# ============================================================
# ABOUT
# ============================================================

@app.route("/about")
def about():

    return render_template(
        "about.html"
    )


# ============================================================
# RESULT / TRAINING
# ============================================================

@app.route("/result")
def result():

    return render_template(
        "result_train.html"
    )


# ============================================================
# REMEDIES
# ============================================================

@app.route("/remedies")
def remedies():

    return render_template(
        "remedies.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("index")
    )


# ============================================================
# UPDATE - LEGACY PROFILE ROUTE
# ============================================================

@app.route(
    "/update",
    methods=["POST"]
)
def update():

    return editProfile()


# ============================================================
# EDIT PROFILE
# ============================================================

@app.route(
    "/editProfile",
    methods=["GET", "POST"]
)
def editProfile():

    user = get_current_user()

    if user is None:

        return redirect(
            url_for("login")
        )


    # ========================================================
    # GET REQUEST
    # ========================================================

    if request.method == "GET":

        return render_template(
            "edit_profile.html",
            user=user
        )


    # ========================================================
    # FORM DATA
    # ========================================================

    username = request.form.get(
        "username",
        ""
    ).strip()

    new_email = request.form.get(
        "email",
        ""
    ).strip().lower()

    current_password = request.form.get(
        "current_password",
        ""
    ).strip()

    security_answer = request.form.get(
        "security_answer",
        ""
    ).strip()


    # ========================================================
    # USERNAME VALIDATION
    # ========================================================

    if not username:

        flash(
            "Username cannot be empty.",
            "danger"
        )

        return redirect(
            url_for("editProfile")
        )


    if len(username) < 3:

        flash(
            "Username must contain at least 3 characters.",
            "danger"
        )

        return redirect(
            url_for("editProfile")
        )


    # ========================================================
    # EMAIL VALIDATION
    # ========================================================

    if not valid_email(new_email):

        flash(
            "Please enter a valid email address.",
            "danger"
        )

        return redirect(
            url_for("editProfile")
        )


    # ========================================================
    # CURRENT PASSWORD
    # ========================================================

    if not current_password:

        flash(
            "Current password is required.",
            "danger"
        )

        return redirect(
            url_for("editProfile")
        )


    if not password_matches(
        current_password,
        user.password
    ):

        flash(
            "Current password is incorrect.",
            "danger"
        )

        return redirect(
            url_for("editProfile")
        )


    # ========================================================
    # USERNAME DUPLICATE CHECK
    # ========================================================

    existing_username = User.query.filter(
        User.username == username,
        User.id != user.id
    ).first()

    if existing_username:

        flash(
            "Username already exists.",
            "danger"
        )

        return redirect(
            url_for("editProfile")
        )


    # ========================================================
    # PROFILE IMAGE
    # ========================================================

    image_file = request.files.get(
        "profile_image"
    )

    if image_file and image_file.filename:

        original_name = secure_filename(
            image_file.filename
        )

        allowed_extensions = {
            "jpg",
            "jpeg",
            "png",
            "webp"
        }

        extension = (
            original_name
            .rsplit(".", 1)[-1]
            .lower()
            if "." in original_name
            else ""
        )


        if extension not in allowed_extensions:

            flash(
                "Profile image must be JPG, JPEG, PNG or WEBP.",
                "danger"
            )

            return redirect(
                url_for("editProfile")
            )


        filename = (
            f"user_{user.id}_"
            f"{int(datetime.utcnow().timestamp())}."
            f"{extension}"
        )


        save_path = os.path.join(
            PROFILE_IMAGE_FOLDER,
            filename
        )


        # Save new image
        image_file.save(
            save_path
        )


        # Remove old image
        if user.profile_image:

            old_path = os.path.join(
                PROFILE_IMAGE_FOLDER,
                user.profile_image
            )

            if os.path.exists(
                old_path
            ):

                try:

                    os.remove(
                        old_path
                    )

                except Exception:

                    pass


        # Save new image filename
        user.profile_image = filename


    # ========================================================
    # UPDATE USERNAME
    # ========================================================

    user.username = username


    # ========================================================
    # EMAIL CHANGE
    # ========================================================

    if new_email != user.email:

        existing_email = User.query.filter(
            User.email == new_email,
            User.id != user.id
        ).first()


        if existing_email:

            flash(
                "Email address already exists.",
                "danger"
            )

            return redirect(
                url_for("editProfile")
            )


        # ----------------------------------------------------
        # SECURITY VERIFICATION
        # ----------------------------------------------------

        if not user.security_question or not user.security_answer:

            flash(
                "Please set your security question and answer in your profile first.",
                "danger"
            )

            return redirect(
                url_for("profile")
            )


        if not security_answer:

            flash(
                "Security answer is required when changing your email.",
                "danger"
            )

            return redirect(
                url_for("editProfile")
            )


        if not security_answer_matches(
            security_answer,
            user.security_answer
        ):

            flash(
                "Incorrect security answer.",
                "danger"
            )

            return redirect(
                url_for("editProfile")
            )


        # IMPORTANT:
        # Actually save the new email.
        user.email = new_email


    # ========================================================
    # SAVE ALL CHANGES
    # ========================================================

    db.session.commit()


    flash(
        "Profile updated successfully.",
        "success"
    )


    return redirect(
        url_for("profile")
    )

# ============================================================
# PROFILE
# ============================================================

@app.route("/profile")
def profile():

    user = get_current_user()

    if user is None:

        return redirect(
            url_for("login")
        )

    history = History.query.filter(
        History.userId == user.id
    ).order_by(
        History.date_created.desc()
    ).all()

    return render_template(
        "profile.html",
        user=user,
        security_questions=SECURITY_QUESTIONS,
        details=user.to_dict(),
        history=history,
        history_items=history,
        total_scans=len(history),
        today_scans=History.query.filter(
            History.userId == user.id,
            db.func.date(
                History.date_created
            ) == datetime.utcnow().date()
        ).count(),
        last_scan=history[0]
        if history
        else None
    )


# ============================================================
# SECURITY SETTINGS
# ============================================================

@app.route(
    "/securitySettings",
    methods=["POST"]
)
def securitySettings():

    user = get_current_user()

    if user is None:

        return redirect(
            url_for("login")
        )

    question = request.form.get(
        "security_question",
        ""
    ).strip()

    answer = request.form.get(
        "security_answer",
        ""
    ).strip()

    current_password = request.form.get(
        "current_password",
        ""
    )

    if question not in SECURITY_QUESTIONS:

        flash(
            "Please select a valid security question.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    if not answer:

        flash(
            "Security answer cannot be empty.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    if len(answer) < 2:

        flash(
            "Security answer must contain at least 2 characters.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    if not current_password:

        flash(
            "Current password is required.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    if not password_matches(
        current_password,
        user.password
    ):

        flash(
            "Current password is incorrect.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    user.security_question = question

    user.security_answer = hash_security_answer(
        answer
    )

    db.session.commit()

    flash(
        "Security verification settings updated successfully.",
        "success"
    )

    return redirect(
        url_for("profile")
    )


# ============================================================
# CHANGE PASSWORD
# ============================================================

@app.route(
    "/changePassword",
    methods=["POST"]
)
def changePassword():

    user = get_current_user()

    if user is None:

        return redirect(
            url_for("login")
        )

    oldPass = request.form.get(
        "oldPass",
        ""
    )

    newPass = request.form.get(
        "newPass",
        ""
    )

    confPass = request.form.get(
        "confPass",
        ""
    )

    if not oldPass or not newPass or not confPass:

        flash(
            "Please fill all password fields.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    if len(newPass) < 6:

        flash(
            "New password must contain at least 6 characters.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    if newPass != confPass:

        flash(
            "New passwords do not match.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    if not password_matches(
        oldPass,
        user.password
    ):

        flash(
            "Current password is incorrect.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    user.password = hash_password(
        newPass
    )

    db.session.commit()

    flash(
        "Password updated successfully.",
        "success"
    )

    return redirect(
        url_for("profile")
    )


# ============================================================
# RESET SCAN HISTORY
# ============================================================

@app.route(
    "/resetHistory",
    methods=["POST"]
)
def resetHistory():

    user = get_current_user()

    if user is None:

        return redirect(
            url_for("login")
        )

    password = request.form.get(
        "password",
        ""
    )

    if not password:

        flash(
            "Password is required to reset scan history.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    if not password_matches(
        password,
        user.password
    ):

        flash(
            "Incorrect password. Scan history was not deleted.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    histories = History.query.filter(
        History.userId == user.id
    ).all()

    for history in histories:

        db.session.delete(
            history
        )

    db.session.commit()

    flash(
        "Your scan history has been reset successfully.",
        "success"
    )

    return redirect(
        url_for("profile")
    )


# ============================================================
# SECURITY VERIFICATION
# ============================================================

@app.route(
    "/verifySecurity",
    methods=["GET", "POST"]
)
def verifySecurity():

    user_id = session.get(
        "security_reset_user_id"
    )

    if not user_id:

        return redirect(
            url_for("forgot")
        )

    user = User.query.get(
        user_id
    )

    if user is None:

        clear_security_session()

        return redirect(
            url_for("forgot")
        )

    if not user.security_question or not user.security_answer:

        clear_security_session()

        return render_template(
            "forgot.html",
            error=(
                "Security verification is not configured "
                "for this account. Please log in and set it "
                "from your Profile."
            )
        )

    if request.method == "GET":

        return render_template(
            "security_verify.html",
            question=user.security_question
        )

    answer = request.form.get(
        "security_answer",
        ""
    ).strip()

    if not answer:

        flash(
            "Please enter your security answer.",
            "danger"
        )

        return redirect(
            url_for("verifySecurity")
        )

    attempts = session.get(
        "security_attempts",
        0
    )

    if attempts >= SECURITY_MAX_ATTEMPTS:

        clear_security_session()

        flash(
            "Too many incorrect attempts. Please try again.",
            "danger"
        )

        return redirect(
            url_for("forgot")
        )

    if not security_answer_matches(
        answer,
        user.security_answer
    ):

        attempts += 1

        session["security_attempts"] = attempts

        if attempts >= SECURITY_MAX_ATTEMPTS:

            clear_security_session()

            flash(
                "Too many incorrect attempts. Please try again.",
                "danger"
            )

            return redirect(
                url_for("forgot")
            )

        remaining = (
            SECURITY_MAX_ATTEMPTS
            - attempts
        )

        flash(
            f"Incorrect security answer. {remaining} attempts remaining.",
            "danger"
        )

        return redirect(
            url_for("verifySecurity")
        )

    session["security_verified"] = True

    session["reset_user_id"] = user.id

    session.pop(
        "security_reset_user_id",
        None
    )

    session.pop(
        "security_attempts",
        None
    )

    return redirect(
        url_for("reset")
    )


# ============================================================
# OUTPUT / AI PREDICTION
# ============================================================

@app.route(
    "/output",
    methods=["POST", "GET"]
)
def output():

    user = get_current_user()

    if user is None:

        return redirect(
            url_for("login")
        )

    image_path = ""

    result = None

    if request.method == "POST":

        if "imagefile" not in request.files:

            return render_template(
                "output.html",
                result="Please select an image.",
                image=""
            )

        image_file = request.files[
            "imagefile"
        ]

        if image_file.filename == "":

            return render_template(
                "output.html",
                result="Please select an image.",
                image=""
            )

        filename = secure_filename(
            image_file.filename
        )

        if not filename:

            return render_template(
                "output.html",
                result="Invalid image filename.",
                image=""
            )

        extension = (
            filename.rsplit(
                ".",
                1
            )[-1].lower()
            if "." in filename
            else ""
        )

        allowed_extensions = {
            "jpg",
            "jpeg",
            "png",
            "webp"
        }

        if extension not in allowed_extensions:

            return render_template(
                "output.html",
                result="Please upload JPG, JPEG, PNG or WEBP image.",
                image=""
            )

        model_value = request.form.get(
            "model",
            "0"
        )

        try:

            modelNo = int(
                model_value
            )

        except ValueError:

            modelNo = 0

        if modelNo not in range(3):

            modelNo = 0

        unique_filename = (
            f"{int(datetime.utcnow().timestamp())}_"
            f"{secrets.token_hex(4)}_"
            f"{filename}"
        )

        save_path = os.path.join(
            TEST_IMAGE_FOLDER,
            unique_filename
        )

        image_file.save(
            save_path
        )

        image_path = (
            "images/test/"
            + unique_filename
        )

        image = Image.open(
            save_path
        )

        prediction = classify.predict(
            image,
            modelNo
        )

        result = (
            "{} with a {:.2f}% Confidence.".format(
                prediction["class"],
                prediction["confidence_percent"]
            )
        )

        new_history = History(
            userId=user.id,
            result=result,
            image=image_path
        )

        db.session.add(
            new_history
        )

        db.session.commit()

        print(
            "New scan:",
            result
        )

    return render_template(
        "output.html",
        result=result,
        image=image_path
    )


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["POST"]
)
def register():

    username = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    newPass = request.form.get(
        "newPass",
        ""
    )

    confPass = request.form.get(
        "confPass",
        ""
    )

    security_question = request.form.get(
        "security_question",
        ""
    ).strip()

    security_answer = request.form.get(
        "security_answer",
        ""
    ).strip()


    if (
        not username
        or not email
        or not newPass
        or not confPass
        or not security_question
        or not security_answer
    ):

        return render_template(
            "login.html",
            regError="Please enter all required fields.",
            name=username,
            email=email,
            security_question=security_question,
            security_answer=security_answer,
            security_questions=SECURITY_QUESTIONS
        )


    if len(username) < 3:

        return render_template(
            "login.html",
            regError="Username must contain at least 3 characters.",
            name=username,
            email=email,
            security_question=security_question,
            security_answer=security_answer,
            security_questions=SECURITY_QUESTIONS
        )


    if not valid_email(email):

        return render_template(
            "login.html",
            regError="Please enter a valid email address.",
            name=username,
            email=email,
            security_question=security_question,
            security_answer=security_answer,
            security_questions=SECURITY_QUESTIONS
        )


    if len(newPass) < 6:

        return render_template(
            "login.html",
            regError="Password must contain at least 6 characters.",
            name=username,
            email=email,
            security_question=security_question,
            security_answer=security_answer,
            security_questions=SECURITY_QUESTIONS
        )


    if newPass != confPass:

        return render_template(
            "login.html",
            regError="Passwords do not match.",
            name=username,
            email=email,
            security_question=security_question,
            security_answer=security_answer,
            security_questions=SECURITY_QUESTIONS
        )


    if security_question not in SECURITY_QUESTIONS:

        return render_template(
            "login.html",
            regError="Please select a valid security question.",
            name=username,
            email=email,
            security_question="",
            security_answer=security_answer,
            security_questions=SECURITY_QUESTIONS
        )


    if len(security_answer) < 2:

        return render_template(
            "login.html",
            regError="Security answer must contain at least 2 characters.",
            name=username,
            email=email,
            security_question=security_question,
            security_answer=security_answer,
            security_questions=SECURITY_QUESTIONS
        )


    existing_username = User.query.filter_by(
        username=username
    ).first()

    if existing_username:

        return render_template(
            "login.html",
            regError="Username already exists.",
            name=username,
            email=email,
            security_question=security_question,
            security_answer=security_answer,
            security_questions=SECURITY_QUESTIONS
        )


    existing_email = User.query.filter_by(
        email=email
    ).first()

    if existing_email:

        return render_template(
            "login.html",
            regError="Email already exists.",
            name=username,
            email=email,
            security_question=security_question,
            security_answer=security_answer,
            security_questions=SECURITY_QUESTIONS
        )


    new_user = User(
        username=username,
        email=email,
        password=hash_password(
            newPass
        ),
        role="user",
        is_active=True,
        security_question=security_question,
        security_answer=hash_security_answer(
            security_answer
        )
    )


    try:

        db.session.add(
            new_user
        )

        db.session.commit()

    except IntegrityError:

        db.session.rollback()

        return render_template(
            "login.html",
            regError="Username or email already exists.",
            name=username,
            email=email,
            security_question=security_question,
            security_answer=security_answer,
            security_questions=SECURITY_QUESTIONS
        )


    return redirect(
        url_for("login")
    )


# ============================================================
# FORGOT PASSWORD
# ============================================================

@app.route(
    "/forgot",
    methods=["GET", "POST"]
)
def forgot():

    if request.method == "GET":

        return render_template(
            "forgot.html"
        )

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    if not email:

        return render_template(
            "forgot.html",
            error="Please enter your email address."
        )

    user = User.query.filter_by(
        email=email
    ).first()

    if user is None:

        return render_template(
            "forgot.html",
            error="No account was found with this email address."
        )

    if not user.is_active:

        return render_template(
            "forgot.html",
            error="This account is disabled."
        )

    if not user.security_question or not user.security_answer:

        return render_template(
            "forgot.html",
            error=(
                "Security verification is not configured "
                "for this account. Please log in and set it "
                "from your Profile."
            )
        )

    session.pop(
        "security_verified",
        None
    )

    session.pop(
        "reset_user_id",
        None
    )

    session["security_reset_user_id"] = user.id

    session["security_attempts"] = 0

    return redirect(
        url_for("verifySecurity")
    )


# ============================================================
# RESET PASSWORD
# ============================================================

@app.route(
    "/reset",
    methods=["GET", "POST"]
)
def reset():

    if not session.get(
        "security_verified"
    ):

        return redirect(
            url_for("forgot")
        )

    user_id = session.get(
        "reset_user_id"
    )

    user = User.query.get(
        user_id
    )

    if user is None:

        session.clear()

        return redirect(
            url_for("login")
        )

    if request.method == "GET":

        return render_template(
            "reset.html"
        )

    newPass = request.form.get(
        "newPass",
        ""
    )

    confPass = request.form.get(
        "confPass",
        ""
    )

    if len(newPass) < 6:

        return render_template(
            "reset.html",
            error="Password must contain at least 6 characters."
        )

    if newPass != confPass:

        return render_template(
            "reset.html",
            error="Passwords do not match."
        )

    user.password = hash_password(
        newPass
    )

    db.session.commit()

    session.clear()

    flash(
        "Password reset successfully. Please login.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["POST", "GET"]
)
def login():

    if request.method == "GET":

        return render_template(
            "login.html",
            security_questions=SECURITY_QUESTIONS
        )

    username_or_email = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    if (
        not username_or_email
        or not password
    ):

        return render_template(
            "login.html",
            loginError=(
                "Please enter username/email "
                "and password."
            )
        ,
            security_questions=SECURITY_QUESTIONS)

    user = User.query.filter(
        (User.username == username_or_email)
        |
        (User.email == username_or_email)
    ).first()

    if user is None:

        return render_template(
            "login.html",
            loginError=(
                "Username or email not found."
            )
        ,
            security_questions=SECURITY_QUESTIONS)

    if not user.is_active:

        return render_template(
            "login.html",
            loginError=(
                "Your account has been disabled. "
                "Please contact the administrator."
            )
        ,
            security_questions=SECURITY_QUESTIONS)

    if not password_matches(
        password,
        user.password
    ):

        return render_template(
            "login.html",
            loginError="Password Incorrect."
        ,
            security_questions=SECURITY_QUESTIONS)

    session.clear()

    session.permanent = True

    session["logged"] = True

    session["userId"] = user.id

    session["role"] = user.role

    print(
        "Logged in user:",
        user.username
    )

    return redirect(
        url_for("output")
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "GET":

        return render_template(
            "admin/login.html"
        )

    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    if not username or not password:

        return render_template(
            "admin/login.html",
            error="Please enter username and password."
        )

    admin = User.query.filter(
        User.username == username,
        User.role == "admin"
    ).first()

    if admin is None:

        return render_template(
            "admin/login.html",
            error="Invalid admin credentials."
        )

    if not admin.is_active:

        return render_template(
            "admin/login.html",
            error="Admin account is disabled."
        )

    if not password_matches(
        password,
        admin.password
    ):

        return render_template(
            "admin/login.html",
            error="Invalid admin credentials."
        )

    session.clear()

    session.permanent = True

    session["admin_logged"] = True

    session["adminId"] = admin.id

    session["role"] = "admin"

    return redirect(
        url_for("admin_dashboard")
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route(
    "/admin/logout"
)
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route(
    "/admin/dashboard"
)
def admin_dashboard():

    total_users = User.query.filter(
        User.role == "user"
    ).count()

    total_scans = History.query.count()

    today = datetime.utcnow().date()

    today_scans = History.query.filter(
        db.func.date(
            History.date_created
        ) == today
    ).count()

    active_users = User.query.filter(
        User.role == "user",
        User.is_active == True
    ).count()

    disabled_users = User.query.filter(
        User.role == "user",
        User.is_active == False
    ).count()

    disease_stats = {}

    for disease in class_names:

        disease_stats[disease] = History.query.filter(
            History.result.like(
                f"{disease}%"
            )
        ).count()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_scans=total_scans,
        today_scans=today_scans,
        active_users=active_users,
        disabled_users=disabled_users,
        disease_stats=disease_stats
    )


# ============================================================
# ADMIN USERS
# ============================================================

@app.route(
    "/admin/users"
)
def admin_users():

    users = User.query.filter(
        User.role == "user"
    ).order_by(
        User.id.desc()
    ).all()

    user_scan_counts = {}

    for user in users:

        user_scan_counts[user.id] = History.query.filter(
            History.userId == user.id
        ).count()

    return render_template(
        "admin/users.html",
        users=users,
        user_scan_counts=user_scan_counts
    )


# ============================================================
# ADMIN USER DETAILS
# ============================================================

@app.route(
    "/admin/users/<int:user_id>"
)
def admin_user_details(
    user_id
):

    user = User.query.get(
        user_id
    )

    if user is None:

        flash(
            "User not found.",
            "danger"
        )

        return redirect(
            url_for("admin_users")
        )

    history = History.query.filter(
        History.userId == user.id
    ).order_by(
        History.date_created.desc()
    ).all()

    return render_template(
        "admin/user_details.html",
        user=user,
        history=history
    )


# ============================================================
# ENABLE / DISABLE USER
# ============================================================

@app.route(
    "/admin/users/<int:user_id>/toggle",
    methods=["POST"]
)
def admin_toggle_user(
    user_id
):

    user = User.query.get(
        user_id
    )

    if user is None:

        flash(
            "User not found.",
            "danger"
        )

        return redirect(
            url_for("admin_users")
        )

    if user.role == "admin":

        flash(
            "Admin account cannot be disabled here.",
            "danger"
        )

        return redirect(
            url_for("admin_users")
        )

    user.is_active = not user.is_active

    db.session.commit()

    if user.is_active:

        flash(
            f"{user.username} has been enabled.",
            "success"
        )

    else:

        flash(
            f"{user.username} has been disabled.",
            "warning"
        )

    return redirect(
        url_for("admin_users")
    )


# ============================================================
# DELETE USER
# ============================================================

@app.route(
    "/admin/users/<int:user_id>/delete",
    methods=["POST"]
)
def admin_delete_user(
    user_id
):

    user = User.query.get(
        user_id
    )

    if user is None:

        flash(
            "User not found.",
            "danger"
        )

        return redirect(
            url_for("admin_users")
        )

    if user.role == "admin":

        flash(
            "Admin account cannot be deleted.",
            "danger"
        )

        return redirect(
            url_for("admin_users")
        )

    histories = History.query.filter(
        History.userId == user.id
    ).all()

    for history in histories:

        db.session.delete(
            history
        )

    if user.profile_image:

        profile_path = os.path.join(
            PROFILE_IMAGE_FOLDER,
            user.profile_image
        )

        if os.path.exists(
            profile_path
        ):

            try:

                os.remove(
                    profile_path
                )

            except Exception:

                pass

    db.session.delete(
        user
    )

    db.session.commit()

    flash(
        "User deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin_users")
    )


# ============================================================
# ADMIN ALL SCANS
# ============================================================

@app.route(
    "/admin/scans"
)
def admin_scans():

    scans = History.query.order_by(
        History.date_created.desc()
    ).all()

    scan_users = {}

    for scan in scans:

        scan_users[
            scan.userId
        ] = User.query.get(
            scan.userId
        )

    disease_stats = {}

    for disease in class_names:

        disease_stats[disease] = History.query.filter(
            History.result.like(
                f"{disease}%"
            )
        ).count()

    return render_template(
        "admin/scans.html",
        scans=scans,
        scan_users=scan_users,
        disease_stats=disease_stats
    )


# ============================================================
# ADMIN PROFILE
# ============================================================

@app.route(
    "/admin/profile"
)
def admin_profile():

    admin = User.query.get(
        session.get("adminId")
    )

    if admin is None:

        session.clear()

        return redirect(
            url_for("admin_login")
        )

    return render_template(
        "admin/profile.html",
        admin=admin
    )


# ============================================================
# ADMIN CHANGE PASSWORD
# ============================================================

@app.route(
    "/admin/changePassword",
    methods=["POST"]
)
def admin_change_password():

    admin = User.query.get(
        session.get("adminId")
    )

    if admin is None:

        session.clear()

        return redirect(
            url_for("admin_login")
        )

    current_password = request.form.get(
        "current_password",
        ""
    )

    new_password = request.form.get(
        "new_password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )

    if not current_password:

        flash(
            "Enter current password.",
            "danger"
        )

        return redirect(
            url_for("admin_profile")
        )

    if not password_matches(
        current_password,
        admin.password
    ):

        flash(
            "Current password is incorrect.",
            "danger"
        )

        return redirect(
            url_for("admin_profile")
        )

    if len(new_password) < 6:

        flash(
            "New password must contain at least 6 characters.",
            "danger"
        )

        return redirect(
            url_for("admin_profile")
        )

    if new_password != confirm_password:

        flash(
            "New passwords do not match.",
            "danger"
        )

        return redirect(
            url_for("admin_profile")
        )

    admin.password = hash_password(
        new_password
    )

    db.session.commit()

    flash(
        "Admin password updated successfully.",
        "success"
    )

    return redirect(
        url_for("admin_profile")
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    print(
        "\n=========================================="
    )

    print(
        "RiceLeafXNet Flask Application"
    )

    print(
        "=========================================="
    )

    print(
        "Local URL:"
    )

    print(
        f"http://127.0.0.1:{port}"
    )

    print(
        "Admin URL:"
    )

    print(
        f"http://127.0.0.1:{port}/admin/login"
    )

    print(
        "==========================================\n"
    )

    app.run(
        debug=True,
        port=port
    )