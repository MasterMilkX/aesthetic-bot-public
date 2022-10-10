import mysql.connector
from PIL import Image, ImageFont, ImageDraw
import random
import numpy as np
import os
import sys
 
from level_gen_sql import Tileset, AsciiLevel, SQLLevel
import utils

#CONNECT TO THE SQL DATABASE
mydb = mysql.connector.connect(
  host="localhost",
  user="aesth_bot",
  password="AR1Z0N4_iceD-T",
  database="aesthetic-bot"
)
cursor = mydb.cursor(buffered=True)


# GET THE LEVELS SORTED BY OLDEST / LEAST EVALUATED FIRST
# note: returns back a dictionary of the database info
def getUnevalLevels(authorType):

	#IMPORT THE LEVELS FOR PAIRING

	#import users (sort by least evaluated then oldest)
	db_set = f"{authorType}_levels"
	sel_users = f"SELECT * FROM {db_set} ORDER BY EVALS, TIME_MADE";
	cursor.execute(sel_users)
	sqlRes = cursor.fetchall()

	cols = cursor.column_names
	LEVELS = []
	for entry in sqlRes:
		l = {}
		for k,v in zip(cols,entry):
			l[k] = v
		LEVELS.append(l)

	return LEVELS

# check if a level is currently in an active poll
def inPoll(level_id, levelType):
	#import users from the user-gen pair db
	l = f"{levelType.upper()}_LEVEL_ID"
	sel_polls = f"SELECT {l} FROM vote_pairs WHERE TIME_FINISH IS NULL";
	cursor.execute(sel_polls)
	sqlRes = cursor.fetchall()

	for entry in sqlRes:
		if level_id == entry[0]:
			return True
	return False



# CREATE A PAIR LEVEL SET GIVEN AN INPUT GENERATED LEVEL
def create_pair(pair_user_level,pair_gen_level):
	#randomly assign A/B pair
	pairing = {}
	coinFlip = random.random()
	real_level = ('A' if coinFlip < 0.5 else 'B')
	not_real_level = ('B' if real_level == 'A' else 'A')


	pairing[real_level] = pair_user_level
	pairing[not_real_level] = pair_gen_level
	pairing['real'] = real_level
	

	#create a new sql entry for the pairing table
	pair_sql = "INSERT INTO vote_pairs (PAIR_ID, USER_LEVEL_ID, GEN_LEVEL_ID, REAL_LEVEL_AB, TIME_MADE, TIME_FINISH, A_VOTES, B_VOTES, TWITTER_ID) \
				VALUES (null, %s, %s, %s, CURRENT_TIMESTAMP, null, null, null, null)"
	pair_val = (pairing[real_level]['ID'], pairing[not_real_level]['ID'],real_level)
	cursor.execute(pair_sql, pair_val)
	mydb.commit()
	if cursor.rowcount > 0:
		print("> New pair inserted successfully!")

	return pairing

# UPDATE THE TWITTER ID FOR A PAIR ENTRY IN THE DATABASE
def setPairTwitID(pairID, twitID):
	pair_sql = "UPDATE vote_pairs  SET TWITTER_ID = %s WHERE PAIR_ID = %s"
	pair_val = (twitID,pairID)
	cursor.execute(pair_sql, pair_val)
	mydb.commit()

# UPDATE THE A AND B VOTES AND TIME FINISHED (ASSUMING NOW) FOR A PAIR ENTRY IN THE DATABASE
def setPairTwitVotes(pairID, a_votes, b_votes):
	pair_sql = "UPDATE vote_pairs SET A_VOTES = %s, B_VOTES = %s, TIME_FINISH = CURRENT_TIMESTAMP WHERE PAIR_ID = %s"
	pair_val = (a_votes,b_votes,pairID)
	cursor.execute(pair_sql, pair_val)
	mydb.commit()

# INCREMENT THE NUMBER OF TIMES A LEVEL WAS EVALUATED IN THE DATABASE
def incEvalLevels(authorType, levelID):
	if authorType == "user":
		level_sql = "UPDATE user_levels SET EVALS = EVALS + 1 WHERE ID = %s"
	else:
		level_sql = "UPDATE gen_levels SET EVALS = EVALS + 1 WHERE ID = %s"
	level_val = (levelID,)
	cursor.execute(level_sql, level_val)
	mydb.commit()

# GET THE AUTHOR OF A USER LEVEL
def getUserLevelAuthor(levelID):
	sel_user = f"SELECT AUTHOR FROM user_levels WHERE ID = {levelID}";
	cursor.execute(sel_user)
	author = cursor.fetchone()[0]
	return author
	

# RETURNS THE PAIRING ID FOR 2 FILES
def getPairID(realID,genID):
	sel_pair = "SELECT PAIR_ID FROM vote_pairs WHERE USER_LEVEL_ID = %s AND GEN_LEVEL_ID = %s";
	sel_pair_val = (realID, genID)
	cursor.execute(sel_pair,sel_pair_val)
	pid = cursor.fetchone()
	if pid == None:
		return -1
	else:
		return pid[0]

# GET THE REAL LEVEL LABEL FROM A PAIR
def getPairRealLabel(pairID):
	sel_pair = f"SELECT REAL_LEVEL_AB FROM vote_pairs WHERE PAIR_ID = {pairID}";
	cursor.execute(sel_pair)
	label = cursor.fetchone()[0]
	return label

# GET THE LEVEL ID FOR THE USER LEVEL AND THE GENERATED LEVEL
def getPairLevelIDs(pairID):
	sel_pair = f"SELECT USER_LEVEL_ID, GEN_LEVEL_ID FROM vote_pairs WHERE PAIR_ID = {pairID}";
	cursor.execute(sel_pair)
	res = cursor.fetchone()
	return {'user':res[0],'gen':res[1]}

