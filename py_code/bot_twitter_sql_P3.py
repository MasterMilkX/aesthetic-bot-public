##################################### 
##                                 ##
##                                 ##
##    AESTHETIC BOT TWITTER CODE   ##
##                                 ##
##    part 3: mass pair training   ##
##                                 ##
##                                 ##
##################################### 

# Written by Milk

#general imports
import random
import numpy as np
import math
import os
import sys
from datetime import date

#external files
from level_gen_sql import Tileset
import pair_gen_sql
import pair_EXT_gen_sql
import twitter_bot
import utils
import aesthetic_bot



print("***********************    AESTHETIC BOT TWITTER: PART 3    ************************")
print("MASS PAIR TRAINING".center(84))

# global variables
TILENAMES = ["zelda","pokemon","pacman","amongus","dungeon"]

conf_file = "aesth_config.yaml"
conf = utils.readConfig(conf_file)
if conf['SHOW_CONFIG']:
	print(f"---------- CONFIGURATION FILE: {conf_file} -----------")
	for k,v in conf.items():
		k2 = k+":"
		print(f"* {k2.ljust(40)}{v}")

	print("--------------------------------------------------------------------")


BINARY = (conf['UPDATE_BOT_DIR'][-1] == 'b')
print(f'**  USING [ {("BINARY" if BINARY else "WHOLE")} ] FORMAT FOR TRAINING **')

#  -----------------------    SETUP    ------------------------  #

TILESETS = {}
AESTH_BOT_CNN = {}


# get the tilesets
for t in TILENAMES:
	TILESETS[t] = Tileset(t)

# get the fitness CNN bots (from the updating directory)
for t in TILENAMES:
	botCNN = aesthetic_bot.FitnessCNN(TILESETS[t],("binary" if BINARY else 'whole'))
	botCNN.importModel(conf['UPDATE_BOT_DIR'],t)
	AESTH_BOT_CNN[t] = botCNN



#  ------------------    BEGIN THE TRAINING    ----------------  #


# break up the original pairing datas and concatenate
pair_data_set = utils.getPairTrainData(conf['MIN_VOTE_REQ'],BINARY)

full_tr_maps = {}
full_tr_scores = {}
for TILE in TILENAMES:
	full_tr_maps[TILE] = []
	full_tr_scores[TILE] = []

	map_set = {'real':[],'fake':[]}
	score_set = {'real':[],'fake':[]}
	pair_dat = pair_data_set['maps'][TILE]
	for i in range(len(pair_dat['real'])):  #assume same number of real to fake for both score and maps
		map_set['real'].append(pair_data_set['maps'][TILE]['real'][i])
		map_set['fake'].append(pair_data_set['maps'][TILE]['fake'][i])
		score_set['real'].append(pair_data_set['scores'][TILE]['real'][i])
		score_set['fake'].append(pair_data_set['scores'][TILE]['fake'][i])

		full_tr_maps[TILE].append({'real':map_set['real'][:],'fake':map_set['fake'][:]})
		full_tr_scores[TILE].append({'real':score_set['real'][:],'fake':score_set['fake'][:]})


# show the pairings
if conf['DEBUG_MODE']:
	if not os.path.exists("p3_pair_imgs"):
		os.makedirs("p3_pair_imgs")

	print("> [DEBUG] Displaying training data and associated scores...")

	for TILE in TILENAMES:
		utils.showMultiMaps(full_tr_maps[TILE][-1]['real'],TILE,'REAL',full_tr_scores[TILE][-1]['real'],f"p3_pair_imgs/{TILE}_REAL.png")
		utils.showMultiMaps(full_tr_maps[TILE][-1]['fake'],TILE,'FAKE',full_tr_scores[TILE][-1]['fake'],f"p3_pair_imgs/{TILE}_FAKE.png")

# or train like normal
else:
	# 3a. train on all available sets
	d = conf['UPDATE_BOT_DIR']
	for TILE in TILENAMES:

		tr_map_set = full_tr_maps[TILE]
		tr_score_set = full_tr_scores[TILE]

		#no data, so skip
		if len(tr_score_set) == 0:
			print(f"> NO PAIRS LISTS FOUND FOR [ {TILE} ]....skipping!\n")
			continue

		print(f"> TRAINING ON [ {TILE} ] PAIR SET ({len(tr_score_set)} entries)")

		# 3b. import the model
		updateCNN = aesthetic_bot.FitnessCNN(Tileset(TILE),("binary" if BINARY else 'whole'))
		model_name = updateCNN.getModel(d,TILE)

		# 3c. train on the rating
		for i in range(len(tr_score_set)):
			updateCNN.importModel(d,model_name)
			loss, _ = updateCNN.train(conf['UPDATE_BOT_EPOCH'],tr_map_set[i],tr_score_set[i])
		#print(f"-- final loss: {loss[-1]}\n")

		# 3d. export back (and rename)
		rename_model = f"{TILE}-TWIT_UP-[{date.today().strftime('%b-%d-%y')}]"
		if conf['OVERWRITE_BOT']:
			os.rename(os.path.join(d,model_name),os.path.join(d,rename_model)+".h5")
		updateCNN.exportModel(d,rename_model)



