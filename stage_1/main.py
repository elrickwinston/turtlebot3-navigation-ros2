#!/usr/bin/env python3
import ast

#set constants
angle_min= -1.57079637051
angle_max= 1.53938043118
angle_incr = 0.0314159281552

'''
TODO: this is simple just return the length of a given list.
'''
def get_length(scan_data):
    return len(scan_data)

'''
TODO: find the index of the closest point in the scan_data
'''
def get_index_of_closest_point(scan_data):
    closest = float('inf')
    index = 0
    for i in range(len(scan_data)):
        if scan_data[i] > 0 and scan_data[i] < closest:
            closest = scan_data[i]
            index = i
    return index


'''
TODO: calculate the angle in rad for the closest point in scan_data
'''
def get_angle_of_closest_point(scan_data):
    index = get_index_of_closest_point(scan_data)
    angle = angle_min + index * angle_incr
    return angle


def get_laserdata(path):
    file = open(path, "r")

    laserdata_raw = file.read()
    laserdata = ast.literal_eval(laserdata_raw)

    return laserdata


if __name__ == "__main__":

    #what is wrong with the print statement below? The print should look like this in your console:
    '''
    ####################
    Python exercise
    ####################
    '''
    print("####################")
    print("Python exercise")
    print("####################")
    import ipdb; ipdb.set_trace()

    #read raw laser data
    scan_data = get_laserdata("laser-testdata_1")

    import ipdb; ipdb.set_trace()

    #print length of scan_data
    print("Length of scan data: {0}".format(get_length(scan_data)))

    #print index of closest point
    print("Index of closest point: {0}".format(get_index_of_closest_point(scan_data)))

    #print angle of closest point
    print("Angle of closest point: {0}".format(get_angle_of_closest_point(scan_data)))

    #print value of closest point
    print("Value of closest point: {0}".format(scan_data[get_index_of_closest_point(scan_data)]))
