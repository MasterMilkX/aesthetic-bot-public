import random
import os
import math

import numpy as np
import tensorflow as tf
from keras import Sequential
from keras.layers import Dense, BatchNormalization, ReLU, Conv2D, Flatten, MaxPooling2D
from tqdm import tqdm
import utils

# a regression model that outputs a value (representing user vote) based on an input map
class FitnessCNN():
    def __init__(self,tileset,output='whole'):
        self.tileset = tileset
        self.nn_size = 4   #minimum size of the maps
        self.channels = tileset.num_tiles
        self.nn_out = output
        
        self.makeModel()
        
    #make a regression model to try to predict the rating value
    def makeModel(self):
        rm = Sequential()

        rm.add(Conv2D(self.channels*4,(2,2),strides=(2,2),padding='same',input_shape=[self.nn_size,self.nn_size,self.channels]))
        rm.add(BatchNormalization())
        rm.add(ReLU())
        rm.add(MaxPooling2D(pool_size=(2, 2),strides=(1, 1), padding='same'))

        rm.add(Conv2D(self.channels*2,(2,2),strides=(2,2),padding='same'))
        rm.add(BatchNormalization())
        rm.add(ReLU())
        rm.add(MaxPooling2D(pool_size=(2, 2),strides=(1, 1), padding='same'))

        rm.add(Conv2D(self.channels,(2,2),strides=(2,2),padding='same'))
        rm.add(BatchNormalization())
        rm.add(ReLU())

        rm.add(Flatten())
        rm.add(Dense(self.channels, activation='relu'))
        
         # use whole values to predict (raw vote difference model)
        if self.nn_out == 'whole':
            rm.add(Dense(1, activation="linear"))
        # use 0-1 to predict (vote percentage model)
        else:
            rm.add(Dense(1,activation='sigmoid'))
    

        rm.compile(loss="mse", optimizer="adam",metrics=['accuracy'])
        #rm.summary()
        self.reg_model = rm
    
    #convert the maps to be input into the neural network
    def convert_maps(self,maps):
        tmaps = []
        submap_set = {}
        
        #get all levels in the set
        smi = 0
        for li in range(len(maps)):
            l = maps[li]
            
            #crop to the smallest shape
            for i in range(np.prod(l.shape)):
                c = i % l.shape[0]
                r = math.floor(i / l.shape[0])

                #check if out of bounds
                if((r+self.nn_size)>l.shape[0] or (c+self.nn_size)>l.shape[0]):
                    continue

                #get the map crop area (window)
                twin = l[r:r+self.nn_size,c:c+self.nn_size]
                
                #save
                tmaps.append(twin.astype(int))
                submap_set[smi] = li   #save the tmap ID to the associated og map
                smi+=1

        #print(f"> Created {len(tmaps)} cropped sub-levels from the tileset")
            
        #save the original maps (before preprocessing)
        tmaps = np.array(tmaps)
         
        #encode maps
        return np.array([utils.encodeMap(m) for m in tmaps]), submap_set

    #evaluate a population of maps 
    def eval_map_population(self,pop):
        #convert the maps to an appropriate format
        conv_pop, pop_key = self.convert_maps(pop)
        
        #return the predictions
        raw_preds = np.array(self.reg_model(conv_pop,training=False)).squeeze()
        
        #get the combined scores for each item
        pop_score = {}
        for i in range(len(pop)):
            pop_score[i] = []
        for pi in range(len(raw_preds)):
            pop_score[pop_key[pi]].append(raw_preds[pi])
            
        #return the averaged score for each set
        all_avgs = [np.average(np.array(x)) for x in pop_score.values()]
        return all_avgs
        
            
    #train the network on the input maps (selected generated and user map) and their associated scores (from the fitness function)
    def train(self,epochs,input_maps,input_scores,DEBUG=False):
        if DEBUG:
            print(f"-- TRAINING REG MODEL ON [ {self.tileset.tileFile} ] for [ {epochs} ] EPOCHS --")
            
        #split up the maps and scores to associate and train individually
        real_maps = input_maps['real']
        conv_rm,rm_key = self.convert_maps(real_maps)
        fake_maps = input_maps['fake']
        conv_fm,fm_key = self.convert_maps(fake_maps)
            
        #expand scores for each subset map
        real_scores = []
        for k in rm_key.values():
            real_scores.append(input_scores['real'][k])
        fake_scores = []
        for k in fm_key.values():
            fake_scores.append(input_scores['fake'][k])
            
        #use the minimum number as the number of patterns to try on and randomly select from the larger
        max_num_patt = max(len(conv_rm),len(conv_fm))
        print(f"# real:{len(conv_rm)} / # fake:{len(conv_fm)} => {max_num_patt}")
        if len(conv_fm) > len(conv_rm):   #add more to real
            ind = random.choices(range(len(conv_rm)),k=(max_num_patt-len(conv_rm)))
            conv_rm = np.concatenate((conv_rm,conv_rm[ind]),axis=0)
            real_scores += np.array(real_scores)[ind].tolist()
        elif len(conv_rm) > len(conv_fm):   #add more to fake
            ind = random.choices(range(len(conv_fm)),k=(max_num_patt-len(conv_fm)))
            conv_fm = np.concatenate((conv_fm,conv_fm[ind]),axis=0)
            fake_scores += np.array(fake_scores)[ind].tolist()

                    
        #sanity check
