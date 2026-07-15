from unittest import result

import mysql.connector
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="praveenadevafra@123",
    database="mealmind"
    )

cursor = db.cursor()
current_attendance = 0
attendance_history = []
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "admin123":
            return redirect('/dashboard')
        return "Invalid Login"
    return render_template('login.html')


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():

    food_required = current_attendance * 0.8

    food_saved = food_required * 0.1

    return render_template(
        'dashboard.html',
        attendance=current_attendance,
        food=food_required,
        saved=food_saved
    )
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
 global current_attendance
 if request.method == 'POST':
        current_attendance = int(request.form['attendance'])
        food_required = current_attendance * 0.8
        food_saved = round(food_required * 0.1, 2)
        attendance_history.append(
            {
                "attendance": current_attendance,
                "food": food_required
                }
                )
        cursor.execute(
            "INSERT INTO attendance (attendance_count) VALUES (%s)",
            (current_attendance,)
            )
        db.commit()
        return render_template(
            "attendance.html",
            attendance=current_attendance,
            food=food_required,
            saved=food_saved
            )
 return render_template("attendance.html")


recipes = {
    "Idly": {"Rice": 0.08, "Dal": 0.03},
    "Pongal": {"Rice": 0.10, "Dal": 0.04},
    "Poori": {"Wheat Flour": 0.12, "Oil": 0.03},
    "Masala": {"Potato": 0.08},
    "Upma": {"Rava": 0.10},
    "Dosa": {"Rice": 0.10, "Dal": 0.03},
    "Chapati": {"Wheat Flour": 0.10},
    "Rice": {"Rice": 0.25},
    "Sambar": {"Dal": 0.04, "Vegetables": 0.08},
    "Rasam": {"Dal": 0.02},
    "Dal": {"Dal": 0.04},
    "Kurma": {"Vegetables": 0.08, "Oil": 0.02},
    "Kara Kuzhambu": {"Dal": 0.03, "Vegetables": 0.08},
    "Vegetable Curry": {"Vegetables": 0.10},
    "Vada": {"Dal": 0.05, "Oil": 0.02},
    "Idiyappam": {"Rice": 0.08},
    "Veg Biryani": {"Rice": 0.30, "Vegetables": 0.12},
    "Paneer Gravy": {"Paneer": 0.05, "Oil": 0.02},
    "Chutney": {"Oil": 0.01}
    }
def calculate_meal(items, attendance):
    result = {}
    for item in items:
        if item in recipes:
            for ingredient, qty in recipes[item].items():
                
                if ingredient not in result:
                    result[ingredient] = 0
                    result[ingredient] += attendance * qty

    return result




@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == 'POST':
        attendance = int(request.form['attendance'])
        menu = request.form['menu']
        hostel_menu = {
            "Monday": {
                "Breakfast": ["Idly", "Pongal"],
                "Lunch": ["Rice", "Sambar"],
                "Dinner": ["Chapati", "Kurma"]
                },
                "Tuesday": {
                    "Breakfast": ["Poori", "Masala"],
                    "Lunch": ["Rice", "Kara Kuzhambu"],
                    "Dinner": ["Dosa", "Chutney"]
                    },
                "Wednesday": {
                    "Breakfast": ["Upma", "Chutney"],
                    "Lunch": ["Rice", "Sambar"],
                    "Dinner": ["Chapati", "Dal"]
                },
                "Thursday": {
                    "Breakfast": ["Idly", "Chutney"],
                    "Lunch": ["Rice", "Rasam"],
                    "Dinner": ["Dosa", "Sambar"]
                },
                "Friday": {
                     "Breakfast": ["Pongal", "Vada"],
                     "Lunch": ["Rice", "Vegetable Curry"],
                     "Dinner": ["Chapati", "Kurma"]
                },
                "Saturday": {
                    "Breakfast": ["Poori", "Masala"],
                    "Lunch": ["Rice", "Kara Kuzhambu"],
                    "Dinner": ["Dosa", "Chutney"]
                },
                "Sunday": {
                    "Breakfast": ["Idiyappam", "Kurma"],
                    "Lunch": ["Veg Biryani"],
                    "Dinner": ["Chapati", "Paneer Gravy"]
                }
            }
        today_menu = hostel_menu[menu]
        breakfast_items = today_menu["Breakfast"]
        lunch_items = today_menu["Lunch"]
        dinner_items = today_menu["Dinner"]
        breakfast_prediction = calculate_meal(
             breakfast_items,
             attendance
             )
        lunch_prediction = calculate_meal(
            lunch_items,
            attendance
            )
        dinner_prediction = calculate_meal(
            dinner_items,
            attendance
            )
        rice = attendance * 0.25
        dal = attendance * 0.04
        vegetables = attendance * 0.08
        cursor.execute(
            """
            INSERT INTO prediction_history
            (menu, attendance, rice, dal, vegetables)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (menu, attendance, rice, dal, vegetables)
            )
        db.commit()
        breakfast_prediction = "<br>".join(
             [f"{k} : {round(v,2)} Kg" for k, v in breakfast_prediction.items()]
             )
        lunch_prediction = "<br>".join(
            [f"{k} : {round(v,2)} Kg" for k, v in lunch_prediction.items()]
            )
        dinner_prediction = "<br>".join(
            [f"{k} : {round(v,2)} Kg" for k, v in dinner_prediction.items()]
            )
        return render_template(
            "prediction_result.html",
            menu=menu,
            attendance=attendance,
            today_menu=today_menu,
            rice=rice,
            dal=dal,
            vegetables=vegetables,
            breakfast_prediction=breakfast_prediction,
            lunch_prediction=lunch_prediction,
            dinner_prediction=dinner_prediction
            )
    return render_template('prediction.html')






@app.route('/reports')
def reports():
    cursor.execute(
        "SELECT * FROM attendance ORDER BY id DESC"
        )
    history = cursor.fetchall()
    return render_template(
    'reports.html',
    history=history
)

@app.route('/ngo')
def ngo():

    food_required = current_attendance * 0.8
    food_saved = food_required * 0.1

    return render_template(
        'ngo.html',
        saved=food_saved
    )
@app.route('/analytics')
def analytics():

    if len(attendance_history) == 0:

        return render_template(
            'analytics.html',
            total=0,
            highest=0,
            lowest=0,
            average=0
        )

    attendance_values = [
        record["attendance"]
        for record in attendance_history
    ]

    total = len(attendance_values)
    highest = max(attendance_values)
    lowest = min(attendance_values)
    average = round(sum(attendance_values) / total, 2)

    return render_template(
        'analytics.html',
        total=total,
        highest=highest,
        lowest=lowest,
        average=average,
        history=attendance_history
    )
@app.route('/about')
def about():
    return render_template('about.html')
inventory_data = {
"rice": 0,
"vegetables": 0,
"milk": 0,
"oil": 0
}

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    global inventory_data
    if request.method == 'POST':
        inventory_data["rice"] = int(request.form['rice'])
        inventory_data["vegetables"] = int(request.form['vegetables'])
        inventory_data["milk"] = int(request.form['milk'])
        inventory_data["oil"] = int(request.form['oil'])
        cursor.execute(
             """
               INSERT INTO inventory
               (rice, vegetables, milk, oil)
               VALUES (%s, %s, %s, %s)
               """,
               (
                   inventory_data["rice"],
                   inventory_data["vegetables"],
                   inventory_data["milk"],
                   inventory_data["oil"]
                     )
                       )
        db.commit()
        return "Inventory Saved Successfully"
    return render_template('inventory.html')




if __name__ == '__main__':
    app.run(debug=True) 
