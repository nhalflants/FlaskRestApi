from os import curdir, name
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
import sqlite3
from models.item import ItemModel
from flask import jsonify

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=True, help='This field is mandatory')
    parser.add_argument('store_id', type=int, required=True, help='This field is mandatory')
    
    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)

        if item:
            return item.json()
        return {'message': 'Not found'}, 404

        # item = next(filter(lambda item: item['name'] == name, items), None)
        # return {'item': item}, 200 if item is not None else 404

    @jwt_required(fresh=True)
    def post(self, name):  
        # Check first for error to avoid loading data if request will fail      
        # if next(filter(lambda item: item['name'] == name, items), None):
        if ItemModel.find_by_name(name):    
            return {'message': f'An item with name {name} already exists'}, 400

        # request_data = request.get_json()
        request_data = Item.parser.parse_args()

        item = ItemModel(name, request_data['price'], request_data['store_id'])
        
        # items.append(item)
        try:
            item.save()
        except:
            return {'message': 'An error occured inserting the item'}, 500
        
        return item.json(), 201

    @jwt_required()
    def delete(self, name):
        # global items
        # items = list(filter(lambda x: x['name'] != name, items))
        
        # connection = sqlite3.connect('data.db')
        # cursor = connection.cursor()
        
        # query = "DELETE FROM items WHERE name=?"
        # cursor.execute(query, (name,))
        
        # connection.commit()
        # connection.close()
        claims = get_jwt()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required'}, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete()
            return {'message': f'item {name} deleted'}
        return {'message': f'item {name} not found'}, 404

    def put(self, name):
        data = Item.parser.parse_args()
        
        # item = next(filter(lambda x: x['name'] == name, items), None)
        item = ItemModel.find_by_name(name)
        # updated_item = ItemModel(name, data['price'])
        if item is None:
            # item = {'name': name, 'price': data['price']}
            # items.append(item)
            
            # try:
            #     updated_item.insert()
            # except:
            #     return {'message', 'An error occured inserting the item'}, 500

            item = ItemModel(name, data['price'], data['store_id'])
        else:
            # try:
            #     updated_item.update()
            # except:
            #     return {'message', 'An error occured updating the item'}, 500

            item.price = data['price']

        item.save()    
        return item.json()


class ItemList(Resource):
    @classmethod
    def get_items(cls):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM items"
        results = cursor.execute(query)
        items = []
        for row in results:
            items.append({'name': row[0], 'price': row[1]})
        
        connection.close()
        return items

    @jwt_required(optional=True)
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {
                'items': items
            }, 200
        return {
            'items': [item['name'] for item in items],
            'message': 'More data available if user is logged in'
        }, 200
        # return {'items': list(map(lambda x: x.json(), ItemModel.find_all()))}
        # return {'items': [item.json() for item in ItemModel.query.all()]}