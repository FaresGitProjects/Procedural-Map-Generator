
import numpy as np
import random
import imageio
from collections import deque
from copy import deepcopy

import profile
import pstats

# Biomes
#       Forest
#       Grasslands
#       Desert
#       Snowy
#       Mountains
#       Water
#       Null***
#       White Space***

# Non-Biome Locales
#       Port
#       Town
#       City
#       Capital

# Configuration Parameters
#       scale:       Int: The size of the map
#       percentFill: Float: The percentage of the map to fill with seeds
#       mode:        String: The PGA used -> multi-seed expansion - single-seed expansion
#       dominants:   Array[Float]: Chance of each biome being expanded [F, G, D, S, M]    
#       d-bias:      Array[Float]: Chance of a specific direction being expanded

# brown: rgb(255,235,205)

class Biomes:
    FOREST: tuple = (50, 100, 30)
    GRASSLAND: tuple = (90, 200, 20)
    DESERT: tuple = (230, 200, 150)
    SNOWY: tuple = (170, 230, 240)
    MOUNTAIN: tuple = (120, 120, 120)
    WATER: tuple = (10,10, 250)
    
    NULLSPACE: tuple = (0,0,0)
    SEED: tuple = (10,10, 250) #(255, 255, 255)
    
    @staticmethod
    def _bioset():
        return {key: value for key, value in vars(Biomes).items() if not (key.startswith('_') or key == "NULLSPACE" or  key == "SEED")}



