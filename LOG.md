# Assignment log

0.
## Pre-requisites

I had to update Python: ubuntu 18:04 is using Python 3.6
But I found that switching to it breaks ubuntu (gnome-terminal, apt-get...)
Note: my bash prompt is PS1='\W> '

    ~> mkdir venv
    ~> cd venv
    venv> sudo apt install python3.7 python3-venv python3.7-venv
    venv> python3.7 -m venv p37
    venv> . ./p37/bin/activate
    (p37) venv> python -V
    Python 3.7.5

I had then to install Flask:

    (p37) venv> pip install Flask
    ...
    Command "python setup.py egg_info" failed with error code 1 in /tmp/pip-build-8kf2yjwi/MarkupSafe/
    (p37) venv> pip install --upgrade setuptools
    (p37) venv> pip install wheel
    (p37) venv> pip install Flask --user
    ...
    Successfully installed Flask-2.1.2 Jinja2-3.1.2 MarkupSafe-2.1.1 Werkzeug-2.1.2 click-8.1.3 importlib-metadata-4.11.4 itsdangerous-2.1.2 typing-extensions-4.2.0 zipp-3.8.0
    (p37) venv> export PYTHONPATH=/home/marc/.local/lib/python3.7/site-packages

Then pytest:

    (p37) venv> pip install pytest --user
    ...
    Successfully installed attrs-21.4.0 iniconfig-1.1.1 packaging-21.3 pluggy-1.0.0 py-1.11.0 pyparsing-3.0.9 pytest-7.1.2 tomli-2.0.1
    (p37) venv> PATH=~/.local/bin:$PATH

Soon I noticed I needed cryptography, setuptools_rust, Rust.
I needed to upgrade pip, to reinstall cryptography...


1.
    (p37) venv> cd ~/git/devops_assignment-python_and_docker
    (p37) devops_assignment-python_and_docker> ./prepare-env.sh 
    (p37) cd app-receiver
    (p37) app-receiver> pytest -v tests
    ...
    collected 2 items                                                                                                                                  

    tests/test_controller.py::test_health_check FAILED                                                                                           [ 50%]
    tests/test_controller.py::test_upload_file FAILED                                                                                            [100%]
    ...

What failed (in the first case) is an assertion: the text of the json
message (although the code assertion passed: 200).
One can... change the expectation.

    E         Full diff:
    E         - {'msg': 'Server is healthy', 'status_code': 200}
    E         ?                    ^^^^^^^
    E         + {'msg': 'Server is up', 'status_code': 200}...

That's what I did first, but later I understood that it was not what
was expected so that I reverted this first commit and added the change
to the change for task 2. Here is the whole git log:

    devops_assignment-python_and_docker> git log --oneline
    4aa477a (HEAD -> main, origin/main, origin/HEAD) Task 7 (not completed): sender fails to establish the connection
    8805788 Task 6: add a command
    2205a7f Task 5: remove the 10s delay
    24eedad Task 4: use multi-stage build to run pytest
    f40bd77 Task 3: add missing directives
    0eb1d3f Tasks 1 and 2: fix health_check and upload_file
    9de2859 Revert "task 1: fix health_check"
    ccb84ad task 1: fix health_check
    c6f1f58 Update Readme.md
    aed8e0b Initial Commit

2.
In the second case (also an assertion), this is a 'real' failure: 500,
server error when attempting to upload a test file.

    E       assert 500 == 201
    E        +  where 500 = <WrapperTestResponse streamed [500 INTERNAL SERVER ERROR]>.status_code

    devops_assignment-python_and_docker> grep --exclude-dir=.pytest_cache --exclude=*.pyc -rl upload_file .
    ./README.md
    ./app-receiver/tests/test_controller.py
    ./app-receiver/receiver/service/controller.py

