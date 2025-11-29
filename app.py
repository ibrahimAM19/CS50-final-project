from flask import Flask, redirect,url_for,render_template,request,session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from datetime import datetime,timedelta,date



"""
def login_required(f):


    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function
"""

conn = sqlite3.connect("clients.db",check_same_thread= False )
conn.row_factory = sqlite3.Row
db = conn.cursor() 
#db.execute("CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,email TEXT NOT NULL UNIQUE, password TEXT NOT NULL)")
app = Flask(__name__)

app.secret_key = "yesindeed"

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/register",methods = ["GET","POST"])
def register():
    if request.method == "POST":
        #client regster
        if request.form.get("form_id") == "clients":
           
           user = request.form.get("username")
           email = request.form.get("emailf")
           password = request.form.get("password")
           cpassword = request.form.get("cpassword")
           rowP = db.execute("SELECT * FROM clients WHERE username = ?",(user,)).fetchall()
           rowE = db.execute("SELECT * FROM clients WHERE email = ?",(email,)).fetchall()
           #check if all information is provided
           if not user or not email or not password or not cpassword:
               return render_template("error.html" , message = " please enter all the information")
           elif password != cpassword:
            return render_template("error.html" , message = " password are not the same")
           #check if the username and email avilable
           elif len(rowP) > 0:
               return render_template("error.html" , message = " username is aleardy taken")
           elif len(rowE) > 0 :
               return render_template("error.html" , message = " email is aleardy taken")

            #insert in database then redirtct
           else:
            hash_password  = generate_password_hash(password)
            db.execute("INSERT INTO clients (username,email,password) Values(?,?,?)",(user , email,hash_password))
            conn.commit()
            session["clients_id"] = db.execute("SELECT id FROM clients WHERE username = ?",(user,)).fetchone()['id']
            return redirect("/indexf")
           

    #todo
        elif request.form.get("form_id") == "owners":
                user = request.form.get("usernameo")
                email = request.form.get("emailo")
                password = request.form.get("passwordo")
                cpassword = request.form.get("cpasswordo")
                store = request.form.get("store")
                location= request.form.get("location")
                rowP = db.execute("SELECT * FROM owners WHERE username = ?",(user,)).fetchall()
                rowE = db.execute("SELECT * FROM owners WHERE email = ?",(email,)).fetchall()
                if not user or not email or not password or not cpassword or not store or not location:
                    return render_template("error.html" , message = " please enter all the information")
                elif password != cpassword:
                    return render_template("error.html" , message = " password are not the same")
                elif len(rowP) > 0:
                    return render_template("error.html" , message = " username is aleardy taken")
                elif len(rowE) > 0 :
                    return render_template("error.html" , message = " email is aleardy taken")
                else:
                    hash_password  = generate_password_hash(password)
                    db.execute("INSERT INTO owners (store, username, email, location, password) VALUES (?,?,?,?,?)", (store,user,email,location,hash_password))
                    conn.commit()
                    session["owners_id"] = db.execute("SELECT id FROM owners WHERE username = ?",(user,)).fetchone()['id']            
                    return redirect("/indexo")
        
    else:    
        return render_template("register.html")
    


@app.route("/login",methods = ["GET","POST"])
def login():
    session.clear()
    if request.method == "POST":
        #client login
        if request.form.get("form_id") == "clients":
           
           user = request.form.get("username")
           password = request.form.get("password")
           row = db.execute("SELECT * FROM clients WHERE username =  ? ", (user,)).fetchall()
           if not user or not password :
               return render_template("error.html" , message = " please enter all the information")
           
           elif len(row) > 0:
             row = row[0]
             db_pass = row['password']
             if check_password_hash(db_pass,password):
                session["clients_id"] =  db.execute("SELECT id FROM clients WHERE username = ?",(user,)).fetchone()['id']
                return redirect("/indexf")
             else:
                 return   render_template("error.html" , message = "wrong password")
           else:
               return render_template("error.html" , message = " wrong username or password")
        
        #todo
        elif   request.form.get("form_id") == "owners":
               
           user = request.form.get("username")
           password = request.form.get("password")
           row = db.execute("SELECT * FROM owners WHERE username =  ? ", (user,)).fetchall()
           if not user or not password :
               return render_template("error.html" , message = " please enter all the information")
           
           elif len(row) > 0:
             row = row[0]
             db_pass = row['password']
             if check_password_hash(db_pass,password):
                session["owners_id"] =  db.execute("SELECT id FROM owners WHERE username = ?",(user,)).fetchone()['id']
                return redirect("/indexo")
             else:
                 return   render_template("error.html" , message = "wrong password")
           else:
               return render_template("error.html" , message = " wrong username or password")
             
        
    else:    
        return render_template("login.html")