class ProMapGenDriver:
    defconfig = {"scale": 10, "percentFill": None, "mode": "seed-biome", "rolls": None,
                 "biome-dist": [.2,.2,.2,.2,.2,.2], 
                 "direct-dist": {'U':.25,'R':.25,'D':.25,'L':.25}}
    
    def __init__(self, config = defconfig): 
        self.locales = ['C','T','P']
        self.seeds = []
        
        populate = lambda key: config[key] if key in config else self.defconfig[key]
        self.config = {k: populate(k) for k in self.defconfig.keys()}
        self.rolls = self.config["rolls"]
        self.map = [[Biomes.NULLSPACE for _ in range(config["scale"])] for _ in range(config["scale"])]

    def generate(self):
        if self.config["mode"] == "seed-biome":
            self._plantSeeds()
            self._expandSeeds()
        elif self.config["mode"] == "seed-continental":
            self._plantSeeds()
            
            
    def _scan(self, cmap: list):
        count = 0
        for i in range(len(cmap)):
            for j in range(len(cmap)):
                if cmap[i][j]==Biomes.SEED:
                    print(f"bad-coord:({i,j})")
                    count += 1
        print("count: ", count)
                
    
    def _plantSeeds(self):
        percentFill = self.config["percentFill"]
        scale = self.config["scale"]
        
        for _ in range(int(percentFill*(scale**2)) if percentFill != None else 1):
            # print(i)
            # Randomly select spot on map
            x = random.randint(0, scale-1)
            y = random.randint(0, scale-1)
            coord = [x, y]
                
            if self.map[coord[0]][coord[1]] != Biomes.SEED:
                self.map[coord[0]][coord[1]] = Biomes.SEED
                self.seeds.append(coord)
            else:
            # Spot occupied; Probe for next available space
                found = False
                while coord[0] < scale and not found:
                    while coord[1] < scale and not found:
                        # print(self)
                        if self.map[coord[0]][coord[1]] != Biomes.SEED:
                            self.map[coord[0]][coord[1]] = Biomes.SEED
                            self.seeds.append(deepcopy(coord))
                            found = True
                        coord[1] += 1
                    coord[1] = 0
                    coord[0] += 1
            
        self._scan(self.map)
    
    def _expandSeeds(self):
        bio_dist = self.config["biome-dist"]
        dir_dist = self.config["direct-dist"]
    
        def _expand(coord):
            x = coord[0]
            y = coord[1]
                
            biome = self.map[x][y]
            
            directions = {'U':[(x-1), y],'R':[x, (y+1)],'D':[(x+1), y],'L':[x, (y-1)]}
            mod_dir_dist = deepcopy(dir_dist)
            # Resolve directions
            
            # assert(len(directions)==len(mod_dir_dist))
            
            if x+1 >= self.config["scale"] or self.map[x+1][y] != Biomes.NULLSPACE:
                directions.pop('D')
                mod_dir_dist['D'] = 0
                
            if x-1 < 0 or self.map[x-1][y] != Biomes.NULLSPACE:
                directions.pop('U')
                mod_dir_dist['U'] = 0
                
            if y+1 >= self.config["scale"] or self.map[x][y+1] != Biomes.NULLSPACE:
                directions.pop('R')
                mod_dir_dist['R'] = 0
                
            if y-1 < 0 or self.map[x][y-1] != Biomes.NULLSPACE:
                directions.pop('L')
                mod_dir_dist['L'] = 0
            
            
            
            print(f"modified: {mod_dir_dist}")
            print(f"directions: {directions}")
            
            
            # probabilities = [ mod_dir_dist[k] for k in mod_dir_dist if mod_dir_dist[k] != 0 ]
            probabilities = { k:v for (k,v) in mod_dir_dist.items() if v != 0}
            
            
            # No Expansion - Remove from list
            if not directions:
                return -1
            
            rolls = self.config["rolls"]
            
            if rolls:
                rolls = random.randint(1, len(directions))
                print(f"rolls: {rolls}")
            
            expanded = [coord]
            for _ in range(rolls): 
                choice = random.choices(list(directions.keys()), list(probabilities.values()))[0]
                print(f"selection: { directions[choice] }")
                
                expa_co = directions[choice]
                expanded.append(expa_co)
                
                self.map[expa_co[0]][expa_co[1]] = biome
                
                directions.pop(choice)
                probabilities.pop(choice)
        
            print("\n")
            # Expanded
            return expanded
        
        self.seeds.sort()
        bset = Biomes._bioset()
        print(bset)
        # Beginning of BFS
        
        q_list = [deque([self.seeds[i]]) for i in range(len(self.seeds))]
        
        # Choose Biome for Seeds
        for q in q_list:
            self.map[q[0][0]][q[0][1]] = random.choices(list(bset.values()), bio_dist)[0]
        
        # for q in q_list:
        #     assert(self.map[q[0][0]][q[0][1]] != Biomes.SEED)
        
        
            
        

        print(f"\n{q_list}\n")
        print(f"\n{self.map}\n")
        print(f"\n{self.seeds}\n")
        
        
        while len(q_list) != 0: 
            print("q-len: ", len(q_list))
            i = 0
            while i < len(q_list):
                # self._scan(self.map)
                print("q[i]-len: ", len(q_list[i]))
                nu_q = deque()
                print("i: ",i)
                for j in range(len(q_list[i])):
                    print("j: ",j)
                    expanded = _expand(q_list[i][j])      
                    if expanded != -1:
                        [nu_q.append(item) for item in expanded]
                       
                if len(nu_q):
                    q_list[i] = nu_q
                else:
                    q_list.pop(i)
                i+=1
                
        

    
     
    
    def __str__(self) -> str:
        # Convert the array to a NumPy array
        print(self.map)
        try:
            numpy_depiction = np.array(self.map, dtype=np.uint8)
            imageio.imwrite('image.png', numpy_depiction)
        except Exception as e:
            print("Error Caught ========", e)
        return "NA"


if __name__ == "__main__":
    # main()
    pass

# Biomes
#       Forest
#       Grasslands
#       Desert
#       Snowy
#       Mountains
#       Water

#       Null***
#       White Space***



def main():
    pmg = ProMapGenDriver({"scale": 50, "percentFill": .08, "mode": "seed-biome", "rolls": 1,
                           "biome-dist": [.5, .5, .1, .1, .1, .1],
                           "direct-dist": {"U":.5, "R": .5, "D": .1, "L": .1}
                          })
    pmg.generate()
    
    print(pmg)
    
    
main()



# # code to be profiled
# profile.run("main()", "profile")

# # generate report
# p = pstats.Stats("profile")
# p.strip_dirs().sort_stats("time").print_stats()