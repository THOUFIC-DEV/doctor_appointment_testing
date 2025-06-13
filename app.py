from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from flask_mail import Mail, Message
import requests
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Groq API config
GROQ_API_KEY = "API should be added here"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    response_text = ""
    if request.method == "POST":
        user_message = request.form.get("message", "")
        if not user_message:
            response_text = "Please enter a message."
        else:
            try:
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
    "model": "llama3-8b-8192",
    "messages": [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant for a doctor appointment system. "
                "If the user asks any questions not related to the medical field, answer them politely, "
                "informing them that you are not trained for general queries unrelated to healthcare."
            )
        },
        {
            "role": "user",
            "content": (
                "You are medical assistant to support user to book appointments and give suggestions to based on their symptoms\n"
                "🔹 Intent: Find Doctors by Specialization and Location\n"
                'User says:\n\n"I need a cardiologist in Chennai"\n'
                '"Show dermatologists in Coimbatore"\n'
                '"Are there any neurologists available in Madurai?"\n\n'
                "Bot should respond with (template logic):\n\n"
                "Here are some Cardiologists available in Chennai:\n"
                "Dr. Arjun – Fee: ₹600, Timings: 09:00 - 17:00\n"
                "Dr. Bala – Fee: ₹500, Timings: 10:00 - 18:00\n"
                "Dr. Ajeez – Fee: ₹750, Timings: 12:00 - 00:00\n"
                "Dr. Barath – Fee: ₹650, Timings: 10:00 - 18:00\n\n"
                "🔹 Intent: Ask for Cheapest Doctor in City/Specialty\n"
                'User says:\n\n"Who is the cheapest cardiologist in Tutucorin?"\n'
                '"Lowest fee dermatologist in Madurai?"\n\n'
                "Bot responds:\n\n"
                "The most affordable Dermatologist in Madurai is Dr. Revathi.\n"
                "Fee: ₹300, Timings: 10:00 - 18:00\n\n"
                "🔹 Intent: Doctor's Availability\n"
                'User says:\n\n"What time is Dr. Surya available?"\n'
                '"Is Dr. Kiran available after 5 PM?"\n\n'
                "Bot responds:\n\n"
                "Dr. Surya is available from 09:30 to 17:30 in Madurai (Specialization: Cardiology).\n"
                "Please ensure to book within those hours.\n\n"
                "🔹 Intent: Book Appointment / Simulate Appointment Flow\n"
                'User says:\n\n"I want to book an appointment with Dr. Gowri"\n'
                '"Schedule me with a general physician in Trichy"\n\n'
                "Bot responds:\n\n"
                "You are requesting an appointment with Dr. Gowri (Dermatologist in Chennai).\n"
                "Consultation Fee: ₹450\n"
                "Available: 10:00 - 18:00\n"
                "Shall I go ahead and book your slot?\n\n"
                "🔹 Intent: List Doctors by Specialization\n"
                'User says:\n\n"List all neurologists in Tamil Nadu"\n'
                '"Which cities have dermatologists?"\n\n'
                "Bot responds:\n\n"
                "Here are cities with Neurologists:\n\n"
                "Chennai: Dr. Vasanth, Dr. Sathya, Dr. Sri\n"
                "Coimbatore: Dr. Vijay, Dr. Anitha, Dr. Ajay\n"
                "Madurai: Dr. Divya, Dr. Ramya, Dr. Reni\n"
                "Trichy: Dr. Nithya, Dr. Shravan, Dr. Joseph\n"
                "Tutucorin: Dr. Yamini, Dr. Devi, Dr. Guru\n\n"
                "🔹 Intent: Find Doctors by Time Availability\n"
                'User says:\n\n"Who is available between 9 to 11 AM in Coimbatore?"\n'
                '"Doctors available after 5 PM in Trichy"\n\n'
                "Bot responds:\n\n"
                "In Coimbatore between 09:00 to 11:00:\n"
                "Dr. Vikram (Cardiology, 09:30 - 17:30)\n"
                "Dr. Subha (Dermatology, 09:30 - 17:30)\n\n"
                "🔹 Intent: General Medical Guidance\n"
                'User says:\n\n"What kind of doctor should I see for skin issues?"\n'
                '"Which specialist treats chest pain?"\n\n'
                "Bot responds:\n\n"
                "For skin-related issues, you should consult a Dermatologist.\n"
                "For chest pain, it's recommended to consult a Cardiologist."
            )
        },
        {
            "role": "user",
            "content": user_message 
        }
    ]
}

                groq_response = requests.post(GROQ_API_URL, headers=headers, json=data)
                groq_response.raise_for_status()
                result = groq_response.json()
                response_text = result["choices"][0]["message"]["content"]
            except Exception as e:
                response_text = f"Error: {str(e)}"
    
    return render_template("chatbot.html", response=response_text)