@app.route("/logout")
def logout():
    session.pop("clients_id", None)
    session.pop("ownesr_id", None)
    return redirect("/")






#mian





@app.route("/indexf")
def indexf():
    if session.get("clients_id") is None:
        return redirect ("/login")
    return render_template("indexf.html")
@app.route("/indexo")
def indexo():
    if session.get("owners_id") is None:
        return redirect ("/login")
    return render_template("indexo.html")

@app.route("/Sechdule",methods =["GET","POST"] )
def Sechdule():
    Days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    if session.get("owners_id") is None:
        return redirect ("/login")
    
    if request.method == "POST":
        db.execute("DELETE FROM slots WHERE  owner_id = ?",(session["owners_id"],) )
        conn.commit()
        days = request.form.getlist("days")
        start = request.form.getlist("start")
        end =request.form.getlist("end")
        slot =request.form.getlist("per_hour")
       
        for index,d in enumerate(Days):
            if d in days:
                t1 = datetime.strptime(start[index], "%H:%M")
                t2 = datetime.strptime(end[index], "%H:%M")
                if t1 == t2:
                   diff = 24
                else: 
                    diff = (t2-t1).seconds / 3600 
                if  not slot[index]:
                    s = 1
                else:
                    s = int(slot[index])      
                slots_per_day = diff *s 
                for x in range(int(slots_per_day + 1)):
                        print(x)
                        t = t1.strftime("%H:%M")
                        try:
                                db.execute("INSERT INTO slots (owner_id,day,time) VALUES (?,?,?)",( session["owners_id"],d,t))
                                conn.commit()
                        except:
                                pass    
                        t1 = t1 + timedelta (minutes= 60 /s)
        db.execute("DELETE FROM booking WHERE owner_id = ?",(session["owners_id"],))

        # for booking table
        # deldet prevous days
        before_today = date.today().isoformat()   # '2025-11-29'=
        db.execute("DELETE FROM booking WHERE date < ?", (before_today,))
        conn.commit()
        today = date.today()
        fullDays = []
        for i in range(7):
            d = today + timedelta(days=i)
            fullDays.append(d)
        day = ""
        
        for d in fullDays:
            rows = db.execute(
            "SELECT day,time FROM slots WHERE owner_id = ? AND day = ?",
            (session["owners_id"],d.strftime("%A"))
            ).fetchall()
            times = [r["time"] for r in rows]
            day = d.strftime("%A")    
            date_only =d.strftime("%Y-%m-%d")
            time_only = d.strftime("%H:%M")
            start = datetime.strptime("00:00", "%H:%M")
            end   = datetime.strptime("23:59", "%H:%M")
            current = start
            if day in [d["day"] for d in rows]:
                while current < end:
                
                    print(current.strftime("%H:%M"))
                    
                    if current.strftime("%H:%M") in times:
                        try:
                            db.execute("INSERT INTO booking (owner_id,day,time,date,status) VALUES (?,?,?,?,'AV')",( session["owners_id"],day,current.strftime("%H:%M"),date_only))
                            
                        except:
                            pass 
                        conn.commit() 
                    current += timedelta(minutes=5)
                            
                    
        return render_template("set.html",days =days,start = start,end  =end, slot= slots_per_day)
        return render_template("error.html",message = "faaaalse")
    else:
        return render_template("Sechdule.html")
    
@app.route("/viwe_Sechdule") 
def viwe_Sechdule():

    if session.get("owners_id") is None:
       return redirect ("/login")
    
    row = db.execute("select  * from booking WHERE owner_id =?",( session["owners_id"],)).fetchall()
    
    return render_template("veiw_s.html", x =row)


