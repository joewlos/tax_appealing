# -*- coding: utf-8 -*-
'''
INITIALIZE
'''
# Import required Flask packages
from flask import (
	Flask, 
	jsonify,
	redirect,
	render_template,
	request,
	send_from_directory,
	url_for
)

# Import other required packages
from flask_security import (
	current_user,
	login_required,
	login_user,
	Security,
	SQLAlchemyUserDatastore
)
from flask_security.forms import LoginForm, RegisterForm
from flask_security.utils import encrypt_password, verify_password
from graphing.comp import *
import os

# Initialize app with static folder declared
app = Flask(__name__, static_folder='static')

# Configure for db if local or on Heroku
if 'ON_HEROKU' not in os.environ:
	from config import Configuration
	app.config['SQLALCHEMY_DATABASE_URI'] = Configuration.URI
	app.config['SECRET_KEY'] = Configuration.SECRET
	app.config['SECURITY_PASSWORD_SALT'] = Configuration.SECRET
else:
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
	app.config['SECRET_KEY'] = os.environ['SECRET']
	app.config['SECURITY_PASSWORD_SALT'] = os.environ['SECRET']

# Don't track modifications and allow registrations
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_REGISTERABLE'] = True

# Initialize the db
from models.shared import db
db.init_app(app)

# Import the property and user models
from models.property import Properties
from models.user import Users, Roles

# Setup security
user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)
security = Security(app, user_datastore)

# Import custom forms for appeals
from forms.appeal import AppealForm


'''
CONTEXT
'''
# Global variable for login pages that have city background
@app.context_processor
def inject_data():
	return {
		'city_background': [
			'user_login',
			'user_register'
		]
	} 


'''
BASE VIEWS
'''
# Homepage 
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():

	# Render the index template
	return render_template('index.html')

# About
@app.route('/about', methods=['GET'])
def about():

	# Render the about template
	return render_template('about.html')

# Cook County
@app.route('/cook_county', methods=['GET'])
def cook():

	# Render the about template
	return render_template('cook_county.html')

# Cook County
@app.route('/terms_conditions', methods=['GET'])
def terms():

	# Render the about template
	return render_template('terms_conditions.html')


'''
ACCOUNT
'''
# Login user and redirect to correct property page
@app.route('/user_login', methods=['GET', 'POST'])
@app.route('/user_login/<prop_id>', methods=['GET', 'POST'])
def user_login(prop_id=None):

	# If the user is already authenticated, redirect
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	# Get the login user form
	form = LoginForm()

	# Validate the form if submitted via post request
	if request.method == 'POST':
		if form.validate_on_submit():
			email = form.email.data
			user = Users.check_user(email)

			# Complete the login and redirect to correct page
			login_user(user)
			if not prop_id:
				return redirect(url_for('index'))  # Should be account page
			else:
				return redirect(url_for('prop', prop_id=prop_id))

		# Return the failure message if form not validated
		else:
			err_msg = 'Invalid Email or Password!'
			return render_template('user_login.html',
				prop_id=prop_id, login_user_form=form, err_msg=err_msg)

	# Render the template
	return render_template('user_login.html',
		prop_id=prop_id, login_user_form=form, err_msg=False)

# Register for a new account and direct to prop
@app.route('/user_register', methods=['GET', 'POST'])
@app.route('/user_register/<prop_id>', methods=['GET', 'POST'])
def user_register(prop_id=None):

	# If the user is already authenticated, redirect
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	# Get the register user form
	form = RegisterForm()

	# Validate the form if submitted view post request
	if request.method == 'POST':
		email = form.email.data
		pswd = form.password.data
		confirm = form.password_confirm.data
		if form.validate_on_submit():

			# Create user and update password
			user_datastore.create_user(email=email, password=pswd)
			db.session.commit()
			user = Users.check_user(email)

			# Complete the login and redirect to correct page
			login_user(user)
			if not prop_id:
				return redirect(url_for('index'))  # Should be account page
			else:
				return redirect(url_for('prop', prop_id=prop_id))

		# Check if the user email exists
		else:
			if Users.check_user(email):
				err_msg = 'An Account for this Email Already Exists!'

			# If the password doesn't match
			elif pswd != confirm:
				err_msg = 'Passwords Do Not Match!'

			# Catch for any other errors
			else:
				err_msg = 'Invalid Email!'
			
			# Return the template with the correct error message
			return render_template('user_register.html',
				prop_id=prop_id, register_user_form=form, err_msg=err_msg)

	# Render the template
	return render_template('user_register.html',
		prop_id=prop_id, register_user_form=form, err_msg=False)

