##################################### 
##                                 ##
##                                 ##
##    AESTHETIC BOT TWITTER CODE   ##
##                                 ##
##     part 0: generate levels     ##
##                                 ##
##                                 ##
##################################### 

# Written by Milk

# general imports
import random
import numpy as np
import math
import os
import time
import sys

# external files
import level_gen_sql
import aesthetic_bot
import TPKLDiv
import utils

# global variables
TILENAMES = ["zelda","pokemon","pacman","amongus","dungeon"]

print("***********************    AESTHETIC BOT TWITTER: PART 0    ************************")
print("BACKEND LEVEL GENERATOR".center(84))

conf_file = "aesth_config.yaml"
conf = utils.readConfig(conf_file)
if conf['SHOW_CONFIG']:
	print(f"---------- CONFIGURATION FILE: {conf_file} -----------")
	for k,v in conf.items():
		k2 = k+":"
		print(f"* {k2.ljust(40)}{v}")

	print("--------------------------------------------------------------------")


BINARY = (conf['AESTHETIC_BOT_DIR'][-1] == 'b')
print(f'**  USING [ {("BINARY" if BINARY else "WHOLE")} ] FORMAT FOR EVALUATION **')


#  -----------------------    SETUP    ------------------------  #

TILESETS = {}
AESTH_BOT_CNN = {}
TILE_PATTERNS = {}
TILE_PATT_DICT = {}

# get the tilesets
for t in TILENAMES:
	TILESETS[t] = level_gen_sql.Tileset(t)

# get the fitness CNN bots
for t in TILENAMES:
	botCNN = aesthetic_bot.FitnessCNN(TILESETS[t],("binary" if BINARY else 'whole'))
	botCNN.importModel(conf['AESTHETIC_BOT_DIR'],t)
	AESTH_BOT_CNN[t] = botCNN

# get the tile patterns (array and dict)
for t in TILENAMES:
	all_user_levels = utils.getAscUserLevels(t)
	TILE_PATT_DICT[t] = TPKLDiv.getTPProb(all_user_levels)
	if conf['EVO_RANK_TP_SEL']:
		TILE_PATTERNS[t] = TPKLDiv.getPatternList2dSorted(all_user_levels)
	else:
		TILE_PATTERNS[t] = TPKLDiv.getPatternList2d(all_user_levels)


#  ------------------    BEGIN THE PIPELINE    ----------------  #


while True:

	# 1a. make a new level for each tileset by evolving it and evaluating it
	for curTilename in TILENAMES:
		print(f"> GENERATING [ {curTilename} ] MAPS...")
		curTileset = TILESETS[curTilename]
		tilesetPatterns = TILE_PATTERNS[curTilename]

		# 1b. Get the best generated map and export it
		bestGenLevels = []
		bestFit = []
		for trialNo in range(conf['EVO_TRIALS']):
			AesthBot = AESTH_BOT_CNN[curTilename]
			EvoBot = aesthetic_bot.StraightBotTP(curTileset,conf['EVO_POPSIZE'],conf['EVO_MUTATION_RATE'],tilesetPatterns,mu=conf['EVO_MU'],exprate=conf['EVO_DIM_RATE'],rank_tp_sel=conf['EVO_RANK_TP_SEL'])
			EvoBot.user_fun = AesthBot.eval_map_population

			#toggle exporting to a gif
			exportGif = False
			gifconf = None
			if conf['EVO_GIF']:  #assume all other variables are included as well
				exportGif = True
				gif_iter = conf['GIF_ITER']
				gif_fps = conf['GIF_FPS']
				gif_dir = conf['GIF_DIR']
				if not os.path.exists(gif_dir):
					os.mkdir(gif_dir)
				gifconf = {'name':os.path.join(gif_dir,f'{curTilename}_{trialNo}.gif'),'iter_off':gif_iter,'fps':gif_fps}


			#evolve for X iterations
			EvoBot.train(conf['EVO_ITERATIONS'],showPop=exportGif,showSett=gifconf)

			#continue training if fitness still negative and able to improve
			iter_ct = 0
			while (EvoBot.high_pop_fit() <= (0.5 if BINARY else 0)) and iter_ct < 10:
				EvoBot.train(100,False)
				iter_ct+=1

			#save the best map from the population
			best_map = EvoBot.best_map()
			bestGenLevels.append(best_map)
			bestFit.append(EvoBot.high_pop_fit())


		# final selection
		best_index = 0
		if conf['EVO_FINAL_SEL'] == "evo_fitness":	
			best_index = np.argmax(bestFit)         # highest fitness
		elif conf['EVO_FINAL_SEL'] == "entropy":
			best_index = np.argmax([bestFit[i]*utils.entropy(bestGenLevels[i]) for i in range(len(bestGenLevels))])  #entropy
		elif conf['EVO_FINAL_SEL'] == "pseudo_twitter":
			best_index = np.argmax([utils.twitterFit(m,TILE_PATT_DICT[curTilename],SAMP_WEIGHT=0.7,TWIT_OFFSET=7) for m in bestGenLevels])      #evaluate by twitter surrogate
		elif conf['EVO_FINAL_SEL'] == 'twit_entropy':
			best_index = np.argmax([utils.twitterFit(m,TILE_PATT_DICT[curTilename],SAMP_WEIGHT=0.7,TWIT_OFFSET=7)*utils.entropy(m) for m in bestGenLevels])
		genLevel = bestGenLevels[best_index]

		# 1c. add the generated level to the database
		if not conf['DEBUG_MODE']:
			print(f"> EXPORTING LEVEL TO DATABASE")
			genAsciiLevel = level_gen_sql.AsciiLevel(curTileset,genLevel.shape[0])
			genAsciiLevel.importLevel(genLevel)

			genLevelSQL = level_gen_sql.SQLLevel()
			botLoc = os.path.join(conf['AESTHETIC_BOT_DIR'],AESTH_BOT_CNN[curTilename].getModel(conf['AESTHETIC_BOT_DIR'],curTilename))
			genLevelSQL.setLevel(curTileset,genAsciiLevel,'gen',author=botLoc)
			genLevelSQL.exportSQLLevel()
		#otherwise just show it
		else:
			if not os.path.exists("p0_final_imgs"):
				os.makedirs("p0_final_imgs")
			print(f"> [DEBUG] VIEWING LEVEL")
			txt = ['$' if x == best_index else '' for x in range(len(bestGenLevels))]
			utils.showMultiMaps(bestGenLevels,curTilename,'',txt,f"p0_final_imgs/{curTilename}_FINAL.png")



	#delay and repeat, otherwise end the program
	if conf['REPEAT_STEP_0']:
		print(f" -------   WAITING [ {conf['STEP_0_FREQ']} ] MINUTES UNTIL RESTARTING    -------")
		time.sleep(conf['STEP_0_FREQ']*60)
	else:
		sys.exit(0)
		break