# After app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mohamedthoufic00447@gmail.com'        
app.config['MAIL_PASSWORD'] = 'gbxt blxw xnno mmjc'           
app.config['MAIL_DEFAULT_SENDER'] = 'mohamedthoufic00447@gmail.com'

mail = Mail(app)

def send_email(to, subject, body):
    if not to:
        print("No recipient email provided. Skipping email send.")
        return
    try:
        msg = Message(subject, recipients=[to])
        msg.body = body
        mail.send(msg)
        print(f"Email sent successfully to {to}")
    except Exception as e:
        print(f"Failed to send email to {to}: {str(e)}")
        raise  # re-raise to propagate error for debugging


# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new_database_fresh.db'
db = SQLAlchemy(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)  # <-- Add this line


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False, default='password')
    location = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=True)
    consultation_fee = db.Column(db.Integer, nullable=True)
    start_time = db.Column(db.String(5))
    end_time = db.Column(db.String(5))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Confirmed, Canceled
    comment = db.Column(db.String(255))


    # Relationships
    doctor = db.relationship('Doctor', backref='appointments')
    patient = db.relationship('User', backref='appointments')


class BlockedSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)
    reason = db.Column(db.String(150), default='Offline')

    doctor = db.relationship('Doctor', backref='blocked_slots')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another.', 'warning')
            return redirect(url_for('register'))

        new_user = User(name=name, username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in. Don’t forget to check out our Chatbot for quick assistance.', 'info')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('book_appointment'))
        return "Invalid credentials"

    return render_template('login.html')

@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        doctor = Doctor.query.filter_by(name=name, password=password).first()
        if doctor:
            session['doctor_id'] = doctor.id
            return redirect(url_for('doctor_dashboard'))
        return "Invalid doctor credentials"
    return render_template('doctor_login.html')

@app.route('/doctor/dashboard', methods=['GET', 'POST'])
def doctor_dashboard():
    if 'doctor_id' not in session:
        return redirect(url_for('doctor_login'))

    doctor = Doctor.query.get(session['doctor_id'])

    if request.method == 'POST':
        if 'action' in request.form and 'appointment_id' in request.form:
            appointment_id = int(request.form['appointment_id'])
            action = request.form['action']
            comment = request.form.get('comment', '')
            appointment = Appointment.query.get(appointment_id)

            if appointment and appointment.doctor_id == doctor.id:
                if action == 'confirm':
                    appointment.status = 'Confirmed'
                    appointment.comment = comment  # Save comment
                elif action == 'cancel':
                    appointment.status = 'Canceled'
                    appointment.comment = comment  # Save comment

                db.session.commit()
                flash(f"Appointment {action}ed successfully", "success")
            else:
                flash("Unauthorized action or appointment not found", "danger")

            return redirect(url_for('doctor_dashboard'))

        # Blocked slot logic
        date = request.form.get('blocked_date')
        start_time = request.form.get('blocked_start_time')
        end_time = request.form.get('blocked_end_time')
        reason = request.form.get('blocked_reason', 'Offline')

        if not date or not start_time or not end_time:
            flash("Please fill all slot blocking fields", "danger")
            return redirect(url_for('doctor_dashboard'))

        try:
            st = datetime.strptime(start_time, "%H:%M").time()
            et = datetime.strptime(end_time, "%H:%M").time()
            if et <= st:
                flash("End time must be after start time", "danger")
                return redirect(url_for('doctor_dashboard'))
        except ValueError:
            flash("Invalid time format for blocked slot", "danger")
            return redirect(url_for('doctor_dashboard'))

        new_slot = BlockedSlot(
            doctor_id=doctor.id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            reason=reason
        )
        db.session.add(new_slot)
        db.session.commit()
        flash("Blocked slot added successfully", "success")
        return redirect(url_for('doctor_dashboard'))

    appointments = Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.date, Appointment.time).all()
    blocked_slots = BlockedSlot.query.filter_by(doctor_id=doctor.id).order_by(BlockedSlot.date.desc()).all()

    return render_template('doctor_dashboard.html', doctor=doctor, appointments=appointments, blocked_slots=blocked_slots)

