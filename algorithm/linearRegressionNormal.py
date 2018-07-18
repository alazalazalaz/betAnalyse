


def main(X, Y):
	'''线性回归-常规方程法:θ = (X转置矩阵 * X)的逆矩阵 * X转置矩阵 * Y 
	X为m*n的矩阵，m表示样本组的数量，n表示每个样本的特征，特征1，特征2...特征n
	Y为m*1的向量，m为每个样本组对应的正确结果，
	octave版本： a = pinv(A'*A)*A'*Y

	DEMO
	# X = np.mat([[1, 0], [1, 1], [1, 2]])
	# Y = np.mat([[1], [2], [3]])
	# a = main(X, Y)
	# print(X)
	# print(Y)
	# print(a)

	# #pridict
	# P = np.mat([[1, 3], [1, 4]])
	# print(P*a)
	'''
	return (X.T * X).I * X.T * Y