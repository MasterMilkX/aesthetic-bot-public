import pair_gen_sql

sorted_user_levels = pair_gen_sql.getUnevalLevels("user")
nextUserLevel = list(filter(lambda x: not pair_gen_sql.inPoll(x['ID'],"user"), sorted_user_levels))[0]
print(nextUserLevel)