@app.route('/delete_blocked_slot/<int:slot_id>', methods=['POST'])
def delete_blocked_slot(slot_id):
    if 'doctor_id' not in session:
        return redirect(url_for('doctor_login'))

    slot = BlockedSlot.query.get(slot_id)
    if slot and slot.doctor_id == session['doctor_id']:
        db.session.delete(slot)
        db.session.commit()
        flash("Blocked slot deleted", "success")
    else:
        flash("Blocked slot not found or unauthorized", "danger")
    return redirect(url_for('doctor_dashboard'))

@app.route('/book', methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    locations = db.session.query(Doctor.location).distinct().all()
    specializations = db.session.query(Doctor.specialization).distinct().all()
    selected_location = request.args.get('location')
    selected_specialization = request.args.get('specialization')
    max_fee = request.args.get('max_fee')

    doctor_query = Doctor.query

    if selected_location:
        doctor_query = doctor_query.filter_by(location=selected_location)
    if selected_specialization:
        doctor_query = doctor_query.filter_by(specialization=selected_specialization)
    if max_fee:
        try:
            max_fee_int = int(max_fee)
            doctor_query = doctor_query.filter(Doctor.consultation_fee <= max_fee_int)
        except ValueError:
            pass
    
    appointments = Appointment.query.options(joinedload(Appointment.doctor)).filter_by(patient_id=session['user_id']).all()


    doctors = doctor_query.all()

    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        date = request.form['date']
        time = request.form['time']

        if not doctor_id or not date or not time:
            return "All fields are required", 400

        doctor = Doctor.query.get(int(doctor_id))
        if not doctor:
            return "Doctor not found", 400

        try:
            appointment_time = datetime.strptime(time, "%H:%M").time()
            start = datetime.strptime(doctor.start_time, "%H:%M").time()
            end = datetime.strptime(doctor.end_time, "%H:%M").time()
        except ValueError:
            return "Invalid time format", 400

        if not (start <= appointment_time <= end):
            return f"Doctor is only available between {doctor.start_time} and {doctor.end_time}.", 400

        blocked = BlockedSlot.query.filter_by(doctor_id=int(doctor_id), date=date).filter(
            BlockedSlot.start_time <= time, BlockedSlot.end_time > time).first()
        if blocked:
            return f"Selected time {time} is blocked for {blocked.reason}. Please choose another slot.", 400

        existing = Appointment.query.filter_by(doctor_id=int(doctor_id), date=date, time=time).first()
        if existing:
            return "This time slot is already booked for the selected doctor."

        appointment = Appointment(
            doctor_id=int(doctor_id),
            date=date,
            time=time,
            patient_id=session['user_id']
        )
        db.session.add(appointment)
        db.session.commit()
        return redirect(url_for('view_appointments'))

    return render_template('book_appointment.html', doctors=doctors, locations=locations, specializations=specializations, selected_location=selected_location, selected_specialization=selected_specialization, max_fee=max_fee)

@app.route('/confirm_appointment/<int:appointment_id>', methods=['POST'])
def confirm_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        appointment.status = 'Confirmed'
        appointment.comment = request.form.get('comment', '')
        db.session.commit()

        send_email(
            to=appointment.patient.email,
            subject="Your Appointment is Confirmed",
            body=f"Dear {appointment.patient.name},\n\nYour appointment with Dr. {appointment.doctor.name} on {appointment.date} at {appointment.time} has been confirmed.\n\nComments: {appointment.comment or 'None'}\n\nThank you."
        )
        flash('Appointment confirmed with comment.', 'success')
    return redirect(url_for('doctor_dashboard'))

@app.route('/cancel_appointment/<int:appointment_id>')
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if appointment:
        appointment.status = 'Canceled'
        
        db.session.commit()

        # Send cancellation email to patient
        send_email(
            to=appointment.patient.email,
            subject="Your Appointment is Canceled",
            body=f"Dear {appointment.patient.name},\n\nYour appointment with Dr. {appointment.doctor.name} on {appointment.date} at {appointment.time} has been canceled.\n\nPlease contact us for rescheduling."
        )
        flash('Appointment cancelled with comment.', 'unsuccess')
    return redirect(url_for('doctor_dashboard'))

@app.route('/view_appointments')
def view_appointments():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    appointments = Appointment.query.filter_by(patient_id=session['user_id']).all()
    return render_template('view_appointments.html', appointments=appointments)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/test_email")
def test_email():
    try:
        send_email("mohamedthoufic00447@gmail.com", "Test Email", "This is a test email from Flask.")
        return "Email sent!"
    except Exception as e:
        return f"Error sending email: {e}"

if __name__ == '__main__':
    if os.path.exists('new_database_fresh.db'):
        os.remove('new_database_fresh.db')

    with app.app_context():
        db.create_all()
        if Doctor.query.count() == 0:
            db.session.add_all([
                Doctor(name='Arjun', password='arjun123', location='Chennai', specialization='Cardiology', consultation_fee=600, start_time='09:00', end_time='17:00'),
                Doctor(name='Bala', password='bala123', location='Chennai', specialization='Cardiology', consultation_fee=500, start_time='10:00', end_time='18:00'),
                Doctor(name='Ajeez', password='ajeez123', location='Chennai', specialization='Cardiology', consultation_fee=750, start_time='12:00', end_time='00:00'),
                Doctor(name='Barath', password='barath123', location='Chennai', specialization='Cardiology', consultation_fee=650, start_time='10:00', end_time='18:00'),

                Doctor(name='Dinesh', password='dinesh123', location='Coimbatore', specialization='Cardiology', consultation_fee=600, start_time='09:30', end_time='17:30'),
                Doctor(name='Mohan', password='mohan123', location='Coimbatore', specialization='Cardiology', consultation_fee=800, start_time='10:00', end_time='18:00'),
                Doctor(name='Vikram', password='vikram123', location='Coimbatore', specialization='Cardiology', consultation_fee=500, start_time='09:30', end_time='17:30'),
                Doctor(name='Vinodh', password='vinodh123', location='Coimbatore', specialization='Cardiology', consultation_fee=700, start_time='10:00', end_time='18:00'),

                Doctor(name='Karthik', password='karthik123', location='Madurai', specialization='Cardiology', consultation_fee=650, start_time='09:30', end_time='17:30'),
                Doctor(name='Anand', password='anand123', location='Madurai', specialization='Cardiology', consultation_fee=550, start_time='10:00', end_time='18:00'),
                Doctor(name='Surya', password='surya123', location='Madurai', specialization='Cardiology', consultation_fee=350, start_time='09:30', end_time='17:30'),
                Doctor(name='Jaya', password='jaya123', location='Madurai', specialization='Cardiology', consultation_fee=400, start_time='10:00', end_time='18:00'),
                
                Doctor(name='Kavitha', password='kavitha123', location='Trichy', specialization='Cardiology', consultation_fee=700, start_time='09:00', end_time='17:00'),
                Doctor(name='Priya', password='priya123', location='Trichy', specialization='Cardiology', consultation_fee=650, start_time='10:00', end_time='18:00'),
                Doctor(name='Nivetha', password='nivetha123', location='Trichy', specialization='Cardiology', consultation_fee=500, start_time='09:00', end_time='17:00'),
                Doctor(name='Priya', password='priya123', location='Trichy', specialization='Cardiology', consultation_fee=450, start_time='10:00', end_time='18:00'),
                
                Doctor(name='Sneha', password='sneha123', location='Tutucorin', specialization='Cardiology', consultation_fee=300, start_time='09:00', end_time='17:00'),
                Doctor(name='Lavanya', password='lavanya123', location='Tutucorin', specialization='Cardiology', consultation_fee=400, start_time='10:00', end_time='18:00'),
                Doctor(name='Pavi', password='pavi123', location='Tutucorin', specialization='Cardiology', consultation_fee=350, start_time='09:00', end_time='17:00'),
                Doctor(name='Jaanu', password='jaanu23', location='Tutucorin', specialization='Cardiology', consultation_fee=500, start_time='10:00', end_time='18:00'),

                # Dermatology
                Doctor(name='Meena', password='meena123', location='Chennai', specialization='Dermatology', consultation_fee=350, start_time='09:00', end_time='17:00'),
                Doctor(name='Gowri', password='gowri123', location='Chennai', specialization='Dermatology', consultation_fee=450, start_time='10:00', end_time='18:00'),
                Doctor(name='Abdur', password='abdur123', location='Chennai', specialization='Dermatology', consultation_fee=500, start_time='09:00', end_time='17:00'),
                Doctor(name='Gowshik', password='gowshik123', location='Chennai', specialization='Dermatology', consultation_fee=600, start_time='10:00', end_time='18:00'),

                Doctor(name='Swarna', password='swarna123', location='Coimbatore', specialization='Dermatology', consultation_fee=700, start_time='09:30', end_time='17:30'),
                Doctor(name='Shruthi', password='shruthi123', location='Coimbatore', specialization='Dermatology', consultation_fee=600, start_time='10:00', end_time='18:00'),
                Doctor(name='Subha', password='subha123', location='Coimbatore', specialization='Dermatology', consultation_fee=500, start_time='09:30', end_time='17:30'),
                Doctor(name='Preethi', password='preethi123', location='Coimbatore', specialization='Dermatology', consultation_fee=350, start_time='10:00', end_time='18:00'),

                Doctor(name='Fathima', password='fathima123', location='Madurai', specialization='Dermatology', consultation_fee=500, start_time='09:00', end_time='17:00'),
                Doctor(name='Razeena', password='razeena123', location='Madurai', specialization='Dermatology', consultation_fee=400, start_time='10:00', end_time='18:00'),
                Doctor(name='Yaser', password='yaser123', location='Madurai', specialization='Dermatology', consultation_fee=350, start_time='09:00', end_time='17:00'),
                Doctor(name='Revathi', password='revathi123', location='Madurai', specialization='Dermatology', consultation_fee=300, start_time='10:00', end_time='18:00'),

                Doctor(name='Kiran', password='kiran123', location='Trichy', specialization='Dermatology', consultation_fee=600, start_time='09:00', end_time='17:00'),
                Doctor(name='Sindu', password='sindu123', location='Trichy', specialization='Dermatology', consultation_fee=500, start_time='10:00', end_time='18:00'),
                Doctor(name='Vimal', password='vimal123', location='Trichy', specialization='Dermatology', consultation_fee=350, start_time='09:00', end_time='17:00'),
                Doctor(name='Bindu', password='bindu123', location='Trichy', specialization='Dermatology', consultation_fee=400, start_time='10:00', end_time='18:00'),

                Doctor(name='Malar', password='malar123', location='Tutucorin', specialization='Dermatology', consultation_fee=400, start_time='09:00', end_time='17:00'),
                Doctor(name='Indhu', password='indhu123', location='Tutucorin', specialization='Dermatology', consultation_fee=300, start_time='10:00', end_time='18:00'),
                Doctor(name='Tamil', password='tamil123', location='Tutucorin', specialization='Dermatology', consultation_fee=500, start_time='09:00', end_time='17:00'),
                Doctor(name='Ameer', password='ameer123', location='Tutucorin', specialization='Dermatology', consultation_fee=600, start_time='10:00', end_time='18:00'),

                # Similarly add for Neurology
                Doctor(name='Vasanth', password='vasanth123', location='Chennai', specialization='Neurology', consultation_fee=600, start_time='09:00', end_time='17:00'),
                Doctor(name='Sathya', password='sathya123', location='Chennai', specialization='Neurology', consultation_fee=450, start_time='10:00', end_time='18:00'),
                Doctor(name='Sri', password='sri123', location='Chennai', specialization='Neurology', consultation_fee=500, start_time='10:00', end_time='18:00'),

                Doctor(name='Vijay', password='vijay123', location='Coimbatore', specialization='Neurology', consultation_fee=775, start_time='09:00', end_time='17:00'),
                Doctor(name='Anitha', password='anitha123', location='Coimbatore', specialization='Neurology', consultation_fee=600, start_time='10:00', end_time='18:00'),
                Doctor(name='Ajay', password='ajay123', location='Coimbatore', specialization='Neurology', consultation_fee=550, start_time='09:00', end_time='17:00'),
                
                Doctor(name='Divya', password='divya123', location='Madurai', specialization='Neurology', consultation_fee=350, start_time='09:00', end_time='17:00'),
                Doctor(name='Ramya', password='ramya123', location='Madurai', specialization='Neurology', consultation_fee=400, start_time='10:00', end_time='18:00'),
                 Doctor(name='Reni', password='reni23', location='Madurai', specialization='Neurology', consultation_fee=500, start_time='10:00', end_time='18:00'),

                Doctor(name='Nithya', password='nithya123', location='Trichy', specialization='Neurology', consultation_fee=700, start_time='09:00', end_time='17:00'),
                Doctor(name='Shravan', password='shravan123', location='Trichy', specialization='Neurology', consultation_fee=600, start_time='10:00', end_time='18:00'),
                Doctor(name='Joseph', password='joseph123', location='Trichy', specialization='Neurology', consultation_fee=500, start_time='09:00', end_time='17:00'),
           

                Doctor(name='Yamini', password='yamini123', location='Tutucorin', specialization='Neurology', consultation_fee=500, start_time='09:00', end_time='17:00'),
                Doctor(name='Devi', password='devi123', location='Tutucorin', specialization='Neurology', consultation_fee=400, start_time='10:00', end_time='18:00'),
                Doctor(name='Guru', password='guru123', location='Tutucorin', specialization='Neurology', consultation_fee=300, start_time='09:00', end_time='17:00'),

                # Similarly add for Orthopedics
                Doctor(name='Suresh', password='suresh123', location='Chennai', specialization='Orthopedics', consultation_fee=480, start_time='10:00', end_time='18:00'),
                Doctor(name='Gokul', password='gokul123', location='Chennai', specialization='Orthopedics', consultation_fee=520, start_time='09:00', end_time='17:00'),

                Doctor(name='Lakshmi', password='lakshmi123', location='Coimbatore', specialization='Orthopedics', consultation_fee=725, start_time='09:30', end_time='17:30'),
                Doctor(name='Balaji', password='balaji123', location='Coimbatore', specialization='Orthopedics', consultation_fee=775, start_time='10:00', end_time='18:00'),

                Doctor(name='Vijaya', password='vijaya123', location='Madurai', specialization='Orthopedics', consultation_fee=375, start_time='10:00', end_time='18:00'),
                Doctor(name='Kiran', password='kiran123', location='Madurai', specialization='Orthopedics', consultation_fee=425, start_time='09:00', end_time='17:00'),

                Doctor(name='Sathish', password='sathish123', location='Trichy', specialization='Orthopedics', consultation_fee=800, start_time='10:00', end_time='18:00'),
                Doctor(name='Shalini', password='shalini123', location='Trichy', specialization='Orthopedics', consultation_fee=770, start_time='09:00', end_time='17:00'),

                Doctor(name='Gopi', password='gopi123', location='Tutucorin', specialization='Orthopedics', consultation_fee=300, start_time='10:00', end_time='18:00'),
                Doctor(name='Mani', password='mani123', location='Tutucorin', specialization='Orthopedics', consultation_fee=275, start_time='09:00', end_time='17:00'),

                # General Medicine
                Doctor(name='Shree', password='shree123', location='Chennai', specialization='General Medicine', consultation_fee=550, start_time='08:30', end_time='16:30'),
                Doctor(name='Kiranmayi', password='kiranmayi123', location='Chennai', specialization='General Medicine', consultation_fee=600, start_time='09:00', end_time='17:00'),
                Doctor(name='Sameera', password='sameera123', location='Chennai', specialization='General Medicine', consultation_fee=400, start_time='09:00', end_time='17:00'),
                Doctor(name='Ajmal', password='ajmal123', location='Chennai', specialization='General Medicine', consultation_fee=500, start_time='09:00', end_time='17:00'),

                Doctor(name='Kavya', password='kavya123', location='Coimbatore', specialization='General Medicine', consultation_fee=800, start_time='08:30', end_time='16:30'),
                Doctor(name='Bhaskar', password='bhaskar123', location='Coimbatore', specialization='General Medicine', consultation_fee=650, start_time='09:00', end_time='17:00'),
                Doctor(name='Nikitha', password='nikitha123', location='Coimbatore', specialization='General Medicine', consultation_fee=500, start_time='09:00', end_time='17:00'),
                Doctor(name='Suresh', password='suresh123', location='Coimbatore', specialization='General Medicine', consultation_fee=400, start_time='09:00', end_time='17:00'),

                Doctor(name='Parth', password='parth123', location='Madurai', specialization='General Medicine', consultation_fee=500, start_time='08:30', end_time='16:30'),
                Doctor(name='Ishwarya', password='ishwarya123', location='Madurai', specialization='General Medicine', consultation_fee=300, start_time='09:00', end_time='17:00'),
                Doctor(name='Parveen', password='parveen123', location='Madurai', specialization='General Medicine', consultation_fee=400, start_time='08:30', end_time='16:30'),
                Doctor(name='Soori', password='soori123', location='Madurai', specialization='General Medicine', consultation_fee=350, start_time='09:00', end_time='17:00'),

                Doctor(name='Vivek', password='vivek123', location='Trichy', specialization='General Medicine', consultation_fee=800, start_time='08:30', end_time='16:30'),
                Doctor(name='Lalitha', password='lalitha123', location='Trichy', specialization='General Medicine', consultation_fee=780, start_time='09:00', end_time='17:00'),
                Doctor(name='Yogi', password='yogi123', location='Trichy', specialization='General Medicine', consultation_fee=600, start_time='08:30', end_time='16:30'),

                Doctor(name='Usha', password='usha123', location='Tutucorin', specialization='General Medicine', consultation_fee=300, start_time='08:30', end_time='16:30'),
                Doctor(name='Ganga', password='ganga123', location='Tutucorin', specialization='General Medicine', consultation_fee=280, start_time='09:00', end_time='17:00'),
            ])
            db.session.commit()

    app.run(debug=True)
