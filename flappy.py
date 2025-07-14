import pygame
import sys
import os
import json
import random
from datetime import datetime

# --------------------------- User Management ---------------------------

# represents a user in the system
class User:
    # initialize a new user with their username, password, and score system
    def __init__(self, username, password):
        self.username = username
        self.password = password
        # each user has a Score object to track their game progress
        self.score = Score() 

    # convert the user object to a dictionary for saving to a JSON file.
    # this includes username, password, current score, and high score.
    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "score": self.score.current_score,
            "high_score": self.score.high_score
        }

# tracks scores for a user
class Score:
    # initialize the score system with a current score of 0 and high score of 0
    def __init__(self):
        self.current_score = 0
        self.high_score = 0

    # increase the current score by 1 point 
    def increment(self):
        self.current_score += 1

    # reset the current score to 0
    def reset(self):
        self.current_score = 0

    # update the high score if the current score exceeds the stored high score
    def update_high_score(self):
        if self.current_score > self.high_score:
            self.high_score = self.current_score

    # display the current score and high score on the game screen.
    def display_score(self, screen, font, color=(25,25,112)):
        current_score_text = font.render(f"Score: {self.current_score}", True, color)
        high_score_text = font.render(f"High Score: {self.high_score}", True, color)

        # Position the score text on the top-left of the screen
        screen.blit(current_score_text, (10, 10))
        screen.blit(high_score_text, (10, 50))

# manages user accounts and score data stored in a JSON file
class UserDatabase:
    def __init__(self, db_filename="users.json"):
        # initialize the database with a filename for storing user data
        # if the file exists, load users from it; otherwise, create an empty database
        self.db_filename = db_filename
        self.load_users()
        
    # Load users from the JSON file into the 'self.users' dictionary.
    def load_users(self):
        # if the file doesn't exist, initialize an empty dictionary
        if os.path.exists(self.db_filename):
            with open(self.db_filename, 'r') as file:
                # load JSON data
                data = json.load(file)
                # transform the loaded data into User objects
                self.users = {
                    username: User(user_data["username"], user_data["password"],)
                    for username, user_data in data.items()
                } 
                # eet current and high scores for each user
                for username, user_data in data.items():
                    self.users[username].score.current_score = user_data.get("score", 0)
                    self.users[username].score.high_score = user_data.get("high_score", 0)
        else:
            # initalize an empty user dictionary
            self.users = {}

    # save the current state of the 'self.users' dictionary to the JSON file
    def save_users(self):
        with open(self.db_filename, 'w') as file:
            data = {
                # each user object is converted to a dictionary using the 'to_dict' method
                username: user.to_dict()
                for username, user in self.users.items()
            }
            # write the data to the file in JSON format
            json.dump(data, file, indent=4)

    # create a new user account if the username is not already taken
    def create_account(self, username, password):
        if username in self.users:
            # returns False if the username already exists
            return False
        # create a new user object
        new_user = User(username, password)
        # add the user to the dictionary
        self.users[username] = new_user
        # save the updated database to the JSON file
        self.save_users()
        # returns True if the account is successfully created
        return True

    # check if a username and password combination is valid for login
    def login(self, username, password):
        if username in self.users and self.users[username].password == password:
            return True
        return False

    # update the high score for a user if the new score is higher
    def update_high_score(self, username, new_score):
        # check if the user exists in the database
        if username in self.users:
            user = self.users[username]
            if new_score > user.score.high_score:
                user.score.high_score = new_score
                # save changes to the file
                self.save_users()
    
    # retrieve the high score for a given username
    def get_high_score(self, username):
        if username in self.users:
            return self.users[username].score.high_score
        # returns 0 if the user doesn't exist in the database
        return 0

# --------------------------- Display Screens ---------------------------

