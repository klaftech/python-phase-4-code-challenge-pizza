#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    def get(self):
        restaurants = [restaurant.to_dict(only=('address','id','name')) for restaurant in Restaurant.query.all()]
        return make_response(restaurants, 200)
    

class RestaurantsByID(Resource):
    @classmethod
    def get_model_by_id(cls,id):
        model = Restaurant.query.filter_by(id=id).first()
        return model

    def get(self, id):
        model = self.__class__.get_model_by_id(id)
        if model is None:
            return make_response(
                {"error": "Restaurant not found"},
                404
            )
        return make_response(model.to_dict(), 200)
    
    def delete(self, id):
        model = self.__class__.get_model_by_id(id)
        if model is None:
            return make_response(
                {"error": "Restaurant not found"},
                404
            )
        db.session.delete(model)
        db.session.commit()
        return make_response("", 204)


class Pizzas(Resource):
    def get(self):
        pizzas = [pizza.to_dict(only=('id','ingredients','name')) for pizza in Pizza.query.all()]
        return make_response(pizzas, 200)


class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            rp = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(rp)
            db.session.commit()
            return make_response(rp.to_dict(), 201) 
        except Exception as e:
            return make_response(
                {"errors": ['validation errors']},
                400
            )

api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantsByID, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')



if __name__ == "__main__":
    app.run(port=5555, debug=True)
