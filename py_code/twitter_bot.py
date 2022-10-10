import tweepy
import os
import json
import requests
from requests_oauthlib import OAuth1Session


# CONNECTS AND PERFORMS ACTIONS FOR THE AESTHETIC BOT TWITTER ACCOUNT
class TwitterAcc():
	def __init__(self,auth_cred_file):
		#get the tokens by importing credentials from a file
		cred = {}
		with open(auth_cred_file,'r') as cf:
			cred = json.loads(cf.read())


		# authentication and login

		# TWEEPY VERSION (FOR EVERYTHING)
		auth = tweepy.OAuth1UserHandler(
		   cred['consumer_key'], cred['consumer_key_secret'],
		   cred['oauth_token'], cred['oauth_token_secret']
		)
		self.tweepyAPI = tweepy.API(auth)

		# REQUESTS VERSION (FOR POLLING ONLY)
		self.posterURL = 'https://api.twitter.com/2/tweets'
		self.requestAPI = OAuth1Session(cred['consumer_key'],
		                          client_secret=cred['consumer_key_secret'],
		                          resource_owner_key=cred['oauth_token'],
		                          resource_owner_secret=cred['oauth_token_secret'])

		good = "GOOD!" if self.tweepyAPI.get_user(screen_name='[TWITTER_HANDLE_HERE]').screen_name != "" else "BAD!"
		print(f"testing tweepy API: {good}")
		#print(f"testing request API: {}")


	# SEND A TEXT POST (and return the id of the post)
	def sendTextPost(self,txt,replyID=None):
		if replyID:
			twit_post = self.tweepyAPI.update_status(status=txt,in_reply_to_status_id=replyID)
		else:
			twit_post = self.tweepyAPI.update_status(status=txt)
		return twit_post.id

	# SEND AN IMAGE POST (and return the id of the post)
	def sendImgPost(self,imgLoc,txt,replyID=None):
		if replyID:
			twit_post = self.tweepyAPI.update_status_with_media(filename = imgLoc, status = txt,in_reply_to_status_id=replyID)
		else:
			twit_post = self.tweepyAPI.update_status_with_media(filename = imgLoc, status = txt)
		return twit_post.id

	# SEND A POLL POST (and return the id of the post)
	def sendPollPost(self, question, choices, replyID=None, pollMin=180):
		if replyID:
			poll_setup = {"text":question, "poll":{"options":choices,"duration_minutes":pollMin}, "reply":{"in_reply_to_tweet_id": str(replyID)}}
		else:
			poll_setup = {"text":question, "poll":{"options":choices,"duration_minutes":pollMin}}

		poll_post = self.requestAPI.post(self.posterURL,json=poll_setup,headers={'Content-type': "application/json"})
		print(f'poll status: {poll_post}')
		if not self.validStatus(str(poll_post)):
			#replace to send an error message to yourself
			# self.sendUserMessage("[TWITTER_HANDLE_HERE]","Oh no! Our poll! It's broken! 😬")

		return json.loads(poll_post.content)["data"]["id"]

	# MAKE SURE THE POST WAS SUCCESSFUL
	def validStatus(self,stat):
		return ("200" in stat) or ("201" in stat)

	# SEND A MESSAGE TO MAIN USERS's TWITTER ACCOUNT
	def sendUserMessage(self,user,msg):
		user_id = user = self.tweepyAPI.get_user(screen_name=user).id_str
		self.tweepyAPI.send_direct_message(user_id, msg)

	# GET THE VOTES FROM A POLL
	def getVotes(self,pollID):
		#retrieve the vote data
		vote_res_url = f"https://api.twitter.com/2/tweets?ids={pollID}&expansions=attachments.poll_ids"
		poll_vote_get = self.requestAPI.get(vote_res_url,headers={'Content-type': "application/json"})
		get_res = json.loads(poll_vote_get.content)
		choice_res = get_res['includes']['polls'][0]['options']
		
		#break up the choices and get  by label
		choice_set = {}
		for c in range(len(choice_res)):
			item = get_res['includes']['polls'][0]['options'][c]
			choice_set[item['label']] = item['votes']
		return choice_set




	# CREATE A LEVEL A vs B PAIR IMAGE AND VOTE THREAD POST
	def newLevelVotePost(self,pairIMGLoc,poll_time=180):
		#image post
		txt = "Vote in the thread below!"
		id_1 =  self.sendImgPost(pairIMGLoc,txt)
		print(f"> NEW TWITTER PAIR IMAGE POST MADE: {id_1}")
		
		#poll post
		question = "Map A or Map B?"
		choices_str = ["A","B"]
		id_2 = self.sendPollPost(question, choices_str, id_1, poll_time)
		print(f"> NEW TWITTER POLL MADE: {id_2}")
		return id_2

	# POST THE FOLLOW UP REPLY WITH THE ANSWER TO THE REAL MAP FOR AFTER THE POLL HAS COMPLETED
	def newAnswerPost(self,pollID,realLabel,editor_link="[LINK COMING SOON]",author=None):
		if author:
			answer_txt = f"Thanks for voting!\nThe human-made map is < {realLabel} > designed by {author[:16]}\nYou can make a map here: {editor_link} !"
		else:
			answer_txt = f"Thanks for voting!\nThe human-made map is < {realLabel} >\nYou can make a map here: {editor_link} !"
		answer_post = self.sendTextPost(answer_txt,pollID)

		print(f" > FOLLOW UP TWITTER POST FOR {pollID} MADE: {answer_post}")

		return answer_post

	# POST THE FOLLOW UP REPLY WITH THE AUTHORS (if duo user) AFTER THE POLL HAS COMPLETED
	def newDuoAnswerPost(self,pollID,editor_link="[LINK COMING SOON]",authors=None):
		if authors:
			answer_txt = f"Thanks for voting!\nBoth levels are human made:\n"
			if authors[0] != "":
				answer_txt +=  f" - [ A ] is designed by {authors[0][:16]}\n" 
			if authors[1] != "":
				answer_txt += f" - [ B ] is designed by {authors[1][:16]}\n"
			answer_txt += f"You can make a map here: {editor_link} !"
		else:
			answer_txt = f"Thanks for voting!\nBoth levels are generated.\nYou can make a map here: {editor_link} !"
		answer_post = self.sendTextPost(answer_txt,pollID)

		print(f" > FOLLOW UP TWITTER POST FOR {pollID} MADE: {answer_post}")

		return answer_post




