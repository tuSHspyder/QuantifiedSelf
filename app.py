from flask import Flask,render_template,request,redirect,session
from models import Tracker, db, User,Log
import datetime,logging

logging.basicConfig(filename='debug.log' ,level= logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///Database.sqlite3"
app.secret_key = '123'
db.init_app(app)

setting=[]
last={}


@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        test = User.query.filter(User.username==request.form['uname']).first()
        # print(test.username)
        if test is None:
            user= User(username=request.form['uname'])
            db.session.add(user)
            db.session.commit()
            test = User.query.filter(User.username==request.form['uname']).first()
            session['id']=test.userid
            session['username']=test.username
            # print("login if :",session['id'],session['username'])
            return redirect('/dashboard')
        else:
            session['username']=test.username
            session['id']=test.userid
            return redirect('/dashboard')
    if len(session)>0 and session['id'] is not None:
        return redirect('/dashboard')
    return render_template("login.html")

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if request.method=="POST":
        return redirect('/add_tracker')
    trackers = Tracker.query.filter(Tracker.userid==session['id']).all()
    for i in trackers:
        logs = Log.query.filter(Log.tid==i.tid).all()
        # print(logs)
        if logs==[]:
            last[i.tid]="Not yet tracked"
        else:
            last[i.tid]=logs[-1].time
    # print(trackers.tid)
    return render_template("dashboard.html",session=session,trackers=trackers,last=last)

@app.route("/add_tracker", methods=["GET","POST"])
def add_tracker():
    if request.method=="POST":
        tracker = Tracker(tname=request.form['name'],tdescription=request.form['description'],ttype=request.form['type'],tsetting=request.form['setting'],userid=session['id'])
        db.session.add(tracker)
        db.session.commit()
        return redirect("/dashboard")
    return render_template("add_tracker.html")

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/")

@app.route("/tracker/<tid>/delete", methods=["GET"])
def delete_tracker(tid):
    tracker = Tracker.query.filter(Tracker.tid==tid).first()
    db.session.delete(tracker)
    db.session.commit()
    return redirect("/dashboard")

@app.route("/tracker/<tid>/update", methods=["GET","POST"])
def update_tracker(tid):
    tracker = Tracker.query.filter(Tracker.tid==tid).first()
    if request.method=="POST":
        tracker.tname=request.form['name']
        tracker.tdescription=request.form['description']
        # track=Tracker(tname=request.form['name'],tdescription=request.form['description'])
        # db.session.update(track)
        db.session.commit()
        return redirect("/dashboard")
    return render_template("update_tracker.html",tracker=tracker)

@app.route("/tracker/<tid>/add_log", methods=["GET","POST"])
def addlog(tid):
    tracker = Tracker.query.filter(Tracker.tid==tid).first()
    if request.method=="POST":
    #     print(request.form['time'])
    #     print(request.form['value'])
    #     print(request.form['note'])
        log=Log(time=request.form['time'],tracker=tracker.tname,value=int(request.form['value'])*2,note=request.form['note'],tid=tracker.tid)
        db.session.add(log)
        db.session.commit()
        return redirect("/dashboard")
    setting=tracker.tsetting
    setting=setting.split(",")
    now = datetime.datetime.now()
    passthisnow = str(now.date()) + 'T' + str(now.time().strftime("%H:%M"))
    return render_template("add_log.html",tracker=tracker,setting=setting,time=passthisnow)


@app.route("/tracker/<tid>", methods=["GET","POST"])
def display(tid):
    data=[]
    label=[]
    type='line'
    
    tracker = Tracker.query.filter(Tracker.tid==tid).first()
    logs = Log.query.filter(Log.tid==tid).order_by(Log.time).all()
    # if tracker.ttype=="Numerical":
    for log in logs:
        data.append(log.value)
        label.append(log.time)

    if tracker.ttype=="Boolean":
        l=[]
        label=[]
        x = data.count("True")
        l.append(x)
        x = data.count("False")
        l.append(x)
        data=l
        label.append("True")
        label.append("False")
        type='bar'

    if tracker.ttype=="Multiple Choice":
        setting=tracker.tsetting
        setting=setting.split(",")
        l=[]
        label=[]
        for i in setting:
            x = data.count(i)
            l.append(x)
            label.append(i)
        data=l
        type='pie'
  
    # print(label)
    # print(data)
    return render_template("tracker_details.html",logs=logs,data=data,label=label,type=type)
    # return render_template("test.html",logs=logs,data=data,label=label)

@app.route("/tracker/<tid>/<logid>/delete", methods=["GET"])
def delete_log(tid,logid):
    log = Log.query.filter(Log.logid==logid,Log.tid==tid).first()
    db.session.delete(log)
    db.session.commit()
    return redirect("/tracker/"+str(tid))

@app.route("/tracker/<tid>/<logid>/update", methods=["GET","POST"])
def update_log(tid,logid):
    log = Log.query.filter(Log.logid==logid,Log.tid==tid).first()
    tracker = Tracker.query.filter(Tracker.tid==tid).first()
    if request.method=="POST":
        log.time = request.form['time']
        log.value = request.form['value']
        log.note = request.form['note']
        db.session.commit()
        return redirect("/tracker/"+str(tid))
    setting=tracker.tsetting
    setting=setting.split(",")
    return render_template("update_log.html",log=log,tracker=tracker,setting=setting)

if __name__=='__main__':
    app.run(host='0.0.0.0')

# http://127.0.0.1:5000/