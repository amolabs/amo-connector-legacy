from flask import Flask, jsonify
from flask_restful import reqparse, Resource, Api
from ecdsa.util import sha256


class MockAuth(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user')
        parser.add_argument('operation')

        args = parser.parse_args()

        if args['operation']['name'] != 'upload':
            return jsonify({}), 403


class MockStorage(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('owner', type=str, required=True)
        parser.add_argument('metadata', type=dict, required=True)
        parser.add_argument('data', type=str, required=True)

        args = parser.parse_args()

        digested = sha256(args['data']).hexdigest()

        return {
            'id': 'aabbccddeeff',
        }


app = Flask("MockStorage")
api = Api(app)
api.add_resource(MockStorage, '/api/v1/parcels')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
