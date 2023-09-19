from prometheus_client import Gauge, generate_latest, Gauge
from kubernetes import client, config
import concurrent.futures
import http.client
import json
from flask import Flask, Response
import re
import os
import ast
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

env_platform = os.getenv("ENV_PLATFORM")

###################
# CONST VARIABLES #
###################
twemproxy_name_str = os.getenv("TWEMPROXY_NAME")
twemproxy_name = ast.literal_eval(twemproxy_name_str)
pattern_ip = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b' # example: 172.24.245.4
pattern_name_redis = "server\d+"
json_array = []
platform = "physical"
#######################
# END CONST VARIABLES #
#######################

####################
# KUBENETE CONFIFG #
####################
# Load Kubernetes configuration from default location
if env_platform == "k8s":
    config.load_kube_config(config_file="./cluster-ott-dev.yaml")

    # Create a Kubernetes API client
    api_instance = client.CoreV1Api()

    namespace = os.getenv("NAMESPACE")
    label_selector = os.getenv("LABEL")

    platform = "kubernete"
########################
# END KUBENETE CONFIFG #
########################

#####################
# METRICS VARIABLES #
#####################
# COMMON VARIABLES
pod_name = ""
uptime = ""
total_connection = ""
curr_connection = ""
pool_name = ""
client_connections = ""
client_eof = ""
client_err = ""
server_ejects = ""
forward_error = ""
fragments = ""
# REDIS SERVER VARIABLES
redis_ip = ""
server_eof = ""
server_err = ""
server_timedout = ""
server_connections = ""
server_ejected_at = ""
requests = ""
request_bytes = ""
responses = ""
response_bytes = ""
in_queue = ""
in_queue_bytes = ""
out_queue = ""
out_queue_bytes = ""
#########################
# END METRICS VARIABLES #
#########################

###########################################
# DEFINE METRICS VARIABLES FOR PROMETHEUS #
###########################################
# COMMON VARIABLES
uptime_metric = Gauge('twemproxy_uptime', 'Nutcracker Uptime', labelnames=['platform', 'pod_name', 'pool'])
total_connection_metric = Gauge('twemproxy_total_connections', 'Total Connections', labelnames=['platform', 'pod_name', 'pool'])
curr_connection_metric = Gauge('twemproxy_current_connections', 'Current Connections', labelnames=['platform', 'pod_name', 'pool'])
client_connections_metric = Gauge('twemproxy_client_connections', 'Client Connections', labelnames=['platform', 'pod_name', 'pool'])
client_eof_metric = Gauge('twemproxy_client_eof', f'{pool_name} Client EOF', labelnames=['platform', 'pod_name', 'pool'])
client_err_metric = Gauge('twemproxy_client_err', f'{pool_name} Client Errors', labelnames=['platform', 'pod_name', 'pool'])
server_ejects_metric = Gauge('twemproxy_server_ejects', f'{pool_name} Server Ejects', labelnames=['platform', 'pod_name', 'pool'])
forward_error_metric = Gauge('twemproxy_forward_error', f'{pool_name} Server Ejects', labelnames=['platform', 'pod_name', 'pool'])
fragments_metric = Gauge('twemproxy_fragments', f'{pool_name} Fragments metrics', labelnames=['platform', 'pod_name', 'pool'])

# REDIS SERVER VARIABLES
server_eof_metric = Gauge('twemproxy_server_eof', 'Redis Server EOF', labelnames=['platform', 'pod_name', 'pool', "redis"])
server_err_metric = Gauge('twemproxy_server_err', 'Redis Server ERR', labelnames=['platform', 'pod_name', 'pool', "redis"])
server_timedout_metric = Gauge('twemproxy_server_timedout', 'Timeout to Redis', labelnames=['platform', 'pod_name', 'pool', "redis"])
server_connections_metric = Gauge('twemproxy_server_connections', 'Connections to Redis', labelnames=['platform', 'pod_name', 'pool', "redis"])
server_ejected_at_metric = Gauge('twemproxy_server_ejected_at', 'Ejected', labelnames=['platform', 'pod_name', 'pool', "redis"])
requests_metric = Gauge('twemproxy_requests', 'Requests to Redis', labelnames=['platform', 'pod_name', 'pool', "redis"])
request_bytes_metric = Gauge('twemproxy_request_bytes', 'Request bytes to Redis', labelnames=['platform', 'pod_name', 'pool', "redis"])
responses_metric = Gauge('twemproxy_responses', 'Responses to Redis', labelnames=['platform', 'pod_name', 'pool', "redis"])
response_bytes_metric = Gauge('twemproxy_response_bytes', 'Responses bytes to Redis', labelnames=['platform', 'pod_name', 'pool', "redis"])
in_queue_metric = Gauge('twemproxy_in_queue', 'In queue Redis', labelnames=['platform', 'pod_name', 'pool', "redis"])
in_queue_bytes_metric = Gauge('twemproxy_in_queue_bytes', 'In queue bytes Redis', labelnames=['platform', 'pod_name', 'pool', "redis"])
out_queue_metric = Gauge('twemproxy_out_queue', 'Out qeue Redis', labelnames=['platform', 'pod_name', 'pool', "redis"])
out_queue_bytes_metric = Gauge('twemproxy_out_queue_bytes', 'Out qeue bytes Redis', labelnames=['platform', 'pod_name', 'pool', "redis"])
###############################################
# END DEFINE METRICS VARIABLES FOR PROMETHEUS #
###############################################

