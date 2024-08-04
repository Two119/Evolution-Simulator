from carnivore import *
sin_table = [math.sin(math.radians(i)) for i in range(360)]
cos_table = [math.cos(math.radians(i)) for i in range(360)]

pygame.mixer.init()
songs = [pygame.mixer.Sound("song_" + str(i) + ".ogg") for i in range(1, 4)]
song_channel = pygame.mixer.Channel(0)
current_song = secrets.randbelow(3)
song_channel.play(songs[current_song])

class Button:
    def __init__(self, position, textures, function):
        self.textures = textures
        self.onlick = function[0]
        self.args = function[1]
        self.pos = position
        self.current = 0
        self.rect = self.textures[self.current].get_rect(topleft=self.pos)
        self.click_delay = 0
        self.max_delay = 500
        self.delaying = False
        self.clicksound = pygame.mixer.Sound("click.ogg")
    def update(self):
        self.current = 0
        if self.delaying:
            self.click_delay += 1
        if self.click_delay >= self.max_delay:
            self.delaying = False
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                if not self.delaying:
                    self.onlick(self.args)
                    self.clicksound.play()
            self.current = 1
        win.blit(self.textures[self.current], self.pos)
        self.rect = self.textures[self.current].get_rect(topleft=self.pos)

start_button_sheet = scale_image(pygame.image.load("start_buttons.png").convert(), 1.5)
stats_button_sheet = scale_image(pygame.image.load("stats_buttons.png").convert(), 1.5)
exit_button_sheet = scale_image(pygame.image.load("exit_buttons.png").convert(), 1.5)

start_button_spritesheet = SpriteSheet(start_button_sheet, [2, 1], [255, 255, 255]).sheet[0]
stats_button_spritesheet = SpriteSheet(stats_button_sheet, [2, 1], [255, 255, 255]).sheet[0]
exit_button_spritesheet = SpriteSheet(exit_button_sheet, [2, 1], [255, 255, 255]).sheet[0]

def set_state(x):
    global game_state
    game_state = 1
    
    
global show_stats
show_stats = False

def show_stats(x):
    global show_stats
    show_stats = not show_stats
    pygame.mouse.set_pos((pygame.mouse.get_pos()[0] + 100, pygame.mouse.get_pos()[1] + 100))

