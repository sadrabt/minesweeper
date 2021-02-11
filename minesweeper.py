import random
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk


ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"
DIRECTIONS = (UP, DOWN, LEFT, RIGHT,
              f"{UP}-{LEFT}", f"{UP}-{RIGHT}",
              f"{DOWN}-{LEFT}", f"{DOWN}-{RIGHT}")
TALL_GRASS="dark green"
SHORT_GRASS="light green"
SCARED_POKEMON="yellow"
POKE_BALL="red"
POKEMON = "☺"
FLAG = "♥"
UNEXPOSED = "~"
EXPOSED = "0"
TASK_ONE="TSK 1"
TASK_TWO="TSK 2"
#images used
IMG_GRASS=Image.open("images/unrevealed.png")
IMG_0=Image.open("images/zero_adjacent.png")
IMG_1=Image.open("images/one_adjacent.png")
IMG_2=Image.open("images/two_adjacent.png")
IMG_3=Image.open("images/three_adjacent.png")
IMG_4=Image.open("images/four_adjacent.png")
IMG_5=Image.open("images/five_adjacent.png")
IMG_6=Image.open("images/six_adjacent.png")
IMG_7=Image.open("images/seven_adjacent.png")
IMG_8=Image.open("images/eight_adjacent.png")
POKEBALL=Image.open("images/pokeball.png")
CHARIZARD=Image.open("images/pokemon_sprites/charizard.png")
CYNDAQUIL=Image.open("images/pokemon_sprites/cyndaquil.png")
PIKACHU=Image.open("images/pokemon_sprites/pikachu.png")
PSYDUCK=Image.open("images/pokemon_sprites/psyduck.png")
TOGEPI=Image.open("images/pokemon_sprites/togepi.png")
UMBREON=Image.open("images/pokemon_sprites/umbreon.png")
IMAGES_LIST=[IMG_0, IMG_1, IMG_2, IMG_3, IMG_4, IMG_5, IMG_6, IMG_7, IMG_8, IMG_GRASS,POKEBALL, CHARIZARD, CYNDAQUIL, PIKACHU, PSYDUCK, TOGEPI, UMBREON]
class BoardModel(object):
    """ This is class is responsible for the internal game state"""
    def __init__(self,grid_size, num_pokemon):
        """initializes and instance of the BoardModel class
            Parameters:
                grid_size(int): size of the grid
                num_pokemon(int): number of pokemons
            Returns:
                None
        """
        self._grid_size=grid_size
        self._num_pokemon=num_pokemon
        self.game()
        self.generate_pokemons()

    def game(self):
        """Create Game string
            Parameters:
                None
            Returns:
                None
        """
        self._game= UNEXPOSED * self._grid_size ** 2
    def generate_pokemons(self):
        """Pokemons will be generated and given a random index within the game.

       Parameters:
            None
        Returns:
            None
        """
        cell_count = self._grid_size ** 2
        pokemon_locations = ()

        for _ in range(self._num_pokemon):
            if len(pokemon_locations) >= cell_count:
                break
            index = random.randint(0, cell_count-1)

            while index in pokemon_locations:
                index = random.randint(0, cell_count-1)

            pokemon_locations += (index,)

        self._pokemon_locations=pokemon_locations
    def position_to_index(self, position):
        """Convert the row, column coordinate in the grid to the game strings index.

        Parameters:
            position (tuple<int, int>): The row, column position of a cell.

        Returns:
            (int): The index of the cell in the game string.
        """
        y, x = position
        return y * self._grid_size + x
    def replace_character_at_index(self, index, character):
        """A specified index in the game string at the specified index is replaced by
        a new character.
        Parameters:
            index (int): The index in the game string where the character is replaced.
            character (str): The new character that will be replacing the old character.

        Returns:
            (str): The updated game string.
        """
        return self._game[:index] + character + self._game[index + 1:]
    def flag_cell(self, index):
        """Toggle Flag on or off at selected index. If the selected index is already
            revealed, the game would return with no changes.
            
            Parameters:
                index (int): The index in the game string where a flag is placed.
            Returns
                None
        """
        if self._game[index] == FLAG:
            self._game = self.replace_character_at_index( index, UNEXPOSED)

        elif self._game[index] == UNEXPOSED:
            self._game = self.replace_character_at_index(index, FLAG)
    def index_in_direction(self, index,  direction):
        """The index in the game string is updated by determining the
        adjacent cell given the direction.
        The index of the adjacent cell in the game is then calculated and returned.

        Parameters:
            index (int): The index in the game string.
            direction (str): The direction of the adjacent cell.

        Returns:
            (int): The index in the game string corresponding to the new cell position
            in the game.
            None for invalid direction.
        """
        # convert index to row, col coordinate
        col = index % self._grid_size
        row = index // self._grid_size
        if RIGHT in direction:
            col += 1
        elif LEFT in direction:
            col -= 1
        # Notice the use of if, not elif here
        if UP in direction:
            row -= 1
        elif DOWN in direction:
            row += 1
        if not (0 <= col < self._grid_size and 0 <= row < self._grid_size):
            return None
        return self.position_to_index((row, col))
    
    def neighbour_directions(self, index):
        """Seek out all direction that has a neighbouring cell.

        Parameters:
            index (int): The index in the game string.

        Returns:
            (list<int>): A list of index that has a neighbouring cell.
        """
        neighbours = []
        for direction in DIRECTIONS:
            neighbour = self.index_in_direction(index,  direction)
            if neighbour is not None:
                neighbours.append(neighbour)

        return neighbours
    def number_at_cell( self, index):
        """Calculates what number should be displayed at that specific index in the game.

        Parameters:
            index (int): Index of the currently selected cell

        Returns:
            (int): Number to be displayed at the given index in the game string.
        """
        if self._game[index] != UNEXPOSED:
            return int(self._game[index])

        number = 0
        for neighbour in self.neighbour_directions(index):
            if neighbour in self._pokemon_locations:
                number += 1

        return number
    def check_win(self):
        """Checking if the player has won the game.

        Parameters:
            None

        Returns:
            (bool): True if the player has won the game, false if not.

        """
        return UNEXPOSED not in self._game and self._game.count(FLAG) == len(self._pokemon_locations)
    
    def reveal_cells(self, index):
        """Reveals all neighbouring cells at index and repeats for all
        cells that had a 0.

        Does not reveal flagged cells or cells with Pokemon.

        Parameters:
            index (int): Index of the currently selected cell

        Returns:
            None
        """
        number =self.number_at_cell(index)
        self._game = self.replace_character_at_index(index, str(number))
        clear = self.big_fun_search(index)
        for i in clear:
            if self._game[i] != FLAG:
                number = self.number_at_cell( i)
                self._game = self.replace_character_at_index( i, str(number))
    def big_fun_search(self, index):
        """Searching adjacent cells to see if there are any Pokemon"s present.

        Find all cells which should be revealed when a cell is selected.

        For cells which have a zero value (i.e. no neighbouring pokemons) all the cell"s
        neighbours are revealed. If one of the neighbouring cells is also zero then
        all of that cell"s neighbours are also revealed. This repeats until no
        zero value neighbours exist.

        For cells which have a non-zero value (i.e. cells with neighbour pokemons), only
        the cell itself is revealed.

        Parameters:
            index (int): Index of the currently selected cell

        Returns:
            (list<int>): List of cells to turn visible.
        """
        queue = [index]
        discovered = [index]
        visible = []

        if self._game[index] == FLAG:
            return queue

        number = self.number_at_cell(index)
        if number != 0:
            return queue

        while queue:
            node = queue.pop()
            for neighbour in self.neighbour_directions(node):
                if neighbour in discovered:
                    continue

                discovered.append(neighbour)
                if self._game[neighbour] != FLAG:
                    number = self.number_at_cell(neighbour)
                    if number == 0:
                        queue.append(neighbour)
                visible.append(neighbour)
        return visible
    
    def get_game(self):
        """ Returns a representation of the game
            Parameters:
                None
            Returns:
            str: the game string    
        """
        return self._game
    def get_pokemon_locations(self):
        """ Return the indices for pokemon locations
            Parameters:
                None
            Returns:
                tuple<int>: indices of where the pokemons are
        """
        return self._pokemon_locations
    def get_num_attempted_catches(self):
        """ Returns the number of pokeballs placed on the board
            Paramters:
                None
            Returns:
                int: number of flags in the game string
        """
        return self._game.count(FLAG)
    def get_num_pokemon(self):
        """ return the number of pokemons
            Paramters:
                None
            Returns:
                int: number of pokemons
        """
        return self._num_pokemon

    def check_loss(self):
        """ Return true if game is lost and fase if not
            Parameters:
                None
            Returns:
                bool: if game is lost or not
        """
        for index in self._pokemon_locations:
            if self._game[index]!=FLAG and self._game[index]!=UNEXPOSED:
                return True
        return False
    def expose_pokemons(self):
        """Exposes all the pokemons on the board
            Parameters:
                None
            Returns:
                None
        """
        for index in self._pokemon_locations:
            self._game = self.replace_character_at_index( index, POKEMON)
    def set_game(self,game ):
        """sets the game string
            Parameters:
                game(str): game string
            Returns:
                None
        """
        self._game=game
    def set_pokemon_locations(self, locations):
        """sets the pokemon locations string
            Parameters:
                locations(tuple): tuple containing pokemon locations
            Returns:
                None
        """
        self._pokemon_locations=locations
        
