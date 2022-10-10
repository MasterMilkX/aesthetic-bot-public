# INTERFACES WITH THE VOTE_PAIRS_EXT TABLE ONLY - DIRECT COPY OF PAIR_GEN_SQL.PY


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



# check if a level is currently in an active poll
def inPoll(level_id, duoType):
	#import users from the user-gen pair db
	sel_polls = f"SELECT LEVEL_A, LEVEL_B FROM vote_pairs_ext WHERE LEVEL_DUO_TYPE = '{duoType}' AND TIME_FINISH IS NULL";
	cursor.execute(sel_polls)
	sqlRes = cursor.fetchall()

	for entry in sqlRes:
		if level_id == entry[0] or level_id == entry[1]:
			return True
	return False



# CREATE A PAIR LEVEL SET GIVEN A SET AND DUO TYPE
def create_pair(levelX,levelY, duo_type):
	#randomly assign A/B pair
	pairing = {}
	coinFlip = random.random()
	level1 = ('A' if coinFlip < 0.5 else 'B')
	level2 = ('B' if level1 == 'A' else 'A')


	pairing[level1] = levelX
	pairing[level2] = levelY
	pairing['duo_type'] = duo_type
	

	#create a new sql entry for the pairing table
	pair_sql = "INSERT INTO vote_pairs_ext (PAIR_ID, LEVEL_A, LEVEL_B, LEVEL_DUO_TYPE, TIME_MADE, TIME_FINISH, A_VOTES, B_VOTES, TWITTER_ID) \
				VALUES (null, %s, %s, %s, CURRENT_TIMESTAMP, null, null, null, null)"
	pair_val = (pairing['A']['ID'], pairing['B']['ID'],duo_type)
	cursor.execute(pair_sql, pair_val)
	mydb.commit()
	if cursor.rowcount > 0:
		print(f"> New duo pair [ {duo_type} ] inserted successfully!")

	return pairing

# UPDATE THE TWITTER ID FOR A PAIR ENTRY IN THE DATABASE
def setPairTwitID(pairID, twitID):
	pair_sql = "UPDATE vote_pairs_ext SET TWITTER_ID = %s WHERE PAIR_ID = %s"
	pair_val = (twitID,pairID)
	cursor.execute(pair_sql, pair_val)
	mydb.commit()

# UPDATE THE A AND B VOTES AND TIME FINISHED (ASSUMING NOW) FOR A PAIR ENTRY IN THE DATABASE
def setPairTwitVotes(pairID, a_votes, b_votes):
	pair_sql = "UPDATE vote_pairs_ext SET A_VOTES = %s, B_VOTES = %s, TIME_FINISH = CURRENT_TIMESTAMP WHERE PAIR_ID = %s"
	pair_val = (a_votes,b_votes,pairID)
	cursor.execute(pair_sql, pair_val)
	mydb.commit()



# RETURNS THE PAIRING ID FOR 2 LEVELS
def getPairID(levelA,levelB, levelType):
	sel_pair = "SELECT PAIR_ID, LEVEL_A, LEVEL_B FROM vote_pairs_ext WHERE LEVEL_DUO_TYPE = %s";
	sel_pair_val = (levelType, )
	cursor.execute(sel_pair,sel_pair_val)
	sqlRes = cursor.fetchall()

	for entry in sqlRes:
		if (entry[1] == levelA and entry[2] == levelB) or (entry[1] == levelB and entry[2] == levelA):
			return entry[0]
	return -1


# GET THE LEVEL ID FOR THE PAIR LEVELS
def getPairLevelIDs(pairID):
	sel_pair = f"SELECT LEVEL_A, LEVEL_B FROM vote_pairs_ext WHERE PAIR_ID = {pairID}";
	cursor.execute(sel_pair)
	res = cursor.fetchone()
	return {'A':res[0],'B':res[1]}

# GET THE PAIRING VOTES 
def getPairVotes(pairID):
	sel_pair = f"SELECT A_VOTES, B_VOTES FROM vote_pairs_ext WHERE PAIR_ID = {pairID}";
	cursor.execute(sel_pair)
	res = cursor.fetchone()
	return {'A':res[0],'B':res[1]}

# GET ALL RELEVANT INFORMATION FROM THE PAIRING
def getAllPair(pairID):
	sel_pair = f"SELECT LEVEL_A, LEVEL_B, LEVEL_DUO_TYPE, A_VOTES, B_VOTES FROM vote_pairs_ext WHERE PAIR_ID = {pairID}";
	cursor.execute(sel_pair)
	res = cursor.fetchone()
	return {'LEVEL_A':res[0],'LEVEL_B':res[1],'DUO_TYPE':res[2],'A':res[3],'B':res[4], }

# RETURNS THE RAW LEVELS, TILESET NAME, AND VOTES FOR THE LEVELS FOR A PAIR WITH A GIVEN ID
# note: use for training a fitnessCNN agent
def pair2Rating(pairID):
	allDat = getAllPair(pairID)

	DUO_TILESET = None

	#get the user levels
	if allDat['DUO_TYPE'] == "user":
		#import the user level
		userLevel1 = SQLLevel()
		ur1 = userLevel1.importSQLLevel("user",int(allDat['LEVEL_A']))
		if not ur1:
			return None
		ascii1 = userLevel1.ascii_level.level

		#import the OTHER user level
		userLevel2 = SQLLevel()
		ur2 = userLevel2.importSQLLevel("user",int(allDat['LEVEL_B']))
		if not ur2:
			return None
		ascii2 = userLevel2.ascii_level.level

		DUO_TILESET = userLevel2.dat['tileName']

	elif allDat['DUO_TYPE'] == "gen":
		#import the generated level
		genLevel1 = SQLLevel()
		gr1 = genLevel1.importSQLLevel("gen",int(allDat['LEVEL_A']))
		if not gr1:
			return None
		ascii1 = genLevel1.ascii_level.level

		#import the generated level
		genLevel2 = SQLLevel()
		gr2 = genLevel2.importSQLLevel("gen",int(allDat['LEVEL_B']))
		if not gr2:
			return None
		ascii2 = genLevel2.ascii_level.level

		DUO_TILESET = genLevel2.dat['tileName']


	#create level to rating dictionary

	# NOTE: REAL VS. FAKE DOESN'T MATTER SINCE THEY COULD BOTH BE REAL OR FAKE 
	#        - THIS IS JUST TO KEEP WITH CONSISTENCY WITH THE ACCESS FOR OTHER SCRIPTS
	#        - ASSUME A = REAL AND B = FAKE

	vote_result = {}
	vote_result['real'] = {}
	vote_result['fake'] = {}

	vote_result['real']['level'] = ascii1
	vote_result['fake']['level'] = ascii2
	vote_result['real']['votes'] = allDat['A']
	vote_result['fake']['votes'] = allDat['B']
	vote_result["tileset"] = DUO_TILESET

	return vote_result

# RETRIEVE THE IDS OF ALL OF THE PAIRINGS
def getAllPairIDs():
	sel_pair = f"SELECT PAIR_ID FROM vote_pairs_ext WHERE TIME_FINISH is not NULL";
	cursor.execute(sel_pair)
	ids = []
	for res in cursor.fetchall():
		ids.append(res[0])
	return ids






