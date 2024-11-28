#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='127.0.0.1',
                       port=8889,
                       user='root',
                       password='root',
                       db='airline_ticket_db',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
	return render_template('login.html')

#Define route for register
@app.route('/register1')
def register():
	return render_template('customer_register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM user WHERE username = %s and password = %s'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

#Authenticates the register
@app.route('/register1Auth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM user WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This customer already exists"
		return render_template('customer_register.html', error = error)
	else:
		ins = 'INSERT INTO Customer VALUES(%s, %s)'
		cursor.execute(ins, (username, password))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/register2Auth', methods=['GET', 'POST'])
def register2Auth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM user WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This customer already exists"
		return render_template('customer_register.html', error = error)
	else:
		ins = 'INSERT INTO Customer VALUES(%s, %s)'
		cursor.execute(ins, (username, password))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/home')
def home():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    cursor.execute(query, (username))
    data1 = cursor.fetchall()
    for each in data1:
        print(each['blog_post'])
    cursor.close()
    return render_template('home.html', username=username, posts=data1)

		
@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['username']
	cursor = conn.cursor()
	blog = request.form['blog']
	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
	cursor.execute(query, (blog, username))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')


@app.route('/customer_register')
def customer_register():
    return render_template('customer_register.html')

@app.route('/staff_register')
def staff_register():
    return render_template('staff_register.html')

@app.route('/search-flights', methods=['GET'])
def searchFlights():
    # Get form data
    source_city = request.args.get('source-city')
    source_airport = request.args.get('departure-airport')
    destination_city = request.args.get('destination-city')
    destination_airport = request.args.get('destination-airport')
    departure_date = request.args.get('departure-date')
    return_date = request.args.get('return-date')

    # Construct the query
    cursor = conn.cursor()
    query = '''
    SELECT 
        f.flight_number,
        f.airline_name,
        f.departure_datetime,
        f.arrival_datetime,
        f.base_price,
        f.flight_status,
        a1.airport_name AS departure_airport,
        a1.city AS departure_city,
        a2.airport_name AS destination_airport,
        a2.city AS destination_city
    FROM l
        Flight AS f
    JOIN 
        Airport AS a1 ON f.departure_airport_code = a1.airport_code
    JOIN 
        Airport AS a2 ON f.arrival_airport_code = a2.airport_code
    WHERE 
        a1.city = %s AND a1.airport_name = %s
        AND a2.city = %s AND a2.airport_name = %s
        AND f.departure_datetime >= %s
    '''
    # If return date is provided, add it to the query (optional)
    params = [source_city, source_airport, destination_city, destination_airport, departure_date]
    if return_date:
        query += " AND return_date = %s"
        params.append(return_date)

    # Execute the query
    cursor.execute(query, params)
    flights = cursor.fetchall()
    cursor.close()

    # Pass results to the template
    return render_template('search_results.html', flights=flights)
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
