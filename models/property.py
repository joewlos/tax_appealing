# -*- coding: utf-8 -*-
'''
PROPERTY MODEL
'''
import numpy as np
from shared import db
from sqlalchemy import and_, between, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import aliased

# Property model for querying details and comps
class Properties(db.Model):
	__tablename__ = "properties"

	# Primary Key
	id = db.Column("pin14_id", db.BIGINT, primary_key=True)

	# Data
	age = db.Column(db.Integer)
	air = db.Column(db.TEXT)
	apartments = db.Column(db.Integer)
	assessor_office_url = db.Column(db.TEXT)
	attic = db.Column(db.TEXT)
	basement = db.Column(db.TEXT)
	building_assessed_2015 = db.Column(db.Integer)
	building_assessed_2016 = db.Column(db.Integer)
	building_sqft = db.Column(db.Integer)
	city = db.Column(db.TEXT)
	classification = db.Column(db.Integer)
	desc = db.Column(db.TEXT)
	est_market_value_2015 = db.Column(db.Integer)
	est_market_value_2016 = db.Column(db.Integer)
	exterior = db.Column(db.TEXT)
	fireplaces = db.Column(db.Integer)
	full_baths = db.Column(db.Integer)
	half_baths = db.Column(db.Integer)
	garage = db.Column(db.TEXT)
	image_url = db.Column(db.TEXT)
	land_assessed_2015 = db.Column(db.Integer)
	land_assessed_2016 = db.Column(db.Integer)
	land_sqft = db.Column(db.Integer)
	neighborhood = db.Column(db.Integer)
	official_pin14 = db.Column(db.TEXT)
	property_location = db.Column(db.TEXT)
	res_type = db.Column(db.TEXT)
	township = db.Column(db.TEXT)
	use = db.Column(db.TEXT)

	# Init
	def __init__(
		self,
		id, 
		age, 
		air, 
		apartments, 
		assessor_office_url, 
		attic, 
		basement,
		building_assessed_2015, 
		building_assessed_2016, 
		building_sqft, 
		city, 
		classification,
		desc, 
		est_market_value_2015,
		est_market_value_2016,
		exterior,
		fireplaces, 
		full_baths, 
		half_baths, 
		garage, 
		image_url,
		land_assessed_2015, 
		land_assessed_2016, 
		land_sqft, 
		neighborhood, 
		official_pin14, 
		property_location,
		res_type, 
		township, 
		use
	):
		self.pin14_id = id
		self.age = age
		self.air = air
		self.apartments = apartments
		self.assessor_office_url = assessor_office_url
		self.attic = attic
		self.basement = basement
		self.building_assessed_2015 = building_assessed_2015
		self.building_assessed_2016 = building_assessed_2016
		self.building_sqft = building_sqft
		self.city = city
		self.classification = classification
		self.desc = desc
		self.est_market_value_2015 = est_market_value_2015
		self.est_market_value_2016 = est_market_value_2016
		self.exterior = exterior
		self.fireplaces = fireplaces
		self.full_baths = full_baths
		self.half_baths = half_baths
		self.garage = garage
		self.image_url = image_url
		self.land_assessed_2015 = land_assessed_2015
		self.land_assessed_2016 = land_assessed_2016
		self.land_sqft = land_sqft
		self.neighborhood = neighborhood
		self.official_pin14 = official_pin14
		self.property_location = property_location
		self.res_type = res_type
		self.township = township
		self.use = use

	# Representation
	def __repr__(self):
		return '<pin14 %r>' % self.id


	'''
	SEARCH FOR PROPERTY
	'''
	# Add a property for full address, trimming whitespace
	@hybrid_property
	def full_location(self):
		loc = '{0}, {1}'.format(self.property_location.strip(),
			self.city.strip())
		return loc

	# The full trimmed address also needs an expression for queries
	@full_location.expression
	def full_location(cls):
		ad = func.rtrim(func.ltrim(cls.property_location))
		city = func.rtrim(func.ltrim(cls.city))
		return func.concat(ad, ', ', city)

	# Filter addresses for homepage autocomplete
	@classmethod
	def get_similar_addresses(class_, search, n):
		Properties = class_

		# Break the search term by space
		all_terms = search.split(' ')

		# Construct the query, like for each word
		q = Properties.query
		for term in all_terms:
			term = '%{}%'.format(term.upper().replace(',', ''))
			q = q.filter(Properties.full_location.like(term))

		# Add columns to the query and execute for only the specified n
		q = q.order_by(
			Properties.full_location
		).add_columns(
			Properties.id.label('id'),
			Properties.full_location.label('address')
		).limit(n).all()

		# Return the results as list of dict
		results = [x._asdict() for x in q]
		return results

	# Get a prop id from an address or return none
	@classmethod
	def get_address(class_, address):
		Properties = class_

		# Filter by full location
		address = address.upper().strip()
		q = Properties.query.filter(Properties.full_location == address).first()

		# Return the id or return none if not found
		if q:
			return q.id
		else:
			return None


	'''
	PROPERTY DETAILS
	'''
	# Calculate property tax for the property
	@hybrid_property
	def tax_amount(self):
		
		# Values for calc
		level = 0.1
		equalizer = 2.9627
		rate = 0.07266

		# Use the market value to calculate the tax
		value = self.est_market_value_2016
		tax = int(value * level * equalizer * rate)
		return tax

	# The tax also needs an expression for queries
	@tax_amount.expression
	def tax_amount(cls):

		# Values for calc
		level = 0.1
		equalizer = 2.9627
		rate = 0.07266

		# Use the market value to calculate the tax
		value = cls.est_market_value_2016
		tax = func.round(value * level * equalizer * rate)
		return tax

	# Get the details of a single property as a dict
	@classmethod
	def get_property(class_, prop_id):
		Properties = class_

		# Query the id and return as dict
		q = Properties.query.filter_by(id=prop_id).first()
		return q

	# Query a single property id for comparables
	@classmethod
	def get_comparables(class_, prop_id):
		Properties = class_
		
		# Alias for the matching properties
		s = aliased(Properties, name='matching_properties')

		# Join the table to the subquery
		q = Properties.query.join(
			s, and_(
				Properties.id == prop_id,
				Properties.id != s.id,  # Don't match to self
				Properties.township == s.township,
				Properties.neighborhood == s.neighborhood,
				Properties.use == s.use,
				Properties.exterior == s.exterior,
				Properties.classification == s.classification,
				between(Properties.age, s.age - 20, s.age + 20),
				between(Properties.building_sqft, s.building_sqft - 300, s.building_sqft + 300),
				between(Properties.building_sqft, s.land_sqft - 400, s.land_sqft + 400)
			)
		).add_columns(
			Properties.id,
			Properties.est_market_value_2016.label('value'),
			Properties.tax_amount.label('tax_amount'),
			s.id.label('match_id'),
			s.est_market_value_2016.label('match_value'),
			s.tax_amount.label('match_tax_amount')
		).all()

		# Convert the results to a list of dicts with values and comps
		query = [x._asdict() for x in q]
		results = {'lower': []}
		for i, row in enumerate(query):

			# On first iteration, add k,v to results dict
			if i == 0:
				results['id'] = row['id']
				results['value'] = row['value']
				results['tax_amount'] = row['tax_amount']

			# If the market value is lower, add to the low list
			if row['value'] >= row['match_value']:
				results['lower'].append({
					'match_id': row['match_id'],
					'match_value': row['match_value'],
					'match_tax_amount': row['match_tax_amount']
				})

		# Get values for z-score if there's more than 1 property to check
		if len(results['lower']) > 1:
			values = [x['match_tax_amount'] for x in results['lower']]
			low_mean = sum(values) / len(results['lower'])
			low_std = np.array(values).std()
			
			# Check the z-score of each result
			outliers = []
			for i,x in enumerate(results['lower']):
				z_score = (x['match_tax_amount'] - low_mean) / low_std
				
				# Z-score threshold for outliers
				threshold = 3
				if np.abs(z_score) > threshold:
					outliers.append(i)

			# Pop the outliers from the list
			for o in outliers:
				results['lower'].pop(o)

		# Create comparables from lowest six if available
		results['comparable'] = []
		if results['lower']:
			comps = sorted(results['lower'], key=lambda k: k['match_value'])
			results['comparable'] = comps[:6]

		# Add summary statistics for comparables
		results['count_comparable'] = len(results['comparable'])
		comp_sum = sum([x['match_tax_amount'] for x in results['comparable']])

		# If the values are available, get averages
		if results['count_comparable']:
			results['avg_comparable'] = int(comp_sum / results['count_comparable'])
		else:
			results['avg_comparable'] = 0

		# Return the results
		return results