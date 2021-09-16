from flask import Flask, jsonify, render_template, request, redirect, make_response
import boto3
import json

app = Flask(__name__)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Todo")


@app.route("/", methods=['GET', 'POST'])
def hello_from_root():
    if request.method == 'POST':
        item = {
            'id': request.form['id'],
            'Title': request.form['title'],
            'Description': request.form['description']
        }

        print("ITEM:", item)

        try:
            table.put_item(Item=item)
            return redirect('/test-flask')
        except Exception as e:
            print(e)
    else:
        todos = table.scan()['Items']
        body = {
            "statusCode": 200,
            "message": "Go Serverless v2.0! Your route executed successfully!",
            "body": todos
        }
        # return jsonify(message=body)
        return render_template('index.html', todos=todos)


@app.route("/update/<int:id>", methods=['GET', 'PUT'])
def update_todo(id):
    todo = table.get_item(Key={'id': str(id)})['Item']
    if request.method == 'PUT':
        result = table.update_item(Key={'id': str(id)},
                                   ExpressionAttributeNames={
            'title': 'Title',
            # Use the # character in an expression to dereference an attribute name because name is reserved keyword in dynamodb
            'description': 'Description'
        },
            ExpressionAttributeValues={
            ':Title': request.form['title'],
            ':Description': request.form['description']
        },
            UpdateExpression='SET title = :Title, description = :Description',

            # Returns all of the attributes of the item, as they appear after the UpdateItem operation.
            ReturnValues='UPDATED_NEW',
        )
        response = {
            "statusCode": 200,
            "body": json.dumps(result['Attributes'])
        }
        return redirect('/test-flask', response=response)
    else:
        return render_template('update.html', todo=todo)


@app.route("/details/<int:id>", methods=['GET'])
def todo_details(id):
    todo = table.get_item(Key={'id': str(id)})['Item']
    # response = {
    #     "isBase64Encoded": False,
    #     "statusCode": 200,
    #     "headers": {"Content-Type": "application/json"},
    #     "body": json.dumps(todo)
    # }
    return render_template('details.html', todo=todo)


@app.route("/hello")
def hello():
    return jsonify(message='Hello from path!')


@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)
