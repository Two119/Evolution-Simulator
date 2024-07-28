from carnivore import *
sin_table = [math.sin(math.radians(i)) for i in range(360)]
cos_table = [math.cos(math.radians(i)) for i in range(360)]

class Herbivore:
    def __init__(self, x, y, _type_, traits, generation):
        self.x = x
        self.y = y

        self.type = _type_
        self.traits = traits
        self.food_requirement = traits[2]

        self.hunger = (self.food_requirement/1.8)
        self.delay = time.time()
        self.vital_status = 1

        self.vel = [0, 0]
        self.speed = traits[3]
        self.move_angle = secrets.choice(range(-180, 180))
        self.move_delay = time.time()

        self.rect = pygame.rect.Rect(x - self.traits[1], y - self.traits[1], self.traits[1]*2, self.traits[1]*2)

        self.target = None
        self.plant_target = None
        self.plant = None
        self.target_creature = None
        
        self.life_timer = time.time()
        
        self.gen = generation
        
        self.calculation_timer = time.time()
        self.run_angle = 0
        
    def new(self):
        if self.target == None:
            dists = [[], []]
            for count, creature in enumerate(creatures):
                if creature.type == self.type and creature.vital_status == 1 and creature.hunger <= creature.food_requirement/2 and creature.__hash__() != self.__hash__():  
                    dists[0].append(count)
                    dists[1].append(math.dist([self.x, self.y], [creature.x, creature.y]))
            if dists[1] != []:

                    self.target = dists[0][dists[1].index(min(dists[1]))]
                    self.target_creature = creatures[self.target]
                    creatures[self.target].target = creatures.index(self)
                    creatures[self.target].target_creature = self
                    creatures[dists[0][dists[1].index(min(dists[1]))]].target = creatures.index(self)

        
        if self.target != None:
            if self.target_creature in creatures:
                self.target = creatures.index(self.target_creature)
                if creatures[self.target].target != creatures.index(self):
                    self.target = None
                    self.target_creature = None
                    return
                self.move_angle = angle_between([(self.x, self.y), (creatures[self.target].x, creatures[self.target].y)])

                if self.rect.colliderect(creatures[self.target].rect):
                    new_color = secrets.choice([creatures[self.target].traits[0], self.traits[0]])
                    new_radius = secrets.choice([creatures[self.target].traits[1], self.traits[1]])
                    new_hunger = secrets.choice([creatures[self.target].traits[2], self.traits[2]])
                    new_speed = secrets.choice([creatures[self.target].traits[3], self.traits[3]])

                    to_vary = secrets.randbelow(7)

                    if to_vary == 2:

                        variation = secrets.randbelow(4)

                        if variation == 1:
                            addon = secrets.choice(range(-2, 2))

                            while addon == 0:
                                addon = secrets.choice(range(-2, 2))
                                
                            new_radius += addon * 2
                            
                            if addon > 0:
                                new_hunger -= addon
                                new_speed -= addon/3.5
                                
                            if addon < 0:
                                new_hunger += addon
                                new_speed += addon/5

                        if variation == 3:
                            addon = secrets.choice(range(-2, 2))

                            while addon == 0:
                                addon = secrets.choice(range(-2, 2))

                            new_speed += addon/5
                            if addon > 0:
                                new_hunger += addon
                            if addon < 0:
                                new_speed -= addon


                    recombined_traits = [new_color, new_radius, new_hunger, new_speed]
                    child = Herbivore(self.x, self.y, self.type, recombined_traits, self.gen + 1)
                    creatures.append(child)
                    self.hunger += 5
                    creatures[self.target].hunger += 5
                    creatures[self.target].target = None
                    self.target = None
            else:
                self.target = None
                self.target_creature = None
    def search_plants(self):
        if self.plant_target == None:
            dists = [math.dist((self.x, self.y), plant) for plant in plant_manager.plants]
       
            if len(dists) > 0:
                self.plant_target = dists.index(min(dists))
                self.plant = plant_manager.plants[self.plant_target]
            
        else:
            if self.plant in plant_manager.plants:
                self.move_angle = angle_between([(self.x, self.y), self.plant])
                if self.rect.collidepoint(self.plant):
                    plant_manager.plants.remove(self.plant)
                    self.hunger -= 4
            
                    if self.hunger <= 0:
                        self.hunger = 1
                        
                    self.plant_target = None
            else:
                self.plant_target = None
                self.plant = None

    def update(self):
        
        self.rect.x = self.x - self.traits[1]
        self.rect.y = self.y - self.traits[1]

        if time.time() - self.move_delay >= 0.25:
            self.move_angle += secrets.choice(range(-5, 5))

        if time.time() - self.delay >= 1.5:
            self.hunger += 1
            self.delay = time.time()

        if self.hunger > self.food_requirement:
            self.vital_status = 0
            
        self.search_plants()
            
        if self.hunger < self.food_requirement/2:
            self.new()
        else:
            self.target = None

        dists = [math.dist((self.x, self.y), (carnivore.x, carnivore.y)) for carnivore in carnivores]
        
        if min(dists) <= 200:
            
            best_average_dist = 0
            if (time.time() - self.calculation_timer) >= 0.25:
                for i in range(360):
                    check_point = [self.x + self.speed*cos_table[i]*15, self.y + self.speed*sin_table[i]*15]
                    avg_dist = 0
                    if check_point[0] <= - 1300 or check_point[0] >= win.get_width() + 1300:
                        avg_dist = -1000000
                        
                    if check_point[1] <= - 1300 or check_point[1] >= win.get_height() + 1300:
                        avg_dist = -1000000    
                                            
                    num_enemies = 0
                    for carnivore in carnivores:
                        if math.dist((self.x, self.y), (carnivore.x, carnivore.y)) <= 200:
                            avg_dist += math.dist(check_point, (carnivore.x, carnivore.y))
                            num_enemies += 1

                    avg_dist /= num_enemies
                    if avg_dist > best_average_dist:
                        best_average_dist = avg_dist
                        self.move_angle = i
                        self.run_angle = i
                self.calculation_timer = time.time()
            else:
                self.move_angle = self.run_angle
                
            for plant in plant_manager.plants:
                if math.dist((self.x, self.y), plant) <= 35 and (self.hunger > (self.food_requirement*2/3)):
                    self.move_angle = angle_between([(self.x, self.y), plant])
                    if self.rect.collidepoint(plant):
                        
                        plant_manager.plants.remove(plant)
                        
                        self.hunger -= 4
                        if self.hunger <= 0:
                            self.hunger = 1
                            
                        self.plant_target = None
                        self.plant = None
                        break
            
        if self.move_angle >= 360:
            self.move_angle = self.move_angle - 360
        if self.move_angle < 0:
            self.move_angle = 360 + self.move_angle 
            
        win.blit(herbivore_images[round(self.move_angle)], (self.x + cam_offset[0], self.y + cam_offset[1]))
            
        self.vel = [self.speed*math.cos(math.radians(self.move_angle)), self.speed*math.sin(math.radians(self.move_angle))]

        self.x += self.vel[0]
        self.y += self.vel[1]
        
        if self.x <= -1300 or self.y <= -1300:
            self.move_angle -= 180

            self.x -= self.vel[0]*2
            self.y -= self.vel[1]*2

        if self.x >= win.get_width() + 1300 or self.y >= win.get_height() + 1300:
            self.move_angle -= 180

            self.x -= self.vel[0]*2
            self.y -= self.vel[1]*2
            


