from flask import Flask, render_template,flash,redirect,url_for,session,request,logging,make_response
from wtforms import Form,StringField,TextAreaField,SelectField,PasswordField,validators,IntegerField,DateField
from passlib.hash import sha256_crypt
from datetime import date
from flask import g
import sqlite3
import datetime

app = Flask(__name__)

database = 'C:\sqlite\jobs.db'

now=datetime.datetime.now()

@app.route('/apply',methods=['GET','POST'])
def apply():
    if request.method=='POST':
        code=request.form['job']
        username=session.get('username')
        date=now.strftime("%Y/%m/%d")
        db=get_db()
        cur=db.cursor()
        cur.execute("Insert into job_application(username,job_code,date_applied,status) values(?,?,?,?)",[username,code,date,"pending"])
        db.commit()
        cur.close()
    return redirect(url_for('viewjob'))

@app.route('/company',methods=['GET','POST'])
def company():
    if request.method=='POST':
        username=request.form['company']
        username1=session.get('username')
        db=get_db()
        cur=db.cursor()
        cur.execute("select * from user where username=?",[username])
        temp=cur.fetchall()
        info = temp[0]
        cur.execute("select * from provider where username=?",[username])
        temp=cur.fetchall()
        details=temp[0]
        cur.close()
        return render_template('company.html',username=username1,info=info,detail=details)
    return redirect(url_for('viewjob'))
        
@app.route('/viewjob',methods=['GET','POST'])
def viewjob():
    if request.method=='POST':
        code=request.form['jobcode']
        username=session.get('username')
        db=get_db()
        cur=db.cursor()
        cur.execute("Select * from job_offers where job_code=?",[code])
        jobs=cur.fetchall()
        job=jobs[0]
        cur.execute("Select * from provider where username=(Select username from company_jobs where job_code=?)",[code])
        temp=cur.fetchall()
        company=temp[0]
        cur.execute("Select count(*) from job_application where job_code=? and username=?",[code,username])
        temp=cur.fetchall()
        temp1=temp[0]
        count=temp1[0]
        if count==0:
            return render_template("job.html",username=username,job=job,company=company,apply=0)
        else:
            return render_template("job.html",username=username,job=job,company=company,apply=1)
    return redirect(url_for('seeker'))


@app.route('/deleteapplication',methods=['GET','POST'])
def deleteapplication():
    if request.method=='POST':
        code=request.form['jobcode']
        username=session.get('username')
        db=get_db()
        cur=db.cursor()
        cur.execute("delete from job_application where job_code=? and username=?",[code,username])
        db.commit()
        cur.close()
    return redirect(url_for('seeker'))



class RegistrationForm(Form):
    mychoices= [('Job Seeker','Job Seeker'),('Job Provider','Job Provider')]
    name= StringField('Name/Company Name',[validators.Length(min=1,max=50)])
    username= StringField('Username',[validators.Length(min=1,max=50)])
    email= StringField('Email',[validators.Length(min=1,max=50)])
    category= SelectField('Category',choices=mychoices)
    password= PasswordField('Password',[validators.DataRequired(),validators.EqualTo('confirm',message='Password do not match')])
    confirm= PasswordField('Confirm Password',[validators.Length(min=1,max=50)])
    

