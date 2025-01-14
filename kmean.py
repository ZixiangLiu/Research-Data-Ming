#!/usr/bin/env
# Python 
# Zixiang Liu

import matplotlib.pyplot as plt
import numpy as np
import random
import sys

'''
This program read a output file that each row is a list of number of appearance in one blog
then use k-means to calculate it clusters
'''
num_cluster_default = 4
wordstart_default = 0
wordend_default = 100
same_k_repeat = 1000

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

'''
calculate the distance between two blogs
input:	blog1, blog2: two lists of numbers
output:	distance = sum of square of difference
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
input:	one list of numbers, one blog in this program
output:	normalized list
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
input:	one list of numbers, one blog in this program
output:	normalized list
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
input:	totallist:	list of smaller lists, each smaller list is a blog, containning numbers as frequencies
	debugging:	boolean, set true to print info while running
output: nomalized totallist
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
input:	pivots:		centers of the K-means algorithm
	inputlist:	list of smaller lists, each smaller list is a blog, containning numbers as frequencies
	group:		dictionary, key is pivots index, value is list of inputlist indexes in that cluster
output: sum of distances in each group
'''
def distsumer(pivots, inputlist, group):
	sumofdist = 0
	for key, value in group.items():
		for index in value:
			sumofdist += blog_dist(pivots[key], inputlist[index])
	return sumofdist



'''
calculate the k-means cluster
input:	num_cluster:	number of clusters
	inputlist:	list of smaller lists, each smaller list is a blog, containning numbers as frequencies
	dist:		function to calculate distance between two blogs
	max_iter:	max times of iteration before abortion, default 300
	debugging:	boolean, true to print info while running
output:	group:		dictionary, key is pivots index, value is list of inputlist indexes in that cluster
	pivots:		centers of the K-means algorithm
	num_of_iter:	total number of iteration to get the output
	distsum:	sum of each blog's distance to its corresponding center of the result
'''
def kmean_cal(num_cluster, inputlist, dist, max_iter = 300, debugging = False):
	length = len(inputlist)
	# each pivot is an list
	pivots = [inputlist[i] for i in random.sample(range(len(inputlist)), num_cluster)]
	distsum = 0

	# group is a dictionary of clusters, key pivot index, value is a list of input list index
	group = {}

	# initialize values to lists
	for i in range(0, num_cluster):
		group[i] = []

	old_group = {}
	num_of_iter = max_iter

	for i in range(0, max_iter):
		if debugging:
			print("Iteration No.{}".format(i))
		for k in range(0, length):
			min_dist = sys.maxsize
			min_index = 0
			for j in range(0, num_cluster):
				distance = dist(inputlist[k], pivots[j])
				if distance < min_dist:
					min_dist = distance
					min_index = j
			group[min_index].append(k)
			if debugging:
				print("blog No.{} is in cluster No.{}".format(k, min_index))

		# condition of convergence, if new iteration did not change items in cluster
		if group == old_group:
			num_of_iter = i
			distsum = distsumer(pivots, inputlist, group)
			if debugging:
				print("New iteration did not change cluster, end of iteration\n")
			break;

		old_group = {}

		for k in range(0, num_cluster):
			list_len = len(pivots[0])
			count_matrix = []
			for j in group[k]:
				count_matrix.append(inputlist[j])
			pivots[k] = [sum(np.array(count_matrix)[:, j])/float(len(group[k])) for j in range(0, list_len)]
			# save the current result in a seperate dictionary
			old_group[k] = [j for j in group[k]]
			group[k] = []

		if debugging:
			print("End of iteration No.{}\n\n".format(i))
		distsum = distsumer(pivots, inputlist, group)
	return group, pivots, num_of_iter, distsum

bloglist = tfidfs(tf(bloglist))
output = []
klist = range(1, len(bloglist))
distsumlist = []
for num_cluster in klist:
	outputtemp = []
	outputmin = [0, 0, 0, sys.maxsize]
	for i in range(0,same_k_repeat):
		outputtemp = kmean_cal(num_cluster, bloglist, blog_dist, debugging = False)
		if outputtemp[3] < outputmin[3]:
			outputmin = outputtemp
	distsumlist.append(outputmin[3])

plt.plot(klist, distsumlist)
plt.title("Try to find elbow")
plt.xlabel("k")
plt.ylabel("sum of distance")
plt.show()
# outputdict, pivots, num_of_iter, sumofdist = output
# for key, value in outputdict.items():
# 	print("Cluster No.{} has blog {}".format(key, value))
# print("Went through {} iterations.".format(num_of_iter))

