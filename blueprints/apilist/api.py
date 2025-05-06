from flask import Blueprint, request, make_response, jsonify 
from bson import ObjectId
import requests
import globals 
import string
from flask_jwt_extended import jwt_required, get_jwt_identity

api_bp = Blueprint("api_bp", __name__)


API_KEY = 'o1LlHDrpMx7YiXiE9hXwwQ==mrxycYUPUQJYXbj0' 

API_URL = 'https://api.api-ninjas.com/v1/iplookup?address='

WHO_URL = 'https://api.api-ninjas.com/v1/whois?domain='

SEC_FILINGS = 'https://api.api-ninjas.com/v1/sec'


def get_ip(ip_address):
    headers = {'X-Api-Key': API_KEY}
    response = requests.get(f"{API_URL}{ip_address}", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to retrieve data from API Ninjas'}
    

@api_bp.route("/api/v1.0/iplookup", methods=['GET'])
def ip_lookup():
    ip_address = request.args.get('ip')  
    if not ip_address:
        return jsonify({'error': 'IP address is required'}), 400
    

    ip_info = get_ip(ip_address)
    
    return jsonify(ip_info)


def get_domain(domain):
    headers = {'X-Api-Key': API_KEY}
    response = requests.get(f"{WHO_URL}{domain}", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to retrieve data from API Ninjas'}
    
    
@api_bp.route("/api/v1.0/whois", methods=['GET'])
def whois():
    domain = request.args.get('domain')  
    if not domain:
        return jsonify({'error': 'Domain is required'}), 400
    

    domain_info = get_domain(domain)
    
    return jsonify(domain_info)


def get_sec(sec_ticker, sec_filings):
    headers = {'X-Api-Key': API_KEY}
    try:
        response = requests.get(f"{SEC_FILINGS}?ticker={sec_ticker}&filing={sec_filings}", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f'Failed to retrieve data from API Ninjas. Status code: {response.status_code}'}
    
    except requests.exceptions.RequestException as e:
        return {'error': f'Error during API request: {str(e)}'}

@api_bp.route("/api/v1.0/sec", methods=['GET'])
def sec_filings():
    sec_ticker = request.args.get('ticker') 
    sec_filings = request.args.get('filing')  

    if not sec_ticker or not sec_filings:
        return jsonify({'error': 'Both ticker and form type (filing) are required'}), 400

    try:
        sec_info = get_sec(sec_ticker, sec_filings)

        if 'error' in sec_info:
            return jsonify(sec_info), 400

        return jsonify(sec_info)

    except Exception as e:
        return jsonify({'error': str(e)}), 500