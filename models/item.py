from db import db

class ItemModel(db.Model):
	__tablename__ = 'items'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), unique=False, nullable=False)
	description = db.Column(db.String(80))
	price = db.Column(db.Float(precision=2), unique=False, nullable=False)

	# ===================================================================
	store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), unique=False, nullable=False)
	store = db.relationship('StoreModel', back_populates='items')
	# above back_populates is a relationship from StoreModel to ItemModel
	# it means that StoreModel has a list of items
	# we can access that list of items by doing store.items
	# we can also access the store that an item belongs to by doing item.store
	# this is a one to many relationship
	# ===================================================================
	tags = db.relationship('TagModel', secondary='items_tags', back_populates='items')
