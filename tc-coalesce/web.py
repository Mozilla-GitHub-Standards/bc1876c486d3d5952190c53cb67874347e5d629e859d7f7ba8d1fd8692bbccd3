import traceback
import sys
import os
import flask
from flask import Flask, jsonify, Response
import json
import redis
from urlparse import urlparse

app = flask.Flask(__name__)

pf = "coalesce.v1."

try:
    redis_url = urlparse(os.environ['REDIS_URL'])
except KeyError:
    traceback.print_exc()
    sys.exit(1)

rds = redis.Redis(host=redis_url.hostname,
                  port=redis_url.port,
                  password=redis_url.password,
                  decode_responses=True)

@app.route('/')
def root():
    """
    GET: Return an index of available api
    """
    # TODO: return an index on available api
    return jsonify({'versions': ['v1']})

@app.route('/v1/list')
def coalasce_lists():
    """
    GET: returns a list of all coalesced objects load into the listener
    """
    list_keys_set = rds.smembers(pf + "list_keys")
    if len(list_keys_set) == 0:
        return jsonify(**{ pf + 'list_keys' : []})
    list_keys = [x for x in list_keys_set]
    return jsonify(**{ pf + 'list_keys' : list_keys})

@app.route('/v1/stats')
def stats():
    """
    GET: returns stats
    """
    pf_key = pf + 'stats'
    stats = rds.hgetall(pf_key)
    return flask.jsonify(**stats)

@app.route('/v1/list/<key>')
def list(key):
    """
    GET: returns list
    """
    pf_key = pf + 'lists.' + key
    coalesced_list = rds.lrange(pf_key, start=0, end=-1)
    return jsonify(**{ key : coalesced_list})

# DEBUG: remove before release
@app.route('/v1/pending_status')
def pending_status():
    """
    GET: return list of pending tasks
    """
    pending_tasks_set = rds.smembers( pf + "pending_tasks")
    pending_tasks_list = [x for x in pending_tasks_set]
    return jsonify(**{ 'pending_tasks' : pending_tasks_list})



if __name__ == '__main__':
    # TODO: remove debug arg
    app.run(host='0.0.0.0', debug=False)
