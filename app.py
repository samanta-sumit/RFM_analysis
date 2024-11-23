from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import model
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = 'uploaded_data.csv'
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            
            return redirect(url_for('top_customers'))
    return render_template('upload.html')



@app.route('/visualize', methods=['GET'])
def visualize():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_data.csv')
    data = model.load_data(file_path)
    stats, top_emails = model.visualize_data(data)
    
    return render_template('visualize.html', stats=stats.to_html(), top_emails=top_emails.to_html(index=False))
    

@app.route('/top_customers', methods=['GET', 'POST'])
def top_customers():
    num_customers = int(request.form.get('num_customers', 50))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_data.csv')
    data = model.load_data(file_path)
    top_customers = model.calculate_rfm(data)
    top_customers = top_customers.nlargest(num_customers, 'RFM_Score')
    return render_template('top_customers.html', customers=top_customers.to_dict(orient='records'))

@app.route('/send_coupons', methods=['POST'])
def send_coupons():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_data.csv')
    data = model.load_data(file_path)
    top_customers = model.calculate_rfm(data)
    for index, customer in top_customers.iterrows():
        email_body = f"""
        Dear Customer,

        Thank you for being a loyal customer! As a token of our appreciation, we are pleased to offer you a special coupon.

        Your coupon code is: {customer['Coupon_Code']}

        Enjoy your shopping!

        Best regards,
        Your Company
        """
        send_email(customer['Email'], "Exclusive Coupon for Loyal Customer", email_body)
    return "Coupons sent successfully!"

def send_email(to_email, subject, body):
    from_email = 'hardikspatil23@gmail.com'
    password = 'icsk guxc gftn kdyn'
    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, message.as_string())
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")


@app.route('/get_visualization_data', methods=['GET'])
def get_visualization_data():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_data.csv')
    data = model.load_data(file_path)
    _, top_emails = model.visualize_data(data)
    return top_emails.to_json(orient='records')


if __name__ == '__main__':
    app.run(debug=True)


