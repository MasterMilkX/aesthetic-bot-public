# AESTHETIC BOT TWITTER ERROR MONITOR
# Sends a DM to @MasterMilkX if the code stops or errors out for any reason

#general imports
import sys
import time
import os
from multiprocessing import Process
import psutil

# external files
import twitter_bot
import utils

watch_files = ['twit_p0.out', 'twit_p1.out']
watch_procs = ['bot_twitter_sql_P0.py', 'bot_twitter_sql_P1.py']


# import the twitter bot api and functions
conf_file = "aesth_config.yaml"
conf = utils.readConfig(conf_file)
TwitterBot = twitter_bot.TwitterAcc(conf['TWIT_AUTH_FILE'])


# watch a file and output every new line
def follow(f):
	# seek the end of the file
	f.seek(0, os.SEEK_END)
	
	# start infinite loop
	while True:
		# read last line of file
		line = f.readline()

		# sleep if file hasn't been updated
		if not line:
			time.sleep(1)
			continue

		yield line

# watch the generator follow of a file
def followFile(f):
	logfile = open(f,"r")
	loglines = follow(logfile)

	# iterate over the generator
	for line in loglines:

		# found an error message in the file output
		if "error" in line.lower():
			# SEND A MESSAGE TO THE MAIN USER
			#TwitterBot.sendUserMessage("[TWITTER_HANDLE_HERE]",f"Oh no! Our code ({f})! It's broken! 😬")
			sys.exit(0)


# watch processes and check if still running
def watchProcs():
	while True:
		#Iterate over the all the running process
		py_set = []
		for proc in psutil.process_iter():
			try:
				pinfo = proc.cmdline()

				if len(pinfo) == 0:
					continue

				# Check if process name contains the given name string.
				if ('python' in pinfo[0]):
					#print(pinfo)
					py_set.append(' '.join(pinfo))
					continue
			except (psutil.AccessDenied , psutil.ZombieProcess, psutil.NoSuchProcess):
				pass
				
		# check if searched for process is found
		broke = []
		for wp in watch_procs:
			if not any(wp in x for x in py_set):
				broke.append(wp)
		
		# something's wrong!
		if len(broke) > 0:
			#senf a message to the main user
			#TwitterBot.sendUserMessage("[TWITTER_HANDLE_HERE]",f"Oh no! Our program(s) ({broke})! It's broken! 😬")
			sys.exit(0)

		#otherwise if found and all is good, sleep for a bit
		else:
			time.sleep(20)

		



# run everything in parallel
if __name__ == '__main__':
	proc = []

	# watch the output files
	for wf in watch_files:
		p = Process(target=followFile,args=(wf,))
		p.start()
		print(f"> Watching file: {wf}...")
		proc.append(p)

	# watch the processes
	p = Process(target=watchProcs)
	p.start()
	proc.append(p)
	print(f"> Watching processes named: {watch_procs}")

	#join all together now
	for p in proc:
		p.join()


