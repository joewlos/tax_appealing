# -*- coding: utf-8 -*-
'''
APPEAL FORM
'''
# Import required packages
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, validators

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

	# Options for box 1 dropdowns
	taxpayer_options = [
		'Owner',
		'Former Owner Liable for Tax',
		'Tenant Liable for Tax',
		'Executor',
		'Beneficiary of Trust',
		'Other'
	]
	type_options = [
		'Current Year Appeal Only',
		'Current Year and Certificate of Error',
		'Certificate of Error Only',
		'Taxable',
		'Exempt'
	]
	usage_options = [
		'Single Family',
		'6 Apartments or Less',
		'Mixed Use',
		'Other'
	]

	# Box 1 fields
	name = StringField('Taxpayer_Name', 
		validators=[
			validators.Length(min=4, max=120),
			validators.DataRequired(message='Name Required')
		]
	)
	email = StringField('Taxpayer_Email', 
		validators=[
			validators.Email(message='Invalid Email Address'),
			validators.DataRequired(message='Email Required')
		]
	)
	address = StringField('Taxpayer_Street', 
		validators=[
			validators.Length(min=4, max=120),
			validators.DataRequired(message='Street Address Required')
		]
	)
	city = StringField('Taxpayer_City', 
		validators=[
			validators.Length(min=4, max=120),
			validators.DataRequired(message='City Required')
		]
	)
	state = SelectField('Taxpayer_State', 
		choices=states.keys(),
		validators=[
			validators.InputRequired(message='State Required')
		]
	)
	zipcode = StringField('Taxpayer_Zipcode', [validators.Length(min=5, max=5)])
	phone = StringField('Taxpayer_Phone', [validators.Length(min=4, max=120)])
	relation = SelectField('Taxpayer_Relation', choices=taxpayer_options, 
		validators=validators.Required())

	# Box 2 fields
	appeal_type = SelectField('Appeal_Type', 
		choices=type_options, 
		validators=[
			validators.InputRequired(message='Appeal Type Required')
		]
	)
	appeal_usage = SelectField('Appeal_Usage', 
		choices=type_options, 
		validators=[
			validators.InputRequired(message='Usage Required')
		]
	)
	purchase_2016 = StringField('Purchase_2016', 
		validators=[
			validators.DataRequired(message='Purchase Year Required')
		]
	)
	purchase_price = StringField('Appeal_Price', [validators.Length(min=4, max=120)])