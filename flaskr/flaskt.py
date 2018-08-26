import os

import sqlite3

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

import mapcalc

import math

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

    return render_template('alt_ad.html')



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

       

        if result['target_address']:
        
            target_address = result['target_address']

        else:

            target_address = 0


        #print('a')

        result2=result.copy()

        le=int((len(result)-3)/4)

        #print(result)
        dist=float(result['dis'])/10.0

        dist=pow(2,dist)
        
        a=float(result['unit'])

        if target_address != 0:

            target_coords = mapcalc.get_coords_from_address(target_address)

       	else:

            target_coords = (float(result['lag']),float(result['lng']))
        
        #print(result['color3'])
            
        for i in range(le):

            if result2['color'+str(i+1)]=='':
      
                break

            dist_key = 'dist_' +str(i+1)

            req_type_key = 'req_type_' + str(i+1)

            search_term_key = 'search_term_' + str(i+1)

            color='color'+str(i+1)

            if result2[color]!=str(i+1):

                result2[search_term_key]=result2[color]

            #print(result2,end='zzzzzzzzzzzzzzzzzzzzzzzzzzzz')

            search_item = mapcalc.add_user_inputs(result2[req_type_key], result2[dist_key], result2[search_term_key],a)

            user_inputs.append(search_item)

        #print(user_inputs)
        #print(len(user_inputs),end=' here is length ')

        list_of_results = []

        for param in user_inputs:

            list_of_results.append(mapcalc.result_list(param, target_coords,dist*a))

        final_coords = mapcalc.res_locations(list_of_results, user_inputs,target_coords,dist*a)
        #print(final_coords)
        #return render_template("toomany.html")
        if final_coords == 0:
            return render_template("not_found.html")
        elif final_coords == 1:
            return render_template("toomany.html")
        else:
            return render_template("heatmap.html", map_center_lat = target_coords[0], map_center_lng = target_coords[1], points_list = mapcalc.formatted_google_maps_lines(final_coords))
