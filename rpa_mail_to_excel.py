import os
import sys
import smtplib
import mimetypes
from email.message import EmailMessage

# --- 環境変数から設定を取得 ---
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
EMAIL_TO = os.environ.get("EMAIL_TO")  # 送信先（複数ならカンマ区切り）

def send_mail_with_attachment(subject, body, file_path):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg.set_content(body)

    # 添付ファイル
    if file_path:
        ctype, encoding = mimetypes.guess_type(file_path)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(file_path, "rb") as f:
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(file_path))

    # Gmail SMTP
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)
    print("メール送信完了")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ファイルパスをコマンドライン引数で指定してください。例: python rpa_mail_to_excel.py /path/to/file.pdf")
        exit(1)
    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"指定されたファイルが存在しません: {file_path}")
        exit(1)
    subject = "自動送信ファイル"
    body = "オオタユウトさんから送られてきました。"
    send_mail_with_attachment(subject, body, file_path)
