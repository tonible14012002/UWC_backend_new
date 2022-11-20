import json
import copy
from django.shortcuts import render
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
     MCPSerializer
)
from django.conf import settings
from mysql import connector as mysql_connector

import sys
sys.path.insert(1, 'C:\\Users\WIN\Documents\GitHub\\UWC_backend_new\\uwc\\account\\')

from utils import connect_db
from account.token import JWT_SECRET, JWT_ALGORITHM
from datetime import datetime, timedelta
import jwt
from account.token import auth_required
import requests
import numpy as np
from math import inf
from math import isinf
from python_tsp.heuristics import solve_tsp_local_search
from python_tsp.exact import solve_tsp_dynamic_programming

# Create your views here.

DEPOT = {
    'longtitude': 106.625786,
    'latitude': 10.810676
}
TREATMENT_PLANT = {
    'longtitude': 106.628212,
    'latitude': 10.811756
}
THRESHOLD = 0.15

def MakeDistanceMatrix(data):
    data.insert(0, TREATMENT_PLANT)  # dest
    data.insert(0, DEPOT)  # src

    final_URL = 'http://127.0.0.1:5000/table/v1/driving/'
    for item in data:
        final_URL += str(item['longtitude']) + ',' + str(item['latitude']) + ';'
    final_URL = final_URL.rstrip(';')
    final_URL += '?annotations=distance'
    response = requests.get(final_URL).json() # query api for part of the matrix

    right_corner = np.array(response['distances'])
    # introduce first node as a dummy and extending the distance matrix
    row = np.array([np.append(np.array([0, 0]), np.asarray([inf for _ in range(len(data) - 2)]))])
    col = np.array([np.append(np.array([0]), row)]).T
    dist_matrix = np.c_[col, np.r_[row, right_corner]]
    return dist_matrix
def FindOrder(data):
    # return a permutation array and the total distance
    dist_matrix = MakeDistanceMatrix(data)
    if len(data) <= 10: # exact search when the number of MCPs is small
        permutation, distance = solve_tsp_dynamic_programming(dist_matrix)
    else:
        # local search when the number of MCPs is big
        permutation, distance = solve_tsp_local_search(dist_matrix)
        while isinf(distance): # redo until distance is finite
            permutation, distance = solve_tsp_local_search(dist_matrix)
    # trim the dummy node and return ascending orders of MCPs
    if permutation[1] == 1:
        return np.array(permutation[2:-1])-3, distance
    return np.array(permutation[-2:1:-1])-3, distance
@api_view(['POST','GET'])
@auth_required
def RouteWithoutID(request):
    # GET all routes with brief info
    if request.method == 'GET':
        try:
            connection = connect_db()
            cursor = connection.cursor(dictionary=True)
            cursor.callproc('RetrieveRoutes', [request.user['id']])
            routes = cursor.stored_results()
            connection.close()
        except mysql_connector.Error as e:
            return Response({"message": e.msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(routes, status=status.HTTP_200_OK)
    # POST: Create a new route, return the same route with defined orders of MCPs
    serializer = MCPSerializer(data=request.data, many=True)
    if serializer.is_valid():
        route_data = serializer.data
        try:
            # create a new route, without MCPs
            connection = connect_db()
            cursor = connection.cursor()
            res = cursor.callproc('InsertRoute', (request.user['id'], None))
            route_id = res[0] # return route id
            # rearrange the MCPs then add them to the route
            temp_list = copy.deepcopy(route_data)
            permutation, distance = FindOrder(temp_list) # solve the tsp problem
            for i, j in enumerate(permutation):
                # j is the index in route_data
                cursor.callproc('InsertMCPToRoute',(
                    route_data[j]['MCP_id'],
                    route_id,
                    i #order
                ))
            # update distance
            cursor.callproc('UpdateDistance', (route_id, distance))
            # set result format
            res = {
                'route id': route_id,
                'distance': distance,
                'ordered MCPs': [route_data[index]['MCP_id'] for index in permutation]
            }
            connection.commit()
            connection.close()
            return Response(json.dumps(res), status=status.HTTP_201_CREATED)
        except mysql_connector.Error as e:
            return Response({"message": e.msg}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT','GET','DELETE'])
@auth_required
def RouteWithID(request, id):
    # GET a route layout with its ID
    if request.method == 'GET':
        try:
            connection = connect_db()
            cursor = connection.cursor(dictionary=True)
            distance = cursor.callproc('GetDistance', [id,None])[1] # get distance
            # get MCPs from route
            cursor.execute(f'RetrieveMCPsFromRoute({id})')
            mcps = cursor.fetchall()
            # format result
            res = {
                'route id': id,
                'distance': distance,
                'MCPs': mcps
            }
            connection.close()
        except mysql_connector.Error as e:
            return Response({"message": e.msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(json.dumps(res), status=status.HTTP_200_OK)
    # Update a route with new layout
    elif request.method == 'PUT':
        serializer = MCPSerializer(data=request.data, many=True)
        if serializer.is_valid():
            route_data = serializer.data
            try:
                connection = connect_db()
                cursor = connection.cursor()
                # delete the current layout
                cursor.callproc('DeleteMCPsFromRoute', [id])
                # rearrange the MCPs then add them to the route
                temp_list = copy.deepcopy(route_data)
                permutation, distance = FindOrder(temp_list)  # solve the tsp problem
                for i, j in enumerate(permutation):
                    # j is the index in route_data
                    cursor.callproc('InsertMCPToRoute', (
                        route_data[j]['MCP_id'],
                        id,
                        i  # order
                    ))
                # update distance
                cursor.callproc('UpdateDistance', (id, distance))
                # set result format
                res = {
                    'route id': id,
                    'distance': distance,
                    'ordered MCPs': [route_data[index]['MCP_id'] for index in permutation]
                }
                connection.commit()
                connection.close()
                return Response(json.dumps(res), status=status.HTTP_201_CREATED)
            except mysql_connector.Error as e:
                return Response({"message": e.msg}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # DELETE a route
    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.callproc('DeleteRoute', [id])
        connection.commit()
        connection.close()
        return Response({'detail': 'success'}, status=status.HTTP_200_OK)
    except mysql_connector.Error as e:
        return Response({"message": e.msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['GET'])
@auth_required
def Map(request):
    # Get all MCPs for a single route
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        cursor.callproc('RetrieveMap', [request.user['id']])
        mcps = cursor.stored_results()
        connection.close()
    except mysql_connector.Error as e:
        return Response({"message": e.msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(mcps, status=status.HTTP_200_OK)

@api_view(['GET'])
@auth_required
def RealtimeRoute(request, id):
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        # get MCPs from route
        cursor.execute(f'RetrieveMCPsFromRoute({id})')
        mcps = cursor.fetchall()
        # drop mcps with less than 15% load
        for i in range(len(mcps)-1, -1, -1):
            if mcps[i]['percentage'] < 0.15:
                mcps.pop(i)
        # rearrange the MCPs then return them to UI
        temp_list = copy.deepcopy(mcps)
        permutation, distance = FindOrder(temp_list)  # solve the tsp problem
        # set result format
        res = {
            'route id': id,
            'distance': distance,
            'ordered MCPs': [mcps[index]['MCP_id'] for index in permutation]
        }
        connection.commit()
        connection.close()
    except mysql_connector.Error as e:
        return Response({"message": e.msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(json.dumps(res), status=status.HTTP_200_OK)