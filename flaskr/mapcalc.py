# File containing all the mapping-relevant helper functions for Settler


import googlemaps
import googlemaps.places as places_api
from geopy.distance import vincenty
import itertools
import geocoder

#api_key = "AIzaSyBJLSm__jnoJbfAiL0fSQvpLQM5H9UuBoY"
api_key='AIzaSyDNvdrZ_HEtfsuPYHV9UvZGc41BSFBolOM'

def verify_import():
    return "hey it worked!"

# until the frontend page works, use this list of dicts to add search terms
dummy_user_inputs = [
    {'req_type': 'closer_than', 'dist': 0.25, 'search_term': 'laundry'},
    {'req_type': 'closer_than', 'dist': 0.25, 'search_term': 'gym'},
    {'req_type': 'further_than', 'dist': 0.5, 'search_term': 'nightclub'}
]


def add_user_inputs(req_type, dist, search_term, unit):
    user_dict = {'req_type':req_type, 'dist':unit*(2**float(dist)), 'search_term':search_term}
    return user_dict


# gmaps = googlemaps.Client(key=api_key)

def get_coords_from_address(address):
    gmaps = googlemaps.Client(key=api_key)
    geocode_result = gmaps.geocode(address)
    lat = geocode_result[0]['geometry']['location']['lat']
    lng = geocode_result[0]['geometry']['location']['lng']
    coords = (lat, lng)
    return coords


# function to build and store required search terms
def result_list(req, loc,ra):
    # req is a dict representing one search parameter
    # loc is a latitude-longitude tuple
    search_term = req['search_term']
    gmaps = googlemaps.Client(key=api_key)
    r=int(ra*1609)
    gsearch = googlemaps.places.places(gmaps, search_term, location=loc,radius=r)
    return gsearch['results']


# all this following code belongs elsewhere; this script is just for defining the helper functions
# big_list_of_results = []
#
# for param in dummy_user_inputs:
#     big_list_of_results.append(result_list(param, union_sq))


def res_locations(loc_lists, params,co,dis):
    # Function that takes all the user input and spits out an array of ideal lat-long locations that fit the params
    # loc_lists is a list of lists
    # each inner list contains (dict) locations of the same type of establishment - gym, church etc.
    # params is a list of dicts, where each dict is one parameter the user defined
    # three keys: req_type, dist, search_term
    # see the dummy user data above for an example

    # What it does with all of this data is it checks every possible permutation of the locations
    # Finds a weighted average lat-long (where the weights are inversely proportional to
    # how close/far they want to be from the place).
    # It then checks if that point fulfils the distance requirements from all the parameters.
    # If it does, brilliant, add it to the list of solutions and keep iterating.

    # When done, return that list of solutions.
    # The server can then take that data and give the user a front-end Google Maps API drawing of a heat-map.
    # Okay, enough talk, let's begin.

    # This is the return list
    final_latlongs = []

    # Sanity check
    if len(loc_lists) != len(params):
        print("Something has clearly gone very wrong and there are fewer results than expected")
        return []
    all_combos = list(itertools.product(*loc_lists))
    print(len(all_combos),end='here we go again')
    if  (len(all_combos))>140000:
        return 1
    elif (len(all_combos))==0:
        return 0
    # We don't know for sure what exactly the name of the establishment type according to Google will be.
    # e.g. if you search for "nightclub", Google might think the place is primarily a bar but also a night_club
    # so the search term and the place type don't match up 1:1
    # Instead we rely on the fact that the order of the elements in each combination is the same as it is in the search.

    # For each combination:
    # We do a calculation similar to the Center of Mass in physics
    # The "mass" of the Nth item in the combination is 1/dist in params[N]
    # Approximating the fact that the ideal location is pulled in the direction of places the user wants to be closer to

    for i in range(len(all_combos)):
    # for i in range(100):
        weights = []
        for n in range(len(all_combos[i])):
            dist = params[n]['dist']
            wt = 1/dist
            weights.append(wt)
        # so now we know the weights, so we should actually calculate the lat/long of our center point
        COMlat = 0
        COMlng = 0
        for x in range(len(all_combos[i])):
            COMlat += (all_combos[i][x]['geometry']['location']['lat'] * weights[x])
            COMlng += (all_combos[i][x]['geometry']['location']['lng'] * weights[x])
        COMlng /= sum(weights)
        COMlat /= sum(weights)
        candidate_loc = (COMlat, COMlng)
        # So now we have a candidate for being added to the list of good spots.
        # To see if it deserves to go in or not, calculate the distance of this spot from each establishment
        # If it complies with every instruction we wanted, then add it to the list that the heatmap will draw, hooray!
        add_item = 1
#        for j in range(len(all_combos[i])):
#            t_loc = (all_combos[i][j]['geometry']['location']['lat'], all_combos[i][j]['geometry']['location']['lng'])
#            candidate_dist = vincenty(candidate_loc, t_loc).miles
#            if params[j]['req_type'] == 'closer_than' and candidate_dist > params[j]['dist']:
#                add_item = False
#            if params[j]['req_type'] == 'further_than' and candidate_dist < params[j]['dist']:
#                add_item = False
            # print("Targeting", params[j]['req_type'], params[j]['dist'])
            # print("Got a distance of", candidate_dist)
#        if add_item:
#            final_latlongs.append(candidate_loc)
        #print('get here')            
        for j in range(len(all_combos[i])):
            t_loc = (all_combos[i][j]['geometry']['location']['lat'], all_combos[i][j]['geometry']['location']['lng'])
            candidate_dist = vincenty(candidate_loc, t_loc).miles
            di=vincenty(candidate_loc,co).miles
            t=0
            if params[j]['req_type'] == 'closer_than':
                t=-1
            elif params[j]['req_type'] == 'further_than':
                t=1
            
            if 100*t*(candidate_dist -params[j]['dist'])<0 or di>dis:
                add_item = 0
                break
            
        if add_item==1:
            final_latlongs.append(candidate_loc)

    return final_latlongs
    # print(len(final_latlongs))
    # print(final_latlongs[0])

# this next line should really be in the other script tbh
# heatmap_points = res_locations(big_list_of_results, dummy_user_inputs)

# Function that takes tuples generated by the res_locations function and turns them into lines of Javascript
# that the Google Maps API can render onto a map

def formatted_google_maps_lines(s):  
#    s = validate_coordinates(heatmap_points)  
    g=googlemaps.Client(key=api_key)
    point_code_lines = ""  
    p=''
    for i in range(len(s)):
#        revc=g.reverse_geocode(s[i])
#        pp=geocoder.google(revc[0]['address_components'][0]['long_name'])
        line=''
        if i == (len(s) - 1):# and pp.latlng!=None:
#            p=((pp.latlng[0],pp.latlng[1]))
            line = "new google.maps.LatLng" + str(s[i])
        elif i!=(len(s)-1):# and pp.latlng!=None:
#            p=((pp.latlng[0],pp.latlng[1]))
            line = "new google.maps.LatLng" + str(s[i]) + ","
        point_code_lines += line
    return point_code_lines

 
#def validate_coordinates(heatmap_points):  
#    gmaps = googlemaps.Client(api_key)  
#    valid_points = []  
#    for coords in heatmap_points:  
#        rev_geo = gmaps.reverse_geocode(coords) 
#        v_addr_coords=(rev_geo[0]['geometry']['location']['lat'], rev_geo[0]['geometry']['location']['lng'])  
#        valid_points.append(v_addr_coords)  
#    return valid_points  




