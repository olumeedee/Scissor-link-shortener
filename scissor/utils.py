from flask import request
import string, random, requests, io, qrcode


def generate_short_url(length=5):
    chars = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(chars) for _ in range(length))
    return short_url


def generate_qr_code(link):
    image = qrcode.make(link)
    image_io = io.BytesIO()
    image.save(image_io, 'PNG')
    image_io.seek(0)
    return image_io


def link_analytics(link):
    ip_address = request.remote_addr
    user_agent = request.user_agent.string
    location = get_location(ip_address)
    
    return f'''
        <h2>Link Analytics</h2>
        <p>IP Address: {ip_address}</p>
        <p>Operating System: {user_agent}</p>
        <p>Location: {location}</p>
    '''

def get_location(ip_address):
    response = requests.get(f'http://ip-api.com/json/{ip_address}')
    data = response.json()
    
    if data['status'] == 'fail':
        return 'Location not available'
    
    city = data['city']
    region = data['regionName']
    country = data['country']
    
    return f'{city}, {region}, {country}'