#         unenc = [utils.decodeMap(m) for m in conv_rm[:32]]
#         s = real_scores[:32]
#         showMultiMaps(unenc,self.tileset.tileFile,'',s)

        #combine to X and y
        X_tr = np.concatenate((conv_rm,conv_fm),axis=0)
        y_tr = np.concatenate((real_scores,fake_scores),axis=0)
            
        #train regression model for X epochs on Y batches of maps
        history = self.reg_model.fit(X_tr,y_tr,epochs=epochs,batch_size=min(16,len(X_tr)),shuffle=True,verbose=DEBUG)
        eloss = history.history['loss']
        acc = history.history['accuracy']
                
        return np.array(eloss), np.array(acc)
    
    #export the model to a folder
    def exportModel(self,loc,name):
        if not os.path.exists(loc):
            os.makedirs(loc,exist_ok=True)
        
        self.reg_model.save(os.path.join(loc,name)+".h5")
        
    #import the model to a folder
    def importModel(self,loc,name):
        filename = os.path.join(loc,name)+".h5"
        if not os.path.exists(filename):
            #try to find an appoximation
            new_name = self.getModel(loc,name)
            if new_name != None:
                filename = os.path.join(loc,new_name)
            else:
                print(f"ERROR: {filename} does not exist or file with partial name not found in location: {loc}!")
                return
        
        self.reg_model = tf.keras.models.load_model(filename)
        
    #find a model's full filename based on the approximate name given
    def getModel(self,directory,approx_name):
        d = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        for f in d:
            if approx_name in f:
                return f
        return None


