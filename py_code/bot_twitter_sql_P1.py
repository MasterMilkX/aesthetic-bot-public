##################################### 
##                                 ##
##                                 ##
##    AESTHETIC BOT TWITTER CODE   ##
##                                 ##
##     part 1: post twitter poll   ##
##                                 ##
##                                 ##
##################################### 

# Written by Milk

# general imports
import random
import numpy as np
import math
import os
import subprocess
import time
import sys

# external files
import level_gen_sql
import pair_gen_sql
import pair_EXT_gen_sql
import aesthetic_bot
import twitter_bot
import TPKLDiv
import utils

# global variables

#  -------------------------    SETUP   ------------------------  #

print("***********************    AESTHETIC BOT TWITTER: PART 1    ************************")
print("TWITTER POLL POSTER".center(84))

TILENAMES = ["zelda","pokemon","pacman","amongus","dungeon"]

conf_file = "aesth_config.yaml"
conf = utils.readConfig(conf_file)
if conf['SHOW_CONFIG']:
	print(f"---------- CONFIGURATION FILE: {conf_file} -----------")
	for k,v in conf.items():
		k2 = k+":"
		print(f"* {k2.ljust(40)}{v}")

	print("--------------------------------------------------------------------")


TwitterBot = twitter_bot.TwitterAcc(conf['TWIT_AUTH_FILE'])


# check if in either ext or normal poll
def inPollEither(levelID, levelType):
	return pair_gen_sql.inPoll(levelID, levelType) or pair_EXT_gen_sql.inPoll(levelID, levelType)



#  ------------------    BEGIN THE PIPELINE    ----------------  #