class AddJobForm(Form):
    title=StringField('Job Title',[validators.Length(min=1,max=50)])
    location=StringField('Job Location',[validators.Length(min=1,max=50)])
    mychoices= [('Regular','Regular'),('Internship','Internship')]
    category=SelectField('Category',choices=mychoices)
    jobt= [('Work from home','Home'),('On-site','Onsite'),('Part-time','Part')]
    jobtype=SelectField('Job Type',choices=jobt)
    pref=[('Architecture','Architecture'),('Interior Design','Interior Design'),('Commerce','Commerce'),('Accounts','Accounts'),('Chartered Accountancy','Chartered Accountancy'),('Animation','Animation'),('Fashion Design','Fashion Design'),('Graphic Design','Graphic Design'),('Merchandise Design','Merchandise Design'),('Engineering','Engineering'),('Aerospace','Aerospace'),('Biotech','Biotech'),('Chemical','Chemical'),('Civil','Civil'),('Electrical','Electrical'),('Electronics','Electronics'),('Energy Science and Engineering','Energy Science and Engineering'),('Engineering Design','Engineering Design'),('Engineering Physics','Engineering Physics'),('Game Development','Game Development'),('Image Processing','Image Processing'),('Material Science','Material Science'),('Mechanical','Mechanical'),('Metallurgy','Metallurgy'),('Mobile App Development','Mobile App Development'),('Naval and Ocean','Naval and Ocean'),('Petroleum Engineering','Petroleum Engineering'),('Programming','Programming'),('Software Development','Software Development'),('Software Testing','Software Testing'),('Web Development','Web Development'),('Hospitality','Hospitality'),('Hotel Management','Hotel Management'),('Travel and Tourism','Travel and Tourism'),('MBA','MBA'),('Digital Marketing','Digital Marketing'),('Finance','Finance'),('General Management','General Management'),('HR','HR'),('Market Business Research','Market Business Research'),('Marketing','Marketing'),('Operations','Operations'),('Sales','Sales'),('Strategy','Strategy'),('Supply Chain Management','Supply Chain Management'),('Media','Media'),('Cinematography','Cinematography'),('Content Writing','Content Writing'),('Film Making','Film Making'),('Journalism','Journalism'),('Motion Graphics','Motion Graphics'),('Photography','Photography'),('PR','PR'),('Social Media Marketing','Social Media Marketing'),('Video Making Editing','Video Making Editing'),('Videography','Videography'),('Science','Science'),('Biology','Biology'),('Chemistry','Chemistry'),('Mathematics','Mathematics'),('Physics','Physics'),('Statistics','Statistics'),('Others','Others'),('Acting','Acting'),('Agriculture and Food Engineering','Agriculture and Food Engineering'),('Company Secretary','Company Secretary'),('Data Science','Data Science'),('Event Management','Event Management'),('Humanities','Humanities'),('Law','Law'),('Medicine','Medicine'),('Pharmaceutical','Pharmaceutical'),('Psychology','Psychology'),('Teaching','Teaching'),('UI UX','UI UX'),('Volunteering','Volunteering')]
    preference=SelectField('Preference',choices=pref)
    deadline=DateField('Deadline (YYYY/MM/DD)',format="%Y/%m/%d")
    joindate=DateField('Joining Date (YYYY/MM/DD)',format="%Y/%m/%d")
    duration=StringField('Job Duration')
    description=StringField('Job Description',[validators.Length(min=1,max=1000)])


class SeekerRegistrationForm(Form):
    mychoices= [('Male','Male'),('Female','Female')]
    mychoice1=[('Under Graduate','Under Graduate'),('Graduate','Graduate'),('Post Graduate','Post Graduate'),('Doctrate','Doctrate')]
    gender= SelectField('Gender',choices=mychoices)
    degree= SelectField('Degree',choices=mychoice1)
    contact = IntegerField('Contact',[validators.DataRequired()])
    cvlink= StringField('CV Link',[validators.optional()])

class ProviderRegistrationForm(Form):
    power=IntegerField('Man Power',[validators.DataRequired()])
    description= TextAreaField('Job description',[validators.Length(min=1, max=2000)])
    contact = IntegerField('Contact',[validators.optional()])    


