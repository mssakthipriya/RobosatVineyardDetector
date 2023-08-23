from flask import Flask, render_template, request, jsonify
import os
import subprocess
import requests
from PIL import Image
from io import BytesIO
import time

app = Flask(__name__)

METERS_PER_DEGREE_LATITUDE = 111000

def download_satellite_image(lat, lon, zoom, image_path, distance_km):
    # Calculate bounding box coordinates in degrees
    distance_meters = distance_km * 1000
    delta_latitude = distance_meters / METERS_PER_DEGREE_LATITUDE
    bbox = (lon - delta_latitude, lat - delta_latitude, lon + delta_latitude, lat + delta_latitude)

    # Define the tile server URL (Mapbox Satellite)
    access_token = "YOUR_MAPBOX_ACCESS_TOKEN"  # Replace with your Mapbox access token
    url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]},{zoom}/800x600?access_token=pk.eyJ1Ijoic2FrdGhpcHJpeWEiLCJhIjoiY2xrNm10dDNoMDAxZzNwcWZzNWczc242YSJ9.AcOUSZgtySo5kFdEfz7SaQ"
    
    try:
        # Download the image from the tile server
        response = requests.get(url)
        if response.status_code == 200:
            # Save the image to the specified path
            with open(image_path, 'wb') as file:
                file.write(response.content)
            return True
        else:
            print("Error while downloading the satellite image.")
            return False
    except Exception as e:
        print(f"Error while downloading the satellite image: {e}")
        return False

def check_image_validity(image_path):
    try:
        with Image.open(image_path) as img:
            return img.size[0] > 1 and img.size[1] > 1
    except Exception as e:
        print(f"Error while checking the validity of the image: {e}")
        return False

def convert_to_slippy_tiles(image_path, zoom, output_folder):
    if not os.path.isfile(image_path):
        print("Error: Image file not found.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    georeferenced_image = os.path.join(output_folder, "georeferenced.tif")
    subprocess.run(["gdal_translate", "-a_srs", "EPSG:4326", "-a_ullr", 
                    f"{longitude-0.005}", f"{latitude+0.005}", f"{longitude+0.005}", f"{latitude-0.005}",
                    image_path, georeferenced_image])

    projected_image = os.path.join(output_folder, "projected.tif")
    subprocess.run(["gdalwarp", "-t_srs", "EPSG:3857", georeferenced_image, projected_image])

    subprocess.run(["gdal2tiles.py", "-z", f"{zoom}-18", projected_image, output_folder])

    os.remove(georeferenced_image)
    os.remove(projected_image)

    print("Slippy tiles generated successfully.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        zoom_levels = request.form['zoom_levels']
        distance_km = float(request.form['distance'])
        
        output_folder = "output_images"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        input_image_path = os.path.join(output_folder, "satellite_image.png")
        zoom = int(zoom_levels.split("-")[1])

        if download_satellite_image(latitude, longitude, zoom, input_image_path, distance_km):
            if check_image_validity(input_image_path):
                time.sleep(5)
                convert_to_slippy_tiles(input_image_path, zoom, output_folder)
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'error': 'Invalid or empty image.'})
        else:
            return jsonify({'success': False, 'error': 'Error downloading satellite image.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)

