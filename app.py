from datetime import datetime, timedelta, timezone
import enum
import uuid
from flask import Flask
from flask.views import MethodView
from flask_smorest import Api, Blueprint
from marshmallow import Schema, fields


server = Flask(__name__)

class APIConfig:
    API_TITLE = "Cat Feeder API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

server.config.from_object(APIConfig)

api = Api(server)

meals = Blueprint("meals", "meals", url_prefix="/meals", description="Operations on meals")

meals_list = [
    {
        "id": "1BA0A0CA-AC6E-4636-A382-0A182130AD98",
        "created_at": datetime.now(timezone.utc),
        "amount": 5 # grams
    },
    {
        "id": "E330171F-5A06-4C7C-8B5E-2CEF7EA2208B",
        "created_at": datetime.now(timezone.utc) - timedelta(hours=5),
        "amount": 10 # grams
    }
]

class CreateMeal(Schema):
    amount = fields.Integer()

class Meal(CreateMeal):
    id = fields.UUID()
    created_at = fields.DateTime()

class ListMeals(Schema):
    meals = fields.List(fields.Nested(Meal))

class SortByEnum(enum.Enum):
    amount = "amount"
    created_at = "created_at"

class SortDirectionEnum(enum.Enum):
    asc = "asc"
    desc = "desc"

class ListMealsParameters(Schema):
    order_by = fields.Enum(SortByEnum, load_default=SortByEnum.created_at)
    order = fields.Enum(SortDirectionEnum, load_default=SortDirectionEnum.desc)


@meals.route("")
class MealsCollection(MethodView):

    @meals.arguments(ListMealsParameters, location="query")
    @meals.response(status_code=200, schema=ListMeals)
    def get(self, parameters):
        return {
            "meals": sorted(
                meals_list,
                key=lambda meal: meal[parameters["order_by"].value],
                reverse=parameters["order"] == SortDirectionEnum.asc
            )
        }

    @meals.arguments(CreateMeal)
    @meals.response(status_code=201, schema=Meal) 
    def post(self, meal):
        meal["id"] = uuid.uuid4()
        meal["created_at"] = datetime.now(timezone.utc)
        meal["amount"] = 10
        meals_list.append(meal)
        return meal

api.register_blueprint(meals)
