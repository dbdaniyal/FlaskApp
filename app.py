import os
import secrets

from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from db import db
import models

from blocklist import BLOCKLIST
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint

def create_app(db_url=None):
	app = Flask(__name__)



	app.config["PROPAGATE_EXCEPTIONS"] = True  # that if an exception occurs to an extension of flask than propogate it to the main app so that we can see it
	app.config["API_TITLE"] = "Stores REST API"  # documenation title
	app.config["API_VERSION"] = "v1"
	app.config["OPENAPI_VERSION"] = "3.0.3"  # is a standard for api documentation
	app.config["OPENAPI_URL_PREFIX"] = "/"  # root of our api is at this location

	# below enable swagger docs at: http://127.0.0.1:5000/swagger-ui
	app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
	app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

	app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
	app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

	db.init_app(app)  # what this does, is it initializes the Flask SQLAlchemy extension, giving it our Flask app so that it can connect the Flask app to SQLAlchemy.
	migrate = Migrate(app, db)
	api = Api(app)


	app.config["JWT_SECRET_KEY"] = "268309662981534165755027239585676006684"
	jwt = JWTManager(app)

	@jwt.additional_claims_loader
	def add_claims_to_jwt(identity):
		if identity == 1:
			return {"is_admin": True}
		return {"is_admin": False}

	# below 3 methods are called by flask_jwt_extended when an error occurs.. so here we have shown a custom message
	@jwt.expired_token_loader
	def expired_token_callback(jwt_header, jwt_payload):
		return (
			jsonify({"message": "The token has expired.", "error": "token_expired"}),
			401,
		)

	@jwt.invalid_token_loader
	def invalid_token_callback(error):
		return (
			jsonify(
				{"message": "Signature verification failed.", "error": "invalid_token"}
			),
			401,
		)

	@jwt.unauthorized_loader
	def missing_token_callback(error):
		return (
			jsonify(
				{
					"description": "Request does not contain an access token.",
					"error": "authorization_required",
				}
			),
			401,
		)

	@jwt.token_in_blocklist_loader
	def check_if_token_in_blocklist(jwt_header, jwt_payload):
		return jwt_payload["jti"] in BLOCKLIST

	@jwt.revoked_token_loader
	def revoked_token_callback(jwt_header, jwt_payload):
		return (
			jsonify(
				{"description": "The token has been revoked.", "error": "token_revoked"}
			),
			401,
		)

	api.register_blueprint(ItemBlueprint)
	api.register_blueprint(StoreBlueprint)
	api.register_blueprint(TagBlueprint)
	api.register_blueprint(UserBlueprint)

	return app
