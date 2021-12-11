from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import requests
import subprocess
import json
from utility import verifyCredentials, generateReturnDictionary, userExist

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")

db = client.ImageRecognition
user = db["Users"]

class Register(Resource):
    """ API endpoint for registering users, accepts only post requests"""


    def post(self):
        """ post request to register with username and password"""

        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]


        if userExist(user,username):
            return_json = {
                "status":301,
                "msg":"Invalid Username"
            }

            return jsonify(return_json)


        hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

        user.insert(
            {
                "Username":username,
                "Password":hashed_pw,
                "Tokens":5
           }
        )

        return_json = {
            "status":200,
            "msg":"You successfully signed up for this API"
        }

        return jsonify(return_json)

class Classify(Resource):
    """API endpoint where the classification of image take place"""
    
    def post(self):
        """Post request to provide username, password and image"""

        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]
        url = posted_data["url"]

        return_json, error = verifyCredentials(user,username,password)

        if error:
            return jsonify(return_json)
        
        tokens = user.find({
            "Username":username
        })[0]["Tokens"]

        if tokens <=0:
            return jsonify(generateReturnDictionary(303, "Not Enough Tokens!"))
        
        r = requests.get(url)

        return_json = {}

        # writes the content of the image in a temp file 
        # starts a subprocess to classify the image and stores the result
        with open("temp.jpg","wb") as f:
            f.write(r.content)
            proc = subprocess.Popen("python classify_image.py --model_dir= .--image_file=./temp.jpg")
            proc.communicate()[0]
            proc.wait()
            with open("text.txt","r") as g:
                return_json = json.load(g)
        

        # update the token
        user.update({
            "Username":username
        },{
            "$set":{
                "Tokens":tokens-1
            }
        })

        return return_json

class Refill(Resource):
    """ API endpoint to refill the tokens should be done by the admin"""

    def post(self):

        posted_data = request.get_json()
        username = posted_data["Username"]
        password = posted_data["admin_pw"]
        amount = posted_data["amount"]

        if not userExist(user,username):
            return jsonify(generateReturnDictionary(301,"Invalid Username"))
        
        # should be kept inside a environment variable
        correct_admin_pw = "Your Admin Password"

        if not password == correct_admin_pw:
            return jsonify(generateReturnDictionary(304, "Administrative password is Wrong"))

        user.update({
            "Username":username
        },{
            "$set": {
            "Tokens":amount
            }
        })

        return jsonify(generateReturnDictionary(200,"Refill Successful"))

api.add_resource(Register,"/register")
api.add_resource(Classify, "/classify")
api.add_resource(Refill, "/refill")


if __name__ == "__main__":
    app.run(host="0.0.0.0")