class PokemonGame(object):
    """This class is responsible for Coommunication among classes and event handling"""
    def __init__(self, master, grid_size=10, num_pokemon=15,task=TASK_TWO):
        """Initilizes an instance of the PokemonGame class
            Parameters:
                master(tk.widget): master window
                grid_size(int): size of the grid
                num_pokemon(int): number of pokemons
                task(str): string indicating task
            Returns:
                None                
        """
        #initialise the view and model classes
        self._master=master
        self._grid_size=grid_size
        self._num_pokemon=num_pokemon
        self._task=task
        self._master.title("Pokemon: Got 2 Find Them All!")
        self._master.configure(background="#ffffff")
        self._label=tk.Label(self._master, text="Pokemon: Got 2 Find Them All!",
                             bg="#E06666", fg="white",height=2)
        self._label.pack( fill=tk.X, anchor=tk.N)
        self._model=BoardModel(self._grid_size,self._num_pokemon)
        
        if self._task==TASK_ONE:
            self._view=BoardView(self._master,self._grid_size)
            self._view.draw_board(self._model.get_game())
            self._view.pack(anchor=tk.N)
        else:
            #menubar
            self._menubar=tk.Menu(self._master)
            self._master.config(menu=self._menubar)
            self._filemenu=tk.Menu(self._menubar)
            self._menubar.add_cascade(label="File", menu=self._filemenu)
            self._filemenu.add_command(label="Save game", command=self.savegame)
            self._filemenu.add_command(label="Load game", command=self.openfile)
            self._filemenu.add_command(label="New game", command=self.newgame)
            self._filemenu.add_command(label="Restart game", command=self.resetgame)
            self._filemenu.add_command(label="Quit", command=self.terminate)

            #initilise other classes
            self._view=ImageBoardView(self._master,self._grid_size)
            self._view.draw_board(self._model.get_game())
            self._view.pack(anchor=tk.N)
            self._bar=StatusBar(self._master, self)
            self._bar.pack()
            self._mins=0
            self._secs=0
            self._bar.set_pokeballs(0,self._num_pokemon)
            self.update_time()
            
            
            
        self._view.bind('<Button-1>', self.left_click)
        self._view.bind('<Button-2>', self.right_click)
        self._view.bind('<Button-3>', self.right_click)
        
    def left_click(self, event):
        """reveals the cell that was left clicked and all the surrounding cells if zero pokemons around
            checks if game is lost or won 
            Parameters:
                event: coordinates of where the user clicked
            Returns:
                None
        """
        position=self._view.pixel_to_position(event)
        index=int(self._model.position_to_index(position))
        cell=self._model.get_game()[index]
        if cell==UNEXPOSED:
            self._model.reveal_cells(index)
            if self._model.check_loss():
                self._model.expose_pokemons()
                self._view.draw_board(self._model.get_game())
                if self._task==TASK_ONE:
                    messagebox.showinfo("Game Over!", "You scared the pokemons away!")
                    self._master.destroy()
                else:
                    #stop timer
                    self._master.after_cancel(self._timer_id)
                    awnser=messagebox.askyesno("Game Over!", "You lost! Do you wanna play again?")
                    if awnser:
                        self.newgame()
                    else:
                        self._master.destroy()
            elif self._model.check_win():
                self._view.draw_board(self._model.get_game())
                if self._task==TASK_ONE:
                    messagebox.showinfo("Game Won!", "You Won!")
                    self._master.destroy()
                else:
                    self._master.after_cancel(self._timer_id)
                    awnser=messagebox.askyesno("Game Won!", "You Won! Do you wanna play again?")
                    if awnser:
                        self.newgame()
                    else:
                        self._master.destroy()
            else:
                self._view.draw_board(self._model.get_game())
    def right_click(self, event):
        """Toggles the cell that was right clicked between poke ball and tall grass
            checks if game is won 
            Parameters:
                event: coordinates of where the user clicked
            Returns:
                None
        """
        position=self._view.pixel_to_position(event)
        index=int(self._model.position_to_index(position))
        cell=self._model.get_game()[index]
        if cell==UNEXPOSED  or cell==FLAG:
            if self._task==TASK_ONE:
                self._model.flag_cell(index)
            elif self._model.get_num_attempted_catches()<self._num_pokemon:
                self._model.flag_cell(index)
                self._bar.set_pokeballs(self._model.get_num_attempted_catches(),self._num_pokemon)
            elif cell==FLAG:
                self._model.flag_cell(index)
                self._bar.set_pokeballs(self._model.get_num_attempted_catches(),self._num_pokemon)
                
            if self._model.check_win():
                self._view.draw_board(self._model.get_game())
                if self._task==TASK_ONE:
                    messagebox.showinfo("Game Won!", "You Won!")
                    self._master.destroy()
                else:
                    self._master.after_cancel(self._timer_id)
                    awnser=messagebox.askyesno("Game Won!", "You Won! Do you wanna play again?")
                    if awnser:
                        self.newgame()
                    else:
                        self._master.destroy()
            else:
                self._view.draw_board(self._model.get_game())
    def newgame(self):
        """Creates a new game
            Parameters:
                None
            Returns:
                None
        """
        # the .after metheds add up if not stopped when new game is made
        self._master.after_cancel(self._timer_id)
        self._model.game()
        self._model.generate_pokemons()
        self._view.draw_board(self._model.get_game())
        self._bar.set_pokeballs(self._model.get_num_attempted_catches(),self._num_pokemon)
        self._mins=0
        self._secs=0
        self.update_time()
    def resetgame(self):
        """Reset the game board but not the pokemon locations
            Parameters:
                None
            Returns:
                None
        """
        
        self._master.after_cancel(self._timer_id)
        self._model.game()
        self._view.draw_board(self._model.get_game())
        self._bar.set_pokeballs(self._model.get_num_attempted_catches(),self._num_pokemon)
        self._mins=0
        self._secs=0
        self.update_time()
    def update_time(self):
        """updates time by 1 sec
            Parameters:
                None
            Returns:
                None
        """
        self._bar.update_timer(self._mins,self._secs)
        self._timer_id=self._master.after(1000, self.update_time)
        if self._secs<59:
            self._secs+=1
        else:
            self._secs=0
            self._mins+=1
    def terminate(self):
        """prompts the user for confirmation to terminate program
            Parameters:
                None
            Returns:
                None
        """
        awnser=messagebox.askyesno("Confirmation", "Are you sure you want to leave?")
        if awnser:
            self._master.destroy()
    def savegame(self):
        """saves game as a .txt file
            Parametrs:
                None
            Returns:
                None
        """

        filename=filedialog.asksaveasfilename(defaultextension=".txt",filetypes = (("text files","*.txt"),("all files","*.*")),
                                              title="Pokemon: Got 2 Find Them All!")
        if filename:
            fd= open(filename, 'w', encoding="utf-8")
            text=self._model.get_game()+"\n"+str(self._model.get_pokemon_locations())+"\n"+str(self._mins)+"\n"+str(self._secs)
            fd.write(text)
            fd.close()
    def openfile(self):
        """opens game file previously saved as txt
            Parameter:
                None
            Returns:
                None
        """
        filename=filedialog.askopenfilename(filetypes = (("text files","*.txt"),("all files","*.*")), title="Pokemon: Got 2 Find Them All!")
        if filename:
            fd=open(filename, 'r',encoding="utf-8")
            lines=fd.readlines()
            fd.close()
            if filename.endswith(".txt")  and len(lines)==4 and self.check_game_string(lines[0]) :
                try:
                    self._model.set_game(lines[0].strip())
                    self._model.set_pokemon_locations(eval(lines[1].strip().strip("(").strip(")")))
                    self._mins=int(lines[2].strip())
                    self._secs=int(lines[3].strip())
                    self._view.draw_board(self._model.get_game())
                    self._bar.set_pokeballs(self._model.get_num_attempted_catches(),self._num_pokemon)

                except:
                    messagebox.showerror("Corrupted File", "The file you tried to open is not compatiable")
            else:
                messagebox.showerror("Corrupted File", "The file you tried to open is not compatiable")
                
                    
                    
                

    def check_game_string(self, game):
        """checks to see if a string is suitable to be game string
            Parameters:
                game(str): game string
            Returns:
                bool: True if string is suitablefalse if not
        """
        if len(game)-1==game.count(UNEXPOSED)+game.count(EXPOSED)+ game.count("1")+game.count("2")+game.count("3")\
                      +game.count("4")+game.count("5")+game.count("6")+game.count("7")+game.count("8")+game.count(FLAG):
            return True
        else:
            return False
        

    