# function to display the initial menu screen where users can choose to log in or sign up
def display_initial_menu(screen):
    # large font for the title
    font = pygame.font.SysFont('Arial', 60)
    # smaller font for options
    small_font = pygame.font.SysFont('Arial', 40)

    while True:
        # event loop to handle user interactions
        for event in pygame.event.get():
            # Quit event to close the application
            if event.type == pygame.QUIT:
                pygame.quit()
                # exit the program when the user closes the window
                sys.exit() 
            # detect key presses
            elif event.type == pygame.KEYDOWN:
                # if 'L' is pressed, navigate to login
                if event.key == pygame.K_l:
                    return "login"
                # if 'S' is pressed, navigate to sign up
                elif event.key == pygame.K_s:
                    return "signup"

        # fill the screen with a background color (sky blue)
        screen.fill((135, 206, 235))

        # render the game title text and center it on the screen
        title_text = font.render("Flappy Bird", True, (25, 25, 112))
        screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 300))

        # render the options for login and signup and center them to the screen
        login_text = small_font.render("Press 'L' to Login", True, (25, 25, 100))
        signup_text = small_font.render("Press 'S' to Sign Up", True, (25, 25, 100))
        screen.blit(login_text, (screen.get_width() // 2 - login_text.get_width() // 2, 400))
        screen.blit(signup_text, (screen.get_width() // 2 - signup_text.get_width() // 2, 450))

        # update the display to show the changes
        pygame.display.flip()

# display the login screen and handle user authentication
# 'db' is the database object used for verifying user credentials
def display_login_screen(screen, db):
    font = pygame.font.SysFont('Arial', 50)
    small_font = pygame.font.SysFont('Arial', 30)

    # stores the username and password inputs
    username_input = ""
    password_input = ""
    # tracks which input field is active
    active_input = "username"
    # stores error messages to be displayed
    error_message = ""

    while True:
        # event loop to handle user interactions
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # switch between username and password fields
                if event.key == pygame.K_TAB:
                    active_input = "password" if active_input == "username" else "username"
                # press Enter to attempt login
                elif event.key == pygame.K_RETURN:
                    # call the database's login method to verify credentials
                    if db.login(username_input, password_input):
                        # return the username if login is successful
                        return username_input
                    else:
                        error_message = "Login failed. Try again."
                # delete the last character in the active input field
                elif event.key == pygame.K_BACKSPACE:
                    if active_input == "username":
                        username_input = username_input[:-1]
                    elif event.key == pygame.K_BACKSPACE:
                        password_input = password_input[:-1]
                # add the typed character to the active input field
                else:
                    if active_input == "username":
                        username_input += event.unicode
                    elif active_input == "password":
                        password_input += event.unicode

        # clear the screen with a background color
        screen.fill((100, 149, 237))

        # render the title text and center it on the screen
        title_text = font.render("Login", True, (0, 0, 0))
        screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 50))

        # draw the username input field
        username_label = small_font.render("Username:   ", True, (0, 0, 0))
        username_rect = pygame.Rect(screen.get_width() // 2 - 150, 200, 300, 50)
        pygame.draw.rect(screen, (255, 255, 255), username_rect, 0 if active_input == "username" else 1)
        username_text = small_font.render(username_input, True, (0, 0, 0))
        screen.blit(username_label, (username_rect.x - 120, username_rect.y - 30))
        screen.blit(username_text, (username_rect.x + 5, username_rect.y + (username_rect.height - username_text.get_height()) // 2))

        # instruction text for switching fields with 'Tab'
        text = small_font.render("Press 'Tab' to switch in other label", True, (173,216,230))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 1000))

        # draw the password input field
        password_label = small_font.render("Password:   ", True, (0, 0, 0))
        password_rect = pygame.Rect(screen.get_width() // 2 - 150, 300, 300, 50)
        pygame.draw.rect(screen, (255, 255, 255), password_rect, 0 if active_input == "password" else 1)
        password_text = small_font.render("*" * len(password_input), True, (0, 0, 0))
        screen.blit(password_label, (password_rect.x - 120, password_rect.y - 30))
        screen.blit(password_text, (password_rect.x + 5, password_rect.y + (password_rect.height - password_text.get_height()) // 2))

        # display the error message if login fails
        if error_message:
            error_text = small_font.render(error_message, True, (220,20,60))
            screen.blit(error_text, (screen.get_width() // 2 - error_text.get_width() // 2, 400))

        # update the display to show the changes
        pygame.display.flip()

# display the sign-up screen, allowing users to create a new account
def display_signup_screen(screen, db):
    font = pygame.font.SysFont('Arial', 50)
    small_font = pygame.font.SysFont('Arial', 30)

    # variables to store the entered username and password
    username_input = ""
    password_input = ""
    # default active input field = username
    active_input = "username"
    # message to display if account creation is successful
    success_message = ""
    # message to display if there is an error
    error_message = ""

    while True:
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # handle key events
            elif event.type == pygame.KEYDOWN:
                # switch between username and password fields
                if event.key == pygame.K_TAB:
                    active_input = "password" if active_input == "username" else "username"
                # press Enter to attempt sign up
                elif event.key == pygame.K_RETURN:
                    # check if username and password are filled
                    if not username_input:
                        error_message = "Username is required!"
                        # stores the current time for error message display
                        error_time = pygame.time.get_ticks()
                    elif not password_input:
                        error_message = "Password is required!"
                        # stores the current time for error message display
                        error_time = pygame.time.get_ticks()
                    # check if the username already exists
                    elif db.create_account(username_input, password_input):
                        success_message = "Account created successfully!"
                        error_message = ""
                        success_text = small_font.render(success_message, True, (152, 251, 152))
                        screen.blit(success_text, (screen.get_width() // 2 - success_text.get_width() // 2, 400))
                        pygame.display.flip()
                        # display success message for 2 seconds
                        pygame.time.wait(2000)
                        # exit the function to return to the main menu
                        return
                    else:
                        error_message = "Username already exists!"
                        # stores the current time for error message display
                        error_time = pygame.time.get_ticks()
                        success_message = ""
                # press Backspace to remove last character
                elif event.key == pygame.K_BACKSPACE:
                    if active_input == "username":
                        username_input = username_input[:-1]
                    elif active_input == "password":
                        password_input = password_input[:-1]
                # add characters to that input field
                else:
                    if active_input == "username":
                        username_input += event.unicode
                    elif active_input == "password":
                        password_input += event.unicode

        # background color for the signup screen
        screen.fill((70,130,180))

        # title of the sign-up screen
        title_text = font.render("Sign Up", True, (0, 0, 0))
        screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 50))

        # instruction text for switching fields with 'Tab'
        text = small_font.render("Press 'Tab' to switch in other label", True, (173,216,230))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 1000))

        # username input field
        username_label = small_font.render("Username:", True, (0, 0, 0))
        username_rect = pygame.Rect(screen.get_width() // 2 - 150, 200, 300, 50)
        pygame.draw.rect(screen, (255, 255, 255), username_rect, 0 if active_input == "username" else 1)
        username_text = small_font.render(username_input, True, (0, 0, 0))
        screen.blit(username_label, (username_rect.x - 120, username_rect.y - 30))
        screen.blit(username_text, (username_rect.x + 5, username_rect.y + (username_rect.height - username_text.get_height()) // 2))

        # password input field
        password_label = small_font.render("Password:", True, (0, 0, 0))
        password_rect = pygame.Rect(screen.get_width() // 2 - 150, 300, 300, 50)
        pygame.draw.rect(screen, (255, 255, 255), password_rect, 0 if active_input == "password" else 1)
        password_text = small_font.render("*" * len(password_input), True, (0, 0, 0))
        screen.blit(password_label, (password_rect.x - 120, password_rect.y - 30))
        screen.blit(password_text, (password_rect.x + 5, password_rect.y + (password_rect.height - password_text.get_height()) // 2))

        # success and error messages display
        if success_message:
            success_text = small_font.render(success_message, True, (152, 251, 152))
            screen.blit(success_text, (screen.get_width() // 2 - success_text.get_width() // 2, 500))

        if error_message and pygame.time.get_ticks() - error_time < 1400:
            error_text = small_font.render(error_message, True, (255, 98, 114))
            screen.blit(error_text, (screen.get_width() // 2 - error_text.get_width() // 2, 400))

        pygame.display.flip()

# display the main game menu
def display_game_menu(screen):
    font = pygame.font.SysFont('Arial', 50)
    small_font = pygame.font.SysFont('Arial', 30)

    while True:
        for event in pygame.event.get():
            # quit = inchide aplicatia
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # start the game when 'Enter' is pressed
                if event.key == pygame.K_RETURN:
                    return "start_game"

        # clear the screen and update the game menu
        screen.fill((135, 206, 235))
        title_text = font.render("Flappy Bird", True, (0, 0, 0))
        screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 100))

        start_text = small_font.render("Press 'Enter' to Start Game", True, (0, 0, 0))
        screen.blit(start_text, (screen.get_width() // 2 - start_text.get_width() // 2, 300))

        pygame.display.flip()

# display the 'Game Over' screen at the end of the game
def display_game_over_screen(screen, self):
    # fill the screen with another color
    screen.fill((188, 143, 143))
    
    font = pygame.font.SysFont('Arial', 60)
    small_font = pygame.font.SysFont('Arial', 40)

    # display "Game Over" message
    game_over_text = font.render("GAME OVER", True, (138, 0, 0))
    screen.blit(game_over_text, (screen.get_width() // 2 - game_over_text.get_width() // 2, 200))

    # display final score
    final_score_text = small_font.render(f"Final Score: {self.score_system.current_score}", True, (0, 0, 0))
    screen.blit(final_score_text, (screen.get_width() // 2 - final_score_text.get_width() // 2, 300)) 

    # display high score
    if(self.score_system.high_score < self.score_system.current_score):
        high_score_text = small_font.render(f"High Score: {self.score_system.current_score}", True, (0, 0, 0))
    else:
        high_score_text = small_font.render(f"High Score: {self.score_system.high_score}", True, (0, 0, 0))
    screen.blit(high_score_text, (screen.get_width() // 2 - high_score_text.get_width() // 2, 350)) 

    # update the screen
    pygame.display.flip()

    # wait for 3 seconds before closing the game
    pygame.time.wait(3000)

# display the pause menu during the game
def display_pause_menu(screen):
    font = pygame.font.SysFont('Arial', 60)
    small_font = pygame.font.SysFont('Arial', 40)
    
    pause_message = font.render("Game Paused", True, (25,25,112))
    # display instruction for resuming
    continue_message = small_font.render("Press 'R' to resume the game", True, (25,25,100))
    # display instruction for starting new game
    new_game_message = small_font.render("Press 'N' to start a new game", True, (25, 25, 100))
    # display instruction to quit the game
    quit_message = small_font.render("Press 'Q' to quit the game", True, (25,25,100))

    screen.fill((135,206,250))
    screen.blit(pause_message, (screen.get_width() // 2 - pause_message.get_width() // 2, 300))
    screen.blit(continue_message, (screen.get_width() // 2 - continue_message.get_width() // 2, 400))
    screen.blit(new_game_message, (screen.get_width() // 2 - new_game_message.get_width() // 2, 450))
    screen.blit(quit_message, (screen.get_width() // 2 - quit_message.get_width() // 2, 500))

    pygame.display.flip()

# display the screen of the game at the beggining
def display_start_screen(screen, self):
    # display a message instructing the player to press SPACE to start the game
    font = pygame.font.SysFont('Arial', 30)
    start_text = font.render("Press SPACE to start the game!", True, (0, 0, 0))
    
    # get the coordinates and dimensions of the bird
    bird_x, bird_y = self.bird.rect.centerx, self.bird.rect.centery
    bird_height = self.bird.rect.height          
    
    # calculate the position of the text to center it below the bird
    text_width, text_height = start_text.get_size()
    # center horizontally beneath the bird
    text_x = bird_x - text_width // 2
    # slightly below the bird's bottom edge
    text_y = bird_y + bird_height // 2 + 10
    
    # print the text onto the screen at the calculated position
    screen.blit(start_text, (text_x, text_y))


# --------------------------- Main Program ---------------------------

# initialize pygame
pygame.init()

# screen dimensions
length = 1940
width = 1200

# parameters for pipes
PIPE_WIDTH = 100
PIPE_HEIGHT = 600
# distance between top and bottom pipe
PIPE_GAP = 220
# speed at which pipes move
PIPE_SPEED = 7

# create game window
screen = pygame.display.set_mode((length, width))

# set window title
pygame.display.set_caption('FLAPPY BIRD')

# Bird class
class Bird:
    # constructor
    def __init__(self, x, y, image_path):
        # oordinates
        self.x = x
        self.y = y
        # load image
        self.image = pygame.image.load(image_path)
        # resize image
        self.image = pygame.transform.scale(self.image, (60, 60))
        # create a rectangle around the image
        self.rect = self.image.get_rect()
        # set the center of the image to the bird's position
        self.rect.center = (self.x, self.y)
        # bird speed (initially 0)
        self.speed = 0
        # bird starts with 3 lives
        self.lives = 3

    # move bird up
    def flap(self):
        # the speed that the bird goes up
        self.speed = -9

    # move bird down
    def apply_gravity(self):
        # update bird's position on the y-axis
        self.y += self.speed
        # update the rectangle position of the image
        self.rect.center = (self.x, self.y)
        # gravity 
        self.speed += 0.9
            
    # render and display the bird
    def render(self, screen):
        screen.blit(self.image, self.rect)

    # reduce bird's life
    def reduce_life(self):
        self.lives -= 1
        
# Pipe class
class Pipe:
    # constructor 
    def __init__(self):
        self.width = PIPE_WIDTH
        self.height = random.randint(100, PIPE_HEIGHT)

    # generate pipes (top and bottom)
    def generate_pipes(self):
        # position the pipe on the x-axis 
        self.x = length
        # top pipe (x, y, width, height)
        self.top = pygame.Rect(self.x, 0, self.width, self.height)
        height_bottom = length - PIPE_GAP - self.height
        start_bottom = self.height + PIPE_GAP
        # bottom pipe (x, y, width, height)
        self.bottom = pygame.Rect(self.x, start_bottom, self.width, height_bottom)

    # move the pipes
    def move(self):
        # move the pipes leftward
        self.x -= PIPE_SPEED
        self.top.x = self.x
        self.bottom.x = self.x

    # render and display the pipes
    def render(self, screen):
        # brown color
        pipe_color = (139, 69, 19)
        # draw top pipe
        pygame.draw.rect(screen, pipe_color, self.top)
        # draw bottom pipe
        pygame.draw.rect(screen, pipe_color, self.bottom)

    # check if pipe is off screen (to remove it)
    def is_off_screen(self):
        if self.x + self.width < 0:
            return 1
        return 0

# Collision detector class
class CollisionDetector:  
    # constructor
    def __init__(self, bird, pipes, screen_width, screen_height):
        self.bird = bird
        self.pipes = pipes
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.score = 0

    # detect collision with pipes or screen boundaries
    def detect_collision(self):
        collision_detected = False
        # iterate through pipes
        for pipe in self.pipes:
            # check collision with top pipe
            if self.bird.rect.colliderect(pipe.top):
                print("Collision with the top pipe!")
                collision_detected = True
            # check collision with bottom pipe
            if self.bird.rect.colliderect(pipe.bottom):
                print("Collision with the bottom pipe!")
                collision_detected = True
        
        # check collision with the top screen boundary
        if self.bird.y < 0:
            print("Collision with the top of the screen!")
            collision_detected = True
        # check collision with the bottom screen boundary
        if self.bird.y > self.screen_height - self.bird.rect.height:
            print("Collision with the bottom of the screen!")
            collision_detected = True

        # no collision detected
        return collision_detected

# Game class
class Game:
    # constructor
    def __init__(self):
        # backgrounds
        self.background_color = (135, 206, 235)
        self.background_color1 = (135, 206, 235)
        self.background_color2 = (255, 240, 208)
        self.background_color3 = (255, 209, 253)

        self.screen_width = length
        self.screen_height = width

        # game is running
        self.running = True
        # game starts when space is pressed
        self.game_started = False
        self.paused = False

        # initialize score system
        self.score_system = Score()

        # birds
        self.bird = Bird(length//2, width // 2, '/home/miruna/ia4/blue_bird.png')
        self.bird1 = Bird(length//2, width // 2, '/home/miruna/ia4/blue_bird.png')
        self.bird2 = Bird(length//2, width // 2, '/home/miruna/ia4/green_bird.png')
        self.bird3 = Bird(length//2, width // 2, '/home/miruna/ia4/beige_bird.png')
        
        # list of pipes
        self.pipes = []
        # time of last pipe generation
        self.last_pipe_time = pygame.time.get_ticks()
        # random pipe generation frequency
        self.next_pipe_frequency = random.randint(2500, 4500)
        self.collision_detector = CollisionDetector(self.bird, self.pipes, length, width)

        #i ground images (moving)
        self.ground_image = pygame.image.load('/home/miruna/ia4/iarba.png')
        self.ground_image1 = pygame.image.load('/home/miruna/ia4/iarba.png')
        self.ground_image2 = pygame.image.load('/home/miruna/ia4/flori.png')
        self.ground_image3 = pygame.image.load('/home/miruna/ia4/fluturi.png')
        self.ground_x = 0
        self.ground_y = self.screen_height - self.ground_image.get_height()
        
        # flags to indicate is the game reached level 2/3/4
        self.level_2_reached = False
        self.level_3_reached = False
        self.level_4_reached = False

    # handle user input (key presses)
    def process_input(self):
        for event in pygame.event.get():
            # close game
            if event.type == pygame.QUIT:
                self.running = False
            # handle key presses
            if event.type == pygame.KEYDOWN:
                # pause game
                if event.key == pygame.K_r:
                    self.paused = True
                # flap when space is pressed
                if event.key == pygame.K_SPACE:
                    if not self.game_started:
                        # start the game
                        self.game_started = True
                    self.bird.flap()
                      
    # check for collisions
    def check_collisions(self):
        # update pipes for collision detection
        self.collision_detector.pipes = self.pipes
        if self.collision_detector.detect_collision():
            # reduce life on collision
            self.bird.reduce_life()
            if self.bird.lives == 0:
                # end game if no lives remain
                self.running = False
            else:
                # reset game if bird still has lives
                self.reset_bird_and_pipes()
        else:
            # increment score if no collision
            self.score_system.increment()
    
    # generate pipes
    def generate_pipes(self):
        # check time
        time = pygame.time.get_ticks() - self.last_pipe_time
        if time > self.next_pipe_frequency:
            # generate new pipe
            new_pipe = Pipe()
            new_pipe.generate_pipes()
            # add pipe to list
            self.pipes.append(new_pipe)
            # update last pipe time
            self.last_pipe_time = pygame.time.get_ticks()
            # randomize next pipe frequency
            self.next_pipe_frequency = random.randint(2500, 4500)
            # adjust pipe frequency based on score (difficulty increase)
            if self.score_system.current_score > 4000:
                self.next_pipe_frequency = random.randint(2000, 3000)
            elif self.score_system.current_score > 10000:
                self.next_pipe_frequency = random.randint(1500, 2500)
            
    # move pipes
    def move_pipes(self):
        for pipe in self.pipes:
            pipe.move()
        # remove off-screen pipes
        valid_pipes = []
        for pipe in self.pipes:
            if not pipe.is_off_screen():
                valid_pipes.append(pipe)
        self.pipes = valid_pipes

    # render the game elements (bird, pipes, ground)
    def render(self):
        # fill background color
        screen.fill(self.background_color)
        # render the bird
        self.bird.render(screen)

        # render pipes
        for pipe in self.pipes:
            pipe.render(screen)

        # if the game didn't start, show start screen
        if not self.game_started:
            display_start_screen(screen, self)
    
    # update the ground position (scrolling effect)
    def render_ground(self):
        # move ground left
        self.ground_x -= 7

        # if the ground image has moved completely off-screen, reset its position
        if self.ground_x <= -self.ground_image.get_width():
            self.ground_x = 0
        # draw the ground at the current position
        screen.blit(self.ground_image, (self.ground_x, self.ground_y))
        # draw the second part of the ground to make it seem continuous
        screen.blit(self.ground_image, (self.ground_x + self.ground_image.get_width(), self.ground_y))

    # render user's lives
    def render_lives(self):
        # print lives as *
        font = pygame.font.SysFont('Arial', 40)
        lives_text = " * " * self.bird.lives
        text_surface = font.render(f"Lives: {lives_text}", True, (153, 76, 0))
        screen.blit(text_surface, (10, 10))

    # display the time
    def display_time_game(self):
        # calculate the time passed since the game started (in seconds)
        time_passed = pygame.time.get_ticks() // 1000
        font = pygame.font.SysFont('Arial', 30)
        # create the text for time
        time_text = font.render(f"Time: {time_passed}s", True, (0, 0, 0))
        # display it on the screen
        screen.blit(time_text, (40, self.screen_height - 10))
    
    # display time and date along with score information
    def display_time(self, score_system):
        # get the current date and time
        now = datetime.now()
        time_str = now.strftime('%H:%M:%S')
        date_str = now.strftime('%d-%m-%Y')

        font = pygame.font.SysFont('Arial', 30)

        # create texts for time, date, score, and high score
        time_text = font.render(f"Time: {time_str}", True, (0, 0, 0))
        date_text = font.render(f"Date: {date_str}", True, (0, 0, 0))
        score_text = font.render(f"Score: {score_system.current_score}", True, (0, 0, 0))
        high_score_text = font.render(f"High Score: {score_system.high_score}", True, (0, 0, 0))
        
        # display them on the screen
        screen.blit(time_text, (40, self.screen_height - 160))
        screen.blit(date_text, (40, self.screen_height - 120))
        screen.blit(score_text, (40, self.screen_height - 220))
        screen.blit(high_score_text, (40, self.screen_height - 260))

    # check for background/ground/bird transitions based on the score
    def check_level_transition(self):
        # after 300 points, the game theme is changed
        level_threshold = 300
        current_lvl = (self.score_system.current_score // level_threshold) % 3

        if current_lvl == 1 and not self.level_2_reached:
            self.level_2_reached = True
            self.level_3_reached = False
            self.level_4_reached = False

            # change background
            self.background_color = self.background_color2

            # change ground image
            self.ground_image = self.ground_image2

            # change bird
            # save current bird attributes
            bird_x = self.bird.x
            bird_y = self.bird.y
            bird_rect = self.bird.rect
            bird_rect_center = self.bird.rect.center
            bird_lives = self.bird.lives
            self.bird = self.bird2
            # redefine the position of the new bird to match the old one
            self.bird.x = bird_x
            self.bird.y = bird_y
            self.bird.rect = bird_rect
            self.bird.rect.center = bird_rect_center
            self.bird.lives = bird_lives
            self.collision_detector.bird = self.bird

        elif current_lvl == 2 and not self.level_3_reached:
            self.level_3_reached = True
            self.level_2_reached = False
            self.level_4_reached = False

            # change background
            self.background_color = self.background_color3

            # change ground image
            self.ground_image = self.ground_image3
            
            # change bird
            # save current bird attributes
            bird_x = self.bird.x
            bird_y = self.bird.y
            bird_rect = self.bird.rect
            bird_rect_center = self.bird.rect.center
            bird_lives = self.bird.lives
            self.bird = self.bird3
            # redefine the position of the new bird to match the old one
            self.bird.x = bird_x
            self.bird.y = bird_y
            self.bird.rect = bird_rect
            self.bird.rect.center = bird_rect_center
            self.bird.lives = bird_lives
            self.collision_detector.bird = self.bird

        elif current_lvl == 0 and not self.level_4_reached:
            self.level_4_reached = True
            self.level_2_reached = False
            self.level_3_reached = False

            # change background
            self.background_color = self.background_color1

            # change ground image
            self.ground_image = self.ground_image1

            # change bird
            # save current bird attributes
            bird_x = self.bird.x
            bird_y = self.bird.y
            bird_rect = self.bird.rect
            bird_rect_center = self.bird.rect.center
            bird_lives = self.bird.lives
            self.bird = self.bird1
            # redefine the position of the new bird to match the old one
            self.bird.x = bird_x
            self.bird.y = bird_y
            self.bird.rect = bird_rect
            self.bird.rect.center = bird_rect_center
            self.bird.lives = bird_lives
            self.collision_detector.bird = self.bird

    # start a new game by initializing all parameters
    def start_new_game(self):
        self.background_color = (135, 206, 235)
        self.background_color1 = (135, 206, 235)
        self.background_color2 = (255, 240, 208)
        self.background_color3 = (255, 209, 253)

        self.screen_width = length
        self.screen_height = width

        # game is running
        self.running = True
        # the game only starts after pressing the space bar
        self.game_started = False
        self.paused = False

        # birds
        self.bird = Bird(length//2, width // 2, '/home/miruna/ia4/blue_bird.png')
        self.bird1 = Bird(length//2, width // 2, '/home/miruna/ia4/blue_bird.png')
        self.bird2 = Bird(length//2, width // 2, '/home/miruna/ia4/green_bird.png')
        self.bird3 = Bird(length//2, width // 2, '/home/miruna/ia4/beige_bird.png')
        
        # pipes list
        self.pipes = []
        # time when the last pipe was created and the time for the next one
        self.last_pipe_time = pygame.time.get_ticks()
        self.next_pipe_frequency = random.randint(2500, 4500)
        self.collision_detector = CollisionDetector(self.bird, self.pipes, length, width)

        # ground image that will move
        self.ground_image = pygame.image.load('/home/miruna/ia4/iarba.png')
        self.ground_image1 = pygame.image.load('/home/miruna/ia4/iarba.png')
        self.ground_image2 = pygame.image.load('/home/miruna/ia4/flori.png')
        self.ground_image3 = pygame.image.load('/home/miruna/ia4/fluturi.png')
        self.ground_x = 0
        self.ground_y = self.screen_height - self.ground_image.get_height()
        
        self.level_2_reached = False
        self.level_3_reached = False
        self.level_4_reached = False

        # initialize current score = 0 for a new game
        self.score_system.current_score = 0

    # reset bird and pipes after collision
    def reset_bird_and_pipes(self):
        self.bird.x = self.screen_width // 2
        self.bird.y = self.screen_height // 2
        self.bird.speed = 0
        self.pipes.clear()
        self.game_started = False

    # main game loop
    def running_loop(self, db, clock, username):
        while self.running:
            # check if we need to transition to a new level
            self.check_level_transition()
            # user input command
            self.process_input()

            # drawing and displaying elements
            self.render()
            self.render_ground()
            self.render_lives()
            # display time and date
            self.display_time(self.score_system)
            # display time spent in the game
            self.display_time_game()

            if self.paused:
                # show the pause menu
                display_pause_menu(screen)
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        # pause the game
                        if event.key == pygame.K_r:
                            self.paused = False
                        # exit the game
                        elif event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
                        # start a new game
                        elif event.key == pygame.K_n:
                            self.start_new_game()
            
            if self.game_started and not self.paused:
                # generate pipes only after the game starts
                self.generate_pipes()
                # move pipes
                self.move_pipes()
                # check collisions
                self.check_collisions()
                self.bird.apply_gravity()

                # update the high score if needed
                if self.score_system.current_score > self.score_system.high_score:
                    db.update_high_score(username, self.score_system.current_score)
                                        
            # update the screen
            pygame.display.update()
            clock.tick(60)

        # show Game over screen if the game stopped          
        if not self.running:
            display_game_over_screen(screen, self)
            pygame.display.update()
            pygame.time.wait(3000) 
        pygame.display.update()
        pygame.quit()
        sys.exit()

    # main method to run the game
    def run(self):
        clock = pygame.time.Clock()
        db = UserDatabase()

        while True:
            choice = display_initial_menu(screen)
            if choice == "login":
                # display login screen
                username = display_login_screen(screen, db)
                if username:
                    while True:
                        high_score = db.get_high_score(username)
                        self.score_system.high_score = high_score
                        self.running_loop(db, clock, username)
                        
            elif choice == "signup":
                # check if the account was created successfully
                if display_signup_screen(screen, db):
                    print("Account created successfully!")
                    pygame.display.update()
                
                while True:
                    # after account creation, let the game begin
                    username = display_login_screen(screen, db) 
                    if username:
                        high_score = db.get_high_score(username)
                        self.score_system.high_score = high_score
                        self.running_loop(db, clock, username)

if __name__ == "__main__":
    main = Game()
    main.run()