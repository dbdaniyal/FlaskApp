from flask.views import MethodView
from flask_smorest import abort, Blueprint
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, create_refresh_token, get_jwt_identity

from blocklist import BLOCKLIST
from db import db
from models import UserModel
from schemas import UserSchema

blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
	@blp.arguments(UserSchema)
	def post(self, user_data):
		print("1")
		if UserModel.query.filter(UserModel.username == user_data["username"]).first():
			abort(400, message="User already exists")
		print("2")
		user = UserModel(
			username=user_data["username"],
			password=pbkdf2_sha256.hash(user_data["password"])
		)
		print("3")
		db.session.add(user)
		db.session.commit()
		print("4")

		return {"message": "User created successfully"}, 201


@blp.route("/login")
class UserLogin(MethodView):
	@blp.arguments(UserSchema)
	def post(self, user_data):
		user = UserModel.query.filter(UserModel.username == user_data["username"]).first()
		if user and pbkdf2_sha256.verify(user_data["password"], user.password):
			access_token = create_access_token(identity=user.id, fresh=True)
			refresh_token = create_refresh_token(user.id)
			return {"access_token": access_token, "refresh_token": refresh_token}, 200
		else:
			abort(401, message="Invalid username or password")


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        # Make it clear that when to add the refresh token to the blocklist will depend on the app design
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": new_token}, 200

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


@blp.route("/user/<int:user_id>")
class User(MethodView):
	@blp.response(200, UserSchema)
	def get(self, user_id):
		user = UserModel.query.get_or_404(user_id)
		return user

	def delete(self, user_id):
		user = UserModel.query.get_or_404(user_id)
		db.session.delete(user)
		db.session.commit()
		return {"message": "User deleted"}, 200