class BoardView(tk.Canvas):
    """This class handles the visual representation of the game for task one"""
    def __init__(self, master, grid_size, board_width=600,*args, **kwargs):
        """ intisilizes an instance of the BoardView class
            Parameters:
                master(object): tkinter window
                grid_size(int): size of the gird
                board_width(int); width and hieght of the canvas in pixels
            Returns:
                None
        """
        super().__init__(master, width=board_width, height=board_width,*args, **kwargs)
        self._grid_size=grid_size
        self._board_width=board_width
        self._square_size=round(self._board_width/self._grid_size)
        
        
        
    def draw_board(self, board):
        """Clears the canvas and draws the board using rectangles
            Paramteres:
                board(str):game string
            Returns:
                None
        """
        self.delete(tk.ALL)
        x=0
        y=0
        count=1
        for i in board:
            if i ==UNEXPOSED:
                self.create_rectangle(x,y,x+self._square_size,y+self._square_size, fill=TALL_GRASS)
            elif i==FLAG:
                self.create_rectangle(x,y,x+self._square_size,y+self._square_size, fill=POKE_BALL)
            elif i==POKEMON:
                self.create_rectangle(x,y,x+self._square_size,y+self._square_size, fill=SCARED_POKEMON)
            else:
                self.create_rectangle(x,y,x+self._square_size,y+self._square_size, fill=SHORT_GRASS)
                self.create_text(x+self._square_size/2,y+self._square_size/2, text=i)
            if count==self._grid_size:
                x=0
                y=y+self._square_size
                count=1
            else:
                x=x+self._square_size
                count+=1
    def pixel_to_position(self, event):
        """turn cordinates of an event to tuple representing the position of square
            Parameters:
                event: coordinates of an event
            Returns:
                tuple: row, col coordinates
        """
        
        x=(event.x-(event.x%self._square_size))/self._square_size
        y=(event.y-(event.y%self._square_size))/self._square_size
        return (y,x)