# NORMAL EVOLUTIONARY ALGORITHM THAT EVOLVES A POPULATION OF ASCII MAPS TOWARDS A FITNESS VALUE
class StraightBotTP():
    def __init__(self,tileset,popSize,mutrate,tilepatterns,tp_size=None,mu=0.5,exprate=0.01,rank_tp_sel=False):
        self.tileset = tileset    #use the Tileset class
        self.pop_size = popSize
        self.population = []
        self.user_fun = None    #fitness function to act as the user evaluation of a level
        self.mutRate = mutrate  #chances a tile will mutate
        self.expRate = exprate  #chances a map will change dimensions
        self.changeFit = []
        self.mut_tilepats = tilepatterns   #set of 2d arrays to replace a section of the map
        self.tile_patt_size = (tilepatterns[0].shape[0] if tp_size == None else tp_size)
        self.mu = mu              #mu lambda mutation for evolution and population reselection
        self.rank_tp_sel = rank_tp_sel   #select the tile patterns in ranked form

    #creates a new randomized map population
    def new_pop(self,randomInit=True):
        if randomInit:
            self.population = utils.makeRandomAscMaps(self.pop_size,9)
        else:
            self.population = utils.makeBlankAscMaps(self.pop_size)
        
    #mu + lambda population update
    def evolve_pop(self):
        if self.user_fun == None:
            print("ERROR: <user_fun> not set! Please specify a function to use as the fitness function for the population evaluation!")
            return

        next_gen_pop = []
        pop_fitness = [i[0] for i in sorted(enumerate(self.user_fun(self.population)), key=lambda x:x[1],reverse=True)]


        #total = sum(list(range(self.pop_size+1)))
        #probs = [x/total for x in range(1,self.pop_size+1)]
        #print(pop_fitness)
        
        #get the best samples from the population
        best_population = []
        for p in pop_fitness:
            best_population.append(self.population[p])
            
        #add mutated maps (mu many)
        wpop = list(range(1,self.pop_size+1))
        wpop.reverse()
        mut_maps = random.choices(best_population,weights=wpop,k=int(self.pop_size*self.mu))

        for m in mut_maps:
            next_gen_pop.append(self.mutate(m))
            
        #add top maps
        for b in range(self.pop_size-len(next_gen_pop)):
            i = pop_fitness[b]
            next_gen_pop.append(self.population[i])
            
        self.population = np.array(next_gen_pop)
        
    #get the highest fitness in the population
    def high_pop_fit(self):
        return max(self.user_fun(self.population))
    
    #get the average fitness in the population
    def avg_pop_fit(self):
        return np.average(self.user_fun(self.population))
    
    #get the map from the population with the 
    def best_map(self):
        return self.population[np.argmax(self.user_fun(self.population))]
        
    #get the average NxN size of the population
    def avg_pop_size(self):
        return np.average([len(x) for x in self.population])

        
    #mutate a map 
    def mutate(self,m):
        m2 = m.copy()
        mr = random.random()
        
        #change the dimensions
        if mr <= self.expRate:
            r = random.random()
            #decrease
            if (r < 0.5) and (m.shape[0]>6):
                m2 = m2[:m.shape[0]-1, :m.shape[1]-1]
            #increase
            elif m.shape[0] < 12:
                m2 = np.random.randint(0,16,size=(m.shape[0]+1,m.shape[1]+1))
                m2[0:m.shape[0], 0:m.shape[1]] = m.copy()

            #print(f"m:{m.shape} -> m2:{m2.shape}")
                
        #change tiles randomly based on tile pattern set
        for i in range(np.prod(m2.shape)):
            c = i % m2.shape[1]
            r = math.floor(i / m2.shape[1])
            
            #replace tiles at position with randomly selected tile pattern
            tr = random.random()
            if tr <= self.mutRate:
                if self.rank_tp_sel:
                    tweights = [i for i in range(len(self.mut_tilepats),0,-1)]
                    rep_tp = random.choices(self.mut_tilepats,weights=tweights,k=1)[0]
                else:
                    rep_tp = random.choice(self.mut_tilepats)
                
                #keep within bounds
                h = min(m2.shape[0],r+self.tile_patt_size) - r  
                w = min(m2.shape[1],c+self.tile_patt_size) - c
                
                if h == 0 or w == 0:
                    continue
                
                m2[r:r+h, c:c+w] = rep_tp[:h,:w]
                
                
        return np.array(m2)
            
        
    #evolve a population from scratch for a number of epochs
    def train(self,iterations,randomInit=True,showPop=False,showSett=None):
        #initialize a new population if one not created already
        if len(self.population) == 0:
            self.new_pop(randomInit)
            self.changeFit = []
                    
        #don't show population as evolved
        all_pops = []
        with tqdm(total=iterations) as pbar:
            for e in range(iterations):
                pbar.update(1)
                self.evolve_pop()
                self.changeFit.append(self.avg_pop_fit())  #append the averaged population fitness to show changes
                pbar.set_description(f'iter: {1 + e} - fit: {self.high_pop_fit():.2f} - N: {self.avg_pop_size():.2f}')
                
                if showPop:
                    #showMultiMaps(self.population,self.tileset.tileFile)
                    all_pops.append(self.population)


        #export to a gif
        if showPop:
            tn = self.tileset.tileFile

            outGifname=f"anim_{tn}.gif"
            offset = 1
            fps=8

            #set the arguments if available
            if showSett:
                outGifname = outGifname if not showSett['name'] else showSett['name']
                offset = offset if not showSett['iter_off'] else showSett['iter_off']
                fps = fps if not showSett['fps'] else showSett['fps']

            utils.animateMapPopulation(all_pops[::offset],tn,[f"#{i}" for i in range(iterations)[::offset]],outGif=outGifname,fps=fps)

        