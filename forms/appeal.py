# -*- coding: utf-8 -*-
'''
APPEAL FORM
'''
# Import required packages
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, validators

# Class for filling appeal PDF
class AppealForm(FlaskForm):

	# Options for box 1 dropdown
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
	name = StringField('Taxpayer_Name', [validators.Length(min=4, max=120)])
	email = StringField('Taxpayer_Email', [validators.Length(min=4, max=120)])
	address = StringField('Taxpayer_Street', [validators.Length(min=4, max=120)])
	city = StringField('Taxpayer_City', [validators.Length(min=4, max=120)])
	state = StringField('Taxpayer_State', [validators.Length(min=2, max=2)])
	zipcode = StringField('Taxpayer_Zipcode', [validators.Length(min=5, max=5)])
	phone = StringField('Taxpayer_Phone', [validators.Length(min=4, max=120)])
	relation = SelectField('Taxpayer_Relation', choices=taxpayer_options, 
		validators=validators.Required())

	# Box 2 fields
	appeal_type = SelectField('Appeal_Type', choices=type_options, 
		validators=validators.Required())
	appeal_usage = SelectField('Appeal_Usage', choices=type_options, 
		validators=validators.Required())
	purchase_2016 = StringField('Appeal_2016', [validators.Length(min=4, max=120)])
	purchase_price = StringField('Appeal_Price', [validators.Length(min=4, max=120)])