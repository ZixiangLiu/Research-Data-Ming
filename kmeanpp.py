#!/usr/bin/env
# Python 
# Zixiang Liu

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np
import random
import sys
import time

'''
This program read a output file that each row is a list of number of appearance in one blog
then use k-means to calculate it clusters
'''
num_cluster_default = 4
wordstart_default = 0
wordend_default = 9500
same_k_repeat = 1

# print("Press Enter to select default.")
# num_cluster = input("Please enter K(default {}):".format(num_cluster_default)) or num_cluster_default
# wordstart = input("Please enter word start index(default {}):".format(wordstart_default)) or wordstart_default
# wordend = input("Please enter word end index(default {}):".format(wordend_default)) or wordend_default
# filename = input("\nDefault file output.txt\nPress Enter to select default file.\nEnter the file name: ") or "output.txt"

num_cluster = num_cluster_default
wordstart = wordstart_default
wordend = wordend_default
filename = "output.txt"

inputfile = open(filename, "r")
wordlist = []
bloglist = []
with inputfile as filestream:
	first = True
	for line in filestream:
		linelist = line.split();
		if first:
			for word in linelist:
				wordlist.append(word)
			first = False
		else:
			blog = []
			for count in linelist[wordstart:wordend]:
				blog.append(float(count))
			bloglist.append(blog)

# print(len(wordlist))
# print(len(bloglist[0]))

'''
calculate the distance between two blogs
'''
def blog_dist(blog1, blog2):
	if len(blog1) != len(blog2):
		return None;
	distance = 0
	for i in range(0, len(blog1)):
		distance += (blog1[i] - blog2[i])**2
	return distance


'''
Term frequency:
augmented frequency
'''
def tf(somelist):
	for onelist in somelist:
		maxf = max(onelist)
		if maxf != 0:
			for i in range(0, len(onelist)):
				onelist[i] = 0.5 + 0.5 * onelist[i] / maxf
		else:
			break;
	return somelist


'''
tf–idf
tf * idf
Inverse document frequency:
inverse document frequency smooth
use tfidfs(tf(somelist)) to work
'''
def tfidfs(somelist):
	N = len(somelist)
	somelist = np.array(somelist)
	for i in range(0, len(somelist[0])):
		# start with 1 to make it smooth and none zero
		nt = 1
		for j in range(0, N):
			if somelist[:,i][j] != 0.5:
				nt += 1
		idfs = np.log(N/nt)
		for j in range(0, N):
			somelist[:,i][j] += idfs
	return somelist

'''
normalize data
(i-u)/std
'''
def normalizer(totallist, debugging = False):
	totallength = len(totallist[0])
	if debugging:
		print("start normaling")
	for i in range(0, totallength):
		if debugging:
			print("normalizing column No.{}".format(i))
		listavg = sum(np.array(totallist)[:,i])/float(totallength)
		liststd = np.std(np.array(totallist)[:,i], dtype=np.float64)
		for k in range(0, len(totallist)):
			totallist[k][i] = (totallist[k][i]-listavg)/liststd
	return totallist

'''
Sum of distance to pivot centers
'''
def distsumer(pivots, inputlist, clusters):
	sumofdist = 0
	for key, value in clusters.items():
		for index in value:
			sumofdist += blog_dist(pivots[key], inputlist[index])
	return sumofdist

'''
mindist
find a point with max distance to pivots
'''
def maxdist(inputlist, pivots, dist):
	totalmax = 0
	index = 0
	for i in range(0, len(inputlist)):
		distancemax = 0
		for j in pivots:
			onedist = dist(inputlist[i], j) 
			if onedist > distancemax:
				distancemax = onedist
		if distancemax > totalmax:
			totalmax = distancemax
			index = i
	# print(index)
	return inputlist[index]

'''
centers
'''
def centers(inputlist, num_cluster, dist):
	pivots=[]
	pivots.append(inputlist[random.randint(0, num_cluster-1)])
	# if num_cluster >= 3:
	# 	print(num_cluster, "start with", pivots)
	for i in range(0, num_cluster-1):
		pivots.append(maxdist(inputlist, pivots, dist))
	# if num_cluster >= 3:
	# 	print("End with",pivots)
	return pivots

'''
'''
def init_cluster(num_cluster):
	clusters = {}
	# initialize values to lists
	for i in range(0, num_cluster):
		clusters[i] = []
	return clusters