#############
# FUNCTIONS #
#############
###### GET METRICS TWEMPROXY FROM SERVER PHYSICAL ######
def get_metrics_physical(host, port, url):
    connection = http.client.HTTPConnection(host, port)
    json_data = {}
    try:
        connection.putrequest("GET", url)
        connection.endheaders()
        response = connection.getresponse()
        if response.status == 200:
            data = response.read()
            json_data = json.loads(data.decode("utf-8"))
            print(json.dumps(json_data, indent=2))
        else:
            print(f"HTTP Error: {response.status} {response.reason}")
    except Exception as e:
        json_data = str(e)
        if "service" in json_data:
            json_data = json.loads(json_data)
            json_array.append(json_data)
        else:
            json_data = {}
    finally:
        connection.close()
    return json_array

###### FETCH AND EXPOSE COMMON DATA METRICS ######
def fetch_common_metrics(json_data):
    for key, values in json_data.items():
        if key in twemproxy_name:
            pool_name = key
            client_connections = values.get('client_connections', 0)
            client_eof = values.get('client_eof', 0)
            client_err = values.get('client_err', 0)
            server_ejects = values.get('server_ejects', 0)
            forward_error = values.get('forward_error', 0)
            fragments = values.get('fragments', 0)
    pod_name = json_data.get('source', 0)
    uptime = json_data.get('uptime', 0)
    total_connection = json_data.get('total_connections', 0)
    curr_connection = json_data.get('curr_connections', 0)

    return pod_name, uptime, total_connection, curr_connection, pool_name, client_connections, client_eof, client_err, server_ejects, forward_error, fragments

def expose_common_metrics(json_data):
    ## get data
    pod_name, uptime, total_connection, curr_connection, pool_name, client_connections, client_eof, client_err, server_ejects, forward_error, fragments = fetch_common_metrics(json_data)

    ## set label
    uptime_label = {'platform': platform, 'pod_name': pod_name, 'pool': pool_name}
    total_connection_label = {'platform': platform, 'pod_name': pod_name, 'pool': pool_name}
    curr_connection_label = {'platform': platform, 'pod_name': pod_name, 'pool': pool_name}
    client_connections_label = {'platform': platform, 'pod_name': pod_name, 'pool': pool_name}
    client_eof_label = {'platform': platform, 'pod_name': pod_name, 'pool': pool_name}
    client_err_label = {'platform': platform, 'pod_name': pod_name, 'pool': pool_name}
    server_ejects_label = {'platform': platform, 'pod_name': pod_name, 'pool': pool_name}
    forward_error_label = {'platform': platform, 'pod_name': pod_name, 'pool': pool_name}
    fragments_label = {'platform': platform, 'pod_name': pod_name, 'pool': pool_name}

    ## expose metrics
    uptime_metric.labels(**uptime_label).set(int(uptime))
    total_connection_metric.labels(**total_connection_label).set(int(total_connection))
    curr_connection_metric.labels(**curr_connection_label).set(int(curr_connection))
    client_connections_metric.labels(**client_connections_label).set(int(client_connections))
    client_eof_metric.labels(**client_eof_label).set(int(client_eof))
    client_err_metric.labels(**client_err_label).set(int(client_err))
    server_ejects_metric.labels(**server_ejects_label).set(int(server_ejects))
    forward_error_metric.labels(**forward_error_label).set(int(forward_error))
    fragments_metric.labels(**fragments_label).set(int(fragments))

###### FETCH AND EXPOSE REDIS SERVER DATA METRICS ######
def fetch_redis_metrics(redis_server_data, redis_server):
    redis_ip = redis_server
    server_eof = redis_server_data.get("server_eof", 0)
    server_err = redis_server_data.get("server_err", 0)
    server_timedout = redis_server_data.get("server_timedout", 0)
    server_connections = redis_server_data.get("server_connections", 0)
    server_ejected_at = redis_server_data.get("server_ejected_at", 0)
    requests = redis_server_data.get("requests", 0)
    request_bytes = redis_server_data.get("request_bytes", 0)
    responses = redis_server_data.get("responses", 0)
    response_bytes = redis_server_data.get("response_bytes", 0)
    in_queue = redis_server_data.get("in_queue", 0)
    in_queue_bytes = redis_server_data.get("in_queue_bytes", 0)
    out_queue = redis_server_data.get("out_queue", 0)
    out_queue_bytes = redis_server_data.get("out_queue_bytes", 0)
    return redis_ip, server_eof, server_err, server_timedout, server_connections, server_ejected_at, requests, request_bytes, responses, response_bytes, in_queue, in_queue_bytes, out_queue, out_queue_bytes

