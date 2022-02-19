import sqlite3
from flask_restful import Resource, reqparse
from models.user import UserModel


class RegisterUser(Resource):
    data_parser = reqparse.RequestParser()
    data_parser.add_argument('username', type=str, required=True, help='Username is mandatory')
    data_parser.add_argument('password', type=str, required=True, help='Password is mandatory')

    def post(self):
        data = RegisterUser.data_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': 'A user with that username already exists'}, 400
        
        # connection = sqlite3.connect('data.db')
        # cursor = connection.cursor()

        # query = "INSERT INTO users VALUES (NULL, ?, ?)"
        # cursor.execute(query, (data['username'], data['password']))

        # connection.commit()
        # connection.close()

        user = UserModel(**data)
        user.save()

        return {'message': 'User created'}, 200