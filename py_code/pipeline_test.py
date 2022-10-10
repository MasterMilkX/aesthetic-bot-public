#test the twitter model and generator
import utils
from level_gen_sql import Tileset
from aesthetic_bot import FitnessCNN, StraightBotTP
import TPKLDiv

#use 
TILENAME = "amongus"
test_tileset = Tileset(TILENAME)
print(f"> imported tileset: {TILENAME}")

#setup the fitness
AesthBot = FitnessCNN(test_tileset)
AesthBot.importModel("cnn_models/1/",TILENAME)
print(f"> imported aesthetic bot")

#get the tile patterns
all_user_levels = utils.getAscUserLevels(TILENAME)
tpatts = TPKLDiv.getPatternList2d(all_user_levels)

TESTS = 1

#try the evolution a few times
for i in range(TESTS):
	EvoBot = StraightBotTP(test_tileset,16,0.03,tpatts,mu=0.9)
	EvoBot.user_fun = AesthBot.eval_map_population
	print(f"> initialized evobot #{i}")

	#evolve for 250 iterations
	EvoBot.train(250,showPop=True,outGifname=f'{TILENAME}_t{i}.gif')

	#get the best map and show the stats
	best_map = EvoBot.best_map()
	best_fit = EvoBot.high_pop_fit()

	#show with stats
	#utils.showMap(best_map,TILENAME,f"Fitness: {best_fit}",f"test_{i}.png")
