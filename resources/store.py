from flask_restful import Resource
from models.store import StoreModel

class Store(Resource):

    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()
        return {'message': f'Store {name} not found'}, 404

    def post(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return {'message': f'Store {name} already exists'}, 400
        store = StoreModel(name)
        try:
            store.save()
        except:
            return {'message': 'An error occured while creating the store'}, 500
        
        return store.json(), 201


    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete()
            return {'message': 'Store deleted'}
        return {'message': f'Store {name} doesn\'t exist'}, 400 


class StoreList(Resource):
    def get(self):
        return {'stores': [store.json() for store in StoreModel.find_all()]}