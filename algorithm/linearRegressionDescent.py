import numpy as np


def batchGradientDescent(iterateNum, x ,y , theta, alpha = 0.01): 
	''' 线性回归梯度下降算法
		iterateNum 迭代的次数
		x 		二维数组
		y 		一维数组
		theta 	theta初始值，特征个数，一维数组，可以是单位向量，比如[1, 1, 1]
		alpha	步长，默认0.01
		return 	返回一维数组theta的值
		******************************** D E M O ********************************
		iterateNum = 10000
		x_data = np.array([[1, 2], [3, 4], [5, 6]])
		y_data = np.array([3, 7, 11])
		theta  = np.ones(2)#因为x有两个特征 [1. 1.]
		alpha  = 0.01
		batchGradientDescent(iterateNum, x_data, y_data, theta, alpha)
		******************************** D E M O ********************************
	'''
	xTrains = x.transpose()  
	for i in range(0, iterateNum):  
		hypothesis = np.dot(x,theta) #假设函数，hypothesis

		loss = (hypothesis - y)  #代价函数，cost func
		theta = theta - (alpha / iterateNum) * np.dot(xTrains,loss)
		cost = 1.0/2 * iterateNum * np.sum(np.square(np.dot(x,np.transpose(theta))-y))  
		# print("cost: %f"%cost) 

	return theta 



def main(iterateNum, xy, alpha = 0.01):
	'''线性回归-梯度下降算法
		******************************** D E M O ********************************
		iterateNum = 10000
		xy = np.array([[1, 2, 3], [3, 4, 7], [5, 6, 11]])#xy数组中最后一列表示y的值
		alpha  = 0.01
		batchGradientDescent(iterateNum, x_data, y_data, theta, alpha)
		******************************** D E M O ********************************
	'''
	m, n = np.shape(xy)
	if m <= 0 or n <= 1:
		return False

	x = xy[:, :-1]
	y = xy[:, -1]
	theta = np.ones(n-1)

	return batchGradientDescent(iterateNum, x, y, theta, alpha)





