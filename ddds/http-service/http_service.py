# -*- coding: utf-8 -*-

import json
import requests

from flask import Flask, request
from jinja2 import Environment

app = Flask(__name__)
environment = Environment()


def jsonfilter(value):
    return json.dumps(value)


environment.filters["json"] = jsonfilter


def error_response(message):
    response_template = environment.from_string("""
    {
      "status": "error",
      "message": {{message|json}},
      "data": {
        "version": "1.0"
      }
    }
    """)
    payload = response_template.render(message=message)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def query_response(value, grammar_entry):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": {{value|json}},
            "confidence": 1.0,
            "grammar_entry": {{grammar_entry|json}}
          }
        ]
      }
    }
    """)
    payload = response_template.render(value=value, grammar_entry=grammar_entry)
    print("it's alive!!!")
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def multiple_query_response(results):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "result": [
        {% for result in results %}
          {
            "value": {{result.value|json}},
            "confidence": 1.0,
            "grammar_entry": {{result.grammar_entry|json}}
          }{{"," if not loop.last}}
        {% endfor %}
        ]
      }
    }
     """)
    payload = response_template.render(results=results)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


def validator_response(is_valid):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "is_valid": {{is_valid|json}}
      }
    }
    """)
    payload = response_template.render(is_valid=is_valid)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/dummy_query_response", methods=['POST'])
def dummy_query_response():
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.1",
        "result": [
          {
            "value": "dummy",
            "confidence": 1.0,
            "grammar_entry": null
          }
        ]
      }
    }
     """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/action_success_response", methods=['POST'])
def action_success_response():
    response_template = environment.from_string("""
   {
     "status": "success",
     "data": {
       "version": "1.1"
     }
   }
   """)
    payload = response_template.render()
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/weather", methods=['POST'])
def weather():
    payload = request.get_json()
    # extracting the requested city and country
    city = payload["request"]["parameters"]["wh_city"]["grammar_entry"]
    country = payload["request"]["parameters"]["wh_country"]["grammar_entry"]
    # checking what unit was requested, defaulting to metric if none
    print(payload["request"]["parameters"]["wh_unit"])
    if payload["request"]["parameters"]["wh_unit"]!=None:
      unit=payload["request"]["parameters"]["wh_unit"]["value"]
    else:
      unit="metric"

    # fixing spaces so they work in the link
    city = city.replace(" ", "%20")
    country = country.replace(" ", "%20")   

    print(city)
    print(country)

    # making the request
    API_KEY = '419676e45445c29164b1da280782d527'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&units={unit}&appid={API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    # extracting temperature
    temperature = str(data["main"]["temp"])

    return query_response(value=temperature, grammar_entry=None)

@app.route("/get_weather", methods=['POST'])
def get_weather(unit="metric"):
    payload = request.get_json()
    # extracting the requested city and country
    city = payload["request"]["parameters"]["wh_city"]["grammar_entry"]
    country = payload["request"]["parameters"]["wh_country"]["grammar_entry"]

    # fixing spaces so they work in the link
    city = city.replace(" ", "%20")
    country = country.replace(" ", "%20")      

    # making the request
    API_KEY = '419676e45445c29164b1da280782d527'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&units={unit}&appid={API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    # extracting weather
    weather_type = str(data["weather"][0]["main"])

    return query_response(value=weather_type, grammar_entry=None)
