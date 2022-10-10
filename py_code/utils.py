# UTILITY SCRIPT FOR GENERIC FUNCTIONS

import random
import yaml
import os
import math

from level_gen_sql import Tileset, AsciiLevel, SQLLevelSet
import pair_gen_sql
import pair_EXT_gen_sql
# from pair_gen_sql import getAllPairIDs, pair2Rating
# from pair_EXT_gen_sql import getAllPairIDs as getAllPairIDs_EXT
# from pair_EXT_gen_sql import pair2Rating as pair2Rating_EXT
from TPKLDiv import tp_fitness

from PIL import Image
from tqdm import tqdm
import imageio
import numpy as np
import matplotlib.pyplot as plt

# SHOW AN ASCII 2D MAP AS AN IMAGE
def showMap(m,tilename,label=None,exportFile=None):
	t = Tileset(tilename)
	am = AsciiLevel(t,m.shape)
	am.importLevel(m)
	img = am.makeLevelImg()
	plt.imshow(img)
	plt.axis('off')
	if label != None:
		plt.title(label)

	#export to a file
	if exportFile != None:
		plt.savefig(exportFile)
	
# SHOW MULTIPLE MAPS IN ONE CELL
def showMultiMaps(ms,tilename,text='',textArr=None,exportFile=None):
	t = Tileset(tilename)
	imgs = []
	#make an image for each map
	for m in ms:
		am = AsciiLevel(t,m.shape)
		am.importLevel(m)
		img = am.makeLevelImg()
		imgs.append(img)
		
	plt.figure(figsize=(20,7))
	col = 8
	for i, im in enumerate(imgs):
		plt.subplot(int(len(imgs) / col) + 1, col, i + 1)
		plt.imshow(im)
		plt.axis('off')
		if (textArr != None) and (i < len(textArr)):
			plt.title(textArr[i])
		
		if text != '':
			plt.suptitle(text)

	#export to a file
	if exportFile != None:
		plt.savefig(exportFile)

#display the tile patterns and their frequencies
def showTilePat(tps,tilename,textArr=None):
    t = Tileset(tilename)
    imgs = []
    #make an image for each map
    for tp in tps:
        am = AsciiLevel(t,tp.shape)
        am.importLevel(tp)
        img = am.makeLevelImg()
        imgs.append(img)

    plt.figure(figsize=(20,5))
    col = 16
    for i, im in enumerate(imgs):
        plt.subplot(int(len(imgs) / col) + 1, col, i + 1)
        plt.imshow(im)
        plt.axis('off')
        if (textArr != None) and (i < len(textArr)):
            plt.title(textArr[i])

# TURN POPULATION OF MAPS INTO A GIF
def animateMapPopulation(all_populations,tilename,txtArr=[],outGif="population.gif",fps=4):
	t = Tileset(tilename)
	
	if not os.path.exists("_tmp/"):
		os.mkdir("_tmp/")

	#make a congregated image for each population set
	with tqdm(total=len(all_populations)) as pbar:
		for mi in range(len(all_populations)):
			ms = all_populations[mi]
			imgs = []
			#make an image for each map
			for m in ms:
				am = AsciiLevel(t,m.shape)
				am.importLevel(m)
				img = am.makeLevelImg()
				imgs.append(img)

			plt.figure(figsize=(20,7))
			
			#add individual maps from population
			col = 8
			for i, im in enumerate(imgs):
				plt.subplot(int(len(imgs) / col) + 1, col, i + 1)
				plt.axis('off')
				plt.imshow(im)
				if len(txtArr) > 0:
					plt.suptitle(txtArr[mi])

					
			plt.savefig(f"_tmp/{mi}.png")
			plt.close()
			
			pbar.update(1)
			pbar.set_description(f'saving population {mi+1}...')
			
		
	#export the gif
	pop_imgs = []
	for i in range(len(all_populations)):
		pop_imgs.append(imageio.imread(f"_tmp/{i}.png"))
	imageio.mimsave(outGif, pop_imgs,duration=(1/fps))
	
	#remove old files
	for i in range(len(all_populations)):
		os.remove(f"_tmp/{i}.png")
		
	