class StatusBar(tk.Frame):
    """This class handles the status bar features"""
    def __init__(self, master, parent):
        """initializes an instance of the status bar class
            Parameters:
                mater: the master window
            Returns:
                None
        """
        self._master=master
        self._parent=parent
        super().__init__(self._master, bg="#ffffff")


        pokeball=ImageTk.PhotoImage(Image.open("images/full_pokeball.png"))
        clock=ImageTk.PhotoImage(Image.open("images/clock.png"))



        #pokemon balls
        self._pokemon_frame=tk.Frame(self, bg="#ffffff")
        self._pokemon_frame.pack(side=tk.LEFT)
        self._pokemon_lbl=tk.Label(self._pokemon_frame, image=pokeball, borderwidth=0)
        self._pokemon_lbl.image=pokeball
        self._attempt_lbl=tk.Label(self._pokemon_frame, text=" attempted catches",bg="#ffffff")
        self._pokeballs_lbl=tk.Label(self._pokemon_frame, text=" pokeballs left",bg="#ffffff")
        self._pokemon_lbl.pack(side=tk.LEFT)
        self._attempt_lbl.pack(side=tk.TOP, anchor=tk.NW)
        self._pokeballs_lbl.pack(side=tk.LEFT, anchor=tk.NW)

        #timer
        self._timer_frame=tk.Frame(self, bg="#ffffff", padx=30)
        self._timer_frame.pack(side=tk.LEFT)
        self._clock_lbl=tk.Label(self._timer_frame, image=clock, borderwidth=0)
        self._clock_lbl.image=clock
        self._text_lbl=tk.Label(self._timer_frame, text="Time elapsed",bg="#ffffff")
        self._time_lbl=tk.Label(self._timer_frame, text="m  s",bg="#ffffff")
        self._clock_lbl.pack(side=tk.LEFT)
        self._text_lbl.pack(side=tk.TOP, anchor=tk.NW)
        self._time_lbl.pack(side=tk.LEFT, anchor=tk.NW)

        #buttons
        self._buttons_frame=tk.Frame(self, bg="#ffffff")
        self._buttons_frame.pack(side=tk.LEFT)
        self._newgame=tk.Button(self._buttons_frame, text="New game", bg="#ffffff",
                                relief=tk.GROOVE, command=lambda : PokemonGame.newgame(self._parent))
        self._resetgame=tk.Button(self._buttons_frame, text="Restart game", bg="#ffffff",
                                  relief=tk.GROOVE, command=lambda : PokemonGame.resetgame(self._parent))
        self._newgame.pack(pady=5)
        self._resetgame.pack(pady=5)

    def set_pokeballs(self, attempted, num_pokemon):
        """configures the widgets in the pokemon frame
            Parameters:
                attempted(int): number of pokeballs placed
                num_pokemon(int):  number of pokemons
            Returns:
                None
        """
        self._attempt_lbl.config(text="{} attempted catches".format(attempted))
        self._pokeballs_lbl.config(text="{} pokeballs left".format(num_pokemon-attempted))
                                 
    def update_timer(self, mins, secs):
        """Updates the timer label
            Parameters:
                mins(int): minutes since current game started
                secs(int): seconds since the last whle minute
            Returns:
                None
        """
        self._time_lbl.config(text="{}m {}s".format(mins, secs))
