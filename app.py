import sys
import io
from PIL import Image
import cv2
import torch
from flask import Flask, render_template, request, make_response
from werkzeug.exceptions import BadRequest
import os
from flask import send_file
import json


# creating flask app
app = Flask(__name__)


# # create a python dictionary for your models d = {<key>: <value>, <key>: <value>, ..., <key>: <value>}
# dictOfModels = {}
# # create a list of keys to use them in the select part of the html code
listOfKeys = []
#
# # create a python dictionary for your models d = {<key>: <value>, <key>: <value>, ..., <key>: <value>}
# dictOfModels = {}
# # create a list of keys to use them in the select part of the html code
# listOfKeys = []
# for r, d, f in os.walk("models_train"):
#     for file in f:
#         if ".pt" in file:
#             # example: file = "model1.pt"
#             # the path of each model: os.path.join(r, file)
#             dictOfModels[os.path.splitext(file)[0]] = torch.hub.load('ultralytics/yolov5', 'custom', path=os.path.join(r, file), force_reload=True)
#             # you would obtain: dictOfModels = {"model1" : model1 , etc}
#     for key in dictOfModels :
#         listOfKeys.append(key)     # put all the keys in the listOfKeys
#     print(listOfKeys)

# inference fonction


def get_prediction(img_bytes):
    img = Image.open(io.BytesIO(img_bytes))
    # inference
    model = torch.hub.load('ultralytics/yolov5', 'custom',
                           path='models_train/best.pt', force_reload=True)
    results = model(img, size=640)
    return results


# get method
@app.route('/', methods=['GET'])
def get():
    # in the select we will have each key of the list in option
    # return render_template("index.html", len = len(listOfKeys), listOfKeys = listOfKeys)
    return render_template("index.html")


# post method
@app.route('/', methods=['POST'])
def predict():
    file = extract_img(request)
    img_bytes = file.read()

    # choice of the model
    # results = get_prediction(img_bytes,dictOfModels[request.form.get("model_choice")])
    results = get_prediction(img_bytes)
    # print(f'User selected model : {request.form.get("model_choice")}')

    # updates results.imgs with boxes and labels
    results.render()

    # encoding the resulting image and return it
    for img in results.ims:
        RGB_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        im_arr = cv2.imencode('.jpg', RGB_img)[1]
        response = make_response(im_arr.tobytes())
        response.headers['Content-Type'] = 'image/jpeg'
        response.info = results
        cv2.imwrite('static/results/result.jpg', img)
    # RGB_img = cv2.cvtColor(results, cv2.COLOR_BGR2RGB)
    # im_arr = cv2.imencode('.jpg', RGB_img)[1]
    # response = make_response(im_arr.tobytes())
    # response.headers['Content-Type'] = 'image/jpeg'
    # results.save()
    # print("****", results)
    result_json = results.pandas().xyxy[0].to_json(orient="records")
    result_list = json.loads(result_json)
    context = {}
    counter = 0
    for result in result_list:
        for key, value in result.items():
            if key == 'name':
                context['Name_' + str(counter)] = result[key] + " " +\
                    str(float("{:.2f}".format(result['confidence'])))
        counter = counter + 1
    print(context)

    # return response
    return render_template("results.html", context=context)

    # return sender_template(response, mimetype='image/gif')


def extract_img(request):
    # checking if image uploaded is valid
    if 'file' not in request.files:
        raise BadRequest("Missing file parameter!")

    file = request.files['file']

    if file.filename == '':
        raise BadRequest("Given file is invalid")

    return file


if __name__ == '__main__':
    print('Starting yolov5 webservice...')
    # Getting directory containing models from command args (or default 'models_train')
    # models_directory = 'models_train'
    # if len(sys.argv) > 1:
    #     models_directory = sys.argv[1]
    # print(f'Watching for yolov5 models under {models_directory}...')
    # for r, d, f in os.walk(models_directory):
    #     for file in f:
    #         if ".pt" in file:
    #             # example: file = "model1.pt"
    #             # the path of each model: os.path.join(r, file)
    #             model_name = os.path.splitext(file)[0]
    #             model_path = os.path.join(r, file)
    #             print(f'Loading model {model_path} with path {model_path}...')
    #             dictOfModels[model_name] = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
    #             # you would obtain: dictOfModels = {"model1" : model1 , etc}
    #     for key in dictOfModels :
    #         listOfKeys.append(key) # put all the keys in the listOfKeys

    # print(f'Server now running on {os.environ["JOB_URL_SCHEME"]}{os.environ["JOB_ID"]}.{os.environ["JOB_HOST"]}')

    # starting app
    app.run(debug=True, host='0.0.0.0')
