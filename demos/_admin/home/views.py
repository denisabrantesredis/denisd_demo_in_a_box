import sys
import json
import time
import redis
import requests
from redis.commands.search.query import Query
from flask import render_template, session, request, redirect
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import TextField, NumericField, TagField, GeoField

from datagen import (get_fake_id, get_fake_uuid, get_fake_text, get_fake_number, get_fake_float, get_fake_name, get_fake_timestamp, get_fake_phone, 
                     get_fake_email, get_fake_job_title, get_fake_location, get_fake_boolean, get_fake_coordinates, get_fake_company,
                     get_fake_url, get_fake_ip, get_fake_file_path, get_fake_list_of_strings, get_fake_list_of_ints, get_fake_option)

from redis_utils import get_redis_client, get_index_list

from . import home_bp

def run_query(query_prefix, index_name, offset, num):
    responses = "FAILED TO RUN QUERY"
    r = get_redis_client(session['redis_host'], session['redis_port'], session['redis_user'], session['redis_pass'])
    start = time.perf_counter()
    query = (Query(query_prefix).paging(offset, num))
    try:
        responses = r.ft(index_name).search(query).docs
    except Exception as ex:
        responses = [f"ERROR RUNNING QUERY: {ex}"]    
    end = time.perf_counter()
    elapsed = end - start
    print(f'Query Time: {elapsed:.6f} seconds', file=sys.stdout)
    return responses

def generate_fake_values(attributes):
    this_doc = {}
    for attribute in attributes:
        value = None
        name = attribute['name']

        if attribute['type'] == "id":
            value = get_fake_id(attribute['range'])
        if attribute['type'] == "uuid":
            value = get_fake_uuid()
        if attribute['type'] == "text":
            value = get_fake_text(attribute['range'])
        if attribute['type'] == "number_int":
            value = get_fake_number(attribute['range'])
        if attribute['type'] == "number_float":
            value = get_fake_float(attribute['range'])
        if attribute['type'] == "name_first":
            value = get_fake_name("first")
        if attribute['type'] == "name_last":
            value = get_fake_name("last")
        if attribute['type'] == "name_full":
            value = get_fake_name("full")            
        if attribute['type'] == "email":
            value = get_fake_email()
        if attribute['type'] == "phone":
            value = get_fake_phone()
        if attribute['type'] == "add_street":
            value = get_fake_location("street")
        if attribute['type'] == "add_city":
            value = get_fake_location("citi")                                    
        if attribute['type'] == "add_state":
            value = get_fake_location("state")
        if attribute['type'] == "add_country":
            value = get_fake_location("country")
        if attribute['type'] == "add_zip":
            value = get_fake_location("zipcode")
        if attribute['type'] == "job_title":
            value = get_fake_job_title()
        if attribute['type'] == "job_company":
            value = get_fake_company()
        if attribute['type'] == "url":
            value = get_fake_url()
        if attribute['type'] == "ip":
            value = get_fake_ip()
        if attribute['type'] == "timestamp":
            value = get_fake_timestamp()
        if attribute['type'] == "boolean":
            value = str(get_fake_boolean())
        if attribute['type'] == "filename":
            value = get_fake_file_path(attribute['range'])
        if attribute['type'] == "list_int":
            value = get_fake_list_of_ints(attribute['range'])
        if attribute['type'] == "list_str":
            value = get_fake_list_of_strings(attribute['range'])
        if attribute['type'] == "list_option":
            option_list = attribute['range'].split(",")
            value = get_fake_option(option_list)

        # Handle coordinates - it will be 2 attributes
        if attribute['type'] == "coords":
            value = get_fake_coordinates()
            this_doc['latitude'] = value[0]
            this_doc['longitude'] = value[1]

        else:
            this_doc[name] = value

    return this_doc

def create_index(r, prefix, attributes):
    field_list = []
    index_name = f"idx:{prefix}"
    for attribute in attributes:
        name = attribute['name']
        type = attribute['type']
        if type in ["id", "uuid", "text", "name_first", "name_last", "name_full", "email", "phone", "add_street", "add_state", "add_country", "add_zip", "job_title",
                    "job_company", "url", "ip", "timestamp", "curr_name", "filename", "boolean", "list_option"]:
            field_list.append(TextField(name))
        if type in ["number_int", "number_float"]:
            field_list.append(NumericField(name))
        if type in ["list_int", "list_str"]:
            field_list.append(TagField(name))
        # if type in ["coords"]:
        #     field_list.append(GeoField(name))

    schema_definition = { prefix : field_list}
    result = "failed"
    try:
        index_definition = schema_definition[prefix]
        def_prefix = [f"{prefix}:"]
        index_prefix = f"idx:{prefix}"
        index_type = IndexType.HASH
        if format == "json":
            index_type = IndexType.JSON
        definition = IndexDefinition(prefix=def_prefix, index_type=index_type)
        result = r.ft(index_prefix).create_index(fields=index_definition, definition=definition)
    except Exception as ex:
        result = f"FAILED to create index: {ex}"
    return result    

