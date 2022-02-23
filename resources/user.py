from werkzeug.security import safe_str_cmp
from flask_restful import Resource, reqparse
from models.user import UserModel
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity,
    get_jti,
    get_jwt
)

data_parser = reqparse.RequestParser()
data_parser.add_argument('username', type=str, required=True, help='Username is mandatory')
data_parser.add_argument('password', type=str, required=True, help='Password is mandatory')

class RegisterUser(Resource):
    def post(self):
        data = data_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': 'A user with that username already exists'}, 400

        user = UserModel(**data)
        user.save()

        return {'message': f'User {user.id} created'}, 200


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return user.json()

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        user.delete()
        return {'message': 'User deleted'}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = data_parser.parse_args()
        user = UserModel.find_by_username(data['username'])
        if user and safe_str_cmp(user.password, data['password']):
            if user.id == 1:
                admin_claim = {"is_admin": True}
            else:
                admin_claim = {"is_admin": False}

            access_token = create_access_token(user.id, fresh=True, additional_claims=admin_claim)
            refreh_token = create_refresh_token(user.id, additional_claims=admin_claim)
            return {
                'access_token': access_token,
                'refresh_token': refreh_token
            }, 200

        return {'message': 'Invalid credentials'}, 401


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_jti(get_jwt()) 
        # BLACKLIST.add(jti)
        return {
            'message': 'Successfully logout user'
        }