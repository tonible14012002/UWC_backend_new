import copy
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import MCPSerializer

from mysql import connector as mysql_connector

from account.utils import connect_db
from account.token import auth_required
from .utils import FindOrder, THRESHOLD
# Create your views here.


@api_view(['POST','GET'])
@auth_required
def RouteWithoutID(request):
    # GET all routes with brief info
    if request.method == 'GET':
        try:
            connection = connect_db()
            cursor = connection.cursor(dictionary=True)
            cursor.callproc('RetrieveRoutes', [request.user['id']])
            for temp in cursor.stored_results():
                res = temp.fetchall()
            connection.close()
        except mysql_connector.Error as e:
            return Response({"message": e.msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(res, status=status.HTTP_200_OK)
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
            # get total load from route
            load = cursor.callproc('GetRouteLoad', [route_id, None])
            # update distance
            cursor.callproc('UpdateDistance', (route_id, distance))
            # set result format
            res = {
                'route id': route_id,
                'distance': distance,
                'load': load[1],
                'ordered MCPs': [route_data[index]['MCP_id'] for index in permutation]
            }
            connection.commit()
            connection.close()
            return Response(res, status=status.HTTP_201_CREATED)
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
            cursor = connection.cursor()
            res = cursor.callproc('GetDistance', [id,None])
            distance = res[1]# get distance

            # get total load from route
            load = cursor.callproc('GetRouteLoad', [id,None])

            # get MCPs from route
            cursor = connection.cursor()
            cursor.callproc('RetrieveMCPsFromRoute',(id,))
            for tem in cursor.stored_results():
                mcps = tem.fetchall()
            mcps = [list(item) for item in mcps]

            # format result
            res = {
                'route id': id,
                'distance': distance,
                'total load': load[1],
                'ordered MCPs': sum(mcps, [])
            }
            connection.close()
        except mysql_connector.Error as e:
            return Response({"message": e.msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(res, status=status.HTTP_200_OK)
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
                # get total load from route
                load = cursor.callproc('GetRouteLoad',(id,None))
                # set result format
                res = {
                    'route id': id,
                    'distance': distance,
                    'total load': load[1],
                    'ordered MCPs': [route_data[index]['MCP_id'] for index in permutation]
                }
                connection.commit()
                connection.close()
                return Response(res, status=status.HTTP_201_CREATED)
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
        cursor.callproc('RetrieveMCPsFromRoute',(id,))
        mcps = cursor.fetchall()
        # drop mcps with less than 15% load and update new load
        load = 0 # set new load
        for i in range(len(mcps)-1, -1, -1):
            if mcps[i]['percentage'] < THRESHOLD:
                mcps.pop(i)
                continue
            load += mcps[i]['load'] # update load
        # rearrange the MCPs then return them to UI
        temp_list = copy.deepcopy(mcps)
        permutation, distance = FindOrder(temp_list)  # solve the tsp problem
        # set result format
        res = {
            'route id': id,
            'distance': distance,
            'total load': load,
            'ordered MCPs': [mcps[index]['id'] for index in permutation]
        }
        connection.close()
    except mysql_connector.Error as e:
        return Response({"message": e.msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(res, status=status.HTTP_200_OK)