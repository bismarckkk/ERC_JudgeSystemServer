from multiprocessing import Process
from threading import Thread
import flask
from flask import Flask, request, render_template, url_for, redirect, send_file
import ujson as json
from flask_classful import FlaskView, route
from gevent.pywsgi import WSGIServer
# from db import Database
import datetime


class EndpointAction(object):
    def __init__(self, action):
        self.action = action

    def __call__(self, *args):
        # Perform the action
        answer = self.action()
        # Create the answer (bundle it in a correctly formatted HTTP answer)
        self.response = flask.Response(answer, status=200, headers={})
        # Send it
        return self.response


class Web(Thread):
    def __init__(self, q):
        super().__init__(daemon=True)
        self.q = q
        self.app = Flask(__name__)
        self.cars = {}
        self.http_server = None
        self.add_endpoint('/', self.index)
        self.add_endpoint('/asset-manifest.json', self.ass)
        self.add_endpoint('/manifest.json', self.mani)
        self.add_endpoint('/data', self.data)
        self.add_endpoint('/team', self.getTeamInfo)
        self.add_endpoint('/start', self.start2)
        self.add_endpoint('/stop', self.stop2)

    def add_endpoint(self, endpoint=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint, EndpointAction(handler))

    def response(self, e):
        self.q[0].put(e)

    def index(self):
        return render_template('index.html')

    def ass(self):
        with open('static/asset-manifest.json', 'r') as file:
            js = file.read()
        return js

    def mani(self):
        with open('static/manifest.json', 'r') as file:
            js = file.read()
        return js

    def data(self):
        if not self.q[1].empty():
            self.cars = self.q[1].get()
        re = []
        id2name = {1: '直线赛题', 2: '循白赛题', 3: '曲线赛题'}
        for k, v in self.cars.items():
            te = {'key': k, 'name': k, 'children': []}
            for k1, v1 in v.items():
                te['children'].append({
                    'key': k1,
                    'name': k1,
                    **v1
                })
                te['children'][-1]['connect_time'] = int(te['children'][-1]['connect_time'].timestamp() * 1000)
                if isinstance(te['children'][-1]['start_time'], datetime.datetime):
                    te['children'][-1]['start_time'] = int(te['children'][-1]['start_time'].timestamp() * 1000)
                te['children'][-1]['name'] = id2name[int(te['children'][-1]['name'])]
            re.append(te)
        return json.dumps(re)

    def getTeamInfo(self):
        tid = request.args.get('id')
        # r = db.fetchone("SELECT `name` FROM `jingsai_team` WHERE `id` = '%s'", [tid])
        r = [None]
        if r:
            return r[0]
        else:
            return ''

    def start2(self):
        team = request.args.get('team')
        car = request.args.get('car')
        if not team or not car:
            return 'fail'
        self.response({
            'ip': '127.0.0.1',
            'team': team,
            'car': int(car) + 1,
            'time': datetime.datetime.now(),
            'event': 'start',
            'message': None
        })
        return 'ok'

    def stop2(self):
        team = request.args.get('team')
        car = request.args.get('car')
        if not team or not car:
            return 'fail'
        self.response({
            'ip': '127.0.0.1',
            'team': team,
            'car': int(car) + 1,
            'time': datetime.datetime.now(),
            'event': 'stop',
            'message': None
        })
        return 'ok'

    def run(self):
        self.http_server = WSGIServer(('127.0.0.1', 5000), self.app)
        print("http模块上线")
        self.http_server.serve_forever()
