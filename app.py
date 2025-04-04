# app.py
from flask import Flask, render_template, request, redirect, session, url_for
from auth import auth_bp
from email_template import generate_email_variants
from email_utils import send_email, save_draft, schedule_email
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.register_blueprint(auth_bp)

@app.route('/')
def login():
    if 'credentials' in session:
        return redirect(url_for('founder_form'))
    return render_template('login.html')

@app.route('/form', methods=['GET', 'POST'])
def founder_form():
    if request.method == 'POST':
        session['founder_data'] = request.form.to_dict()
        return redirect(url_for('generate_emails'))
    return render_template('form.html')

@app.route('/generate_emails')
def generate_emails():
    founder_data = session.get('founder_data')
    if not founder_data:
        return redirect(url_for('founder_form'))
    print(founder_data)
    email_variants = generate_email_variants(founder_data)
    session['email_variants'] = email_variants
    return redirect(url_for('preview_emails'))

@app.route('/preview')
def preview_emails():
    return render_template("preview.html", emails=session.get('email_variants', {}))

@app.route('/edit_email', methods=['POST'])
def edit_email_redirect():
    selected = request.form.get('selected_variant')
    return redirect(url_for('edit_email', variant=selected))

@app.route('/edit/<variant>', methods=['GET', 'POST'])
def edit_email(variant):
    email = session['email_variants'].get(variant)
    if not email:
        return "Invalid email variant", 404

    if request.method == 'POST':
        session['selected_email'] = {
            'subject': request.form['subject'],
            'body': request.form['body']
        }
        return redirect(url_for('finalize_email'))

    return render_template("edit.html", subject=email['subject'], body=email['body'])

@app.route("/finalize", methods=["GET", "POST"])
def finalize_email():
    # Check if selected email is stored in the session
    if 'selected_email' not in session:
        return redirect(url_for("preview_emails"))  # Redirect if no email was selected
    
    subject = session['selected_email'].get('subject', '')
    body = session['selected_email'].get('body', '')

    if request.method == "POST":
        if "credentials" not in session:
            return redirect(url_for("auth.login"))
        
        to_emails = request.form.get("to_emails", "")
        # Convert to list of trimmed emails
        to_emails_list = [email.strip() for email in to_emails.split(",") if email.strip()]
        if not to_emails_list:
            return "No recipient emails provided.", 400
        
        # Get the action (Send, Schedule, or Draft)
        action = request.form.get("action")

        if action == "send":
            # Send the email
            send_email(subject, body, to_emails_list)
            # Optionally store the selected email details in session
            session['selected_email'] = {'subject': subject, 'body': body}
            return redirect(url_for("finalize_email"))  # Redirect after sending the email
        
        elif action == "schedule":
            # Schedule the email (implement the scheduling logic)
            schedule_email(subject, body, to_emails_list)
            return redirect(url_for("finalize_email"))  # Redirect after scheduling the email
        
        elif action == "draft":
            # Save as draft (implement the save draft logic)
            save_draft(subject, body, to_emails_list)
            return redirect(url_for("finalize_email"))  # Redirect after saving as draft

    # For GET request, pass the subject and body values
    email = {
        "subject": subject,
        "body": body,
    }

    return render_template("finalize.html", email=email)

if __name__ == '__main__':
    app.run(debug=True)