def get_jupyter_token():
    token = ''
    with open(r'/root/.local/share/jupyter/runtime/jpserver-7-open.html', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.find('token=') != -1:
                start = line.index('token=') + 6
                end = line.index('/>') - 2
                for idx in range(start, end):
                    token = token + line[idx]
                break
        return token


# Basic Content
@home_bp.route('/')
def index():
    print("--> Loading Home Page", file=sys.stdout)
    try:
        redis_host = session['redis_host']
        redis_port = session['redis_port']
        redis_user = session['redis_user']
        redis_pass = session['redis_pass']

    except:
        session['redis_host'] = "127.0.0.1"
        session['redis_port'] = "16154"
        session['redis_user'] = "default"
        session['redis_pass'] = "welcome1"
        redis_host = session['redis_host']
        redis_port = session['redis_port']
        redis_user = session['redis_user']
        redis_pass = session['redis_pass']

    token = get_jupyter_token()

    return render_template('/home.html', redis_host=redis_host,redis_port=redis_port,redis_user=redis_user,redis_pass=redis_pass,token=token)

@home_bp.route('/testconn', methods=['POST'])
def testconn():
    print("--> Testing DB Connectivity", file=sys.stdout)
    session['redis_host'] = request.values.get('redis_host')
    session['redis_port'] = request.values.get('redis_port')
    session['redis_user'] = request.values.get('redis_user')
    session['redis_pass'] = request.values.get('redis_pass')

    try:
        redis_client = get_redis_client(session['redis_host'], session['redis_port'], session['redis_user'], session['redis_pass'])

        if redis_client.ping():
            return "success"
    except:
        return "fail"


# Data Generator Content
@home_bp.route('/datagenerator')
def load_data_generator():
    print("--> Loading Data Generator", file=sys.stdout)
    return render_template('/datagen.html', redis_host=session['redis_host'], redis_port=session['redis_port'], redis_user=session['redis_user'], redis_pass=session['redis_pass'])

@home_bp.route('/createdocs', methods=['POST'])
def create_documents():
    print("--> Creating Documents", file=sys.stdout)

    session['redis_host'] = request.values.get('redis_host')
    session['redis_port'] = request.values.get('redis_port')
    session['redis_user'] = request.values.get('redis_user')
    session['redis_pass'] = request.values.get('redis_pass')

    dataformat = request.values.get('dataformat')
    keyprefix = request.values.get('keyprefix')
    numberofdocs = request.values.get('numberofdocs')
    attributes = json.loads(request.values.get('attributes'))

    print(f"--> Format: {dataformat} | Prefix: {keyprefix} | # of docs: {numberofdocs} | Attributes: {attributes}", file=sys.stdout)

    try:
        r = get_redis_client(session['redis_host'], session['redis_port'], session['redis_user'], session['redis_pass'])
        if r.ping():
            keysize = len(numberofdocs) + 1
            pipe = r.pipeline()
            for i in range(int(numberofdocs)):
                key_id = str(i).zfill(keysize)
                key = f"{keyprefix}:{key_id}"
                
                # Generate Fake values
                doc = generate_fake_values(attributes)
                pipe.hset(key, mapping=doc)

            res = pipe.execute()
            create_index(r, keyprefix, attributes)

            return "success"

    except Exception as ex:
        return f"FAILED: {ex}"


# Geo Demo Content
@home_bp.route('/geodemo')
def load_geodemo_page():
    print("--> Loading GeoDemo Page", file=sys.stdout)
    try:
        redis_host = session['redis_host']
        redis_port = session['redis_port']
        redis_user = session['redis_user']
        redis_pass = session['redis_pass']

    except:
        session['redis_host'] = "127.0.0.1"
        session['redis_port'] = "16154"
        session['redis_user'] = "default"
        session['redis_pass'] = "welcome1"
        redis_host = session['redis_host']
        redis_port = session['redis_port']
        redis_user = session['redis_user']
        redis_pass = session['redis_pass']
                
    return render_template('/geodemo.html', redis_host=redis_host,redis_port=redis_port,redis_user=redis_user,redis_pass=redis_pass)

@home_bp.route('/indexlist', methods=['GET'])
def get_indexlist():
    print("--> Getting List of Indexes", file=sys.stdout)
    try:
        redis_client = get_redis_client(session['redis_host'], session['redis_port'], session['redis_user'], session['redis_pass'])
        return get_index_list(redis_client)
    except:
        return "fail"

@home_bp.route('/geodata', methods=['POST'])
def get_geodata():
    print("--> Get geodata", file=sys.stdout)
    index_name = request.values.get('index_name')
    
    query_prefix = "*"
    doc_list = run_query(query_prefix, index_name, 0, 100)
    print(doc_list, file=sys.stdout)
    docs_dict = []
    for doc in doc_list:
        docs_dict.append(doc.__dict__)
    
    
    return docs_dict


# My Redis Demo Content
@home_bp.route('/login', methods=['POST'])
def connect():
    print("--> User Login", file=sys.stdout)
    username = request.values.get('username')
    password = request.values.get('password')

    # fetch user key from Redis
    query_prefix = f"@username:{username}"
    user_doc = run_query(query_prefix, 'idx:users', 0, 10)
    key = "NOT FOUND"
    for doc in user_doc:
        user_key = doc['id']
        key = user_key.split(":")[1]

    return key

@home_bp.route('/user/<user_key>')
def get_user_data(user_key=None):
    print("--> User Data", file=sys.stdout)

    # fetch user key from Redis
    user_key = f"users:{user_key}"
    print(f"--> SEARCH: {user_key}", file=sys.stdout)
    start = time.perf_counter()
    user_doc = r.hgetall(user_key)
    end = time.perf_counter()
    elapsed = end - start
    decoded = {key.decode('ascii'):user_doc[key].decode('ascii') for key in user_doc.keys()}
    userKey = decoded["userKey"]
    tmNbr = decoded["tmNbr"]
    name = decoded["name"]
    phone = decoded["phone"]
    fax = decoded["fax"]
    email = decoded["email"]
    mobile = decoded["mobile"]
    title = decoded["title"]
    unitId = decoded["unitId"]
    locationAbbr = decoded["locationAbbr"]
    location = decoded["location"]
    state = decoded["state"]
    department = decoded["department"]
    directoryDepartmentKeys = decoded["directoryDepartmentKeys"]
    workbrainJobId = decoded["workbrainJobId"]
    atStoreFlag = decoded["atStoreFlag"]
    contactKey = decoded["contactKey"]
    contactSearchableFlag = decoded["contactSearchableFlag"]
    lastUpdated = decoded["lastUpdated"]
    longitude = decoded["longitude"]
    latitude = decoded["latitude"]
       
    return render_template('/main.html', 
                           key = user_key,
                           userKey = userKey,
                           tmNbr = tmNbr,
                           name = name,
                           phone = phone,
                           fax = fax,
                           email = email,
                           mobile = mobile,
                           title = title,
                           unitId = unitId,
                           locationAbbr = locationAbbr,
                           location = location,
                           state = state,
                           department = department,
                           directoryDepartmentKeys = directoryDepartmentKeys,
                           workbrainJobId = workbrainJobId,
                           atStoreFlag = atStoreFlag,
                           contactKey = contactKey,
                           contactSearchableFlag = contactSearchableFlag,
                           lastUpdated = lastUpdated,
                           longitude = longitude,
                           latitude = latitude,
                           time_elapsed = round(elapsed,4)*1000
                           )

# Insight Tutorials
@home_bp.route('/insight')
def load_insight_page():
    print("--> Loading Insight page", file=sys.stdout)
    try:
        redis_host = session['redis_host']
        redis_port = session['redis_port']
        redis_user = session['redis_user']
        redis_pass = session['redis_pass']

    except:
        session['redis_host'] = "127.0.0.1"
        session['redis_port'] = "16154"
        session['redis_user'] = "default"
        session['redis_pass'] = "welcome1"
        redis_host = session['redis_host']
        redis_port = session['redis_port']
        redis_user = session['redis_user']
        redis_pass = session['redis_pass']
                
    return render_template('/insight.html', redis_host=redis_host,redis_port=redis_port,redis_user=redis_user,redis_pass=redis_pass)

@home_bp.route('/createdata', methods=['POST'])
def createdata():
    print("--> Creating Dataset", file=sys.stdout)
    session['redis_host'] = request.values.get('redis_host')
    session['redis_port'] = request.values.get('redis_port')
    session['redis_user'] = request.values.get('redis_user')
    session['redis_pass'] = request.values.get('redis_pass')
    dataset = request.values.get('dataset')

    try:
        redis_client = get_redis_client(session['redis_host'], session['redis_port'], session['redis_user'], session['redis_pass'])
        if redis_client.ping():
            if dataset == 'geo':
                keysize = 4
                keyprefix = "restaurant"
                pipe = redis_client.pipeline()
                for i in range(100):
                    key_id = str(i).zfill(keysize)
                    key = f"{keyprefix}:{key_id}"
                    
                    attributes = [
                        {"name":"id", "type":"id", "range":"10"},
                        {"name":"name", "type":"job_company", "range":""},
                        {"name":"address", "type":"add_street", "range":""},
                        {"name":"phone", "type":"phone", "range":""},
                        {"name":"coords", "type":"coords", "range":""},
                        {"name":"cousine", "type":"list_option", "range":"['Italian','Asian','BBQ','Pizza','Breakfast','Mexican']"},
                    ]

                    # Generate Fake values
                    doc = generate_fake_values(attributes)
                    pipe.hset(key, mapping=doc)
                    #print(f"Coords: Long: {doc['longitude']}, Lat: {doc['latitude']}")
                    pipe.geoadd("idx:restaurant_geo", [doc['longitude'], doc['latitude'], doc['name']])

                res = pipe.execute()
                create_index(redis_client, keyprefix, attributes)
                return "success"
    except:
        return "fail"
