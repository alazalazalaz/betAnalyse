

oddsWin = 1.01
oddsLose = 9
userWin = 1111
userLose = 100
bet = 1
totalBet = (userWin + userLose) * bet
print("total bet " + str(totalBet))

result1 = totalBet - userWin * oddsWin
result2 = totalBet - userLose * oddsLose

print('if win 需要赔付：' + str(userWin * oddsWin) )
print("庄家收益：" + str(result1))
print('if lose 需要赔付：' + str(userLose * oddsLose) )
print("庄家收益：" + str(result2))