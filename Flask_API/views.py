from fileinput import filename
from . import app
import csv
import json

from flask import render_template, url_for


@app.route("/")
def home():
    img_src = ''
    return "<div style='text-align:center;'><img src='./static/root.jpg' alt='Welcome HOME!'></div>"

@app.route("/display_ngo_details")
def ngo_details(ngo_details=None):
    ngo_details = 'ngo_details.csv'
    csvfile = open(f'../NGO/{ngo_details}', 'r')
    fieldnames = ['Name', 'Registration Number', 'City', 'State', 'Address', 'Sectors Working In']
    jsonfile = open('../NGO/ngo_details.json', 'w')
    reader = csv.DictReader(csvfile)
    next(reader, None)
    ngo_details_json = {}
    for idx, rows in enumerate(reader):
        ngo_details_json[idx] = rows
    jsonfile.write(json.dumps(ngo_details_json))
    return render_template("data_table.html", title = "NGO Details", headers = fieldnames, data = ngo_details_json)

@app.route("/display_atm_details/<city>")
def atm_details(city):
    csvfilename = f'../CITY/{city}/ATM_FILES/CSV/consolidated_atm_list.csv'
    csvfile = open(csvfilename, 'r')
    fieldnames = ['ATM','Heading', 'Operator', 'Contact Details', 'email', 'City', 'Location', 'Address', 'Type', 'Fiat', 'Supported Coins']
    jsonfilename = f'../CITY/{city}/ATM_FILES/CSV/consolidated_atm_list.json'
    jsonfile = open(jsonfilename, 'w')
    reader = csv.DictReader(csvfile)
    atm_details_json = {}
    for idx, rows in enumerate(reader):
        atm_details_json[idx] = rows
    jsonfile.write(json.dumps(atm_details_json))
    return render_template("data_table.html", title = f'{city} ATM List', headers = fieldnames, data = atm_details_json)