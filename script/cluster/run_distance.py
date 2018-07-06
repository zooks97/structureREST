import numpy as np, os
from distance import average_distance_matrix
soaps = np.loadtxt('pca_average_soap.dat') #[]

def average_distance(average_soap1, average_soap2):
    '''
    Calculate distance between to averaged SOAP vectors
    using the average distance kernel from De et al. (2016)
    Args:
        average_soap1 (numpy.ndarray): numpy array of average SOAP vector 1
        average_soap2 (numpy.ndarray): numpy array of average SOAP vector 2
    Returns:
        float: normalized distance between average_soap1 and average_soap2
    '''
    k11 = np.linalg.norm(average_soap1)
    k22 = np.linalg.norm(average_soap2)
    k12 = np.dot(average_soap1, average_soap2)
    d12 = np.sqrt(2 - 2 * (k12 / np.sqrt(k11 * k22)))
    return d12

def average_distance_matrix_p(vectors):
    '''
    Generate distance matrix for a set average SOAP vectors
        using the average distance kernel
    '''
    distance_matrix = np.zeros((len(vectors), len(vectors)))
    for i, v1 in enumerate(vectors):
        for j, v2 in enumerate(vectors[i+1:], start=i+1):
            distance_matrix[i,j] = average_distance(v1, v2)
    return distance_matrix



#~ print soaps.shape
filename = 'distances.dat'
if os.path.exists(filename):
    os.remove(filename)
average_distance_matrix(soaps, filename, "({}(F8.6, ' '))".format(len(soaps)))
#~ 
#~ 
#~ average_distance_matrix_p(soaps)

