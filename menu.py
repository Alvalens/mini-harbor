from abc import ABC, abstractmethod
import random
import copy
import sys
import pygame
import pygame.gfxdraw
import mainClasses as Game
import TimeClass as Time
from mainClasses import Storm, Windy, Rainy
import sys

#initialize pygame
pygame.init()
pygame.font.init()

# abc = abstract base class
class Screen(ABC):
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()

    @abstractmethod
    def run(self):
        pass

# help screen class
# contain game instructions
class Help(Screen):
    def __init__(self, screen):
        super().__init__(screen)

    def run(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 24)

        # Read instructions from file
        with open("assets/simpleInstructions.txt", "r") as file:
            text = file.read().splitlines()
        
        wrapped_text = []
        max_width = 700
        for line in text:
            if font.size(line)[0] > max_width:
                # Wrap text if it exceeds max width
                words = line.split(" ")
                wrapped_line = ""
                for word in words:
                    if font.size(wrapped_line + word)[0] < max_width:
                        wrapped_line += word + " "
                    else:
                        wrapped_text.append(wrapped_line)
                        wrapped_line = word + " "
                wrapped_text.append(wrapped_line)
            else:
                wrapped_text.append(line)

        scroll_offset = 0
        max_scroll_offset = max(0, len(wrapped_text) * 30 - self.screen_height)

        while True:
            self.screen.fill((0, 0, 0))
            y_offset = 100 + scroll_offset  # start at top of screen
            for line in wrapped_text:
                text_surface = font.render(line, True, (255, 255, 255))
                text_rect = text_surface.get_rect(
                    left=50, top=y_offset)  # left-align text
                self.screen.blit(text_surface, text_rect)
                y_offset += 30

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset + 30)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                    scroll_offset = min(max_scroll_offset, scroll_offset - 30)

# button class
class Button():
    def __init__(self, x, y, w, h, text, font_size, font_color, rect_color, border_radius=15):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.SysFont(None, font_size)
        self.font_color = font_color
        self.rect_color = rect_color
        self.border_radius = border_radius
        self.click_sound = pygame.mixer.Sound(
            "assets/audio/btn.mp3")  # Load the click sound

        # Shadow attributes
        self.shadow_offset = 5
        self.shadow_rect = pygame.Rect(
            x + self.shadow_offset, y + self.shadow_offset, w, h)
        self.shadow_color = pygame.Color(20, 20, 20, 50)

    def draw(self, surface):
        # Draw shadow
        pygame.draw.rect(surface, self.shadow_color,
                         self.shadow_rect, border_radius=self.border_radius)

        # Draw button
        pygame.draw.rect(surface, self.rect_color, self.rect,
                         border_radius=self.border_radius)
        text_surface = self.font.render(self.text, True, self.font_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def on_click(self):
        self.click_sound.play()  # Play the click sound when the button is clicked

class StartButton(Button):
    def __init__(self, x, y):
        super().__init__(x, y, 200, 50, "Mulai", 50, (255, 255, 255), (83, 160, 101))


class ExitButton(Button):
    def __init__(self, x, y):
        super().__init__(x, y, 200, 50, "Keluar", 50, (255, 255, 255), (255, 0, 0))


class HelpButton(Button):
    def __init__(self, x, y):
        super().__init__(x, y, 200, 50, "Help", 50, (255, 255, 255), (255, 217, 61))
       

class PlayAgain(Button):
    def __init__(self, x, y):
        super().__init__(x, y, 200, 50, "Main Menu", 50, (255, 255, 255), (37, 150, 190))

    # override is_clicked method from Button class
    def is_clicked(self, pos): # check if the button is clicked
        if self.rect.collidepoint(pos):
            self.click_sound.play()
            return True
        else:
            return False

# loading screen class
# contain loading screen when the game is started
class LoadingScreen(Screen):
    def __init__(self, screen):
        super().__init__(screen)
        self.background_color = (0, 0, 0)
        self.font = pygame.font.SysFont(None, 50)
        self.text = "Tap to Continue"
        self.text_color = (255, 255, 255)
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2))

    def run(self): # run the loading screen
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return True

            self.screen.fill(self.background_color)
            self.screen.blit(self.text_surface, self.text_rect)
            pygame.display.update()