# fetch connected database or connect
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(database)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# login a user
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        valid = False
        db=get_db()
        cur=db.cursor()
        cur.execute("SELECT count(*) FROM USER WHERE USERNAME=?",[username])
        count = cur.fetchall()
        count_num=1
        row=count[0]
        if row[0] == 0:
            count_num=0
        cur.execute("SELECT * FROM USER WHERE USERNAME=?",[username])
        data = cur.fetchall()
        if count_num == 1:
            row=data[0]
            hash1 = row[4]
            valid = sha256_crypt.verify(password,hash1)
            if valid == True:
                session['username'] = username
                usertype=row[3]
                if usertype == "Job Seeker":
                    return redirect(url_for('seeker'))
                else:
                    if usertype == "Job Provider":
                        return redirect(url_for('provider'))
                    else:
                        return redirect(url_for('admin'))
            else:
                flash('Invalid Username or Password')
        else:
            flash('Invalid Username')
    return redirect(url_for('index'))

@app.route('/jobs',methods=['GET','POST'])
def jobs():
    form=AddJobForm(request.form)
    username=session.get('username')
    db=get_db()
    cur=db.cursor()
    cur.execute("Select count(*) from user where username=?",[username])
    count=cur.fetchall()
    row=count[0]
    if(row[0]==0):
        return redirect(url_for('index'))
    else:
        if request.method == 'POST' and form.validate():
            title = form.title.data
            location = form.location.data
            category=form.category.data
            jobtype=form.jobtype.data
            preference=form.preference.data
            deadline=form.deadline.data
            joindate=form.joindate.data
            duration=form.duration.data
            description=form.description.data
            temp=""
            cur.execute("select job_code from job_offers where job_code=(select max(job_code) from job_offers)")
            temp=cur.fetchall()
            print(temp)
            cur.execute("insert into job_offers(job_title,location,job_type,site_type,preference,deadline,duration,join_date,description) VALUES(?,?,?,?,?,?,?,?,?)",(title,location,category,jobtype,preference,deadline,duration,joindate,description))
            db.commit()
            cur.execute("select job_code from job_offers where job_title=? and location=? and job_type=? and site_type=? and preference=? and deadline=? and duration=? and join_date=? and description=?",[title,location,category,jobtype,preference,deadline,duration,joindate,description])
           
            c=cur.fetchall()
            cod=c[0]
            code=cod[0]
            cur.execute("insert into company_jobs(job_code,username,status) values(?,?,?)",(code,username,"open"))
            db.commit()
            cur.close()
            return redirect(url_for('provider'))
        return render_template('addjobs.html',username=username,form=form)


# my profile of a seeker or provider
@app.route('/profile')
def profile():
    username=session.get('username')
    db=get_db()
    cur=db.cursor()
    cur.execute("Select count(*) from user where username=?",[username])
    count=cur.fetchall()
    row=count[0]
    if(row[0]==0):
        return redirect(url_for('index'))
    else:
        cur.execute("select * from user where username=?",[username])
        temp=cur.fetchall()
        info = temp[0]
        if(info[3] == 'Job Seeker'):
            cur.execute("select * from seeker where username=?",[username])
            temp=cur.fetchall()
            details=temp[0]
            cur.execute("select skill from preferences where username=?",[username])
            skill=cur.fetchall()
            cur.execute("select count(*) from preferences where username=?",[username])
            temp=cur.fetchall()
            row=temp[0]
            num=row[0]
            cur.close()
            return render_template('seeker_profile.html',username=username,info=info,detail=details,num=num,skill=skill)
        else:
            cur.execute("select * from provider where username=?",[username])
            temp=cur.fetchall()
            details=temp[0]
            cur.close()
            return render_template('provider_profile.html',username=username,info=info,detail=details)

