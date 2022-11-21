from mysql import connector as mysql_connector
import folium
import polyline
import requests
import webbrowser
import numpy as np
from math import inf
from math import radians, cos, sin, asin, sqrt
from python_tsp.heuristics import solve_tsp_local_search
from python_tsp.exact import solve_tsp_dynamic_programming
from python_tsp.heuristics import solve_tsp_simulated_annealing
from math import isinf
# Test here
#settings.configure()
connection = mysql_connector.connect(
    host="localhost",
    user="root",
    password="12012002Duy",
    database="uwc_2.0"
)
cursor = connection.cursor(dictionary=True)
cursor.callproc('RetrieveMCPsFromRoute', [2])
for resu in cursor.stored_results():
    print(resu.fetchmany(3))



# Create your views here.
depot = {
    'longtitude': 106.625786,
    'latitude': 10.810676
}
treatment_plant = {
    'longtitude': 106.628212,
    'latitude': 10.811756
}
MCP1 = {
    'latitude': 10.773045,
    'longtitude': 106.657501
}

MCP2 = {
    'latitude': 10.786654,
    'longtitude': 106.653745
}

MCP3 = {
    'latitude': 10.780086,
    'longtitude': 106.658821
}

MCP4 = {
    'latitude': 10.775828,
    'longtitude': 106.663421
}

MCP5 = {
    'latitude': 10.764715,
    'longtitude': 106.659960
}

MCP6 = {
    'latitude': 10.770870,
    'longtitude': 106.653347
}

MCP7 = {
    'latitude': 10.778742,
    'longtitude': 106.662589
}

MCP8 = {
    'latitude': 10.776935,
    'longtitude': 106.666257
}

MCP9 = {
    'latitude': 10.782816,
    'longtitude': 106.663459
}

MCP10 = {
    'latitude': 10.784208,
    'longtitude': 106.669609
}

MCP11 = {
    'latitude': 10.786800,
    'longtitude': 106.664690
}

MCP12 = {
    'latitude': 10.783208,
    'longtitude': 106.657961
}

URL = 'http://127.0.0.1:5000/route/v1/driving/'
URL2 = 'http://127.0.0.1:5000/table/v1/driving/'
def dist(x, y):
    # x, y are locations dictionary, containing long- and lat- titude
    response = requests.get(URL+str(x['longtitude'])+','+str(x['latitude'])
                      +';'+str(y['longtitude'])+','+str(y['latitude'])).json()
    return response['routes'][0]['distance']
def GetDistanceMatrix (data):
    final_URL = URL2
    for item in data:
        final_URL += str(item['longtitude'])+','+str(item['latitude'])+';'
    final_URL = final_URL.rstrip(';')
    final_URL += '?annotations=distance'
    response = requests.get(final_URL).json()
    return np.array(response['distances'])
def haversine(x, y):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [x['longtitude'], x['latitude'], y['longtitude'], y['latitude']])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r
def MakeDistanceMatrix(data):
    data.insert(0, treatment_plant)
    data.insert(0, depot)

    right_corner = GetDistanceMatrix(data)
    row = np.array([np.append(np.array([0, 0]), np.asarray([inf for _ in range(len(data) - 2)]))])
    col = np.array([np.append(np.array([0]), row)]).T
    dist_matrix = np.c_[col, np.r_[row, right_corner]]
    return dist_matrix
def FindOrder(data):
    # return a permutation array and the total distance
    dist_matrix = MakeDistanceMatrix(data)
    if len(data) <= 10: # the number of MCPs is small
        return solve_tsp_dynamic_programming(dist_matrix)
    # local search when the number is big
    permutation, distance = solve_tsp_local_search(dist_matrix)
    while isinf(distance):
        permutation, distance = solve_tsp_local_search(dist_matrix)
    return permutation, distance

data_list = [MCP1, MCP2, MCP3, MCP4, MCP5, MCP6, MCP7, MCP8, MCP9]
#print(FindOrder(data_list))
#print(haversine(MCP1, MCP5))



#print(MakeDistanceMatrix(data_list))
def get_route(x, y):
    loc = "{},{};{},{}".format(x['longtitude'], x['latitude'], y['longtitude'], y['latitude'])
    url = "http://router.project-osrm.org/route/v1/driving/"
    r = requests.get(url + loc)
    if r.status_code != 200:
        return {}

    res = r.json()
    routes = polyline.decode(res['routes'][0]['geometry'])
    start_point = [res['waypoints'][0]['location'][1], res['waypoints'][0]['location'][0]]
    end_point = [res['waypoints'][1]['location'][1], res['waypoints'][1]['location'][0]]
    distance = res['routes'][0]['distance']

    out = {'route': routes,
           'start_point': start_point,
           'end_point': end_point,
           'distance': distance
           }

    return out

def get_map(route):
    m = folium.Map(location=[(route['start_point'][0] + route['end_point'][0]) / 2,
                             (route['start_point'][1] + route['end_point'][1]) / 2],
                   zoom_start=13)

    folium.PolyLine(
        route['route'],
        weight=8,
        color='blue',
        opacity=0.6
    ).add_to(m)

    folium.Marker(
        location=route['start_point'],
        icon=folium.Icon(icon='play', color='green')
    ).add_to(m)

    folium.Marker(
        location=route['end_point'],
        icon=folium.Icon(icon='stop', color='red')
    ).add_to(m)
    m.save("map.html")
    webbrowser.open("map.html")
    return m

test_route = get_route(MCP1, MCP2)
#print(test_route)
#get_map(test_route)

corner = np.array([[ 0.,    293.2, 6507.5, 5195.9, 6133.2, 6945.5, 7436.9],
                   [ 293.2, 0.   , 6413.9, 5102.2, 6039.5, 6851.9, 7343.3],
                   [7046.8, 7210.9 ,   0.,  1568.2,  931.1, 1642.4, 1669.6],
                   [5478.6 ,5642.7, 1855.7,    0.,  1481.3, 2293.7, 2785.1],
                   [6975.6, 7139.7 ,1331.6, 1496.9,    0.,   812.3, 2261. ],
                   [7675.3, 7839.4, 1137.1, 2196.7, 1048.3,    0.,  1713.4],
                   [8011.5, 8175.6 , 964.7, 2532.9, 1895.7, 1494.1 ,   0. ]])
row = np.array([[ 0.,  0., inf, inf, inf, inf, inf]])
col = np.array([[ 0., 0.,  0., inf, inf, inf, inf, inf]]).T
dist_matrix = np.c_[col, np.r_[row, corner]]

array = np.array([12,32,434,11,6,7,230])
#print(array[-2:1:-1] - 3)