# SHOW RANDOM SET OF RANDOMLY GENERATED MAPS
def makeRandomAscMaps(num_maps,map_size=None):
	sm = []
	for i in range(num_maps):
		if map_size == None:
			s = random.randint(6,12)
		else:
			s = map_size
		sm.append(np.random.randint(0, 16, size=(s, s)))
		
	return sm

# MAKE A SET OF BLANK ASCII MAPS
def makeBlankAscMaps(num_maps,map_size=None):
	sm = []
	for i in range(num_maps):
		if map_size == None:
			s = random.randint(6,12)
		else:
			s = map_size
		sm.append(np.zeros(shape=(s, s),dtype=int))
		
	return sm
	
# RETURN THE FULL TILESET OBJECTS
def getAllTilesets():
	ts = {}
	for n in ["zelda","pokemon","amongus","pacman","dungeon"]:
		ts[n] = Tileset(n)
	return ts


# GET ALL OF THE SAVED USER LEVELS FOR A TILESET
def getAscUserLevels(TILENAME):
	levelSet = SQLLevelSet("user",TILENAME).levelSet
	asc_levels = [l.ascii_level.level for l in levelSet]
	return asc_levels

# GET ALL OF THE SAVED USER LEVELS FOR A TILESET
def getAscGenLevels(TILENAME):
	levelSet = SQLLevelSet("gen",TILENAME).levelSet
	asc_levels = [l.ascii_level.level for l in levelSet]
	return asc_levels

# GET ALL OF THE USER LEVELS AUTHORED BY A SPECIFIC USER(S)
def getProfileLevelSet(usernames):
	levelSet = SQLLevelSet("user").levelSet
	sel_levels = list(filter(lambda x: x.dat['author'] in usernames, levelSet))

	#sort into tilesets
	profileSet = {}
	for n in ["zelda","pokemon","amongus","pacman","dungeon"]:
		profileSet[n] = []
	for l in sel_levels:
		profileSet[l.dat['tileName']].append(l.ascii_level.level)

	return profileSet


# GET ALL OF THE SAVED LEVELS (OF ALL TILENAMES) THAT WERE IN A PAIRING AND WON
def getWinningLevelSet():
	win_set = {}

	# get all of the levels from each first
	for TILENAME in ["zelda","pokemon","amongus","pacman","dungeon"]:

		win_set[TILENAME] = []

	# grab all of the pairs ids and import their data
	pairIDs = pair_gen_sql.getAllPairIDs()
	for pi in pairIDs:
		pairDat = pair_gen_sql.pair2Rating(pi)
		if pairDat == None:
			continue
		real_votes = pairDat['real']['votes']
		fake_votes = pairDat['fake']['votes']
		tilename = pairDat['tileset']

		# add the winning level
		if real_votes == fake_votes:
			win_set[tilename].append(pairDat['real']['level'])
			win_set[tilename].append(pairDat['fake']['level'])
		elif real_votes > fake_votes:
			win_set[tilename].append(pairDat['real']['level'])
		elif fake_votes > real_votes:
			win_set[tilename].append(pairDat['fake']['level'])

	# (same for the extended pairings)
	pairIDs_ext = pair_EXT_gen_sql.getAllPairIDs()
	for pi in pairIDs_ext:
		pairDat = pair_EXT_gen_sql.pair2Rating(pi)
		if pairDat == None:
			continue

		real_votes = pairDat['real']['votes']
		fake_votes = pairDat['fake']['votes']
		tilename = pairDat['tileset']

		# add the winning level
		if real_votes == fake_votes:
			win_set[tilename].append(pairDat['real']['level'])
			win_set[tilename].append(pairDat['fake']['level'])
		elif real_votes > fake_votes:
			win_set[tilename].append(pairDat['real']['level'])
		elif fake_votes > real_votes:
			win_set[tilename].append(pairDat['fake']['level'])

	return win_set



# SPLIT 2D MAP INTO ONE HOT ENCODED CHANNELS (3D ARRAY)
def encodeMap(m,channels=16):
	map3d = np.zeros((m.shape[0],m.shape[1],channels))
	for r in range(m.shape[0]):
		for c in range(m.shape[1]):
			v = m[r][c]
			map3d[r][c][v] = 1
	return map3d

