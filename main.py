import folium
import argparse
from geopy import Nominatim
import math

def read_file(path, year):
    """
    """
    curr_pointer = 0
    film_year_lst = []
    with open(path, encoding= "utf-8", errors="ignore") as file:
        for line in file:
            curr_pointer += 1
            if curr_pointer >= 15:
                line = line.strip()
                line_lst = line.split("\t")
                while '' in line_lst:
                    line_lst.remove('')
                if '{' in line_lst[0]:
                    line_lst[0] = line_lst[0][:line_lst[0].index('{')]
                if len(line_lst) == 3:
                    line_lst.pop(-1)
                if year in line_lst[0]:
                    film_year_lst.append(line_lst)
    return film_year_lst

def get_coords_of_film_loc(film_addr):
    """
    """
    geoloc = Nominatim(user_agent='map')
    location = geoloc.geocode(film_addr, timeout=None)

    if location == None:
        film_addr_lst = film_addr.split(',')[1:]
        film_addr = ','.join(film_addr_lst)
        location = geoloc.geocode(film_addr, timeout=None)
    if location:
        return location.latitude, location.longitude
    else:
        return None

def get_coords_of_films(films_lst):
    """
    """
    ret_dict = dict()
    for film in films_lst:
        if film[1] in ret_dict:
            ret_dict[film[1]][0].append(film[0])
        else:
            curr_loc = get_coords_of_film_loc(film[1])
            if curr_loc:
                ret_dict[film[1]]= [[film[0]], get_coords_of_film_loc(film[1])]
            else:
                continue
    return ret_dict

def get_distance(my_coords, film_coords):
    """
    """
    dist = 12734.889 * math.asin(math.sqrt((math.sin((film_coords[0]-my_coords[0])/2)) ** 2
    + math.cos(film_coords[0]) * math.cos(my_coords[0]) * (math.sin((my_coords[1]-film_coords[1])/2)) ** 2))
    return dist

def get_distance_dict(film_dict, my_coords):
    """
    """
    dist_lst = []
    for loc in film_dict:
        dist_lst.append((get_distance(my_coords, film_dict[loc][1]),film_dict[loc][1], film_dict[loc][0][0]))
    return sorted(dist_lst, key = lambda x: x[0])[:5]

def create_map(dist_lst, my_coords):
    """
    """
    film_map = folium.Map(my_coords, zoom_start=3)
    fg = folium.FeatureGroup(name = "Locations")
    for ele in dist_lst:
        fg.add_child(folium.Marker(location=ele[1], popup=folium.Popup(ele[2]), icon=folium.Icon(color='purple')))
    fg.add_child(folium.Marker(location=my_coords, popup=folium.Popup("your location"), icon=folium.Icon(color='red')))
    film_map.add_child(fg)
    film_map.add_child(folium.LayerControl())
    film_map.save('Films.html')
    print("The map is created!")



                



curr_lst = read_file('locator1.list', '2014')[0:5]
test_dict = get_coords_of_films(curr_lst)
my_coords = (37.9735346, -122.5310874)
dist_lst = get_distance_dict(test_dict, my_coords)
create_map(dist_lst, my_coords)