@app.route('/admin')
def admin():
    username=session.get('username')
    db=get_db()
    cur=db.cursor()
    cur.execute("Select count(*)  from seeker")
    temp=cur.fetchall()
    temp1=temp[0]
    active1=temp1[0]
    cur.execute("Select count(*) from provider")
    temp=cur.fetchall()
    temp1=temp[0]
    active2=temp1[0]
    cur.execute("Select count(*) from job_offers")
    temp=cur.fetchall()
    temp1=temp[0]
    active3=temp1[0]
    cur.execute("Select user.name,user.username,user.email,seeker.gender,seeker.contact,seeker.degree from user natural join seeker")
    seeker=cur.fetchall()
    cur.execute("Select user.name,user.username,user.email,provider.contact,provider.description from user natural join provider")
    provider=cur.fetchall()
    cur.execute("Select provider.username,job_offers.* from job_offers natural join provider")
    job=cur.fetchall()
    cur.close()
    return render_template('admin.html',username=username,seeker=seeker,provider=provider,job=job,active1=active1,active2=active2,active3=active3)
    

# to delete a user skill
@app.route('/delete',methods=['GET','POST'])
def delete():
    if request.method == 'POST':
        skill=request.form["del"]
        username=session.get('username')
        db=get_db()
        cur=db.cursor()
        cur.execute("delete from preferences where username=? and skill=?",(username,skill))
        db.commit()
        cur.close()
    return redirect(url_for('profile')) 


@app.route('/seeker_email',methods=['GET','POST'])
def seeker_email():
    if request.method == 'POST':
        email=request.form["email"]
        username=session.get('username')
        db=get_db()
        cur=db.cursor()
        cur.execute("update user set email=? where username=?",(email,username))
        db.commit()
        cur.close()
    return redirect(url_for('profile')) 
        
@app.route('/seeker_contact',methods=['GET','POST'])
def seeker_contact():
    if request.method == 'POST':
        contact=request.form["contact"]
        username=session.get('username')
        db=get_db()
        cur=db.cursor()
        cur.execute("update seeker set contact=? where username=?",(contact,username))
        db.commit()
        cur.close()
    return redirect(url_for('profile')) 
  

@app.route('/seeker_degree',methods=['GET','POST'])
def seeker_degree():
    if request.method == 'POST':
        degree=request.form["degree"]
        username=session.get('username')
        db=get_db()
        cur=db.cursor()
        cur.execute("update seeker set degree=? where username=?",(degree,username))
        db.commit()
        cur.close()
    return redirect(url_for('profile')) 

@app.route('/seeker_CVLink',methods=['GET','POST'])
def seeker_CVLink():
    if request.method == 'POST':
        cv=request.form["CVLink"]
        username=session.get('username')
        db=get_db()
        cur=db.cursor()
        cur.execute("update seeker set cvlink=? where username=?",(cv,username))
        db.commit()
        cur.close()
    return redirect(url_for('profile')) 
  
@app.route('/provider_email',methods=['GET','POST'])
def provider_email():
    if request.method == 'POST':
        email=request.form["email"]
        username=session.get('username')
        db=get_db()
        cur=db.cursor()
        cur.execute("update user set email=? where username=?",(email,username))
        db.commit()
        cur.close()
    return redirect(url_for('profile')) 

@app.route('/provider_contact',methods=['GET','POST'])
def provider_contact():
    if request.method == 'POST':
        contact=request.form["contact"]
        username=session.get('username')
        db=get_db()
        cur=db.cursor()
        cur.execute("update provider set contact=? where username=?",(contact,username))
        db.commit()
        cur.close()
    return redirect(url_for('profile')) 

@app.route('/provider_power',methods=['GET','POST'])
def provider_power():
    if request.method == 'POST':
        power=request.form["power"]
        username=session.get('username')
        db=get_db()
        cur=db.cursor()
        cur.execute("update provider set power=? where username=?",(power,username))
        db.commit()
        cur.close()
    return redirect(url_for('profile')) 

@app.route('/provider_description',methods=['GET','POST'])
def provider_description():
    if request.method == 'POST':
        description=request.form["desc"]
        username=session.get('username')
        db=get_db()
        cur=db.cursor()
        cur.execute("update provider set description=? where username=?",(description,username))
        db.commit()
        cur.close()
    return redirect(url_for('profile')) 