# Route for viewing account information
@app.route('/account', methods=['GET'])
@login_required
def account():

	# Get the current user
	user = current_user

	# Render the template
	return render_template('account.html',
		user=user)


'''
SEARCH VIEW
'''
# Show the selected property if address match
@app.route('/search', methods=['POST'])
def search():

	# Get the address and find out if its a match
	address = request.form['autocomplete']
	match = Properties.get_address(address)

	# If there's an exact match, go to the property
	if match:
		return redirect(url_for('prop', prop_id=match))

	# Otherwise, show a list of possible properties
	else:
		possible = Properties.get_similar_addresses(address, 9)
		return render_template('search.html',
			possible=possible, search_term=address)


'''
RETURN JSON FOR SEARCH
'''
# Get list of dicts for autocomplete property search
@app.route('/autocomplete', methods=['GET'])
def autocomplete():

	# Use the database function
	search = request.args.get('q')
	query = Properties.get_similar_addresses(search, 6)

	# Get the addresses and ids as lists
	prop_addresses = [x['address'] for x in query]
	prop_ids = [x['id'] for x in query]

	# Return the results as JSON
	return jsonify(matching_results=prop_addresses)


'''
PROPERTY VIEWS
'''
# Show information on a single property
@app.route('/prop/<prop_id>', methods=['GET'])
def prop(prop_id):

	# Property information and comparables
	prop = Properties.get_property(prop_id)
	comps = Properties.get_comparables(prop_id)

	# If there are not comps, there are no savings and no comp graph
	if 'tax_amount' in comps.keys() and comps['count_comparable']:
		savings = comps['tax_amount'] - comps['avg_comparable']
		plot, layout = comp_graph(comps)
	else:
		savings = None
		plot, layout = None, None

	# Return the property template
	return render_template('prop.html', p=prop, comps=comps,
		savings=savings, plot=plot, layout=layout)

# Form for completing an appeal
@app.route('/appeal/<prop_id>', methods=['GET', 'POST'])
@login_required
def appeal(prop_id):

	# Property information and comparables
	prop = Properties.get_property(prop_id)
	comps = Properties.get_comparables(prop_id)

	# If there are no comps, reroute to the prop page
	if 'tax_amount' not in comps.keys() and not comps['count_comparable']:
		return redirect(url_for('prop', prop_id=prop_id))

	# Find the possible savings
	savings = comps['tax_amount'] - comps['avg_comparable']

	# Get the appeal user form
	form = AppealForm()
	form.email.data = current_user.email

	# Validate the form if submitted view post request
	if request.method == 'POST':
		if form.validate_on_submit():
			return redirect(url_for('index'))

		else:
			for f, e in form.errors.items():
				if e[0] == 'Not a valid choice':
					new_f = f.replace('_', ' ').title()
					err_msg = "{} Not Valid".format(new_f)
				else:
					err_msg = e[0]
			return render_template('appeal.html', 
				p=prop, comps=comps, appeal_form=form, 
				err_msg=err_msg, savings=savings)

	# Return the property template
	return render_template('appeal.html', 
		p=prop, comps=comps, appeal_form=form, 
		err_msg=None, savings=savings)

'''
STATIC FILES
'''
# Serve robots.txt from the static folder
@app.route('/robots.txt', methods=['GET'])
def robots():

	# Send the file from static folder
	doc_path = os.path.join(app.static_folder, 'documents')
	return send_from_directory(doc_path, 'robots.txt')


'''
EXECUTION IN TERMINAL
'''
# Running app with updates for template files
if __name__ == '__main__':
	extra_dirs = [
		'forms',
		'static',
		'templates'
	]
	extra_files = extra_dirs[:]

	# Find all files in extra directories
	for extra_dir in extra_dirs:
		for dirname, dirs, files in os.walk(extra_dir):
			for filename in files:
				filename = os.path.join(dirname, filename)
				if os.path.isfile(filename):
					extra_files.append(filename)

	# Check if Heroku in environ before running
	if 'ON_HEROKU' not in os.environ:
		app.run(extra_files=extra_files, debug=True)
	else:
		app.run()  # On Heroku