"""
book table
CREATE TABLE booking(
     id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    day TEXT NOT NULL,
    time TEXT NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL,
    client_id TEXT,
    UNIQUE(owner_id, day, time,date),
    FOREIGN KEY(owner_id) REFERENCES owners(id),
    FOREIGN KEY(client_id) REFERENCES clients(id)
    );
"""   



@app.route("/search",methods = ["GET","POST"])
def search():
    if session.get("clients_id") is None:
       return redirect ("/login")
    
    if request.method == "POST":
        name = request.form.get("name")
        Towners = db.execute("SELECT * from owners WHERE store LIKE ?  ", (name,) ).fetchall()
        return render_template("show.html",Towners = Towners)
    else:
        return render_template("search.html")
    

@app.route("/book",methods = {"GET","POST"})
def book():
    if session.get("clients_id") is None:
       return redirect ("/login")
    if request.method ==  "POST":
        id = request.form.get("id")
        # insert the secheual on demand
        # delete previous
        before_today = date.today().isoformat()   # '2025-11-29'=
        db.execute("DELETE FROM booking WHERE date < ?", (before_today,))

        today = date.today()
        fullDays = []
        for i in range(7):
            d = today + timedelta(days=i)
            fullDays.append(d)
        day = ""
        
        for d in fullDays:
            rows = db.execute(
            "SELECT day,time FROM slots WHERE owner_id = ? AND day = ?",
            ( id,d.strftime("%A"),)
            ).fetchall()
            times = [r["time"] for r in rows]
            day = d.strftime("%A")    
            date_only =d.strftime("%Y-%m-%d")
            time_only = d.strftime("%H:%M")
            start = datetime.strptime("00:00", "%H:%M")
            end   = datetime.strptime("23:59", "%H:%M")
            current = start
            if day in [d["day"] for d in rows]:
                while current < end:
                
                    print(current.strftime("%H:%M"))
                    
                    if current.strftime("%H:%M") in times:
                        try:
                            db.execute("INSERT INTO booking (owner_id,day,time,date,status) VALUES (?,?,?,?,'AV')",( session["owners_id"],day,current.strftime("%H:%M"),date_only))
                            
                        except:
                            pass 
                        conn.commit() 
                    current += timedelta(minutes=5)
                    #end
        Tbooking = db.execute("SELECT * from booking WHERE owner_id = ?", (id,)).fetchall()
        try:
            owner_id = Tbooking[0]["owner_id"]
        except:
            pass
        return render_template("book.html",Tbooking = Tbooking, owner_id= owner_id)
    else:
        return  render_template("errorr.html", message = "error")
    
@app.route("/my_booking",methods= {"GET","POST"})
def my_booking():
    if session.get("clients_id") is None:
       return redirect ("/login")
    
    if request.method =="POST":
        time = request.form.get("time")
        day = request.form.get("day")
        id =request.form.get("owner_id")
        #return render_template("make.html",x =time , y = day , z =id)
    
        status =  db.execute("SELECT status FROM booking WHERE owner_id =? AND day = ? AND time = ?",(id,day,time)).fetchone()
        if not status:
            return render_template("error.html", message = "enter an avilable time")
        if status[0] == "AV":
            db.execute("UPDATE booking set status = 'booked' , client_id = ?  WHERE owner_id = ? AND day = ? AND time = ? ",( session["clients_id"] , id,day,time))
            conn.commit()
            return redirect("/my_booking")
        else:
            return render_template("error.html",message ="the time is booked")
    else: 

        #row = db.execute("select * from booking WHERE  client_id = ?", (session["clients_id"],) ).fetchall()
        #store = db.execute(" select store from owners WHERE id = (select owner_id from booking WHERE  client_id = ?)", (session["clients_id"],) ).fetchall()
        row = db.execute("Select owners.store, booking.day, booking.time, booking.date, booking.status, booking.client_id From owners INNER JOIN booking ON owners.id = booking.owner_id WHERE client_id= ?", ( session["clients_id"],)).fetchall()
        return render_template("mybooking.html",row = row) 
           



     
if __name__ == "__main__":
    app.run(debug = True)