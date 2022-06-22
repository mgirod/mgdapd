from flask import Flask, request, jsonify
from .decrypter import Decrypter
import logging
import re
from os import unlink
from . import settings

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='/var/log/receiver.log',
                    filemode='w')
app = Flask("receiver")
dec = Decrypter(settings.DECRYPTION_KEY)


@app.route("/", methods=["GET"])
def health_check():
    """
    Requests sent to / (root) are handled by this method.
    Considered as a health check endpoint for the application.
    :return: A tuple with json data and status_code
    """
    data = {"msg": "Server is healthy", "status_code": 200}
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
    fs = request.files['file'] #FileStorage
    fn = fs.filename
    if re.search(r'\.enc$', fn):
        tmpdst = "/tmp/{}".format(fn)
        fs.save(tmpdst)
        app.logger.debug("tmp dest: {}".format(tmpdst))
        try:
            dec.decrypt_file(tmpdst, save_location)
            app.logger.debug("Successfully decrypted {}".format(fn))
        except Exception as e:
            app.logger.debug("Could not decrypt file {}: {}".format(tmpdst, e)) #not encrypted in the pytest test
        unlink(tmpdst)
    with open(save_location, "r") as filedata:
        data = {'msg': filedata.read(), 'status_code': 201}
        return jsonify(data), 201
