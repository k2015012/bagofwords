# Implement bag of words for images. 
import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import sparse_encode
from sklearn.decomposition import MiniBatchDictionaryLearning
from sklearn.neighbors import NearestNeighbors

import os

class BOW:
	sift = cv2.SIFT()
	
	def __init__(self, mypaths, myN=200):
		"""
		paths: a list of image paths
		N: number of codebook clusters, default to be 100
		"""
		self.paths = mypaths
		self.N_codebook = myN
		self.patchSize = 32
		self.gridSpacing = 8

		self.raw_features()
		self.codebook()

	def raw_feature_extract(self, path):
		im = cv2.imread(path)
		if (im==None):
			raise Exception, "Invalid image path %s" %path

		(M, N) = im.shape[:2]

		# Grid sampling
		pointlist=[]
		for i in range(1,M, self.patchSize):
			for j in range(1, N, self.patchSize):
				pointlist.append(cv2.KeyPoint(i,j,1))

		kps, des = self.sift.compute(im, pointlist)
		return des
			
	def raw_features(self):
		raw_features = np.zeros((1,128))
		for path in self.paths:
			des = self.raw_feature_extract(path)
			raw_features = np.append(raw_features, des, axis=0)

		raw_features = np.delete(raw_features, (0), axis=0)
		self.raw_features = raw_features
		print "Raw feature shape: "+str(raw_features.shape)
		# np.savetxt("raw_feature.csv", raw_feature, fmt='%.4f', delimiter=',')

	def codebook(self, showcodebook = False):
		print "Forming codebook through kmean clustering"
		est=KMeans(init='k-means++', n_clusters=self.N_codebook)
		est.fit(self.raw_features)

		self.est=est
		self.codebook=est.cluster_centers_
		print "Codebook shape: "+str(self.codebook.shape)
		# np.savetxt("codebook_kmeans.csv", self.codebook, fmt='%.3f', delimiter=',')
	
	def bow_feature_extract(self, path):
		"""
		BoW feature for a single image
		Simply a histogram, in the new representation
		"""
		des = self.raw_feature_extract(path)
		labels = self.est.predict(des)
		h, edge = np.histogram(labels,bins=np.array(range(self.codebook.shape[0]+1))-0.5,density=True)
		return np.asarray([h])

	def feature(self, paths):
		"""
		path is numpy array
		"""
		out = np.zeros((1,self.N_codebook))
		for path in paths:
			# BoW feature is histogram of raw feature in codebook representation		
			des = self.bow_feature_extract(path)
			out = np.append(out, des, axis=0)
		
		out = np.delete(out, (0), axis=0)
		return out

class BOW_sparsecoding(BOW):

	def codebook(self):
		self.mbdl =  MiniBatchDictionaryLearning(self.N_codebook)
		self.mbdl.fit(self.raw_features)
		

	def bow_feature_extract(self, path):
		des = self.raw_feature_extract(path)
		out = sum(sparse_encode(des, self.mbdl.components_))
		out = np.array([out])
		return out



