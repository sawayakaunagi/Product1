import os
import smtplib
import mimetypes
from email.message import EmailMessage
from flask import Flask, render_template, request, redirect, flash
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'csv', 'docx'])

EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "secret")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_mail_with_attachment(subject, body, file_path, email_to):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = email_to
    msg.set_content(body)

    if file_path:
        ctype, encoding = mimetypes.guess_type(file_path)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(file_path, "rb") as f:
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(file_path))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email_to = request.form.get('email_to')
        file = request.files.get('file')
        if not email_to or not file or file.filename == '':
            flash('メールアドレスとファイルを入力してください')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('許可されていないファイル形式です')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        try:
            send_mail_with_attachment(
                subject="自動送信ファイル",
                body="オオタユウトさんから送られてきました。",
                file_path=filepath,
                email_to=email_to
            )
            flash('メール送信完了')
        except Exception as e:
            flash(f'送信エラー: {e}')
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
        return redirect(request.url)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
