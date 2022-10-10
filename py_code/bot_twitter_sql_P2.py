##################################### 
##                                 ##
##                                 ##
##    AESTHETIC BOT TWITTER CODE   ##
##                                 ##
##  part 2: follow up twitter post ##
##                                 ##
##                                 ##
##################################### 

# Written by Milk

#general imports
import random
import numpy as np
import math
import os
import time
import sys
from datetime import date

#external files
from level_gen_sql import Tileset
import pair_gen_sql
import pair_EXT_gen_sql
import twitter_bot
import utils
import aesthetic_bot

print("***********************    AESTHETIC BOT TWITTER: PART 2    ************************")
print("FOLLOW UP TWITTER POST".center(84))

conf_file = "aesth_config.yaml"
conf = utils.readConfig(conf_file)
#don't need to print it again lol


#  -----------------------    SETUP    ------------------------  #


#system command arguments
TIMEOUT = int(sys.argv[1])      #time poll is live in seconds
TWIT_POLL_ID = sys.argv[2]      #Twitter id of the poll post
DB_PAIR_ID = int(sys.argv[3])   #DB id of the pair

# get the duo option if available
if len(sys.argv) > 4:
	DUO_TYPE = sys.argv[4].split("-")[1]
else:
	DUO_TYPE = None



#  ------------------    BEGIN THE PIPELINE    ----------------  #


# 0. passed the information from bot_twitter_sql_P1.py (poll ID, db pair ID, timeout)
#    once poll has finished after Y hours/minutes, continue
time.sleep(TIMEOUT+10)



##########       HYBRID USER-GEN PAIRING SETUP      ##########

if not DUO_TYPE:

	# grab the level ids from the pair
	pair_id_set = pair_gen_sql.getPairLevelIDs(DB_PAIR_ID)
	USER_LEVEL_ID = pair_id_set['user']
	GEN_LEVEL_ID = pair_id_set['gen']

	TwitterBot = twitter_bot.TwitterAcc(conf['TWIT_AUTH_FILE'])


	print(f"> [ {DB_PAIR_ID} - ({TWIT_POLL_ID}) ] POLL OVER! Retrieving results")


	# 1a. save votes from A and B to database for Pair ID
	vote_set = TwitterBot.getVotes(TWIT_POLL_ID)
	print(vote_set)

	#assume the only choices were A and B
	a_votes = int(vote_set['A'])
	b_votes = int(vote_set['B'])

	pair_gen_sql.setPairTwitVotes(DB_PAIR_ID,a_votes,b_votes)

	# 1b. increment eval count for each item
	pair_gen_sql.incEvalLevels("user",USER_LEVEL_ID)
	pair_gen_sql.incEvalLevels("gen",GEN_LEVEL_ID)

	print(f"> UPDATED user_levels [ {USER_LEVEL_ID} ] and gen_levels [ {GEN_LEVEL_ID} ]")


	# 2. post the end tweet with the real map label, author, and level editor link
	realLabel = pair_gen_sql.getPairRealLabel(DB_PAIR_ID)
	author = pair_gen_sql.getUserLevelAuthor(USER_LEVEL_ID)
	TwitterBot.newAnswerPost(TWIT_POLL_ID,realLabel,conf['EDITOR_LINK'],(None if author == '' else author))



##########       USER-USER / GEN-GEN PAIRING SETUP      ##########

