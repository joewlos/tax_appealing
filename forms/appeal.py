# -*- coding: utf-8 -*-
'''
APPEAL FORM
'''
# Import required packages
from flask_wtf import FlaskForm
from wtforms import (
	BooleanField,
	IntegerField,
	SelectField,
	StringField,
	validators
)
from wtforms.fields.html5 import TelField

# Class for filling appeal form
class AppealForm(FlaskForm):

	# States for form
	states = {
		'AK': 'Alaska',
		'AL': 'Alabama',
		'AR': 'Arkansas',
		'AZ': 'Arizona',
		'CA': 'California',
		'CO': 'Colorado',
		'CT': 'Connecticut',
		'DC': 'District of Columbia',
		'DE': 'Delaware',
		'FL': 'Florida',
		'GA': 'Georgia',
		'HI': 'Hawaii',
		'IA': 'Iowa',
		'ID': 'Idaho',
		'IL': 'Illinois',
		'IN': 'Indiana',
		'KS': 'Kansas',
		'KY': 'Kentucky',
		'LA': 'Louisiana',
		'MA': 'Massachusetts',
		'MD': 'Maryland',
		'ME': 'Maine',
		'MI': 'Michigan',
		'MN': 'Minnesota',
		'MO': 'Missouri',
		'MS': 'Mississippi',
		'MT': 'Montana',
		'NC': 'North Carolina',
		'ND': 'North Dakota',
		'NE': 'Nebraska',
		'NH': 'New Hampshire',
		'NJ': 'New Jersey',
		'NM': 'New Mexico',
		'NV': 'Nevada',
		'NY': 'New York',
		'OH': 'Ohio',
		'OK': 'Oklahoma',
		'OR': 'Oregon',
		'PA': 'Pennsylvania',
		'PR': 'Puerto Rico',
		'RI': 'Rhode Island',
		'SC': 'South Carolina',
		'SD': 'South Dakota',
		'TN': 'Tennessee',
		'TX': 'Texas',
		'UT': 'Utah',
		'VA': 'Virginia',
		'VT': 'Vermont',
		'WA': 'Washington',
		'WI': 'Wisconsin',
		'WV': 'West Virginia',
		'WY': 'Wyoming'
	}
	state_values = states.values()
	state_values.sort()
	state_options = [(i+1, v) for i,v in enumerate(state_values)]

	# Options for box 1 dropdowns
	taxpayer_options = [
		(1, 'Owner'),
		(2, 'Former Owner Liable for Tax'),
		(3, 'Tenant Liable for Tax'),
		(4, 'Executor'),
		(5, 'Beneficiary of Trust'),
		(6, 'Other')
	]
	usage_options = [
		(1, 'Single Family'),
		(2, '6 Apartments or Less'),
		(3, 'Mixed Use'),
		(4, 'Other')
	]

	# Box 1 fields
	name = StringField('Name', 
		validators=[
			validators.Length(min=1, max=120),
			validators.DataRequired(message='Name Required')
		]
	)
	email = StringField('Email', 
		validators=[
			validators.Email(message='Invalid Email Address'),
			validators.DataRequired(message='Email Required')
		]
	)
	address = StringField('Street Address', 
		validators=[
			validators.Length(min=1, max=120),
			validators.DataRequired(message='Street Address Required')
		]
	)
	city = StringField('City', 
		validators=[
			validators.Length(min=1, max=120),
			validators.DataRequired(message='City Required')
		]
	)
	state = SelectField('State', 
		choices=state_options,
		coerce=int,
		validators=[
			validators.InputRequired(message='State Required')
		]
	)
	zipcode = StringField('Zipcode', 
		validators=[
			validators.Length(min=5, max=5),
			validators.DataRequired(message="Zipcode Required")
		]
	)
	phone = TelField('Phone', 
		validators=[
			validators.DataRequired(message="Phone Number Required")
		]
	)
	filer_status = SelectField('Filer Status', 
		choices=taxpayer_options,
		coerce=int,
		validators=[
			validators.InputRequired(message='Filer Status Required')
		]
	)

	# Box 2 fields
	property_usage = SelectField('Property Usage', 
		choices=usage_options, 
		coerce=int,
		validators=[
			validators.InputRequired(message='Property Usage Required')
		]
	)
	purchase_year = StringField('Purchase Year', 
		validators=[
			validators.Length(min=4, max=4),
			validators.DataRequired(message='Purchase Year Required')
		]
	)
	purchase_price = IntegerField('Purchase Price', 
		validators=[
			validators.DataRequired(message='Purchase Price Required')
		]
	)

	# Box 3 fields
	agree = BooleanField('Agree to Terms and Conditions?',
		validators=[
			validators.DataRequired(message='Agreement is Required')
		]
	)