# for seeker registration details
@app.route('/seeker_register',methods=['GET','POST'])
def seeker_register():
    form=SeekerRegistrationForm(request.form)
    db=get_db()
    cur=db.cursor()
    username=session.get('username')
    cur.execute("Select count(*) from user where username=?",[username])
    count=cur.fetchall()
    row=count[0]
    if(row[0]==0):
        return redirect(url_for('index'))
    else:
        if request.method == 'POST' and form.validate():
            gender = form.gender.data
            degree = form.degree.data
            contact = form.contact.data
            cvlink = form.cvlink.data
            cur.execute("INSERT INTO seeker(username,gender,degree,contact,cvlink) VALUES(?,?,?,?,?)",(username,gender,degree,contact,cvlink))
            db.commit()
            cur.close()
            return render_template('seeker.html',username=username)
    return render_template('seeker_register.html',form=form)

# for provider registration details
@app.route('/provider_register',methods=['GET','POST'])
def provider_register():
    form=ProviderRegistrationForm(request.form)
    db=get_db()
    cur=db.cursor()
    username=session.get('username')
    cur.execute("Select count(*) from user where username=?",[username])
    count=cur.fetchall()
    row=count[0]
    if(row[0]==0):
        return redirect(url_for('index'))
    else:
        if request.method == 'POST' and form.validate():
            description=form.description.data
            power=form.power.data
            contact=form.contact.data
            # username=session.get('username')
            # db=get_db()
            # cur=db.cursor()
            cur.execute("INSERT INTO provider(username,description,contact,power) VALUES(?,?,?,?)",(username,description,contact,power))
            db.commit()
            cur.close()
            return redirect(url_for('provider',username=username))
    return render_template('provider_register.html',form=form)

# to add user skills          
@app.route('/skills',methods=['GET','POST'])
def skills():
    if request.method =='POST':
        skill=request.form['skill']
        db=get_db()
        cur=db.cursor()
        username=session.get('username')
        cur.execute("select * from preferences where username=?",[username])
        temp=cur.fetchall()
        valid = True
        for skills in temp:
            if skills[1]==skill:
                valid=False
                break

        if valid == False:
            flash('preference already added','error')
        else:
            cur.execute("INSERT INTO preferences(username,skill) VALUES(?,?)",(username,skill))
            db.commit()
            flash('preference added','success')
        cur.close()
    return redirect(url_for('profile'))    

# seeker dashboard
@app.route('/seeker')
def seeker():
    db=get_db()
    cur=db.cursor()
    username=session.get('username')
    cur.execute("Select count(*) from user where username=?",[username])
    count=cur.fetchall()
    row=count[0]
    if(row[0]==0):
        return redirect(url_for('index'))
    else:
        cur.execute("Select count(*) from seeker where username=?",[username])
        count=cur.fetchall()
        row=count[0]
        if(row[0]==0):
            return redirect(url_for('seeker_register'))
        else:
            cur.execute("Select * from job_offers where preference in (Select skill from preferences where username=?)",[username])
            jobs=cur.fetchall()
            # cur.execute("Select * from job_application where username=?",[username])
            # applied=cur.fetchall()
            # cur.execute("select * from job_offers where job_code in (Select job_code from jobjob_application where username=?)",[username])
            # detail=cur.fetchall()
            cur.execute("Select job_code,job_title,date_applied,status from job_application natural join job_offers")
            applied=cur.fetchall()
            return render_template('seeker.html',username=username,jobs=jobs,applied=applied)

@app.route('/close_job/<id>',methods=['GET','POST'])
def close_job(id):
    db=get_db()
    cur=db.cursor()
    # cur.execute('delete from job_offers where job_code=?',[id])
    # db.commit()
    # cur.execute('delete from company_jobs where job_code=?',[id])
    # db.commit()
    username=session.get('username')
    cur.execute("update company_jobs set status=? where job_code=? and username=?" ,("close",id,username))
    db.commit()
    cur.execute("update job_application set status=? where job_code=?",("Expired",id))
    db.commit()
    cur.close()
    return redirect(url_for('provider'))