# start menu class
# contain start menu and game initialization when the game is started
class StartMenu(Screen):
    def __init__(self, screen):
        super(StartMenu, self).__init__(screen)
        self.wHeight = self.screen_height
        self.wWidth = self.screen_width
        # Create the buttons for the start menu
        self.buttons = []
        self.buttons.append(StartButton(
            self.screen_width // 2 - 100,
            self.screen_height // 2 - 50
        ))
        self.buttons.append(ExitButton(
            self.screen_width // 2 - 100,
            self.screen_height // 2 + 110
        ))
        self.buttons.append(HelpButton(
            self.screen_width // 2 - 100,
            self.screen_height // 2 + 30
        ))
        # Load the background image
        self.background_image = pygame.image.load("assets/newbg.png").convert()

        # Resize the background image to the same size as the screen
        self.background_image = pygame.transform.scale(
            self.background_image, (self.screen_width, self.screen_height))

        self.music_playing = False  # Flag to keep track of whether the music is playing

    def run(self):
        # Main loop
        while True:
            # Handle events
            if not pygame.mixer.music.get_busy():
                # Loop the music indefinitely if it's not already playing
                pygame.mixer.music.load("assets/audio/soundtrack menu.mp3")
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if button.is_clicked(event.pos):
                            button.on_click()
                            if button.text == "Mulai": # if start button is clicked then start the game
                                if self.music_playing:
                                    pygame.mixer.music.stop()
                                # camera (display) coordinates
                                display = pygame.display.set_mode(
                                    (self.wWidth, self.wHeight))
                                # world coordinates
                                wWidth = 1200
                                wHeight = 900
                                worldSurface = pygame.Surface(
                                    (wWidth, wHeight))
                                
                                clock = pygame.time.Clock()
                                # create objects weather
                                Storm1 = Storm(worldSurface=worldSurface, radius =60, speed_radius = 70, spawn_interval = 30000, first_minutes=1)
                                Storm2 = Storm(worldSurface=worldSurface, radius =70, speed_radius = 80, spawn_interval = 35000, first_minutes=5)
                                windy2 = Windy(worldSurface, 60, 70, 30000)
                                windy1 = Windy(worldSurface, 70, 80, 35000)
                                rainy1  = Rainy(worldSurface, 75, 85, 20000)
                                
                                # load resources
                                ubuntuLight30 = pygame.font.Font(
                                    "assets/fonts/Ubuntu-Light.ttf", 30)
                                ubuntuBold30 = pygame.font.Font(
                                    "assets/fonts/Ubuntu-Bold.ttf", 30)
                                ubuntu70 = pygame.font.Font(
                                    "assets/fonts/Ubuntu-Regular.ttf", 70)

                                MUSIC = ["assets/audio/soundtrack 1.mp3",
                                         "assets/audio/soundtrack 2.mp3",
                                         "assets/audio/soundtrack 3.mp3"]
                                pygame.mixer.music.set_endevent(
                                    pygame.USEREVENT)
                                pygame.mixer.music.load(
                                    MUSIC[random.randint(0, 2)])
                                pygame.mixer.music.play()

                                STOP_POLYGONS = [pygame.image.load("assets/stops/circle_dark.png").convert_alpha(),
                                                 pygame.image.load(
                                    "assets/stops/triangle_dark.png").convert_alpha(),
                                    pygame.image.load(
                                    "assets/stops/square_dark.png").convert_alpha()]

                                CARGO_POLYGONS = [pygame.image.load("assets/cargos/circle_light.png").convert_alpha(),
                                                  pygame.image.load(
                                    "assets/cargos/triangle_light.png").convert_alpha(),
                                    pygame.image.load(
                                    "assets/cargos/square_light.png").convert_alpha()]
                                
                                CARGO_ICON = pygame.image.load(
                                    "assets/icons/cargo.png").convert_alpha()

                                LANDS = [pygame.image.load("assets/maps/mapbaru.png").convert_alpha(),
                                         pygame.image.load(
                                    "assets/maps/mapr.png").convert_alpha(),
                                    pygame.image.load(
                                    "assets/maps/mapr.png").convert_alpha(),
                                    pygame.image.load(
                                    "assets/maps/mapbaru.png").convert_alpha()]

                                ICONS = [pygame.image.load("assets/icons/container.png").convert_alpha(),
                                         pygame.image.load(
                                    "assets/icons/line.png").convert_alpha(),
                                    pygame.image.load(
                                    "assets/icons/boat.png").convert_alpha(),
                                    pygame.image.load(
                                    "assets/icons/truck.png").convert_alpha()]

                                # pick and place a map
                                land = random.randint(0, 3)
                                
                                map_width, map_height = LANDS[land].get_size()
                                map_x = (wWidth - map_width) // 2
                                map_y = (wHeight - map_height) // 2
                                worldSurface.blit(LANDS[land], (map_x, map_y))
                                scaled_map = pygame.transform.scale(LANDS[land], (wWidth, wHeight))
                                world = Game.World(scaled_map)
                                validStops = [Game.CIRCLE, Game.TRIANGLE, Game.SQUARE]
                                
                                # scale images
                                scaledCargoPolygons = []
                                for polygon in CARGO_POLYGONS:
                                    scaledCargoPolygons.append(pygame.transform.smoothscale(polygon,
                                                                                            (world.cargoSize,
                                                                                             world.cargoSize)))

                                scaledIcons = []
                                for icon in ICONS:
                                    scaledIcons.append(pygame.transform.smoothscale(icon,
                                                                                    (int(world.stopSize*1.5),
                                                                                     int(world.stopSize*1.5))))

                                # point list for drawing boats and containers
                                rectPoints = [[[-world.cargoSize*1.5, world.cargoSize],
                                               [world.cargoSize*1.5, world.cargoSize],
                                               [world.cargoSize*1.5, - world.cargoSize],
                                               [-world.cargoSize*1.5, -world.cargoSize]],
                                
                                              [[-world.cargoSize, world.cargoSize/2],
                                               [0, world.cargoSize/2],
                                               [world.cargoSize, world.cargoSize/2],
                                               [world.cargoSize, - world.cargoSize/2],
                                               [0, -world.cargoSize/2],
                                               [-world.cargoSize, -world.cargoSize/2]]]
                                

                                def calculateCameraOffset(wWidth, wHeight, world):
                                    # calculate the scale and translation operations to move from
                                    # world coordinates to screen coordinates
                                    return [[wWidth/float(2*world.validStopDistanceX),
                                            wHeight/float(2*world.validStopDistanceY)],
                                            [world.width/2-world.validStopDistanceX,
                                            world.height/2-world.validStopDistanceY]]

                                def interpolateQuadratic(time, maxTime, minOutput, maxOutput):
                                    # interpolate between time range 0->maxTime, to the range minOutput->maxOutput
                                    # using two parabolas
                                    # get time in the interval [0, 1] as opposed to [0, maxTime]
                                    normalizedTime = float(time)/maxTime
                                    # these two functions make a nice in-out ease over [0, 1]
                                    # y = 2x^2           {x < 0.5}
                                    # y = -2(x-1)^2 + 1  {x >= 0.5}
                                    if (normalizedTime < 0.5):
                                        output = 2*(normalizedTime**2)
                                    elif (normalizedTime >= 0.5):
                                        output = -2 * \
                                            ((normalizedTime-1)**2)+1
                                    # map output to the desired output
                                    if (minOutput > maxOutput):
                                        return minOutput-output*abs(maxOutput-minOutput)
                                    return output*abs(maxOutput-minOutput)+minOutput

                                def interpolateLinear(time, maxTime, minOutput, maxOutput):
                                    # interpolate between the time range 0->maxTime to the range minOutput->maxOutput
                                    # using a line
                                    normalizedTime = float(time)/maxTime
                                    output = minOutput + \
                                        (maxOutput-minOutput)*normalizedTime
                                    return output

                                def getCargoMoveTime(cargosMoved):
                                    return max(interpolateLinear(cargosMoved, 900, 0.3, 0.07), 0.07)

                                def getNewStopTime(cargosMoved):
                                    return max(interpolateQuadratic(cargosMoved, 1000, 10, 2), 2)

                                def getNewCargoTime(cargosMoved):
                                    return max(interpolateLinear(cargosMoved, 1000, 3, 1.5), 1.5)

                                def getGameTimerTime(cargosMoved):
                                    return max(interpolateLinear(cargosMoved, 900, 1.0/70, 1.0/160), 1.0/160)

                                def getSwitchStopTime(cargosMoved):
                                    if cargosMoved < 400:
                                        return 10000
                                    return max(interpolateLinear(cargosMoved-400, 600, 50, 10), 10)

                                def togglePaused(paused, timers, world):
                                    paused = not paused
                                    for timer in timers:
                                        timer.toggleActive()
                                    for stop in world.stops:
                                        if stop.usingTimer:
                                            stop.timer.toggleActive()
                                    return paused

                                newStopTimer = Time.Time(Time.MODE_TIMER,
                                                         Time.FORMAT_TOTAL_SECONDS,
                                                         getNewStopTime(world.cargosMoved))
                                newCargoTimer = Time.Time(Time.MODE_TIMER,
                                                          Time.FORMAT_TOTAL_SECONDS,
                                                          getNewCargoTime(world.cargosMoved))
                                cargoMoveTimer = Time.Time(Time.MODE_TIMER,
                                                           Time.FORMAT_TOTAL_SECONDS,
                                                           getCargoMoveTime(world.cargosMoved))
                                switchStopTimer = Time.Time(Time.MODE_TIMER,
                                                            Time.FORMAT_TOTAL_SECONDS,
                                                            getSwitchStopTime(world.cargosMoved))
                                gainResourcesTimer = Time.Time(Time.MODE_TIMER,
                                                               Time.FORMAT_TOTAL_SECONDS,
                                                               Game.RESOURCE_GAIN_DELAY)
                                gameTimer = Time.Time(Time.MODE_STOPWATCH,
                                                      Time.FORMAT_TOTAL_SECONDS)
                                scaleDuration = 2
                                smoothScaleTimer = Time.Time(Time.MODE_TIMER,
                                                             Time.FORMAT_TOTAL_SECONDS,
                                                             scaleDuration)
                                # also make a list that points to the individual timers
                                # for operations on all of them
                                timers = [newStopTimer, newCargoTimer, cargoMoveTimer,
                                          switchStopTimer, gainResourcesTimer, gameTimer, smoothScaleTimer]

                                def drawBase():
                                    # draw the background, lines, and boats
                                    # by drawing the base before the overlay, the event processing loop
                                    # is able to detect clicks correctly as it uses colours to do initial
                                    # detection
                                    if paused:
                                        display.fill((25, 25, 25))
                                    else:
                                        None
                                        display.fill(
                                        Game.COLOURS.get("background"))
                                        
                                    display.blit(scaledWorldSurface,
                                                 (-cameraOffset[1][0]*cameraOffset[0][0],
                                                  -cameraOffset[1][1]*cameraOffset[0][1]),
                                                 None,
                                                 pygame.BLEND_MAX)
                                    # draw the weather
                                    weatherl = [Storm1, Storm2, windy1, windy2, rainy1]
                                    for weather in weatherl:
                                        weather.spawn(display, cameraOffset)
                                        
                                    for i, item in enumerate(world.lines):
                                        item.draw(
                                            display, 10, cameraOffset)
                                        for childLine in item.abandonedChildren:
                                            childLine.draw(
                                                display, 10, cameraOffset)
                                        if (item.segments == []
                                                and item.mouseSegments == []):
                                            world.lines.pop(i)
                                    for boat in world.boats:
                                        boat.draw(
                                            display, rectPoints, world.cargoSize, cameraOffset)
                                    if movingBoat != -1:
                                        movingBoat[0].movingClone.draw(
                                            display, rectPoints, world.cargoSize, cameraOffset)
                                    for movingClone in boatsToMove:
                                        movingClone.draw(display, rectPoints,
                                                         world.cargoSize, cameraOffset)

                                    for container in world.containers:
                                        container.draw(
                                            display, rectPoints, world.cargoSize, cameraOffset)

                                def drawOverlay():
                                    # draw all superimposed elements to the screen
                                    for boat in world.boats:
                                        boat.drawAllCargos(display, rectPoints,
                                                           world.cargoSize, cameraOffset)

                                    numTrucks = 0
                                    for line in world.lines:
                                        for segment in line.tempSegments:
                                            if segment.isTruck:
                                                numTrucks = numTrucks+1
                                                segment.drawTruck(display, 7, cameraOffset,
                                                                   worldSurface, 30/cameraOffset[0][0])

                                    world.resources[Game.TRUCK] = world.totalTrucks-numTrucks

                                    for i in range(len(Game.COLOURS.get("lines"))):
                                        indicatorCoords = (int(world.stopSize*(2.5+i)+(i*10)),
                                                           int(self.wHeight-world.stopSize*1.5))
                                        if i < len(world.lines):
                                            pygame.draw.circle(display,
                                                               Game.COLOURS.get(
                                                                   "lines")[i],
                                                               indicatorCoords,
                                                               world.stopSize/2)
                                        elif i < len(world.lines)+world.resources[Game.LINE]:
                                            pygame.draw.circle(display,
                                                               Game.COLOURS.get(
                                                                   "lines")[i],
                                                               indicatorCoords,
                                                               world.stopSize/2,
                                                               2)
                                        else:
                                            pygame.draw.circle(display,
                                                               Game.COLOURS.get(
                                                                   "whiteOutline"),
                                                               indicatorCoords,
                                                               world.stopSize/2,
                                                               2)

                                    for i, item in enumerate(scaledIcons):
                                        iconCoords = (int(self.wWidth                              # start from the right edge
                                                          # at least 2 icon widths from edge
                                                          - item.get_width()*(2+i)
                                                          # 20 px of space between each icon
                                                          - (i*20)
                                                          - item.get_width()/2),    # center shape at that point
                                                      int(self.wHeight                             # start from bottom edge
                                                          # one icon height away from edge
                                                          - item.get_height()
                                                          - item.get_height()/2))   # center shape at that point
                                        
                                        world.iconHitboxes[i] = pygame.Rect(iconCoords,
                                                                            (item.get_width(),
                                                                             item.get_height()))
                                        resourceText = ubuntuBold30.render(str(world.resources[i]),
                                                                           1,
                                                                           Game.COLOURS.get("whiteOutline"))
                                        display.blit(resourceText,
                                                     (iconCoords[0]+item.get_width()/2-resourceText.get_width()/2,
                                                      iconCoords[1]-35))
                                        display.blit(item,
                                                     iconCoords)

                                    for stop in world.stops:
                                        stop.draw(display,
                                                  stopView,
                                                  world.cargoSize,
                                                  cameraOffset)

                                    if pickingResource:
                                        size = ubuntuLight30.size(
                                            "Mendapat:  ") 
                                        width = ubuntuLight30.size(
                                            "Pilih resource: ")[0]

                                        background = pygame.Surface((size[0]+5+scaledIcons[0].get_width(),
                                                                    int(scaledIcons[0].get_height()*3.3+10)),
                                                                    pygame.SRCALPHA)
                                        background.fill((0, 0, 0, 150))
                                        display.blit(
                                            background, (self.wWidth-background.get_width(), 0))

                                        display.blit(ubuntuLight30.render("Mendapat:",
                                                                          1,
                                                                          Game.COLOURS.get("whiteOutline")),
                                                     (self.wWidth-size[0]-scaledIcons[resource].get_width(),
                                                     scaledIcons[resource].get_height()/2-size[1]/2+5))
                                        display.blit(scaledIcons[resource],
                                                     (self.wWidth-scaledIcons[resource].get_width()-5,
                                                     5))

                                        display.blit(ubuntuLight30.render("Pilih resource:",
                                                                          1,
                                                                          Game.COLOURS.get("whiteOutline")),
                                                     (self.wWidth-width,
                                                     scaledIcons[resource].get_height()*1.4))
                                        for option in options:
                                            display.blit(
                                                option[1], (option[2][0], option[2][1]))

                                    if window == "end" and not isScaling:
                                        # stop music
                                        pygame.mixer.music.stop()
                                        size = ubuntu70.size("Game Over")
                                        display.blit(ubuntu70.render("Game Over",
                                                                     1,
                                                                     Game.COLOURS.get("whiteOutline")),
                                                     (self.wWidth/2-size[0]/2,
                                                     40))
                                        size = ubuntuLight30.size("Pelabuhanmu penuh coy! :(")
                                        display.blit(ubuntuLight30.render("Pelabuhanmu penuh coy! :(",
                                                                          1,
                                                                          Game.COLOURS.get("whiteOutline")),
                                                     (self.wWidth/2-size[0]/2,
                                                     120))
                                        size = ubuntuLight30.size(str(world.cargosMoved)+" barang berhasil ditransportasi")
                                        display.blit(ubuntuLight30.render(str(world.cargosMoved)+" barang berhasil ditransportasi",
                                                                          1,
                                                                          Game.COLOURS.get("whiteOutline")),
                                                     (self.wWidth/2-size[0]/2,
                                                     170))
                                        #restart button
                                        Restart = PlayAgain(self.screen_width // 2 - 100,
                                                            self.screen_height - 180,)
                                        Restart.draw(display)
                                        pos = pygame.mouse.get_pos()
                                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                            if Restart.is_clicked(pos):
                                                Restart.on_click()
                                                self.run()

                                    display.blit(CARGO_ICON, (10, 8))
                                    display.blit(ubuntuLight30.render(str(world.cargosMoved),
                                                                      1,
                                                                      Game.COLOURS.get("whiteOutline")),
                                                 (50, 10))

                                cameraOffset = calculateCameraOffset(
                                    self.wWidth, self.wHeight, world)
                                scaledWorldSurface = pygame.transform.scale(worldSurface,
                                                                            (int(wWidth*cameraOffset[0][0]),
                                                                             int(wHeight*cameraOffset[0][1])))

                                stopView = int(
                                    world.stopSize*((cameraOffset[0][0]+cameraOffset[0][1])/2.0))
                                scaledStopPolygons = []
                                for polygon in STOP_POLYGONS:
                                    scaledStopPolygons.append(pygame.transform.smoothscale(polygon,
                                                                                           (stopView,
                                                                                            stopView)))

                                for shape in range(3):
                                    # spawn a square, circle, and triangle before the game starts,
                                    # trying as many times as needed
                                    while len(world.stops) < shape+1:
                                        world.addRandomStop(
                                            shape, scaledStopPolygons)
                                cameraOffset = calculateCameraOffset(
                                    self.wWidth, self.wHeight, world)
                                stopView = int(
                                    world.stopSize*((cameraOffset[0][0]+cameraOffset[0][1])/2.0))
                                for i in range(len(scaledStopPolygons)):
                                    scaledStopPolygons[i] = pygame.transform.smoothscale(STOP_POLYGONS[i],
                                                                                         (stopView, 
                                                                                          stopView))
                                scaledWorldSurface = pygame.transform.scale(worldSurface,
                                                                            (int(wWidth*cameraOffset[0][0]),
                                                                             int(wHeight*cameraOffset[0][1])))

                                window = "game"
                                running = True
                                isScaling = False        # if the window is zooming out
                                doneScaling = False      # if the game will no longer zoom out
                                pickingResource = False  # if the player is choosing a resource
                                movingLine = -1          # line being edited
                                clickedIcon = -1         # resource being added
                                movingBoat = -1          # boat/container being moved
                                
                                # holding list for boats/containers until they can be legally moved
                                boatsToMove = []
                                paused = False
                                
                                # some hitboxes get generated upon drawing,
                                # so let them generate before they are used
                                drawOverlay()

                                while running:
                                    drawBase()
                                    if world.cargosMoved >= 1000:
                                        world.boatSpeed = 0.5
                                    for event in pygame.event.get():
                                        # if the window's X button is clicked
                                        if event.type == pygame.QUIT:
                                            running = False
                                            sys.exit()
                                        elif event.type == pygame.KEYDOWN:
                                            # press space to pause the 
                                            if event.key == pygame.K_SPACE and window != "end":
                                                paused = togglePaused(
                                                    paused, timers, world)
                                                window = 'game'
                                        elif event.type == pygame.MOUSEBUTTONDOWN:
                                            if event.button == 1:
                                                movingLine = world.getClickedLine(
                                                    display.get_at(event.pos)[:3])
                                                clickedIcon = world.getClickedIcon(
                                                    event.pos)
                                                movingBoat = world.getClickedBoatLine(
                                                    display.get_at(event.pos)[:3])
                                                mouseObject = Game.MousePosition(
                                                    event.pos, cameraOffset)
                                                # if a line was clicked
                                                if movingLine > -1:
                                                    line = world.lines[movingLine]
                                                    line.isMoving = True
                                                    clickedSegment = line.getClickedSegment(event.pos,
                                                                                            mouseObject)
                                                    # create mouse segments and abandon
                                                    # segments on the track
                                                    if clickedSegment > -1:
                                                        line.createMouseSegments(clickedSegment,
                                                                                 mouseObject,
                                                                                 line.segments[clickedSegment].firstPoint,
                                                                                 line.segments[clickedSegment].lastPoint)
                                                        segmentToFollow = 0
                                                    else:
                                                        movingLine = -1
                                                # if an existing boat or container was clicked
                                                elif movingBoat > -1:
                                                    movingBoat = world.getClickedBoat(
                                                        event.pos, movingBoat)
                                                    if movingBoat != -1:
                                                        movingBoat[0].startMouseMove(
                                                        )
                                                # if the container icon was clicked to create a new container
                                                elif clickedIcon == Game.CONTAINER and world.resources[Game.CONTAINER] > 0:
                                                    mouseWorld = mouseObject.getWorld()
                                                    world.containers.append(Game.Container(
                                                        *mouseWorld, speed=world.boatSpeed))
                                                    world.resources[Game.CONTAINER] = world.resources[Game.CONTAINER]-1
                                                # if the boat icon was clicked to create a new container
                                                elif clickedIcon == Game.BOAT and world.resources[Game.BOAT] > 0:
                                                    mouseWorld = mouseObject.getWorld()
                                                    world.boats.append(Game.Boat(*mouseWorld, 
                                                                                 speed=world.boatSpeed))
                                                    world.resources[Game.BOAT] = world.resources[Game.BOAT]-1
                                                # if the new resource selection is showing
                                                elif pickingResource:
                                                    for option in options:
                                                        if option[2].collidepoint(event.pos):
                                                            pickingResource = False
                                                            if paused:
                                                                paused = togglePaused(
                                                                    paused, timers, world)
                                                                window = "game"
                                                            world.resources[option[0]
                                                                            ] = world.resources[option[0]]+1
                                                            if option[0] == Game.TRUCK:
                                                                world.totalTrucks = world.totalTrucks+3 # 2 trucks per resource
                                                # else try to create a new line
                                                else:
                                                    clickedIcon = -1
                                                    # see if any stops can create a new line
                                                    # dont use a for loop because we only want to
                                                    # find one new line
                                                    i = 0
                                                    while (i < len(world.stops)
                                                           and (not world.stops[i].withinRadius(mouseObject.x,
                                                                                                mouseObject.y,
                                                                                                Game.ENDPOINT_SEGMENT_DISTANCE))):
                                                        i = i+1
                                                    if i < len(world.stops) and world.resources[Game.LINE] > 0:
                                                        movingLine = world.createNewLine(mouseObject,
                                                                                         world.stops[i])
                                                        world.resources[Game.LINE] = world.resources[Game.LINE]-1
                                        elif event.type == pygame.MOUSEMOTION:
                                            # move the line around with the mouse
                                            if movingLine > -1:
                                                mouseObject.updateWithView(
                                                    event.pos, cameraOffset)
                                                line = world.lines[movingLine]
                                                # if there are enough Trucks for the segments being edited
                                                # to go over the water, restrict them
                                                if world.resources[Game.TRUCK]-len(line.mouseSegments) < 0:
                                                    for mouseSegment in line.mouseSegments:
                                                        mouseSegment.calculateData()
                                                    point = event.pos
                                                    if len(line.mouseSegments) == 1:
                                                        if line.mouseSegments[0].checkOverWater(worldSurface):
                                                            point = line.mouseSegments[0].getPointsOverWater(3, worldSurface)[
                                                                0]
                                                            mouseObject.updateWithWorld(
                                                                point)
                                                    elif (line.mouseSegments[0].checkOverWater(worldSurface)
                                                          and not line.mouseSegments[1].checkOverWater(worldSurface)):
                                                        segmentToFollow = 1
                                                    elif (line.mouseSegments[1].checkOverWater(worldSurface)
                                                          and not line.mouseSegments[0].checkOverWater(worldSurface)):
                                                        segmentToFollow = 0
                                                    elif (line.mouseSegments[0].checkOverWater(worldSurface)
                                                          and line.mouseSegments[1].checkOverWater(worldSurface)):
                                                        point = line.mouseSegments[segmentToFollow].getPointsOverWater(3, worldSurface)[
                                                            0]
                                                        mouseObject.updateWithWorld(
                                                            point)
                                                        
                                                    if point == event.pos:
                                                        world.lines[movingLine].processMouseSegments(world.stops,
                                                                                                     mouseObject,
                                                                                                     cameraOffset,
                                                                                                     worldSurface)
                                                else:
                                                    world.lines[movingLine].processMouseSegments(world.stops,
                                                                                                 mouseObject,
                                                                                                 cameraOffset,
                                                                                                 worldSurface)
                                                    
                                            # if the a boat is being clicked and moved, see if it can be
                                            # attached to a line
                                            elif movingBoat != -1:
                                                mouseObject.updateWithView(
                                                    event.pos, cameraOffset)
                                                movingBoat[0].movingClone.updateMouse(
                                                    mouseObject)
                                                segment = world.getSegmentFromWorld(mouseObject,
                                                                                    cameraOffset)
                                                if segment != -1:
                                                    if movingBoat[1] == "boat":
                                                        movingBoat[0].movingClone.unsnapFromLine(
                                                        )
                                                        movingBoat[0].movingClone.snapToLine(world.lines[segment[0]],
                                                                                             segment[1])
                                                    elif movingBoat[1] == "container":
                                                        movingBoat[0].movingClone.unsnapFromLine(
                                                        )
                                                        movingBoat[0].movingClone.snapToLine(
                                                            world.lines[segment[0]])
                                                else:
                                                    movingBoat[0].movingClone.unsnapFromLine(
                                                    )
                                                    
                                            # see if a newly created container can go to a line
                                            elif clickedIcon == Game.CONTAINER:
                                                mouseObject.updateWithView(
                                                    event.pos, cameraOffset)
                                                world.containers[-1].updateMouse(
                                                    mouseObject)
                                                line = world.getLineByHitbox(
                                                    mouseObject, cameraOffset)
                                                if line != -1:
                                                    world.containers[-1].unsnapFromLine()
                                                    world.containers[-1].snapToLine(
                                                        world.lines[line])
                                                else:
                                                    world.containers[-1].unsnapFromLine()
                                                    
                                            # see if a newly created boat can go to a line
                                            elif clickedIcon == Game.BOAT:
                                                mouseObject.updateWithView(
                                                    event.pos, cameraOffset)
                                                world.boats[-1].updateMouse(
                                                    mouseObject)
                                                # we have no way of isolating which line was
                                                # clicked on, so check every rect
                                                segment = world.getSegmentFromWorld(mouseObject,
                                                                                    cameraOffset)
                                                if segment != -1:
                                                    world.boats[-1].unsnapFromLine()
                                                    world.boats[-1].snapToLine(world.lines[segment[0]],
                                                                               segment[1])
                                                else:
                                                    world.boats[-1].unsnapFromLine()
                                                    
                                        elif event.type == pygame.MOUSEBUTTONUP:
                                            if event.button == 1:
                                                # commit changes made by the line being edited
                                                if movingLine > -1:
                                                    line = world.lines[movingLine]
                                                    line.isMoving = False
                                                    movingLine = -1
                                                    if len(line.mouseSegments) > 1:
                                                        line.tempSegments.insert(line.mouseSegments[0].index+1,
                                                                                 Game.Segment(line.mouseSegments[0].firstPoint,
                                                                                              line.mouseSegments[1].firstPoint,
                                                                                              line.mouseSegments[1].index))
                                                    line.update(
                                                        worldSurface, True)
                                                    # if the line has no segments, completely remove
                                                    # everything and return resources to the player
                                                    for i in range(len(world.lines)-1, -1, -1):
                                                        if len(world.lines[i].segments) == 0:
                                                            world.removeLine(
                                                                i)
                                                # queue an operation to move the boat
                                                elif movingBoat != -1:
                                                    if movingBoat[0].movingClone.isOnSegment:
                                                        boatsToMove.append(
                                                            movingBoat[0].movingClone)
                                                    elif world.getClickedIcon(event.pos) > -1:
                                                        boatsToMove.append(
                                                            movingBoat[0])
                                                    else:
                                                        movingBoat[0].stopMouseMove(
                                                        )
                                                    movingBoat = -1
                                                # create a new container on the line it was placed on
                                                elif clickedIcon == Game.CONTAINER:
                                                    if world.containers[-1].isOnSegment:
                                                        world.containers[-1].placeOnLine(True,
                                                                                         cameraOffset, world.cargoSize)
                                                    else:
                                                        world.containers.pop()
                                                        world.resources[Game.CONTAINER] = world.resources[Game.CONTAINER]+1
                                                    clickedIcon = -1
                                                # create a new boat on the line it was placed on
                                                elif clickedIcon == Game.BOAT:
                                                    if world.boats[-1].isOnSegment:
                                                        world.boats[-1].placeOnLine()
                                                    else:
                                                        world.boats.pop()
                                                        world.resources[Game.BOAT] = world.resources[Game.BOAT]+1
                                                    clickedIcon = -1
                                                    
                                        elif event.type == pygame.USEREVENT:  # music is done
                                            pygame.mixer.music.load(MUSIC[random.randint(0, 2)])
                                            pygame.mixer.music.play()
                                            
                                    #  add main menu btn to pause screen
                                    if paused and window == 'game':
                                        back = PlayAgain(self.screen_width // 2 - 100, self.screen_height // 2 - 50)
                                        back.draw(display)
                                        pos = pygame.mouse.get_pos()
                                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                            if back.is_clicked(pos):
                                                pygame.mixer.music.stop()
                                                self.run()
                                    # change boats speed based on weather
                                    world.boat_slow_storms(([Storm1, Storm2]))
                                    world.boat_speed_windys(([windy1, windy2]))
                                    world.boat_slow_rain(rainy1)
                                    
                        
                                    newStopTimer.tick()
                                    # if the timer to create a new stop has ended
                                    if newStopTimer.checkTimer(not doneScaling, getNewStopTime(world.cargosMoved)):
                                        stop = random.randint(0, 99)
                                        if stop < 55:  # 55% chance of making a circle stop
                                            stopInfo = world.addRandomStop(Game.CIRCLE,
                                                                           scaledStopPolygons)
                                        elif stop < 90:  # 90-55 = 35% chance for triangles
                                            stopInfo = world.addRandomStop(Game.TRIANGLE,
                                                                           scaledStopPolygons)
                                        elif stop < 100:  # 100-90 = 10% chance for squares
                                            stopInfo = world.addRandomStop(Game.SQUARE,
                                                                           scaledStopPolygons)
                                        if stopInfo[0]:  # the game area was expanded
                                            # start the animation to move the camera
                                            oldCameraOffset = copy.deepcopy(
                                                cameraOffset)
                                            newCameraOffset = calculateCameraOffset(
                                                self.wWidth, self.wHeight, world)
                                            isScaling = True
                                            smoothScaleTimer.restart()
                                        # the game area did not expand because it is done expanding
                                        elif stopInfo[1] and not doneScaling:
                                            oldCameraOffset = copy.deepcopy(
                                                cameraOffset)
                                            newCameraOffset = calculateCameraOffset(
                                                self.wWidth, self.wHeight, world)
                                            isScaling = True
                                            smoothScaleTimer.restart()
                                            doneScaling = True

                                    switchStopTimer.tick()
                                    # if the timer to switch a common stop to a unique stop
                                    # has finished, restart and switch a stop
                                    if switchStopTimer.checkTimer(True):
                                        newShape = world.switchRandomStop(list(range(Game.SQUARE+1, Game.STAR+1)),
                                                                          validStops,
                                                                          worldSurface)
                                        # if a shape was switched and the new shape hasn't already
                                        # been generated
                                        if newShape != -1 and newShape not in validStops:
                                            # add the stop to the list of stops that cargos
                                            # can go to
                                            validStops.append(newShape)

                                    gainResourcesTimer.tick()
                                    # if the timer to give the player resources has ended,
                                    # give the player a random resource and let them choose
                                    # another one between two valid options
                                    if gainResourcesTimer.checkTimer(True) and not pickingResource:
                                        window = 'res'
                                        if not paused:
                                            paused = togglePaused(
                                                paused, timers, world)
                                            
                                        options = [0, 1, 2, 3]
                                        if world.resources[Game.LINE]+len(world.lines) > 6:
                                            options.remove(Game.LINE)
                                        resource = random.choice(options)
                                        world.resources[resource] = world.resources[resource]+1
                                        if resource == Game.TRUCK:
                                            world.totalTrucks = world.totalTrucks+3 # 2 trucks per resource
                                        pickingResource = True
                                        if world.resources[Game.LINE]+len(world.lines) > 6 and Game.LINE in options:
                                            options.remove(Game.LINE)
                                        else:
                                            options.remove(resource)
                                        if len(options) > 2:
                                            options.remove(
                                                random.choice(options))
                                        options[0] = [options[0],
                                                      scaledIcons[options[0]],
                                                      pygame.Rect(self.wWidth-scaledIcons[options[0]].get_width()*4,
                                                                  scaledIcons[options[0]].get_height(
                                                      )*2.3,
                                            scaledIcons[options[0]].get_width(
                                                      ),
                                            scaledIcons[options[0]].get_height())]
                                        options[1] = [options[1],
                                                      scaledIcons[options[1]],
                                                      pygame.Rect(self.wWidth-scaledIcons[options[1]].get_width()*2,
                                                                  scaledIcons[options[1]].get_height(
                                                      )*2.3,
                                            scaledIcons[options[1]].get_width(
                                                      ),
                                            scaledIcons[options[1]].get_height())]
                                        window = ''
                                    newCargoTimer.tick()
                                    newCargoProbability = min(interpolateLinear(
                                        world.cargosMoved, 1200, 30, 50), 50)
                                    # if the cargo spawn timer has finished,
                                    # restart it and add some cargos
                                    if newCargoTimer.checkTimer(True, getNewCargoTime(world.cargosMoved)):
                                        for stop in world.stops:
                                            # random chance for each stop to get a cargo
                                            if random.randint(0, 99) < newCargoProbability:
                                                stop.addRandomCargo(validStops,
                                                                    scaledCargoPolygons)

                                    cargoMoveTimer.tick()
                                    # timer that synchronizes and adds delay to all movements to/from stops
                                    if cargoMoveTimer.checkTimer(True, getCargoMoveTime(world.cargosMoved)):
                                        for stop in world.stops:
                                            for boat in stop.boats:
                                                world.cargosMoved = (world.cargosMoved
                                                                     + stop.processBoat(boat, boatsToMove))
                                            # start counting up with timers on stops if they are overcrowing
                                            if len(stop.cargos) > 6:
                                                if not stop.usingTimer:
                                                    stop.usingTimer = True
                                                    if not stop.timer.isActive:
                                                        stop.timer.toggleActive()
                                                if stop.timer.timeMode != Time.MODE_STOPWATCH:
                                                    stop.timer.tick()
                                                    stop.timer = Time.Time(Time.MODE_STOPWATCH,
                                                                           Time.FORMAT_TOTAL_SECONDS,
                                                                           stop.timer.time)
                                            # the stop is no longer overcrowding, so start making the timer
                                            # go back down
                                            else:
                                                if stop.usingTimer and stop.timer.timeMode == Time.MODE_STOPWATCH:
                                                    stop.timer.tick()
                                                    stop.timer = Time.Time(Time.MODE_TIMER,
                                                                           Time.FORMAT_TOTAL_SECONDS,
                                                                           stop.timer.time)
                                                if stop.timer.checkTimer(False):
                                                    stop.timer = Time.Time(Time.MODE_STOPWATCH,
                                                                           Time.FORMAT_TOTAL_SECONDS,
                                                                           0)
                                                    stop.usingTimer = False
                                                    if stop.timer.isActive:
                                                        stop.timer.toggleActive()
                                            # if the timer has counted past the threshold to lose the game
                                            if stop.timer.time > Game.LOSE_DURATION:
                                                if not paused:
                                                    paused = togglePaused(
                                                        paused, timers, world)
                                                    smoothScaleTimer.toggleActive()
                                                isScaling = True
                                                oldCameraOffset = copy.deepcopy(
                                                    cameraOffset)
                                                stopPosition = stop.getPosition()
                                                newCameraOffset = [[self.wWidth/150.0,
                                                                    self.wHeight/150.0],
                                                                   [stopPosition[0]-75,
                                                                    stopPosition[1]-75]]
                                                window = "end"
                                                smoothScaleTimer.restart()

                                    gameTimer.tick()
                                    timeElapsed = gameTimer.time
                                    gameTimer.restart(
                                        timeElapsed % getGameTimerTime(world.cargosMoved))
                                    # run the actual moving elements controlled by the game at a certain speed
                                    # independent of the speed the screen refreshes
                                    # (since the scaling animation is limited by the cpu and
                                    # using multithreading is overkill)
                                    for tick in range(int(timeElapsed/getGameTimerTime(world.cargosMoved))):
                                        for i in range(len(world.boats)-1, -1, -1):
                                            # move boats
                                            if world.boats[i].canMove:
                                                world.boats[i].move(
                                                    cameraOffset, world.cargoSize)
                                            # if there are no cargos on the boat and the boat
                                            # is in the list to move boats, move it
                                            if len(world.boats[i].cargos) == 0:
                                                # if the moving clone is in the list, that means it needs to
                                                # be moved into another line
                                                if world.boats[i].movingClone in boatsToMove:
                                                    boatsToMove.remove(
                                                        world.boats[i].movingClone)
                                                    if (world.boats[i].stop is not None
                                                            and world.boats[i] in world.boats[i].stop.boats):
                                                        world.boats[i].stop.boats.remove(
                                                            world.boats[i])
                                                    world.boats[i] = world.boats[i].moveLines(
                                                        cameraOffset, world.cargoSize)
                                                # if the boat itself is in the list, that means it needs
                                                # to be removed from the world
                                                elif world.boats[i] in boatsToMove:
                                                    boatsToMove.remove(
                                                        world.boats[i])
                                                    if world.boats[i] in world.boats[i].stop.boats:
                                                        world.boats[i].stop.boats.remove(
                                                            world.boats[i])
                                                    for container in world.boats[i].containers:
                                                        world.containers.remove(
                                                            container)
                                                        world.resources[Game.CONTAINER] = world.resources[Game.CONTAINER]+1
                                                    world.boats[i].line.boats.remove(
                                                        world.boats[i])
                                                    world.boats[i].remove(
                                                    )
                                                    world.resources[Game.BOAT] = world.resources[Game.BOAT]+1
                                                    world.boats.pop(i)
                                        for i in range(len(world.containers)-1, -1, -1):
                                            # if the number of cargos on the boat is low enough
                                            # to take out a container:
                                            if (world.containers[i].head is not None
                                                    and (len(world.containers[i].findFirst().cargos)
                                                         <= len(world.containers[i].findFirst().containers)*6)):
                                                # move it to another line
                                                if world.containers[i].movingClone in boatsToMove:
                                                    boatsToMove.remove(
                                                        world.containers[i].movingClone)
                                                    # find the last container to move off
                                                    tail = world.containers[i].findLast(
                                                    )
                                                    # destination boat
                                                    boat = world.containers[i].movingClone.head
                                                    tail.moveLines(boat, len(boat.containers),
                                                                   cameraOffset, world.cargoSize)
                                                    world.containers[i].stopMouseMove(
                                                    )
                                                # remove it
                                                elif world.containers[i] in boatsToMove:
                                                    boatsToMove.remove(
                                                        world.containers[i])
                                                    tail = world.containers[i].findLast(
                                                    )
                                                    world.containers[i].stopMouseMove(
                                                    )
                                                    world.containers.remove(
                                                        tail)
                                                    tail.findFirst().containers.remove(tail)
                                                    tail.remove()
                                                    world.resources[Game.CONTAINER] = world.resources[Game.CONTAINER]+1

                                        for line in world.lines:
                                            # remove abandoned segments that are split off lines
                                            # if there are no boats or containers on them
                                            for i in range(len(line.abandonedChildren)-1, -1, -1):
                                                isClear = True
                                                if len(line.abandonedChildren[i].boats) > 0:
                                                    isClear = False
                                                for boat in line.boats:
                                                    for container in boat.containers:
                                                        if container.line == line.abandonedChildren[i]:
                                                            isClear = False
                                                if isClear:
                                                    line.abandonedChildren.pop(
                                                        i)

                                    if isScaling:
                                        # scale out the game view
                                        smoothScaleTimer.tick()
                                        for i, item in enumerate(cameraOffset):
                                            for j in range(len(item)):
                                                item[j] = interpolateQuadratic(scaleDuration-smoothScaleTimer.time,
                                                                               scaleDuration,
                                                                               oldCameraOffset[i][j],
                                                                               newCameraOffset[i][j])
                                        stopView = int(
                                            world.stopSize*((cameraOffset[0][0]+cameraOffset[0][1])/2.0))
                                        newWidth = int(
                                            wWidth*cameraOffset[0][0])
                                        newHeight = int(
                                            wHeight*cameraOffset[0][1])
                                        scaledWorldSurface = pygame.Surface(
                                            (newWidth, newHeight))
                                        pygame.transform.scale(worldSurface,
                                                               (newWidth,
                                                                newHeight),
                                                               scaledWorldSurface)
                                        for i in range(len(scaledStopPolygons)):
                                            scaledStopPolygons[i] = pygame.transform.smoothscale(STOP_POLYGONS[i],
                                                                                                 (stopView,
                                                                                                 stopView))
                                        if smoothScaleTimer.checkTimer(True):
                                            isScaling = False
                                            
                                    clock.tick(60)
                                    drawOverlay()
                                    pygame.display.update()

                            elif button.text == "Help":
                                help = Help(self.screen)
                                help.run()
                            elif button.text == "Keluar":
                                # Do something when the "Exit" button is clicked
                                pygame.quit()
                                sys.exit()

            # Draw the background
            self.screen.blit(self.background_image, (0, 0))
            # Draw the buttons
            for button in self.buttons:
                button.draw(self.screen)
            # Update the screen
            pygame.display.update()