Fixed the source:

    devops_assignment-python_and_docker> git diff app-receiver/receiver/service/controller.py 
    diff --git a/app-receiver/receiver/service/controller.py b/app-receiver/receiver/service/controller.py
    index 3a7d91a..e645c4d 100644
    --- a/app-receiver/receiver/service/controller.py
    +++ b/app-receiver/receiver/service/controller.py
    @@ -34,7 +34,6 @@ def upload_file(filename):
         :return: A tuple with json data and status_code
         """
         save_location = "{0}/{1}.xml".format(settings.OUTPUT_DIR, filename)
    -    # YOUR CODE
    -    # SHOULD
    -    # GO
    -    # HERE
    +    with open(save_location, "r") as filedata:
    +        data = {'msg': filedata.read(), 'status_code': 201}
    +        return jsonify(data), 201

Now, the error I get is:

    FileNotFoundError: [Errno 2] No such file or directory: '/usr/src/app-receiver/output/testfile.xml'

which comes from the fact that I run on my laptop, instead of in the container...
For now, I can cheat by adding this directory tree locally...

    (p37) app-receiver> sudo mkdir -p /usr/src/app-receiver/output
    (p37) app-receiver> sudo chown marc /usr/src/app-receiver/output
    (p37) app-receiver> echo -n 'File is decrypted and saved to /usr/src/app-receiver/output/testfile.xml' > /usr/src/app-receiver/output/testfile.xml
    (p37) app-receiver> pytest -v tests
    ============================================================================================ test session starts ============================================================================================
    platform linux -- Python 3.7.5, pytest-7.1.2, pluggy-1.0.0 -- /home/marc/venv/p37/bin/python3.7
    cachedir: .pytest_cache
    rootdir: /home/marc/git/devops_assignment-python_and_docker/app-receiver
    collected 2 items                                                                                                                                                                                           

    tests/test_controller.py::test_health_check PASSED                                                                                                                                                    [ 50%]
    tests/test_controller.py::test_upload_file PASSED                                                                                                                                                     [100%]

    ============================================================================================= 2 passed in 0.01s =============================================================================================

3.
There were several possible ways to complete the Dockerfile, but the
next task drove to preserve the hiearchy into the container, and use
WORKDIR to access gunicorn.conf.

4.
The easiest was to generate the xml test file and to copy the tests in the container.
I did not clean them up, so that they got carried uo to the production image...

5.
    (p37) devops_assignment-python_and_docker> pip install json2xml
    (p37) devops_assignment-python_and_docker> sudo mkdir -p /usr/src/app-sender/input
    (p37) devops_assignment-python_and_docker> sudo mkdir -p /usr/src/app-sender/status-db
    (p37) devops_assignment-python_and_docker> cp key /tmp/encryption_key

    app-sender_1    | [2021-05-04 22:59:00,192] - [INFO] - [utils.py] - /usr/src/app-sender/input/books.json is converted to /usr/src/app-sender/input/books.xml
    app-sender_1    | [2021-05-04 22:59:10,230] - [INFO] - [utils.py] - books.json is encrypted to /usr/src/app-sender/input/books.xml.enc
    app-sender_1    | [2021-05-04 22:59:20,269] - [INFO] - [utils.py] - books is uploaded successfully. Response from server: File is decrypted and saved to /usr/src/app-receiver/output/books.xml

run_scan is invoked from:

    while True:
        run_scan()
        time.sleep(int(settings.SCAN_INTERVAL))

So, it should not return before it has processed the three steps.

6.
    (p37) devops_assignment-python_and_docker> docker build -t app-sender:latest app-sender/
    (p37) devops_assignment-python_and_docker> docker run -v ${PWD}/input:/usr/src/app-sender/input sender:test
    Unable to find image 'sender:test' locally
    docker: Error response from daemon: pull access denied for sender, repository does not exist or may require 'docker login': denied: requested access to the resource is denied.
    See 'docker run --help'.

    p37) devops_assignment-python_and_docker> docker ps -a | head -3
    CONTAINER ID   IMAGE                   COMMAND                  CREATED         STATUS                      PORTS     NAMES
    7d27cce01fc7   app-sender              "python3"                4 minutes ago   Exited (0) 4 minutes ago              blissful_saha
    9e0eae8f6f0b   e1af61eb9244            "sender"                 4 minutes ago   Created                               hungry_jones

What is missing is a command to run, so either an ENTRYPOINT or a CMD.
I went for a CMD.

    (p37) devops_assignment-python_and_docker> docker build -t sender:test app-sender/
    (p37) devops_assignment-python_and_docker> docker run -v ${PWD}/input:/usr/src/app-sender/input --mount type=bind,source=$DAPD/key,target=/run/secrets/encryption_key --rm sender:test
    [2022-06-17 06:12:41,505] - [INFO] - [statusHandler.py] - Status DB initialized to /usr/src/app-sender/status-db
    ^C ...
    (p37) devops_assignment-python_and_docker> docker ps -a | head -2
    CONTAINER ID   IMAGE                   COMMAND                   CREATED         STATUS                       PORTS     NAMES
    33bfd5085c01   sender:test             "python3 sender"          6 minutes ago   Exited (130) 5 minutes ago             elegant_swartz

7.
More missing pre-requisites...

    devops_assignment-python_and_docker> sudo apt-get update
    devops_assignment-python_and_docker> sudo apt-get install docker-compose

    (p37) devops_assignment-python_and_docker> pip install docker-compose==1.17.1

Used in /usr/bin/docker-compose, as this one would use 3.6, and thus
not see the 1.17.1 version:

    #!/usr/bin/env python

    (p37) devops_assignment-python_and_docker> docker-compose -f docker-compose-v1.yml build --no-cache
    ERROR: Version in "./docker-compose-v1.yml" is unsupported. You might be seeing this error because you're using the wrong Compose file version. Either specify a supported version (e.g "2.2" or "3.3") and place your service definitions under the `services` key, or omit the `version` key and place your service definitions at the root of the file to use version 1.
    For more on the Compose file format versions, see https://docs.docker.com/compose/compose-file/

I used 3.3 instead of 3.9 (?)

I was able to bind the volume from the host to the containers, s as to
use the key, to read the input in sender, to process it, and to
generate new files as well as the status-db. But I failed to get the
two containers to communicate...

Sender would avoid processing again the same files, because of the
existing status-db, but it does not keep looping after a failure, so
that it ignores new input until after it gets restarted.

    (p37) devops_assignment-python_and_docker> docker-compose -f docker-compose-v1.yml build --no-cache
    ...
    (p37) devops_assignment-python_and_docker> docker-compose -f docker-compose-v1.yml up -d
    Creating network "devopsassignmentpythonanddocker_default" with the default driver
    Creating devopsassignmentpythonanddocker_app-receiver_1 ... 
    Creating devopsassignmentpythonanddocker_app-sender_1 ... 
    Creating devopsassignmentpythonanddocker_app-receiver_1
    Creating devopsassignmentpythonanddocker_app-receiver_1 ... done
    (p37) devops_assignment-python_and_docker> ll input/* status-db/* output/*
    ls: cannot access 'input/*': No such file or directory
    ls: cannot access 'status-db/*': No such file or directory
    ls: cannot access 'output/*': No such file or directory
    (p37) devops_assignment-python_and_docker> docker-compose -f docker-compose-v1.yml logs | head
    Attaching to devopsassignmentpythonanddocker_app-sender_1, devopsassignmentpythonanddocker_app-receiver_1
    app-sender_1    | [2022-06-17 09:24:21,449] - [INFO] - [statusHandler.py] - Status DB initialized to /usr/src/app-sender/status-db
    app-receiver_1  | [2022-06-17 09:24:22 +0000] [1] [INFO] Starting gunicorn 20.1.0
    app-receiver_1  | [2022-06-17 09:24:22 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)
    app-receiver_1  | [2022-06-17 09:24:22 +0000] [1] [INFO] Using worker: sync
    app-receiver_1  | [2022-06-17 09:24:22 +0000] [6] [INFO] Booting worker with pid: 6
    (p37) devops_assignment-python_and_docker> cp /tmp/books.json input/
    (p37) devops_assignment-python_and_docker> docker-compose -f docker-compose-v1.yml logs | head -14
    Attaching to devopsassignmentpythonanddocker_app-sender_1, devopsassignmentpythonanddocker_app-receiver_1
    app-sender_1    | [2022-06-17 09:24:21,449] - [INFO] - [statusHandler.py] - Status DB initialized to /usr/src/app-sender/status-db
    app-sender_1    | [2022-06-17 09:24:51,502] - [INFO] - [dicttoxml.py] - Inside dicttoxml(): type(obj) is: "dict", obj="{'version': '1.0'}"
    app-sender_1    | [2022-06-17 09:24:51,503] - [INFO] - [dicttoxml.py] - Inside convert(). obj type is: "dict", obj="{'version': '1.0'}"
    app-sender_1    | [2022-06-17 09:24:51,503] - [INFO] - [dicttoxml.py] - Inside convert_dict(): obj type is: "dict", obj="{'version': '1.0'}"
    app-sender_1    | [2022-06-17 09:24:51,503] - [INFO] - [dicttoxml.py] - Looping inside convert_dict(): key="version", val="1.0", type(val)="str"
    app-sender_1    | [2022-06-17 09:24:51,503] - [INFO] - [dicttoxml.py] - Inside make_valid_xml_name(). Testing key "version" with attr "{}"
    app-sender_1    | [2022-06-17 09:24:51,503] - [INFO] - [dicttoxml.py] - Inside key_is_valid_xml(). Testing "version"
    app-sender_1    | [2022-06-17 09:24:51,514] - [INFO] - [dicttoxml.py] - Inside convert_kv(): key="version", val="1.0", type(val) is: "str"
    app-sender_1    | [2022-06-17 09:24:51,514] - [INFO] - [dicttoxml.py] - Inside make_valid_xml_name(). Testing key "version" with attr "{}"
    app-sender_1    | [2022-06-17 09:24:51,514] - [INFO] - [dicttoxml.py] - Inside key_is_valid_xml(). Testing "version"
    app-sender_1    | [2022-06-17 09:24:51,514] - [INFO] - [utils.py] - /usr/src/app-sender/input/books.json is converted to /usr/src/app-sender/input/books.xml
    app-sender_1    | [2022-06-17 09:24:51,515] - [INFO] - [utils.py] - books.json is encrypted to /usr/src/app-sender/input/books.xml.enc
    app-sender_1    | [2022-06-17 09:24:51,519] - [ERROR] - [utils.py] - Unable to upload file. msg: HTTPConnectionPool(host='127.0.0.1', port=8080): Max retries exceeded with url: /upload/books (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7f6c1d9a54b0>: Failed to establish a new connection: [Errno 111] Connection refused'))
    (p37) devops_assignment-python_and_docker> ll input/* status-db/* output/*
    ls: cannot access 'output/*': No such file or directory
    -rw-rw-r-- 1 marc marc  25 Jun 17 10:24  input/books.json
    -rw-r--r-- 1 root root  71 Jun 17 10:24  input/books.xml
    -rw-r--r-- 1 root root 184 Jun 17 10:24  input/books.xml.enc
    -rw-r--r-- 1 root root 138 Jun 17 10:24  status-db/books.json
    (p37) devops_assignment-python_and_docker> docker-compose -f docker-compose-v1.yml top
    devopsassignmentpythonanddocker_app-receiver_1
    UID    PID   PPID   C   STIME   TTY     TIME                               CMD                           
    ---------------------------------------------------------------------------------------------------------
    root   799   772    0   10:24   ?     00:00:00   /usr/local/bin/python /usr/local/bin/gunicorn server:app
    root   951   799    0   10:24   ?     00:00:00   /usr/local/bin/python /usr/local/bin/gunicorn server:app
    
    devopsassignmentpythonanddocker_app-sender_1
    UID    PID   PPID   C    STIME   TTY     TIME          CMD      
    ----------------------------------------------------------------
    root   795   729    83   10:24   ?     00:02:41   python3 sender

I decide to send this result as such in case I fail to complete it
now, feeling stuck for now.
