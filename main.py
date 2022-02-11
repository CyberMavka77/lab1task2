"""
Module for creating map using folium
"""

import argparse
import math
from geopy import Nominatim
import folium

def read_file(path, year):
    """
    function for reading and clearing data from file
    >>> read_file('locator1.list', '2001')[:1]
    [['Broken Sight (2001)', 'Dallas, Texas, USA']]
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
    returns tuple of coordinates of location,
    where film was made using geopy
    >>> get_coords_of_film_loc('Dallas, Texas, USA')
    (32.7762719, -96.7968559)
    """
    geoloc = Nominatim(user_agent='map')
    location = geoloc.geocode(film_addr, timeout=None)

    if not location:
        film_addr_lst = film_addr.split(',')[1:]
        film_addr = ','.join(film_addr_lst)
        location = geoloc.geocode(film_addr, timeout=None)
    if location:
        return location.latitude, location.longitude
    return None

def get_coords_of_films(films_lst):
    """
    returns dictionary of coordinates of every film
    keys are adresses
    this way dictionary is used like a cash
    >>> get_coords_of_films([['Broken Sight (2001)', 'Dallas, Texas, USA']])
    {'Dallas, Texas, USA': [['Broken Sight (2001)'], (32.7762719, -96.7968559)]}
    """
    ret_dict = {}
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
    calculates the distance between two dots on sphere
    >>> get_distance((37.9735346, -122.5310874), (32.7762719, -96.7968559))
    7165.996700646425
    """
    dist = 12734.889 * math.asin(math.sqrt((math.sin((film_coords[0]-my_coords[0])/2)) ** 2
    + math.cos(film_coords[0]) * math.cos(my_coords[0])
    * (math.sin((my_coords[1]-film_coords[1])/2)) ** 2))
    return dist

def get_distance_lst(film_dict, my_coords):
    """
    calculates distance for all the films in dictionary
    >>> get_distance_lst({'Dallas, Texas, USA': [['Broken Sight (2001)'],\
        (32.7762719, -96.7968559)]}, (37.9735346, -122.5310874))
    [(7165.996700646425, (32.7762719, -96.7968559), 'Broken Sight (2001)')]
    """
    dist_lst = []
    for loc in film_dict:
        dist_lst.append((get_distance(my_coords, film_dict[loc][1]),film_dict[loc][1],
        film_dict[loc][0][0]))
    return sorted(dist_lst, key = lambda x: x[0])[:5]

def create_map(dist_lst, my_coords):
    """
    creates html map
    on which the coordinates of 5 nearest films locations
    and user's location is displayed
    """
    film_map = folium.Map(my_coords, zoom_start=3)
    fg_films = folium.FeatureGroup(name = "Film locations")
    fg_me = folium.FeatureGroup(name = "My location")
    for ele in dist_lst:
        fg_films.add_child(folium.Marker(location=ele[1], popup=folium.Popup(ele[2]),
        icon=folium.Icon(color='purple')))
    fg_me.add_child(folium.Marker(location=my_coords, popup=folium.Popup("your location"),
    icon=folium.Icon(color='red')))
    film_map.add_child(fg_films)
    film_map.add_child(fg_me)
    film_map.add_child(folium.LayerControl())
    film_map.save('Films.html')
    print("The map is created!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=str, help="year of film")
    parser.add_argument("lat", type=float, help="latitude")
    parser.add_argument("lon", type=float, help="longitude")
    parser.add_argument("path", type=str, help="path to file")

    args = parser.parse_args()
    year1 = args.year
    my_coords1 = (args.lat, args.lon)
    file_path = args.path

    curr_lst = read_file(file_path, year1)[0:5]
    test_dict = get_coords_of_films(curr_lst)
    dist_lst1 = get_distance_lst(test_dict, my_coords1)
    create_map(dist_lst1, my_coords1)