class ImageBoardView(BoardView):
    """This class handels the visual representation of the game for task two"""
    def __init__(self, master, grid_size, board_width=600,*args, **kwargs):
        """ intisilizes an instance of the BoardView class
            Parameters:
                master(object): tkinter window
                grid_size(int): size of the gird
                board_width(int); width and hieght of the canvas in pixels
            Returns:
                None
        """
        super().__init__(master, grid_size, board_width=600,*args, **kwargs)
        self._resized=[]
        for i in IMAGES_LIST:
            i=i.resize((self._square_size,self._square_size))
            self._resized.append(ImageTk.PhotoImage(i))  
    def draw_board(self, board):
        """Clears the canvas and draws the board using images
            Parameters:
                board(str): the game string
            Returns:
                None
        """
        self.delete(tk.ALL)
        #indexes in the IMAGE LIST
        unrevealed_index=9
        pokeball_index=10
        x=0
        y=0
        count=1
        for char in board:
            if char ==UNEXPOSED:
                self.create_image(x,y, image=self._resized[9], anchor=tk.NW)
            elif char==FLAG:
                self.create_image(x,y, image=self._resized[10], anchor=tk.NW)
            elif char==POKEMON:
                #find a random pokemon image from index 11 to 16 inclusive
                image_location=random.randint(11,16)
                self.create_image(x,y, image=self._resized[image_location], anchor=tk.NW)
            else:
                adjacent=int(char)
                self.create_image(x,y, image=self._resized[adjacent], anchor=tk.NW)
                
            if count==self._grid_size:
                x=0
                y=y+self._square_size
                count=1
            else:
                x=x+self._square_size
                count+=1           
        
                

        
        

def main():
    """main function of the game, creates tk window and PokemonGame class
        Parameter:
            None
        Returns:
            None
    """
    root = tk.Tk()
    game=PokemonGame(root)
    root.mainloop()
    
    
if __name__ == '__main__' :
    main()
    

    