pygame.init()

#traits[1] is radius
#traits[2] is food requirement
#traits[3] is speed
creatures = [Herbivore(secrets.choice(range(-1250, win.get_width() + 1250)), secrets.choice(range(-1250, win.get_height() + 1250)), secrets.randbelow(3), [[0, 0, 125], 10, 15, 5], 0) for i in range(100)]

font = pygame.font.SysFont("Arial", 32)
clock = pygame.Clock()

while True:
    win.fill((0, 0, 255))
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    plant_manager.update()

    if pygame.key.get_pressed()[pygame.K_RIGHT]:
        cam_offset[0] -= 8
    if pygame.key.get_pressed()[pygame.K_LEFT]:
        cam_offset[0] += 8

    if pygame.key.get_pressed()[pygame.K_UP]:
        cam_offset[1] += 8
    if pygame.key.get_pressed()[pygame.K_DOWN]:
        cam_offset[1] -= 8

    """if time.time() - overall_time >= 15:
        print("a")
        orig_ages = [(time.time() - creature.life_timer) for creature in creatures]
        sorted_ages = reversed(sorted(orig_ages))
        new_creatures = []
        for age in sorted_ages:
            new_creatures.append(orig_ages.index(age))
            orig_ages.remove(age)
        
        l = round(len(new_creatures)/4)
        for i in range(l):
            try:
                creatures.pop(new_creatures[i])
                deaths += 1
            except:
                pass
            
        overall_time = time.time()
    """
    [creature.update() for creature in creatures]
    [carnivore.update(creatures) for carnivore in carnivores]

    for count, creature in enumerate(creatures):
        if creature.vital_status == 0:
            creatures.pop(count)
            deaths += 1
            
    for count, carnivore in enumerate(carnivores):
        if carnivore.vital_status == 0:
            carnivores.pop(count)
            #deaths += 1        
    
    pygame.draw.rect(win, [125, 125, 125], pygame.Rect(0, 0, 450, 225))
    pop_text = font.render("Population: H - " + str(len(creatures)) + ", C - " + str(len(carnivores)), False, [0, 0, 0], [125, 125, 125])

    avg_speed = sum([(creature.traits[-1]) for creature in creatures])/len(creatures)
    avg_c_speed = sum([(carnivore.traits[-1]) for carnivore in carnivores])/len(carnivores)
    speed_text = font.render("Speed: H - " + str(round(avg_speed, 3)) + ", C - " + str(round(avg_c_speed, 3)), False, [0, 0, 0], [125, 125, 125])
    
    avg_size = sum([(creature.traits[1]) for creature in creatures])/len(creatures)
    avg_c_size = sum([(carnivore.traits[1]) for carnivore in carnivores])/len(carnivores)
    size_text = font.render("Radius: H - " + str(round(avg_size, 3)) + ", C - " + str(round(avg_c_size, 3)), False, [0, 0, 0], [125, 125, 125])
    
    food_req = sum([(creature.traits[-2]) for creature in creatures])/len(creatures)
    food_text = font.render("Food Req: " + str(round(food_req, 3)), False, [0, 0, 0], [125, 125, 125])
    
    gen_text = font.render("Gens alive: " + str(min([creature.gen for creature in creatures])) + ", " + str(max([creature.gen for creature in creatures])), False, [0, 0, 0], [125, 125, 125])
   
    d_text = font.render("Deaths: " + str(deaths), False, [0, 0, 0], [125, 125, 125])

    win.blit(pop_text, (10, 10))
    win.blit(size_text, (10, 50))
    win.blit(speed_text, (10, 90))
    win.blit(food_text, (10, 130))
    win.blit(gen_text, (10, 170))
    win.blit(d_text, (10, 210))

    """n_packs = 0
    for carnivore in carnivores:
        if carnivore.pack_leader == None:
            n_packs += 1
    print(n_packs, ", ", len(carnivores))"""
    
    pygame.display.update()