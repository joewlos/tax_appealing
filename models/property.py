# -*- coding: utf-8 -*-
'''
PROPERTY MODEL
'''
from shared import db
from sqlalchemy import and_, between, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import aliased

# Property model from scraped data
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
	# Add a property for full address
	@hybrid_property
	def full_location(self):
		return '{0}, {1}'.format(self.property_location.strip(), self.city.strip())

	# The full address also needs an expression for queries
	@full_location.expression
	def full_location(cls):
		loc = func.rtrim(func.ltrim(cls.property_location))
		city = func.rtrim(func.ltrim(cls.city))
		return func.concat(loc, ', ', city)

	# Filter addresses for homepage autocomplete
	@classmethod
	def get_similar_addresses(class_, search):
		Properties = class_

		# Break the term by space for easier search
		all_terms = search.split(' ')

		# Construct the query
		q = Properties.query
		for term in all_terms:
			term = '%{}%'.format(term.upper().replace(',', ''))
			q = q.filter(Properties.full_location.like(term))

		# Add columns to the query and execute for only 10
		q = q.order_by(
			Properties.full_location
		).add_columns(
			Properties.id.label('id'),
			Properties.full_location.label('address')
		).limit(10).all()

		# Get the data back as a list of dicts
		results = [x._asdict() for x in q]
		return results


	'''
	PROPERTY DETAILS
	'''
	# Get the details of a single property as a dict
	@classmethod
	def get_property(class_, prop_id):
		Properties = class_

		# Query the id and return as dict
		q = Properties.query.filter_by(id=prop_id).first()
		return q.__dict__

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
				Properties.id != s.id,
				Properties.neighborhood == s.neighborhood,
				Properties.air == s.air,
				Properties.attic == s.attic,
				Properties.basement == s.basement,
				Properties.garage == s.garage,
				Properties.exterior == s.exterior,
				Properties.classification == s.classification,
				Properties.fireplaces <= s.fireplaces,
				Properties.full_baths <= s.full_baths,
				Properties.half_baths <= s.half_baths,
				Properties.apartments <= s.apartments,
				between(Properties.building_sqft, s.building_sqft - 100, s.building_sqft + 100),
				between(Properties.building_sqft, s.land_sqft - 100, s.land_sqft + 100)
			)
		).add_columns(
			Properties.id,
			Properties.est_market_value_2016.label('value'),
			s.id.label('match_id'),
			s.est_market_value_2016.label('match_value')
		).all()

		# Convert the results to a list of dicts with over- and under-valued
		query = [x._asdict() for x in q]
		results = {
			'lower': [],
			'higher': []
		}
		for i, row in enumerate(query):

			# On first iteration, add k,v to results dict
			if i == 0:
				results['id'] = row['id']
				results['value'] = row['value']

			# If the market value is lower, add to the low list
			if row['value'] >= row['match_value']:
				results['lower'].append({
					'match_id': row['match_id'],
					'match_value': row['match_value']
				})

			# Otherwise, add to the high list
			else:
				results['higher'].append({
					'match_id': row['match_id'],
					'match_value': row['match_value']
				})

		# Add summary statistics to results
		results['count_lower'] = len(results['lower'])
		results['count_higher'] = len(results['higher'])
		sum_lower = sum([x['match_value'] for x in results['lower']]) 
		sum_higher = sum([x['match_value'] for x in results['higher']])
		results['avg_lower'] = sum_lower / results['count_lower']
		results['avg_higher'] = sum_higher / results['count_higher']

		# Return the results
		return results