# GET THE PAIRING VOTES 
def getPairVotes(pairID):
	sel_pair = f"SELECT A_VOTES, B_VOTES FROM vote_pairs WHERE PAIR_ID = {pairID}";
	cursor.execute(sel_pair)
	res = cursor.fetchone()
	return {'A':res[0],'B':res[1]}

# GET ALL RELEVANT INFORMATION FROM THE PAIRING
def getAllPair(pairID):
	sel_pair = f"SELECT USER_LEVEL_ID, GEN_LEVEL_ID, REAL_LEVEL_AB, A_VOTES, B_VOTES FROM vote_pairs WHERE PAIR_ID = {pairID}";
	cursor.execute(sel_pair)
	res = cursor.fetchone()
	return {'user':res[0],'gen':res[1],'real':res[2],'A':res[3],'B':res[4]}

# RETURNS THE RAW LEVELS, TILESET NAME, AND VOTES FOR THE LEVELS FOR A PAIR WITH A GIVEN ID
# note: use for training a fitnessCNN agent
def pair2Rating(pairID):
	allDat = getAllPair(pairID)

	#import the user level
	userLevel = SQLLevel()
	ur = userLevel.importSQLLevel("user",int(allDat['user']))
	if not ur:
		return None
	ascii_user = userLevel.ascii_level.level

	#import the generated level
	genLevel = SQLLevel()
	gr = genLevel.importSQLLevel("gen",int(allDat['gen']))
	if not gr:
		return None
	ascii_gen = genLevel.ascii_level.level

	#create level to rating dictionary
	vote_result = {}
	vote_result['real'] = {}
	vote_result['fake'] = {}

	real = allDat['real']
	fake = "B" if allDat['real'] == "A" else "A"

	vote_result['real']['level'] = ascii_user
	vote_result['fake']['level'] = ascii_gen
	vote_result['real']['votes'] = allDat[real]
	vote_result['fake']['votes'] = allDat[fake]
	vote_result["tileset"] = genLevel.dat['tileName']

	return vote_result

# RETRIEVE THE IDS OF ALL OF THE PAIRINGS
def getAllPairIDs():
	sel_pair = f"SELECT PAIR_ID FROM vote_pairs WHERE TIME_FINISH is not NULL";
	cursor.execute(sel_pair)
	ids = []
	for res in cursor.fetchall():
		ids.append(res[0])
	return ids


#create an image from a pair of maps
# INPUTS: 2 database objects for the pairing (see output from create_pair()) and the pairing ID from the database
def create_pair_img(pair,pairID):
	#grab the objects from the pairing
	a = pair['A']
	b = pair['B']

	#import the tileset
	tilename = a['TILESET']   #assume both maps have the same tileset
	pairTileset = Tileset(tilename)

	#create AsciiLevel objects for both levels
	A_asc = AsciiLevel(pairTileset,int(a['MAP_SIZE']))
	A_asc.importLevel(a['ASCII_MAP'])

	B_asc = AsciiLevel(pairTileset,int(b['MAP_SIZE']))
	B_asc.importLevel(b['ASCII_MAP'])

	#create their images (320x320 regardless of level size)
	A_img = A_asc.makeLevelImg().resize((320,320),Image.NEAREST)
	B_img = B_asc.makeLevelImg().resize((320,320),Image.NEAREST)

	#create consolidated image
	pairIMG = Image.new("RGBA", (720,480), (255,255,255))
	mainIMG = ImageDraw.Draw(pairIMG)

	#show the maps
	ap = (20,60)
	bp = (380,60)

	mainIMG.rectangle((ap[0]-3,ap[1]-3,ap[0]+322,ap[1]+322),fill="#565656")
	pairIMG.paste(A_img, (ap[0],ap[1],ap[0]+320,ap[1]+320))
	mainIMG.rectangle((bp[0]-3,bp[1]-3,bp[0]+322,bp[1]+322),fill="#565656")
	pairIMG.paste(B_img, (bp[0],bp[1],bp[0]+320,bp[1]+320))

	#create helper text
	font = ImageFont.truetype("Courier.ttf", 32)
	mainIMG.text((164,20),"A",(0,0,0),font=font)
	mainIMG.text((530,20),"B",(0,0,0),font=font)
	mainIMG.text((120,420),"Which do you like better?",(0,0,0),font=font)

	return pairIMG






#tester 
if __name__ == "__main__":
	NUM_PAIRS_GEN = 1

	if len(sys.argv) > 1:
		NUM_PAIRS_GEN = int(sys.argv[1])

	for n in range(NUM_PAIRS_GEN):
		tilename = random.choice(["zelda","pokemon","pacman","amongus","dungeon"])

		#get a random user
		userLevel = getUnevalUserLevels()[0]

		#make a random level
		genLevel = level_gen_sql.SQLLevel()
		genLevel.setLevel(Tileset(tilename),utils.makeRandomAscMaps(1)[0],"gen")
		genLevel.exportSQLLevel()

		#make a pair
		db_pair = create_pair(userLevel,genLevel)
		real = db_pair['real']
		db_real = db_pair[real]
		db_gen = db_pair[("B" if real == "A" else "A")]


		#get pairing id
		db_id = getPairID(db_real['ID'],db_gen['ID'])
		print(f"pair created: {db_id}")

		#make an image
		im = create_pair_img(db_pair,db_id)
		tset = tilename
		im.save(os.path.join(PAIR_IMG_DIR,f"pair-{tset}-{db_id}.png"), format='png')
		im.show()