# run indefinitely
while True:

	# 0. randomly select which set type to use based on ratio
	PAIR_TYPE = "hybrid"
	if random.random() > conf['DB_PAIR_RATE']:
		if random.random() > 0.5:
			PAIR_TYPE = "user"
		else:
			PAIR_TYPE = "gen"

	print(f"> USING {PAIR_TYPE} PAIRING MODE!")


	##########       HYBRID USER-GEN PAIRING SETUP      ##########

	if PAIR_TYPE == "hybrid":

		# 1a. get the next user level to be evaluated
		sorted_user_levels = pair_gen_sql.getUnevalLevels("user")

		#check to make sure there's a minimum of levels
		for i in range(len(sorted_user_levels)):
			if sorted_user_levels[i]['EVALS'] > 0:
				last_i = i
				break
		valid_i = 0 if last_i > conf['UNEVAL_USER_MIN'] else last_i
		nextUserLevel = list(filter(lambda x: not inPollEither(x['ID'],"user"), sorted_user_levels))[valid_i]
		userTilename = nextUserLevel["TILESET"]

		# 1b. find matching generated level
		sorted_gen_levels = pair_gen_sql.getUnevalLevels("gen")
		nextGenLevel = list(filter(lambda x: (x['TILESET'] == userTilename) and (not pair_gen_sql.inPoll(x['ID'],"gen")) and (x['EVALS'] == 0), sorted_gen_levels))[-2]


		# 2a. create the pairing
		db_pair = pair_gen_sql.create_pair(nextUserLevel,nextGenLevel)
		realLabel = db_pair['real']
		db_real = db_pair[realLabel]
		db_gen = db_pair[("B" if realLabel == "A" else "A")]

		# 2b. get pairing id to use later
		db_id = pair_gen_sql.getPairID(db_real['ID'],db_gen['ID'])
		print(f"> NEW PAIR CREATED: [ {db_id} ] for the {userTilename} tileset using User level [ {db_real['ID']} ] and Gen level [ {db_gen['ID']} ]")


		# 2c. generate poll img to post on twitter
		im = pair_gen_sql.create_pair_img(db_pair,db_id)
		pairImgFilename = os.path.join(conf['PAIR_IMG_DIR'],f"pair-{userTilename}-{db_id}.png")
		im.save(pairImgFilename, format='png')


		if not conf['DEBUG_MODE']:
			# 3. post the image to twitter and save the poll tweet id to the database for reference
			twitterPollID = TwitterBot.newLevelVotePost(pairImgFilename,int(conf['TWITTER_POLL_MIN']))
			pair_gen_sql.setPairTwitID(db_id,twitterPollID)
			print(f"> PAIR IMAGE CREATED AND POSTED TO TWITTER: {twitterPollID}")


			# 4. run another script with Y hour delay (pass it the poll ID)
			cmd = f"python3 bot_twitter_sql_P2.py {int(conf['TWITTER_POLL_MIN'])*60} {twitterPollID} {db_id}"
			print(f"> Running cmd: '{cmd}'")
			subprocess.Popen(cmd.split(" "))



	##########       USER-USER / GEN-GEN PAIRING SETUP      ##########

	else:

		# 1a. get the next user level to be evaluated
		sorted_levels = pair_gen_sql.getUnevalLevels(PAIR_TYPE)
		validLevels = list(filter(lambda x: not inPollEither(x['ID'],PAIR_TYPE), sorted_levels))
		
		# 1b. get the first level
		levelOne = validLevels[0]
		levelTilename = levelOne["TILESET"]

		# 1c. get the second level based on the first's tileset
		otherValidLevels = list(filter(lambda x: (x['TILESET'] == levelTilename) and (int(x['EVALS']) == 0), validLevels[1:]))
		if len(otherValidLevels) > 0:
			# get the most recently made level if gen, else the next one if user
			level_index = (-2 if PAIR_TYPE == "gen" else 0)
			levelTwo = otherValidLevels[level_index]
		else:
			# get the second made level (even if evaluated)
			otherValidLevels = list(filter(lambda x: (x['TILESET'] == levelTilename), validLevels[1:]))
			levelTwo = otherValidLevels[0]

		# 2a. create the pairing
		db_pair = pair_EXT_gen_sql.create_pair(levelOne,levelTwo, PAIR_TYPE)

		# 2b. get pairing id to use later
		db_id = pair_EXT_gen_sql.getPairID(db_pair['A']['ID'],db_pair['B']['ID'], PAIR_TYPE)
		print(f"> NEW PAIR CREATED: [ {db_id} ] for the {levelTilename} tileset using {PAIR_TYPE} levels [ {db_pair['A']['ID']} ] and [ {db_pair['B']['ID']} ]")


		# 2c. generate poll img to post on twitter
		im = pair_gen_sql.create_pair_img(db_pair,db_id)
		pairImgFilename = os.path.join(conf['PAIR_IMG_DIR'],f"pair-DUO-{levelTilename}-{db_id}.png")
		im.save(pairImgFilename, format='png')


		if not conf['DEBUG_MODE']:
			# 3. post the image to twitter and save the poll tweet id to the database for reference
			twitterPollID = TwitterBot.newLevelVotePost(pairImgFilename,int(conf['TWITTER_POLL_MIN']))
			pair_EXT_gen_sql.setPairTwitID(db_id,twitterPollID)
			print(f"> DUO [ {PAIR_TYPE} ] PAIR IMAGE CREATED AND POSTED TO TWITTER: {twitterPollID}")


			# 4. run another script with Y hour delay (pass it the poll ID)
			cmd = f"python3 bot_twitter_sql_P2.py {int(conf['TWITTER_POLL_MIN'])*60} {twitterPollID} {db_id} DUO-{PAIR_TYPE}"
			print(f"> Running cmd: '{cmd}'")
			subprocess.Popen(cmd.split(" "))










	#delay and repeat, otherwise end the program
	if conf['REPEAT_STEP_1']:
		print(f"**** LOOP COMPLETED -- RUNNING AGAIN IN {conf['STEP_1_FREQ']} MINUTES! ****")
		time.sleep(conf['STEP_1_FREQ']*60)
	else:
		print("**** LOOP COMPLETED ENDING... ****")
		sys.exit(0)
		break



