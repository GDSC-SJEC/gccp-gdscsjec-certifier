from flask import Flask, render_template, redirect, request, flash, url_for, jsonify, abort, send_from_directory, make_response
from flask_sqlalchemy import SQLAlchemy
import datetime, os
import json
import csv
import io
import webbrowser
from time import sleep

app = Flask(__name__)

app.secret_key = "GDSCSJEC"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///certs.db"

db = SQLAlchemy(app)


class Fonts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    font_cdn = db.Column(db.String(500), nullable=True)

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    # is_email_sent = db.Column(db.Boolean, default=False)
    coursename = db.Column(db.String(500), nullable=False)
    # last_update = db.Column(db.String(50), nullable=False, default=x)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    qrcode = db.relationship('QRCode', cascade="all,delete", backref='qrcode')

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    textColor = db.Column(db.String(50), nullable=True)
    bg_image = db.Column(db.String(500), nullable=True)
    font_size = db.Column(db.Integer, nullable=False)
    font_name = db.Column(db.String(250), nullable=False)
    certx = db.Column(db.Integer, nullable=False)
    certy = db.Column(db.Integer, nullable=False)
    qrx = db.Column(db.Integer, nullable=False)
    qry = db.Column(db.Integer, nullable=False)
    certnox = db.Column(db.Integer, nullable=False)
    certnoy = db.Column(db.Integer, nullable=False)
    prefix = db.Column(db.String(20), default='CGV')
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    certificates = db.relationship(
        'Certificate', cascade="all,delete", backref='certificates')



class QRCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    certificate_num = db.Column(db.String(50), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    qr_code = db.Column(db.String(100), nullable=True)
    certificate_id = db.Column(db.Integer, db.ForeignKey('certificate.id'))


@app.route("/")
def dashboard_page():
    postc = len(Certificate.query.order_by(Certificate.id).all())
    return render_template('dashboard.html', favTitle="Hello world", postc=postc)

@app.route('/get-all-fonts', methods=['GET'])
def get_all_fonts():
    fonts = Fonts.query.order_by(Fonts.id).all()
    data = {'font': [fonts.name for fonts in fonts]}
    return jsonify(data)

@app.route("/edit/group/<string:id>", methods=['GET', 'POST'])
def edit_org_page(id):
    if request.method == 'POST':
        name = request.form.get("name")
        certx = request.form.get("certx")
        certy = request.form.get("certy")
        qrx = request.form.get("qrx")
        qry = request.form.get("qry")
        certnox = request.form.get("certnox")
        certnoy = request.form.get("certnoy")
        font_size = request.form.get("font_size")
        font_name = request.form.get("font_name")
        textColor = request.form.get("textColor")
        bg_image = request.files.get("bg_image")
        prefix = request.form.get("prefix")
        date = datetime.datetime.now()
        if id == '0':
            try:
                post = Group(name=name, textColor=textColor, font_size=font_size, font_name=font_name,  certx=certx, certy=certy, qrx=qrx, qry=qry,
                             certnox=certnox, certnoy=certnoy, prefix=prefix, date=date)
                img_name = name.replace(" ", "+")
                if not app.debug:
                    # upload_image(bg_image, folder="backgrounds", name=name)
                    # bg_url = f"https://cgv.s3.us-east-2.amazonaws.com/backgrounds/{img_name}.png"
                    # bg_url = upload(bg_image)
                    pass
                else:
                    try:
                        os.mkdir("static/backgrounds")
                    except Exception:
                        pass
                    bg_image.save(f"static/backgrounds/{img_name}.png")
                    bg_url = f"http://127.0.0.1:5000/static/backgrounds/{img_name}.png"
                post.bg_image = bg_url
                db.session.add(post)
                db.session.commit()
                db.session.commit()
                return jsonify(result=True, status=200)
            except Exception:
                return jsonify(group_error=True)
        else:
            try:
                post = Group.query.filter_by(id=id).first()
                post.name = name
                img_name = name.replace(" ", "+")
                if bg_image:
                    if not app.debug:
                        # upload_image(bg_image, folder="backgrounds", name=name)
                        # bg_url = f"https://cgv.s3.us-east-2.amazonaws.com/backgrounds/{img_name}.png"
                        # bg_url = upload(bg_image)
                        pass
                    else:
                        bg_image.save(f"static/backgrounds/{name}")
                        bg_url = f"http://127.0.0.1:5000/static/backgrounds/{name}"
                post.bg_image = bg_url
                post.date = date
                post.certx = certx
                post.certy = certy
                post.qrx = qrx
                post.qry = qry
                post.font_name = font_name
                post.font_size = font_size
                post.certnox = certnox
                post.certnoy = certnoy
                post.textColor = textColor
                # post.user_id = current_user.id
                db.session.commit()
                return jsonify(result=True, status=200)
            except Exception:
                return jsonify(result=False, status=500)
    grp = Group.query.filter_by(id=id).first()
    post = {
        "id": grp.id,
        "name": grp.name,
        "certx": grp.certx,
        "certy": grp.certy,
        "qrx": grp.qrx,
        "qry": grp.qry,
        "certnox": grp.certnox,
        "certnoy": grp.certnoy,
        "font_size": grp.font_size,
        "font_name": grp.font_name,
        "textColor": grp.textColor,
    }
    return jsonify(favTitle='pk', id=id, post=post)

@app.route("/view/groups", methods=['GET', 'POST'])
def view_org_page():
    post = Group.query.order_by(Group.id).all()
    return render_template('org_table.html', post=post)


@app.route("/view/<string:grp_id>/certificates", methods=['GET', 'POST'])
def view_certificate_page(grp_id):
    post = Certificate.query.filter_by(group_id=grp_id).order_by(Certificate.id)
    return render_template('certificate_table.html', post=post, grp_id=grp_id)


@app.route("/edit/<string:grp_id>/certificates/<string:id>", methods=['GET', 'POST'])
def edit_certificates_page(grp_id, id):
    if request.method == 'POST':
        data = json.loads(request.data)
        name = data["name"]
        coursename = data["course"]
        email = data["email"]
        group = Group.query.filter_by(id=grp_id).first()
        try:
            last_certificate = Certificate.query.filter_by(
                group_id=grp_id).order_by(-Certificate.id).first()
            last_certificate_num = int(
                last_certificate.number[len(last_certificate.number)-4:])
            cert_number = str(last_certificate_num + 1).zfill(4)
        except Exception as e:
            cert_number = '1'.zfill(4)
        number = group.prefix + cert_number
        # userid = current_user.id
        # last_update = x
        if id == '0':
            postcheck = Certificate.query.filter_by(
                email=email, group_id=grp_id).first()
            if (postcheck == None):
                try:
                    post = Certificate(name=name, number=number, email=email, coursename=coursename, group_id=grp_id)
                    db.session.add(post)
                    db.session.commit()
                    # Create QR Code for this certificate
                    # link = f'{config("site_url")}/certify/{number}'
                    # new_qr = QRCode(certificate_num=number, link=link)
                    # qr_image = qrcode.QRCode(version=1, box_size=10, border=5)
                    # qr_image.add_data(link)
                    # qr_image.make(fit=True)
                    # img = qr_image.make_image(fill='black', back_color='white')
                    # buffer = io.BytesIO()
                    # img.save(buffer, format="PNG")
                    # buffer.seek(0)
                    # try:
                    #     if not app.debug:
                    #         # upload_image(buffer, number=number,
                    #         #              folder="qr_codes")
                    #         # img_url = f"https://cgv.s3.us-east-2.amazonaws.com/qr_codes/{number}.png"
                    #         # img_url = upload(buffer)
                    #     else:
                    #         try:
                    #             os.mkdir("static/qr_codes")
                    #         except Exception:
                    #             pass
                    #         img.save("static/qr_codes/"+f"{number}.png")
                    #         img_url = f"http://127.0.0.1:5000/static/qr_codes/{number}.png"
                    #     new_qr.qr_code = f"{img_url}"
                    #     new_qr.certificate_id = post.id
                    #     db.session.add(new_qr)
                    #     db.session.commit()
                    # except Exception as e:
                    #     print(e)
                    # subject = f"Certificate Generated With Certificate Number : {number}"
                    # email_sent = send_email_now(email, subject, 'certificate-bot@cgv.in.net', 'Certificate Generate Bot CGV',
                    #                             'emails/new-certificate.html', number=str(number), name=name, site_url=config("site_url"))
                    # if not email_sent:
                    #     flash("Error while sending mail!", "danger")
                    # else:
                    #     post.is_email_sent = True
                    #     db.session.add(post)
                    #     db.session.commit()
                    #     flash(
                    #         "An email with certificate details has been sent!", "success")
                    return jsonify(certificate_success=True)
                except Exception as e:
                    print(e)
                    return jsonify(certificate_error=True)
            else:
                return jsonify(certificate_duplicate=True)
        else:
            try:
                post = Certificate.query.filter_by(id=id).first()
                post.name = name
                post.coursename = coursename
                post.email = email
                # post.user_id = current_user.id
                post.group_id = grp_id
                # post.last_update = time
                db.session.commit()
                return jsonify(certificate_success=True)
            except Exception as e:
                print(e)
                return jsonify(certificate_error=True)
    cert = Certificate.query.filter_by(id=id).first()
    post = {
        "id": cert.id,
        "name": cert.name,
        "coursename": cert.coursename,
        "email": cert.email,
        "number": cert.number
    }
    return jsonify(id=id, post=post)

@app.route("/delete/<string:grp_id>/certificates/<string:id>", methods=['GET', 'POST'])
def delete_certificates_page(grp_id, id):
    delete_certificates_page = Certificate.query.filter_by(id=id).first()
    db.session.delete(delete_certificates_page)
    db.session.commit()
    flash("Certificate deleted successfully!", "success")
    return redirect(f'/view/{grp_id}/certificates')



@app.route("/certificate/generate/<string:certificateno>", methods=['GET', 'POST'])
def certificate_generate(certificateno, bulkDownload = 0):
    # if (host == True):
    #     try:
    #         ip_address = request.environ['HTTP_X_FORWARDED_FOR']
    #     except KeyError:
    #         ip_address = request.remote_addr
    #     except Exception:
    #         ip_address = ipc
    # else:
    #     ip_address = ipc
    if (request.method == 'GET'):
        bulkDownload = request.values.get('bulk', 0)
        # certificateno = request.form.get('certificateno')
        postc = Certificate.query.filter_by(number=certificateno).first()
        if (postc != None):
            posto = Group.query.filter_by(id=postc.group_id).first()
            postf = Fonts.query.filter_by(name=posto.font_name).first()
            # qr_code = QRCode.query.filter_by(
            #     certificate_num=certificateno).first()
            # img_url = qr_code.qr_code
            return render_template('certificate.html', postf=postf, postc=postc, posto=posto, number=certificateno, bulk = bulkDownload)
        elif (postc == None):
            flash("No details found. Contact your organization!", "danger")
    return render_template('Redesign-generate.html')

@app.route('/upload/<string:grp_id>/certificate', methods=['POST', 'GET'])
def upload_csv(grp_id):
    group = Group.query.filter_by(id=grp_id).first()
    csv_file = request.files['fileToUpload']
    csv_file = io.TextIOWrapper(csv_file, encoding='utf-8')
    csv_reader = csv.reader(csv_file, delimiter=',')
    # This skips the first row of the CSV file.
    next(csv_reader)
    for row in csv_reader:
        try:
            last_certificate = Certificate.query.filter_by(
                group_id=grp_id).order_by(-Certificate.id).first()
            last_certificate_num = int(
                last_certificate.number[len(last_certificate.number)-4:])
            cert_number = str(last_certificate_num + 1).zfill(4)
        except Exception as e:
            cert_number = '1'.zfill(4)
        number = group.prefix + cert_number
        certificate = Certificate(
            number=number, name=row[0], email=row[1], coursename=row[2], group_id=grp_id)
        db.session.add(certificate)
        db.session.commit()
        # Create QR Code for this certificate
        # link = f'{config("site_url")}/certify/{number}'
        # new_qr = QRCode(certificate_num=number, link=link)
        # qr_image = qrcode.QRCode(version=1, box_size=10, border=5)
        # qr_image.add_data(link)
        # qr_image.make(fit=True)
        # img = qr_image.make_image(fill='black', back_color='white')
        # buffer = io.BytesIO()
        # img.save(buffer, format="PNG")
        # buffer.seek(0)
        # try:
        #     if not app.debug:
        #         # upload_image(buffer, number=number, folder="qr_codes")
        #         # img_url = f"https://cgv.s3.us-east-2.amazonaws.com/qr_codes/{number}.png"
        #         img_url = upload(buffer)
        #     else:
        #         try:
        #             os.mkdir("static/qr_codes")
        #         except Exception:
        #             pass
        #         img.save("static/qr_codes/"+f"{number}.png")
        #         img_url = f"http://127.0.0.1:5000/static/qr_codes/{number}.png"
        #     new_qr.qr_code = f"{img_url}"
        #     new_qr.certificate_id = certificate.id
        #     db.session.add(new_qr)
        #     db.session.commit()

        # except Exception as e:
        #     print(e)
    return jsonify(result=True, status=200)

@app.route("/certificate/mass-generate/<string:groupno>")
def massGenerate(groupno):
    certnoList = Certificate.query.filter_by(group_id = groupno).limit(3).all()
    # print(certnoList)
    # print(certnoList[0].group_id)

    # posto = Group.query.filter_by(id=groupno).first()
    # postf = Fonts.query.filter_by(name=posto.font_name).first()

    for member in certnoList:
        # page = render_template("certificate.html", postf=postf, postc=member, posto=posto, number=member.number, bulk = 1)
        # print(type(page))
        # return redirect(url_for(certificate_generate(), postf=postf, postc=member, posto=posto, number=member.number, bulk = 1))
        webbrowser.open(
            f"http://127.0.0.1:5000/certificate/generate/{member.number}"
        )
        sleep(2)


    return "All Files Downloaded"

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)