'''
calculate the k-means cluster
using k means ++
'''
def kmeanpp_cal(num_cluster, inputlist, dist, max_iter = 300, debugging = False):
	length = len(inputlist)
	# each pivot is an list
	start = time.time()
	pivots = centers(inputlist, num_cluster, dist)
	centert = time.time()-start
	distsum = 0

	# clusters is a dictionary of clusters, key pivot index, value is a list of input list index
	clusters = init_cluster(num_cluster)

	old_clusters = {}
	num_of_iter = max_iter
	start = time.time()
	for i in range(0, max_iter):
		# if debugging:
		# 	print("Iteration No.{}".format(i))
		for k in range(0, length):
			min_dist = sys.maxsize
			min_index = 0
			for j in range(0, num_cluster):
				distance = dist(inputlist[k], pivots[j])
				if distance < min_dist:
					min_dist = distance
					min_index = j
			clusters[min_index].append(k)
			# if debugging:
			# 	print("blog No.{} is in cluster No.{}".format(k, min_index))

		# condition of convergence, if new iteration did not change items in cluster
		if clusters == old_clusters:
			num_of_iter = i
			distsum = distsumer(pivots, inputlist, clusters)
			# if debugging:
			# 	print("k=",num_cluster, "iter No.", i, "does not change cluster, end of iteration\n")
			break;

		for k in range(0, num_cluster):
			list_len = len(pivots[0])
			count_matrix = []
			for j in clusters[k]:
				count_matrix.append(inputlist[j])
			# if debugging:
			# 	print("k=",num_cluster, "iter No.", i, "cluster No.", k, "has member", len(count_matrix))
			# unless the cluster is empty
			if clusters[k]:
				pivots[k] = [sum(np.array(count_matrix)[:, j])/float(len(clusters[k])) for j in range(0, list_len)]
			# save the current result in a seperate dictionary
			old_clusters[k] = [j for j in clusters[k]]
			clusters[k] = []

		# if debugging:
		# 	print("End of iteration No.{}\n\n".format(i))
		distsum = distsumer(pivots, inputlist, clusters)
	calt = time.time()-start
	return clusters, pivots, num_of_iter, distsum, centert, calt

'''
Not using k means ++
'''
def kmean_cal(num_cluster, inputlist, dist, max_iter = 300, debugging = False):
	length = len(inputlist)
	# each pivot is an list
	start = time.time()
	pivots = [inputlist[i] for i in random.sample(range(0, length), num_cluster)]
	distsum = 0

	# clusters is a dictionary of clusters, key pivot index, value is a list of input list index
	clusters = init_cluster(num_cluster)

	old_clusters = {}
	num_of_iter = max_iter
	
	for i in range(0, max_iter):
		# if debugging:
		# 	print("Iteration No.{}".format(i))
		for k in range(0, length):
			min_dist = sys.maxsize
			min_index = 0
			for j in range(0, num_cluster):
				distance = dist(inputlist[k], pivots[j])
				if distance < min_dist:
					min_dist = distance
					min_index = j
			clusters[min_index].append(k)
			# if debugging:
			# 	print("blog No.{} is in cluster No.{}".format(k, min_index))

		# condition of convergence, if new iteration did not change items in cluster
		if clusters == old_clusters:
			num_of_iter = i
			distsum = distsumer(pivots, inputlist, clusters)
			# if debugging:
			# 	print("k=",num_cluster, "iter No.", i, "does not change cluster, end of iteration\n")
			break;

		for k in range(0, num_cluster):
			list_len = len(pivots[0])
			count_matrix = []
			for j in clusters[k]:
				count_matrix.append(inputlist[j])
			# if debugging:
			# 	print("k=",num_cluster, "iter No.", i, "cluster No.", k, "has member", len(count_matrix))
			# unless the cluster is empty
			if clusters[k]:
				pivots[k] = [sum(np.array(count_matrix)[:, j])/float(len(clusters[k])) for j in range(0, list_len)]
			# save the current result in a seperate dictionary
			old_clusters[k] = [j for j in clusters[k]]
			clusters[k] = []

		# if debugging:
		# 	print("End of iteration No.{}\n\n".format(i))
		distsum = distsumer(pivots, inputlist, clusters)
	calt = time.time()-start
	return clusters, pivots, num_of_iter, distsum, calt

bloglist = tfidfs(tf(bloglist))

output = []
klist = range(1, len(bloglist)+1)
myt = []
distsumlist = []
kppiter = []
kiter = []
centt = []
calt = []
kmeant = []
for num_cluster in klist:
	start = time.time()
	outputtemp = []
	outputmin = [0, 0, 0, sys.maxsize]
	for i in range(0,same_k_repeat): 
		outputtemp = kmeanpp_cal(num_cluster, bloglist, blog_dist, debugging = False)
		centt.append(outputtemp[4])
		calt.append(outputtemp[5])
		kppiter.append(outputtemp[2])
		if outputtemp[3] < outputmin[3]:
			outputmin = outputtemp

		outputtemp = kmean_cal(num_cluster, bloglist, blog_dist, debugging = False)
		kmeant.append(outputtemp[4])
		kiter.append(outputtemp[2])
		if outputtemp[3] < outputmin[3]:
			outputmin = outputtemp
			
	distsumlist.append(outputmin[3])
	myt.append(time.time()-start)

outputfile= open("time_word{}_repeat{}_iterate.txt".format(wordend-wordstart, same_k_repeat), "w")
for i in [j-1 for j in klist]:
	outputfile.write("{:10} {:10.5f}\n".format(i, myt[i]))
for i in range(0, len(centt)):
	outputfile.write("{:10.5f} {:10.5f} {:10.5f} {:10.5f} {:10.5f} {:10.5f}\n".format(centt[i], calt[i], centt[i]+calt[i], kmeant[i], kppiter[i], kiter[i]))
outputfile.close()



