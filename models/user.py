# -*- coding: utf-8 -*-
'''
USER MODEL
'''
from flask_security import UserMixin, RoleMixin
from shared import db

# Define the relationship between roles and users
roles_users = db.Table('roles_users',
	db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
	db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)

# Roles should include users and admins
class Roles(db.Model, RoleMixin):
	__tablename__ = "roles"

	# Primary key
	id = db.Column(db.Integer(), primary_key=True)

	# Columns
	name = db.Column(db.String(80), unique=True)
	description = db.Column(db.String(255))

	# Representation
	def __repr__(self):
		return '<id %r>' % self.id

# Use email as username
class Users(db.Model, UserMixin):
	__tablename__ = 'users'

	# Primary key
	id = db.Column(db.Integer, primary_key=True)
	
	# Columns
	email = db.Column(db.String(255), unique=True)
	password = db.Column(db.String(255))
	active = db.Column(db.Boolean())
	confirmed_at = db.Column(db.DateTime())
	roles = db.relationship('Roles', secondary=roles_users, 
		backref=db.backref('users', lazy='dynamic'))

	# Representation
	def __repr__(self):
		return '<id %r>' % self.id

	# Check if a user email exists
	@classmethod
	def check_user(class_, email):
		Users = class_

		# Query for the email
		user = Users.query.filter_by(email=email).first()

		# Return true if exists
		if user:
			return user
		else:
			return False