# provider dashboard
@app.route('/provider')
def provider():
    db=get_db()
    cur=db.cursor()
    username=session.get('username')
    cur.execute("Select count(*) from user where username=?",[username])
    count=cur.fetchall()
    row=count[0]
    if(row[0]==0):
        cur.close()
        return redirect(url_for('index'))
    else:
        cur.execute("Select count(*) from provider where username=?",[username])
        count=cur.fetchall()
        row=count[0]
        if(row[0]==0):
            cur.close()
            return redirect(url_for('provider_register'))
        else:
            cur.execute("Select company_jobs.status,s.* from company_jobs,(Select * from job_offers where job_code in (Select job_code from company_jobs where username=?)) s where s.job_code=company_jobs.job_code",[username])
            jobs=cur.fetchall()
            cur.execute("select user.name, user.email, s.* from user join (select seeker.contact, seeker.gender, seeker.degree, seeker.cvlink, t.* from seeker join (select job_application.*, job_offers.* from job_application join job_offers where job_application.job_code in (select job_code from company_jobs where username=?) and job_offers.job_code=job_application.job_code) t where t.username=seeker.username) s where s.username=user.username",[username])
            applicants=cur.fetchall()
            print(applicants)
            cur.close()
            return render_template('provider.html',username=username,jobs=jobs,applicants=applicants)

@app.route('/accept_applicant/<id>/<job_code>',methods=['GET','POST'])
def accept_applicant(id,job_code):
    db=get_db()
    cur=db.cursor()
    cur.execute("update job_application set status=? where username=? and job_code=?",('accepted',id,job_code))
    db.commit()
    return redirect(url_for('provider'))

@app.route('/reject_applicant/<id>/<job_code>',methods=['GET','POST'])
def reject_applicant(id,job_code):
    db=get_db()
    cur=db.cursor()
    cur.execute("update job_application set status=? where username=? and job_code=?",('rejected',id,job_code))
    db.commit()
    return redirect(url_for('provider'))

@app.route('/applicant/<id>')
def applicant(id):
    username=session.get('username')
    db=get_db()
    cur=db.cursor()
    cur.execute("Select count(*) from user where username=?",[username])
    count=cur.fetchall()
    row=count[0]
    if(row[0]==0):
        return redirect(url_for('index'))
    else:
        cur.execute("select * from user where username=?",[id])
        temp=cur.fetchall()
        info = temp[0]
        cur.execute("select * from seeker where username=?",[id])
        temp=cur.fetchall()
        details=temp[0]
        cur.execute("select skill from preferences where username=?",[id])
        skill=cur.fetchall()
        cur.execute("select count(*) from preferences where username=?",[id])
        temp=cur.fetchall()
        row=temp[0]
        num=row[0]
        cur.close()
        return render_template('applicant.html',username=username,info=info,detail=details,num=num,skill=skill)

# logout the user
@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('start.html')

@app.route('/about')
def about():
    return render_template('about.html')

# register a new user(sign up)
@app.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        email=form.email.data
        category=form.category.data
        password=sha256_crypt.encrypt(str(form.password.data))
        valid = True
        db=get_db()
        cur=db.cursor()
        cur.execute("SELECT * FROM USER")
        rows = cur.fetchall()
        for row in rows:
            dbusername = row[0]
            if dbusername == username:
                valid = False
        if valid == False:
            flash('Username not available.','error')
        else:
            cur.execute("INSERT INTO user(username,name,email,category,password) VALUES(?,?,?,?,?)",(username,name,email,category,password))
            db.commit()
        cur.close()
        return redirect(url_for('index'))
    return render_template('register.html',form=form)


if __name__ == '__main__':
    app.secret_key='1234'
    app.run(debug=True)