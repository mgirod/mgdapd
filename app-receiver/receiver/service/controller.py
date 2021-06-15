from flask import Flask, request, jsonify
from .decrypter import Decrypter
from . import settings

app = Flask("receiver")
dec = Decrypter(settings.DECRYPTION_KEY)


@app.route("/", methods=["GET"])
def health_check():
    """
    Requests sent to / (root) are handled by this method.
    Considered as a health check endpoint for the application.
    :return: A tuple with json data and status_code
    """
    data = {"msg": "Server is up", "status_code": 200}
    return jsonify(data), 200


@app.route('/upload/<filename>', methods=['POST'])
def upload_file(filename):
    """
    Requests that are sent to /upload/<filename> are handled by this method.
    Content-type supported by this rest api method is multipart/form-data.
    Request should contain file data (essentially some data of an encrypted xml ).

    app-sender/sender/utils.upload_to_server(**args) method calls
    this method over rest api to upload the file.

    Hint: Locate test_upload_file pytest function in tests/test_controller.py module.
    Implement this upload_file method in a way that pytest for test_upload_file is passing.

    :param filename: Path parameter sent with the request, containing a filename
    :return: A tuple with json data and status_code
    """
    save_location = "{0}/{1}.xml".format(settings.OUTPUT_DIR, filename)
    # YOUR CODE
    # SHOULD
    # GO
    # HERE
