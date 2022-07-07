from email.headerregistry import Address
from unicodedata import name
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from flask_sqlalchemy import SQLAlchemy
from os import path


app = Flask(__name__)
db = SQLAlchemy(app)
DB_NAME = "database.db"
app.config['SECRET_KEY'] = 'hjshjhdjahjs'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
db.init_app(app)


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Firstname = db.Column(db.String(100))
    Lastname = db.Column(db.String(100))
    PhoneNumber = db.Column(db.String(100))
    Address = db.Column(db.String(100))

class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    member_list = db.Column(db.PickleType, nullable=True)
    


    
@app.route('/')
def Index():
    api_url_1="http://so.fthou.se:8080/api/persons"
    api_url_2="http://so.fthou.se:8080/api/families"
    res = requests.get(api_url_1)
    res2=requests.get(api_url_2)
    response= res.json()
    response2=res2.json()
    family_list=[]
    for item in response2:
        family_list.append(item['name'])

    if not path.exists("database.db"):
        db.create_all()

        for item in response:
            id=item['id']
            firstname = item['firstName']
            lastname = item['lastName']
            phoneNumber = item['phoneNumber']
            address = item['address']
            new_member = Member(id=id,
                            Firstname=firstname,
                            Lastname=lastname,
                            PhoneNumber=phoneNumber,
                            Address=address
                            )
            db.session.add(new_member)
            db.session.commit()
        for item in response2:
            arr=[]
            id=item['id']
            name=item['name']

            for i in range(len(item['familyMembers'])):
                arr.append(item['familyMembers'][i]['id'])
            list=arr
            new_family=Family(
                id=id,
                name=name,
                member_list=list
                
            )
            db.session.add(new_family)
            db.session.commit()

    resp=Member.query.all()
    resp2=Family.query.all()
    return render_template("index.html",RESPONSE=resp,RESPONSE2=resp2,FAMILY_LIST=family_list)


@app.route('/add_member', methods=['POST'])
def add_member():
    if request.method == 'POST':
        id = request.form['ID']
        Firstname = request.form['Firstname']
        Lastname = request.form['LastName']
        familyname=request.form.get('select1')
        phoneNumber = request.form['phone']
        address = request.form['Address']
    
        new_member = Member(id=id,
                        Firstname=Firstname,
                        Lastname=Lastname,
                        PhoneNumber=phoneNumber,
                        Address=address
                        )
        db.session.add(new_member)
        db.session.commit()
    if request.method == 'POST':
        familyname=request.form.get('select1')

        Family_to_change=Family.query.filter_by(name=familyname).first()
        ID=Family_to_change.id
        LIST=Family_to_change.member_list
        db.session.delete(Family_to_change)
        LIST.append(int(id))
        new_family=Family(
                id=ID,
                name=familyname,
                member_list=LIST
            
        )
        db.session.add(new_family)
        db.session.commit()

    return redirect(url_for('Index'))


@app.route('/edit/<id>', methods = ['POST', 'GET'])
def get_member(id):
    memberr = Member.query.get_or_404(id)
    return render_template('edit.html',DATA=memberr)
 
@app.route('/update/<id>', methods=['POST'])
def update_member(id):
    member_to_update = Member.query.get_or_404(id)

    if request.method == 'POST':
        Firstname = request.form['FirstName']
        Lastname = request.form['LastName']
        phone = request.form['Phone']
        Address = request.form['address']
        
        member_to_update.Firstname=Firstname
        member_to_update.Lastname=Lastname
        member_to_update.PhoneNumber=phone
        member_to_update.Address=Address
        db.session.add(member_to_update)
        db.session.commit()
    return redirect(url_for('Index'))
 
@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_member(id):
    member_to_delete=Member.query.get_or_404(id)
    ID=id
    db.session.delete(member_to_delete)
    db.session.commit()
    resp2=Family.query.all()
 
    family_id=[1,2,3,4,5]
    for i in family_id:
        item=Family.query.get_or_404(i)
        if (int(ID) in item.member_list):
            Id=item.id
            name=item.name
            newarr=item.member_list
            newarr.remove(int(ID))
            Family_to_update = Family.query.get_or_404(Id)
            db.session.delete(Family_to_update)
            new_family=Family(
                    id=Id,
                    name=name,
                    member_list=newarr
                
            )
            print("done")
            db.session.add(new_family)
            db.session.commit()

            

    return redirect(url_for('Index'))

@app.route('/detail_view/<id>', methods = ['POST', 'GET'])
def details(id):
    Family_to_view = Family.query.get_or_404(id)
    LIST=Family_to_view.member_list
    arr=[]
    for i in LIST:
        Current_member=Member.query.get_or_404(i)
        id=Current_member.id
        Firstname=Current_member.Firstname
        Lastname=Current_member.Lastname
        Phone=Current_member.PhoneNumber
        Address=Current_member.Address
        arr.append([id,Firstname,Lastname,Phone,Address])


    return render_template('detailview.html',DATA=arr)

 
if __name__ == "__main__":
    app.run(port=3000, debug=True)