from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from deepface import DeepFace
from datetime import datetime
import os

app = Flask(__name__)

# --- Config ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'known_faces'
db = SQLAlchemy(app)

# --- User model ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))
    image_path = db.Column(db.String(200))

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')    

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        file = request.files['image']

        if file:
            filename = secure_filename(file.filename)
            unique_name = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            
            file.save(filepath)

            new_user = User(name=name, phone=phone, email=email, address=address, image_path=filepath)
            db.session.add(new_user)
            db.session.commit()

            return "✅ User Added Successfully!"

    return render_template('add_user.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        file = request.files['image']

        if not file:
            return "❌ No image uploaded"

        upload_path = "temp_upload.jpg"
        file.save(upload_path)

        users = User.query.all()
        matched_user = None

        for user in users:
            try:
                user_image_path = os.path.abspath(user.image_path).replace("\\", "/")
                print(f"Checking with: {user.name}, Path: {user_image_path}")

                result = DeepFace.verify(
                    img1_path=upload_path,
                    img2_path=user_image_path,
                    model_name='VGG-Face',
                    distance_metric='cosine',
                    enforce_detection=True,
                    threshold=0.3  # stricter threshold
                )
                
                print(f"Result for {user.name}: {result}")

                if result["verified"]:
                    matched_user = user
                    print(f"✅ Matched with: {user.name}")
                    break
                else:
                    print(f"❌ Not matched with: {user.name}")

            except Exception as e:
                print(f"Error checking with: {user.name}, Error: {e}")
                continue

        # ✅ Fixed: Check before remove
        if os.path.exists(upload_path):
            os.remove(upload_path)
            print("Temporary file removed successfully.")
        else:
            print("Temporary file not found, skipping remove.")

        if matched_user:
            return f"""
            ✅ Welcome {matched_user.name}!<br>
            Phone: {matched_user.phone}<br>
            Email: {matched_user.email}<br>
            Address: {matched_user.address}
            """
        else:
            return "❌ Face not recognized!"

    return render_template('login.html')

# --- Main ---
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    with app.app_context():
        db.create_all()
    app.run(debug=True)