def expose_redis_metrics(json_data):
    for key, values in json_data.items():
        if key in twemproxy_name:
            pool_name = key
    pod_name = json_data.get('source', 0)
    ## get data
    for redis_server, redis_server_data in json_data.get(pool_name, {}).items():
        if re.match(pattern_ip, redis_server) or re.match(pattern_name_redis, redis_server):
            redis_ip, server_eof, server_err, server_timedout, server_connections, server_ejected_at, requests, request_bytes, responses, response_bytes, in_queue, in_queue_bytes, out_queue, out_queue_bytes = fetch_redis_metrics(redis_server_data, redis_server)

            ## set label
            server_eof_label = {'platform': platform,'pod_name': pod_name, 'pool': pool_name, 'redis': redis_ip}
            server_err_label = {'platform': platform,'pod_name': pod_name, 'pool': pool_name, 'redis': redis_ip}
            server_timedout_label = {'platform': platform,'pod_name': pod_name, 'pool': pool_name, 'redis': redis_ip}
            server_connections_label = {'platform': platform,'pod_name': pod_name, 'pool': pool_name, 'redis': redis_ip}
            server_ejected_at_label = {'platform': platform,'pod_name': pod_name, 'pool': pool_name, 'redis': redis_ip}
            requests_label = {'platform': platform,'pod_name': pod_name, 'pool': pool_name, 'redis': redis_ip}
            request_bytes_label = {'platform': platform,'pod_name': pod_name, 'pool': pool_name, 'redis': redis_ip}
            responses_label = {'platform': platform,'pod_name': pod_name, 'pool': pool_name, 'redis': redis_ip}
            response_bytes_label = {'platform': platform,'pod_name': pod_name, 'pool': pool_name, 'redis': redis_ip}
            in_queue_label = {'platform': platform,'pod_name': pod_name, 'pool': pool_name, 'redis': redis_ip}
            in_queue_bytes_label = {'platform': platform,'pod_name': pod_name, 'pool': pool_name, 'redis': redis_ip}
            out_queue_label = {'platform': platform,'pod_name': pod_name, 'pool': pool_name, 'redis': redis_ip}
            out_queue_bytes_label = {'platform': platform,'pod_name': pod_name, 'pool': pool_name, 'redis': redis_ip}

            ## expose metrics
            server_eof_metric.labels(**server_eof_label).set(int(server_eof))
            server_err_metric.labels(**server_err_label).set(int(server_err))
            server_timedout_metric.labels(**server_timedout_label).set(int(server_timedout))
            server_connections_metric.labels(**server_connections_label).set(int(server_connections))
            server_ejected_at_metric.labels(**server_ejected_at_label).set(int(server_ejected_at))
            requests_metric.labels(**requests_label).set(int(requests))
            request_bytes_metric.labels(**request_bytes_label).set(int(request_bytes))
            responses_metric.labels(**responses_label).set(int(responses))
            response_bytes_metric.labels(**response_bytes_label).set(int(response_bytes))
            in_queue_metric.labels(**in_queue_label).set(int(in_queue))
            in_queue_bytes_metric.labels(**in_queue_bytes_label).set(int(in_queue_bytes))
            out_queue_metric.labels(**out_queue_label).set(int(out_queue))
            out_queue_bytes_metric.labels(**out_queue_bytes_label).set(int(out_queue_bytes))
#################
# END FUNCTIONS #
#################

############
# REST API #
############
@app.route('/metrics', methods=['GET'])
def get_metrics():
    if env_platform == "physical":
        server_str = os.getenv("SERVER_PHYSICAL")
        server = ast.literal_eval(server_str)
    else:
        server = []
        port_str = os.getenv("PORT_K8S")
        port = ast.literal_eval(port_str)
        pod_list = api_instance.list_namespaced_pod(namespace, label_selector=label_selector)
        for p in port:
            for pod in pod_list.items:
                pod_ip = pod.status.pod_ip
                server.append({"host": pod_ip, "port": p, "url": pod_ip})
                

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        json_arrays = list(executor.map(lambda server_data: get_metrics_physical(**server_data), server))
    json_array = [item for sublist in json_arrays for item in sublist]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(expose_common_metrics, json_array)
        executor.map(expose_redis_metrics, json_array)

    return Response(generate_latest(), content_type='text/plain; version=0.0.4')
################
# END REST API #
################

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port='80')  # Run the Flask app in debug mode

