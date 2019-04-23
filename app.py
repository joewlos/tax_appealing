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
	Security, 
	SQLAlchemyUserDatastore
)
from flask_security.forms import LoginForm
from flask_security.utils import encrypt_password
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

# Don't track modifications
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the db
from models.shared import db
db.init_app(app)

# Import the property and user models
from models.property import Properties
from models.user import Users, Roles

# Setup security
user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)
security = Security(app, user_datastore)


'''
CONTEXT
'''
# Global variable for pages that have city background
@app.context_processor
def inject_data():
	return {
		'city_background': [
			'/',
			'/index',
			'/login_user'
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
LOGIN 
'''
# Login user and redirect to correct property page
@app.route('/login_user', methods=['GET', 'POST'])
@app.route('/login_user/<prop_id>', methods=['GET', 'POST'])
def login_user(prop_id=None):

	# Get the login user form
	login_user_form = LoginForm()

	# Render the template
	return render_template('login_user.html',
		prop_id=prop_id, login_user_form=login_user_form)


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
PROPERTY VIEW
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
RETURN JSON
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
EXECUTION IN TERMINAL
'''
# Running app with updates for template files
if __name__ == '__main__':
	extra_dirs = [
		'templates',
		'static'
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