start_button = Button(((win.get_width()/2) - (start_button_sheet.get_width()/4), (win.get_height()/2) - (start_button_sheet.get_height()/4)), start_button_spritesheet, [set_state, 1])
stats_button = Button((15, 15), stats_button_spritesheet, [show_stats, 1])
exit_button = Button(((win.get_width()/2) - (exit_button_sheet.get_width()/4), (win.get_height()/2) - (exit_button_sheet.get_height()/4) + 96), exit_button_spritesheet, [lambda x: exit(), 1])

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
        self.shown_angle = self.move_angle

        self.target = None
        self.plant_target = None
        self.plant = None
        self.target_creature = None
        
        self.life_timer = time.time()
        
        self.gen = generation
        
        self.image = scale_image(herbivore_image, self.traits[1]/10)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        
        self.calculation_timer = time.time()
        self.run_angle = 0
        self.destination = [0, 0]
        
        self.final_image = None
        
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
                self.destination = [creatures[self.target].x, creatures[self.target].y]

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
                for i in range(25):
                    self.plant_target = dists.index(min(dists))
                    self.plant = plant_manager.plants[self.plant_target]
                    for carnivore in carnivores:
                        if math.dist((self.x, self.y), (carnivore.x, carnivore.y)) <= (min(dists)+200):
                            if math.dist(self.plant, (carnivore.x, carnivore.y)) <= 200:
                                dists[self.plant_target] = 10000
            
        else:
            if self.plant in plant_manager.plants:
                self.move_angle = angle_between([(self.x, self.y), self.plant])
                self.destination = self.plant
                if self.mask.overlap(plant_manager.mask, [self.plant[0] - self.x, self.plant[1] - self.y]):
                    plant_manager.plants.remove(self.plant)
                    self.hunger -= 4
            
                    if self.hunger <= 0:
                        self.hunger = 1
                        
                    self.plant_target = None
            else:
                self.plant_target = None
                self.plant = None

    def update(self):

        if time.time() - self.move_delay >= 0.25:
            self.move_angle += secrets.choice(range(-5, 5))

        if time.time() - self.delay >= 1.5:
            self.hunger += 1
            self.delay = time.time()

        if self.hunger > self.food_requirement:
            self.vital_status = 0
            
        
        if self.vital_status == 0:
            particle_sheet = SpriteSheet(self.final_image, [self.final_image.get_width()//4, self.final_image.get_height()//4], [255, 255, 255])

            colors = []
            positions = []
            for j, sheet in enumerate(particle_sheet.sheet):
                    for i, surf in enumerate(sheet):
                        colors.append(surf.get_at([0, 0]))
                        if not (colors[-1].r == 0 and colors[-1].g == 0 and colors[-1].b == 0):
                            positions.append([self.x + (i*4), self.y + (j*4)])
                        else:
                            colors.pop()
                        
            death_anims.append(DeathParticleManger((4, 4), positions, colors))
            
        self.search_plants()
            
        if self.hunger < self.food_requirement/2:
            self.new()
        else:
            self.target = None

        dists = [math.dist((self.x, self.y), (carnivore.x, carnivore.y)) for carnivore in carnivores]
        
        if min(dists) <= 200:
            
            best_average_dist = 0
            if (time.time() - self.calculation_timer) >= 0.5:
                for i in range(0, 360, 4):
                    check_point = [self.x + self.speed*cos_table[i]*30, self.y + self.speed*sin_table[i]*30]
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
                        self.destination = check_point
                        self.run_angle = i
                self.calculation_timer = time.time()
            else:
                self.move_angle = self.run_angle
                
            for plant in plant_manager.plants:
                if math.dist((self.x, self.y), plant) <= 35 and (self.hunger > (self.food_requirement*2/3)):
                    self.move_angle = angle_between([(self.x, self.y), plant])
                    self.destination = plant
                    self.plant = plant
                        
                    if self.mask.overlap(plant_manager.mask, [self.plant[0] - self.x, self.plant[1] - self.y]):
                        
                        plant_manager.plants.remove(plant)
                        
                        self.hunger -= 4
                        if self.hunger <= 0:
                            self.hunger = 1
                            
                        self.plant_target = None
                        self.plant = None
                        break
                    
        if self.shown_angle < self.move_angle:
            self.shown_angle += 3.5
        if self.shown_angle > self.move_angle:
            self.shown_angle -= 3.5
            
        new_image = pygame.transform.rotate(self.image, self.shown_angle + 90)
        self.final_image = new_image
        win.blit(new_image, (self.x + cam_offset[0], self.y + cam_offset[1]))
        self.mask = pygame.mask.from_surface(new_image)
        self.rect = new_image.get_rect(topleft=(self.x, self.y))
        
        #pygame.draw.line(win, [255, 255, 255], (self.x + cam_offset[0], self.y + cam_offset[1]), [self.destination[0] + cam_offset[0], self.destination[1] + cam_offset[1]], 8)
        
            
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
global game_state
game_state = 0

bg = pygame.image.load("bg.png").convert()
stats_font = pygame.font.Font("yoster.ttf", 24)
stats_table = scale_image(pygame.image.load("stats.png").convert(), 2)
title = scale_image(pygame.image.load("title.png").convert(), 2)
title.set_colorkey([255, 255, 255])
swap_color(title, [0, 0, 0], [254, 254, 254])
carnivore_deaths = 0
while True:
    win.fill((0, 0, 255))
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    if not song_channel.get_busy():
        current_song = secrets.randbelow(3)
        song_channel.play(songs[current_song])

    if game_state == 0:
        win.blit(bg, (0, 0))
        win.blit(title, ((win.get_width() - title.get_width())/2, (win.get_height() - title.get_height())/2 - 128))
        start_button.update()
        exit_button.update()
    else:
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            game_state = 0
            
            plant_manager = PlantManager()
            creatures.clear()
            creatures = [Herbivore(secrets.choice(range(-1250, win.get_width() + 1250)), secrets.choice(range(-1250, win.get_height() + 1250)), secrets.randbelow(3), [[0, 0, 125], 10, 15, 5], 0) for i in range(100)]
            
            start_traits = [[125, 0, 0], 10, 18, 6]
            
            carnivores.clear()
            
            carnivores = [Carnivore(secrets.choice(range(win.get_width() - 300, win.get_width() + 300)), secrets.choice(range(win.get_height() - 300, win.get_height() + 300)), secrets.randbelow(3), start_traits, 0) for i in range(10)]
            carnivores[0].pack = [carnivore.__hash__() for carnivore in carnivores[1:]]
            for carnivore in carnivores[1:]:
                carnivore.pack_leader = carnivores[0].__hash__()
                
            start_traits[0] = [0, 255, 0]
                
            carnivores_2.clear()
            carnivores_2 = [Carnivore(secrets.choice(range(win.get_width() - 800, win.get_width() + 800)), secrets.choice(range(win.get_height() - 800, win.get_height() + 800)), secrets.randbelow(3), start_traits, 0) for i in range(10)]
            carnivores_2[0].pack = [carnivore.__hash__() for carnivore in carnivores_2[1:]]
            for carnivore in carnivores_2[1:]:
                carnivore.pack_leader = carnivores_2[0].__hash__()

            carnivores = carnivores + carnivores_2
            
            death_anims.clear()
            
            deaths = 0
            
            carnivore_deaths = 0
            
            continue
        
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
        
        for count, creature in enumerate(creatures):
            if creature.vital_status == 0:
                creatures.pop(count)
                deaths += 1
                
        [carnivore.update(creatures) for carnivore in carnivores]
        
        for count, carnivore in enumerate(carnivores):
            if carnivore.vital_status == 0:
                carnivores.pop(count)
                carnivore_deaths += 1
        
        for anim in death_anims:
            anim.update()
            if anim.alpha <= 10:
                death_anims.remove(anim)
        
        #pygame.draw.rect(win, [125, 125, 125], pygame.Rect(0, 0, 450, 225))
        

        stats_button.update()
        
        if show_stats:
            
            win.blit(stats_table, [15, 111])
            
            h_pop_text = stats_font.render(str(len(creatures)), False, [127, 127, 127], [0, 0, 0])
            c_pop_text = stats_font.render(str(len(carnivores)), False, [127, 127, 127], [0, 0, 0])
            win.blit(h_pop_text, [247, 160])
            win.blit(c_pop_text, [464, 160])
            
            h_size_text = stats_font.render(str(round(sum([c.traits[1] for c in creatures])/len(creatures), 2)), False, [127, 127, 127], [0, 0, 0])
            c_size_text = stats_font.render(str(round(sum([c.traits[1] for c in carnivores])/len(carnivores), 2)), False, [127, 127, 127], [0, 0, 0])
            win.blit(h_size_text, [247, 205])
            win.blit(c_size_text, [464, 205])
            
            h_speed_text = stats_font.render(str(round(sum([c.speed for c in creatures])/len(creatures), 2)), False, [127, 127, 127], [0, 0, 0])
            c_speed_text = stats_font.render(str(round(sum([c.speed for c in carnivores])/len(carnivores), 2)), False, [127, 127, 127], [0, 0, 0])
            win.blit(h_speed_text, [247, 250])
            win.blit(c_speed_text, [464, 250])
            
            h_req_text = stats_font.render(str(round(sum([c.traits[-2] for c in creatures])/len(creatures), 2)), False, [127, 127, 127], [0, 0, 0])
            c_req_text = stats_font.render(str(round(sum([c.traits[-2] for c in carnivores])/len(carnivores), 2)), False, [127, 127, 127], [0, 0, 0])
            win.blit(h_req_text, [247, 295])
            win.blit(c_req_text, [464, 295])
            
            h_deaths_text = stats_font.render(str(deaths), False, [127, 127, 127], [0, 0, 0])
            c_deaths_text = stats_font.render(str(carnivore_deaths), False, [127, 127, 127], [0, 0, 0])
            win.blit(h_deaths_text, [252, 335])
            win.blit(c_deaths_text, [464, 335])
            
        """win.blit(pop_text, (10, 10))
        win.blit(size_text, (10, 50))
        win.blit(speed_text, (10, 90))
        win.blit(food_text, (10, 130))
        win.blit(gen_text, (10, 170))
        win.blit(d_text, (10, 210))"""

        """n_packs = 0
        for carnivore in carnivores:
            if carnivore.pack_leader == None:
                n_packs += 1
        print(n_packs, ", ", len(carnivores))"""
        
    pygame.display.update()