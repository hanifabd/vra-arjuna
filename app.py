import datetime
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from helper.VR_Classifier import VR_Classifier
from helper.encoder import JSONEncoder
from flask_pymongo import PyMongo

app = Flask(__name__, template_folder='site')
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config["MONGO_URI"] = "mongodb://localhost:27017/report_db"
mongodb_client = PyMongo(app)
db = mongodb_client.db
CORS(app)

# ==============================================================
# Route of Projects
# ==============================================================

@app.route('/', methods=['GET','POST'])
def vra():
    if request.method == 'GET':
        reports = db.todos.find()
        return render_template('index.html', reports=reports)
    if request.method == 'POST':
        datelog = str(datetime.datetime.now())
        nik = request.form['nik']
        abuse_type = request.form['abuse_type']
        relation = request.form['relation']
        victim_age = request.form['victim_age']
        agressor_age = request.form['agressor_age']
        prev_abuse_report = request.form['prev_abuse_report']
        living_together = request.form['living_together']
        short_chronology = request.form['short_chronology']

        classifier = VR_Classifier()
        encoded_report = classifier.encode([(relation, victim_age, agressor_age, prev_abuse_report, living_together)])
        scaled_report = classifier.scale(encoded_report)
        risk_level = classifier.predict(scaled_report)

        db.todos.insert_one({
            'date_log': datelog,
            'nik' : nik,
            'violence_type': abuse_type,
            'relation': relation,
            'victim_age': victim_age,
            'agressor_age': agressor_age,
            'prev_abuse_report': prev_abuse_report,
            'living_together': living_together,
            'short_chronology': short_chronology,
            'risk_level': risk_level
        })

        reported = [datelog, nik, abuse_type, relation, victim_age, agressor_age, prev_abuse_report, living_together, short_chronology, risk_level]

        return render_template('index.html', _anchor='#report', result=reported)

if __name__ == '__main__':
    app.run()