# CONVERT 3D ENCODED CHANNEL MAP INTO 2D ARRAY FORMAT
def decodeMap(m3c):
	return np.argmax(m3c,axis=2)
	

# NORMAL ENTROPY FUNCTION FOR A MAP
def entropy(m):
	num_tiles = np.prod(m.shape)

	# get tile entropy #
	tileCts = {}
	for a in range(16):  #16 tiles
		tileCts[a] = 0

	for r in m:
		for t in r:
			tileCts[t]+=1

	tileProbs = {}
	for k,v in tileCts.items():
		tileProbs[k] = v/num_tiles

	return sum([-1*(p * math.log10(p)) for p in tileProbs.values() if p > 0])

# RETURN THE "TWITTER" DEFINED FITNESS
def twitterFit(m,tile_patts,SAMP_WEIGHT=0.35,KL_WINDOW_SIZE=2,TWIT_OFFSET=3,MIN_USER_KLDIV=-3):
	return tp_fitness(m,tile_patts,WEIGHT=SAMP_WEIGHT,WINDOW=KL_WINDOW_SIZE)+abs(MIN_USER_KLDIV)+TWIT_OFFSET
	
# READ THE CONFIGURATION FILE
def readConfig(configFile):
	with open(configFile, "r") as cf:
		config = yaml.safe_load(cf)
	return config

# get all of the training pairs as real-fake map/score training data (full list)
def getPairTrainData(min_vote_req=0,BINARY=True):
	TILENAMES = ["zelda","pokemon","pacman","amongus","dungeon"]

	# 1a. get all of the pairings saved to the database
	all_pairIDs = pair_gen_sql.getAllPairIDs()
	pairDataSet = []
	for pid in all_pairIDs:
		vr = pair_gen_sql.pair2Rating(pid)

		# pair not found
		if vr == None:
			print(f"** No valid pairing found for ID [ {pid} ] **")
			continue

		total = (abs(vr['real']['votes']) + abs(vr['fake']['votes']))
		# not enough votes
		if total < min_vote_req:
			print(f"** Not enough votes for ID [ {pid} ] ({total} < {min_vote_req})")
			continue
		pairDataSet.append(vr)

	# 1b. get all of the pairings saved to the database (EXT)
	all_pairIDs = pair_EXT_gen_sql.getAllPairIDs()
	for pid in all_pairIDs:
		vr = pair_EXT_gen_sql.pair2Rating(pid)

		# pair not found
		if vr == None:
			print(f"** No valid pairing found in [EXT] for ID [ {pid} ] **")
			continue

		total = (abs(vr['real']['votes']) + abs(vr['fake']['votes']))
		# not enough votes
		if total < min_vote_req:
			print(f"** Not enough votes for ID [ {pid} ] ({total} < {min_vote_req})")
			continue
		pairDataSet.append(vr)

	random.shuffle(pairDataSet[:30])

	tr_maps = {}
	tr_scores = {}
	for t in TILENAMES:
		tr_maps[t] = {'real':[],'fake':[]}
		tr_scores[t] = {'real':[],'fake':[]}

	for pair_data in pairDataSet:
		TILE = pair_data['tileset']

		# whole Y value input
		if not BINARY:
			real_score = pair_data['real']['votes']-pair_data['fake']['votes']
			fake_score = pair_data['fake']['votes']-pair_data['real']['votes']
		# binary Y value input
		else:
			total = max((abs(pair_data['real']['votes']) + abs(pair_data['fake']['votes'])), 1)
			real_score = pair_data['real']['votes'] / total
			fake_score = pair_data['fake']['votes'] / total

		# 2b. add to the set for the tile
		tr_maps[TILE]['real'].append(pair_data['real']['level'])
		tr_maps[TILE]['fake'].append(pair_data['fake']['level'])
		tr_scores[TILE]['real'].append(real_score)
		tr_scores[TILE]['fake'].append(fake_score)

	return {'maps':tr_maps, 'scores':tr_scores}


# get the pair data for a specific tileset only
def getTilePairTrainData(tileset,min_vote_req=0,BINARY=True):
	pair_dat = getPairTrainData(min_vote_req,BINARY)
	return {'maps':pair_dat['maps'][tileset],'scores':pair_dat['scores'][tileset]}


