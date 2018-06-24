import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import mapcalc

app = Flask(__name__)
app.config.from_object(__name__)
app.debug = True

print("got here")
# Load default config and override config from an environment variable
#app.config.update(dict(
#    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
#    SECRET_KEY='development key',
#    USERNAME='admin',
#    PASSWORD='default'
#))
#app.config.from_envvar('FLASKR_SETTINGS', silent=True)


#def connect_db():
#    """Connects to the specific database."""
#    rv = sqlite3.connect(app.config['DATABASE'])
#    rv.row_factory = sqlite3.Row
#    return rv


@app.route('/')
def show_form():
    return render_template('alt_add.html')

# The following route takes the result of the form on the landing page, and uses all the mapcalc helper functions to:
# - Chop up the user input into dicts
# - Geocode the given address into coordinates
# - Use the data it's calculated to find the user appropriate locations


@app.route('/calc', methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        union_sq = (40.736278, -73.9912)
        result = request.form
        user_inputs = []
        target_address = result['target_address']
        dist=float(result['dis'])
        a=float(result['unit'])
        target_coords = mapcalc.get_coords_from_address(target_address)
        for i in range(2):
            dist_key = 'dist_' +str(i+1)
            req_type_key = 'req_type_' + str(i+1)
            search_term_key = 'search_term_' + str(i+1)
            search_item = mapcalc.add_user_inputs(result[req_type_key], result[dist_key], result[search_term_key])
            user_inputs.append(search_item)

        list_of_results = []
        for param in user_inputs:
            list_of_results.append(mapcalc.result_list(param, target_coords,dist*a))
        final_coords = mapcalc.res_locations(list_of_results, user_inputs,target_coords,dist*a)
        # return str(mapcalc.formatted_google_maps_lines(final_coords))
        return render_template("heatmap.html", map_center_lat = target_coords[0], map_center_lng = target_coords[1], points_list = mapcalc.formatted_google_maps_lines(final_coords))