else:

	# grab the level ids from the pair
	pair_id_set = pair_EXT_gen_sql.getPairLevelIDs(DB_PAIR_ID)
	LEVEL_A = pair_id_set['A']
	LEVEL_B = pair_id_set['B']

	TwitterBot = twitter_bot.TwitterAcc(conf['TWIT_AUTH_FILE'])


	print(f"> DUO {DUO_TYPE} [ {DB_PAIR_ID} - ({TWIT_POLL_ID}) ] POLL OVER! Retrieving results")


	# 1a. save votes from A and B to database for Pair ID
	vote_set = TwitterBot.getVotes(TWIT_POLL_ID)
	print(vote_set)

	#assume the only choices were A and B
	a_votes = int(vote_set['A'])
	b_votes = int(vote_set['B'])

	pair_EXT_gen_sql.setPairTwitVotes(DB_PAIR_ID,a_votes,b_votes)

	# 1b. increment eval count for each item
	pair_gen_sql.incEvalLevels(DUO_TYPE,LEVEL_A)
	pair_gen_sql.incEvalLevels(DUO_TYPE,LEVEL_B)

	print(f"> UPDATED {DUO_TYPE} LEVELS [ {LEVEL_A} ] and [ {LEVEL_B} ]")


	# 2. post the end tweet with the author (if user duo) and level editor link
	# 2 user levels
	if DUO_TYPE == "user":
		authorA = pair_gen_sql.getUserLevelAuthor(LEVEL_A)
		authorB = pair_gen_sql.getUserLevelAuthor(LEVEL_B)
		TwitterBot.newDuoAnswerPost(TWIT_POLL_ID,conf['EDITOR_LINK'],[authorA,authorB])

	# 2 generated levels
	else:
		TwitterBot.newDuoAnswerPost(TWIT_POLL_ID,conf['EDITOR_LINK'],None)
	




# 3. (optional) train aesthetic bot NN on vote difference + maps from database info
if conf['TRAIN_AFTER_POLL']:
	print("> TRAINING AESTHETIC CNN BOT ON NEW PAIRING RESULT")
	d = conf['UPDATE_BOT_DIR']

	BINARY = (conf['UPDATE_BOT_DIR'][-1] == 'b')
	print(f'**  USING [ {("BINARY" if BINARY else "WHOLE")} ] FORMAT FOR TRAINING **')

	# # 3a. get score/vote data from the pair
	if DUO_TYPE:
		pair_data = pair_EXT_gen_sql.pair2Rating(DB_PAIR_ID)
	
	else:
		pair_data = pair_gen_sql.pair2Rating(DB_PAIR_ID)

	# # whole Y value input
	# if not BINARY:
	# 	real_score = pair_data['real']['votes']-pair_data['fake']['votes']
	# 	fake_score = pair_data['fake']['votes']-pair_data['real']['votes']
	# # binary Y value input
	# else:
	# 	total = abs(pair_data['real']['votes']) + abs(pair_data['fake']['votes'])
	# 	real_score = pair_data['real']['votes'] / total
	# 	fake_score = pair_data['fake']['votes'] / total


	# print(f"real votes: {pair_data['real']['votes']} | fake votes: {pair_data['fake']['votes']}")
	# print(f"real score: {real_score} | fake score: {fake_score}")

	# train on entire set of submitted pair data for the tileset
	full_pair_dat = utils.getTilePairTrainData(pair_data['tileset'],conf['MIN_VOTE_REQ'],BINARY)

	# 3b. import the model
	updateCNN = aesthetic_bot.FitnessCNN(Tileset(pair_data['tileset']),("binary" if BINARY else 'whole'))
	model_name = updateCNN.getModel(d,pair_data['tileset'])
	updateCNN.importModel(d,model_name)

	# 3c. train on the rating
	# tr_maps = {'real':[pair_data['real']['level']], 'fake':[pair_data['fake']['level']]}
	# tr_scores = {'real':[real_score],'fake':[fake_score]}
	tr_maps = full_pair_dat['maps']
	tr_scores = full_pair_dat['scores']
	updateCNN.train(conf['UPDATE_BOT_EPOCH'],tr_maps,tr_scores)

	# 3d. export back (and rename)
	rename_model = f"{pair_data['tileset']}-TWIT_UP-[{date.today().strftime('%b-%d-%y')}]"
	if conf['OVERWRITE_BOT']:
		os.rename(os.path.join(d,model_name),os.path.join(d,rename_model)+".h5")
	updateCNN.exportModel(d,rename_model)

	print(f"> FINISHED UPDATING BOT! - SAVED TO: {rename_model}")

sys.exit(0)

