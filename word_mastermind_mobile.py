import random
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line

# Load words from a file
def load_words(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if len(line.strip()) == 5]

# List of words from file
WORD_LIST = load_words('english_words_5letters.txt')

ENGLISH_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class WordMastermindApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.secret_word = self.generate_word()
        self.guess_count = 0
        self.games_played = 0
        self.games_won = 0
        self.letter_labels = []
        self.keyboard_buttons = {}
        self.keyboard_letter_states = {char: 'default' for char in ENGLISH_ALPHABET}
        
    def generate_word(self):
        return random.choice(WORD_LIST)
    
    def check_guess(self, secret_word, guess):
        feedback = [''] * 5
        secret_word_letters = list(secret_word)
        guess_letters = list(guess)

        # 1st pass: Check for correct letters in correct positions (green)
        for i in range(5):
            if guess_letters[i] == secret_word_letters[i]:
                feedback[i] = 'green'
                secret_word_letters[i] = None
                guess_letters[i] = None

        # 2nd pass: Check for correct letters in wrong positions (yellow)
        for i in range(5):
            if guess_letters[i] is not None:
                if guess_letters[i] in secret_word_letters:
                    feedback[i] = 'yellow'
                    secret_word_letters[secret_word_letters.index(guess_letters[i])] = None
                    guess_letters[i] = None
        
        # 3rd pass: Remaining letters are not in the word (grey)
        for i in range(5):
            if feedback[i] == '':
                feedback[i] = 'grey'
                
        return feedback

    def build(self):
        # Fundo azul claro em vez de branco
        Window.clearcolor = (0.85, 0.92, 1, 1)  # Azul claro suave
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=8, spacing=5)
        
        # Header: Título e Regras lado a lado - MAIS ESPAÇO
        header_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=15)
        
        # Left side: Title + Instructions
        left_layout = BoxLayout(orientation='vertical', size_hint=(0.4, 1), spacing=3)
        title = Label(
            text='Word\nMastermind',
            font_size='22sp',
            color=(0, 0, 0, 1),
            bold=True,
            size_hint=(1, 0.7),
            halign='center',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        left_layout.add_widget(title)
        
        instructions = Label(
            text='Type 5-letter word',
            font_size='11sp',
            color=(0.3, 0.3, 0.3, 1),
            size_hint=(1, 0.3)
        )
        left_layout.add_widget(instructions)
        header_layout.add_widget(left_layout)
        
        # Right side: Rules - BEM ESPAÇADAS
        rules_text = (
            "Rules:\n"
            "• 5 letters, 6 attempts\n"
            "• Green = Correct spot\n"
            "• Yellow = Wrong spot\n"
            "• Grey = Not in word"
        )
        rules_label = Label(
            text=rules_text,
            font_size='11sp',
            color=(0, 0, 0, 1),
            halign='left',
            valign='middle',
            size_hint=(0.6, 1)
        )
        rules_label.bind(size=rules_label.setter('text_size'))
        header_layout.add_widget(rules_label)
        
        main_layout.add_widget(header_layout)
        
        # Input field - COMPACTO
        input_layout = BoxLayout(size_hint=(1, 0.07), spacing=5)
        self.guess_input = TextInput(
            hint_text='Enter word',
            multiline=False,
            font_size='18sp',
            size_hint=(0.65, 1)
        )
        self.guess_input.bind(on_text_validate=self.submit_guess)
        input_layout.add_widget(self.guess_input)
        
        submit_btn = Button(text='Submit', font_size='18sp', size_hint=(0.35, 1), bold=True)
        submit_btn.bind(on_press=self.submit_guess)
        input_layout.add_widget(submit_btn)
        
        main_layout.add_widget(input_layout)
        
        # Game grid (6 rows x 5 columns) - MUITO MAIOR!
        self.grid_layout = GridLayout(cols=5, spacing=8, size_hint=(1, 0.52), padding=10)
        for i in range(6):
            row = []
            for j in range(5):
                lbl = Label(
                    text='',
                    font_size='36sp',
                    color=(0, 0, 0, 1),
                    size_hint=(None, None),
                    size=(70, 70),
                    bold=True
                )
                # Fundo branco com borda preta (espaços vazios visíveis)
                with lbl.canvas.before:
                    Color(1, 1, 1, 1)  # Branco
                    lbl.rect = Rectangle(pos=lbl.pos, size=lbl.size)
                    Color(0, 0, 0, 1)  # Preto para borda
                    lbl.border = Line(rectangle=(lbl.x, lbl.y, lbl.width, lbl.height), width=2)
                
                def update_graphics(instance, value):
                    instance.rect.pos = instance.pos
                    instance.rect.size = instance.size
                    instance.border.rectangle = (instance.x, instance.y, instance.width, instance.height)
                
                lbl.bind(pos=update_graphics, size=update_graphics)
                self.grid_layout.add_widget(lbl)
                row.append(lbl)
            self.letter_labels.append(row)
        
        main_layout.add_widget(self.grid_layout)
        
        # Keyboard - COMPACTO
        keyboard_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.14), spacing=2)
        
        key_rows = [
            ENGLISH_ALPHABET[0:9],
            ENGLISH_ALPHABET[9:18],
            ENGLISH_ALPHABET[18:26]
        ]
        
        for row_str in key_rows:
            row_layout = BoxLayout(spacing=2)
            for char in row_str:
                btn = Button(
                    text=char,
                    font_size='12sp',
                    background_color=(1, 1, 1, 1),  # Fundo branco
                    color=(0, 0, 0, 1),              # Texto preto
                    bold=True,
                    background_normal='',
                    border=(2, 2, 2, 2)
                )
                # Adicionar borda preta visual
                with btn.canvas.before:
                    Color(0, 0, 0, 1)  # Preto
                    btn.border_line = Line(rectangle=(btn.x, btn.y, btn.width, btn.height), width=1.5)
                
                def update_btn_border(instance, value):
                    instance.border_line.rectangle = (instance.x, instance.y, instance.width, instance.height)
                
                btn.bind(pos=update_btn_border, size=update_btn_border)
                self.keyboard_buttons[char] = btn
                row_layout.add_widget(btn)
            keyboard_layout.add_widget(row_layout)
        
        main_layout.add_widget(keyboard_layout)
        
        # Reset button - COMPACTO
        reset_btn = Button(
            text='New Game',
            font_size='18sp',
            size_hint=(1, 0.06),
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        reset_btn.bind(on_press=self.reset_game)
        main_layout.add_widget(reset_btn)
        
        return main_layout

    def submit_guess(self, instance):
        guess = self.guess_input.text.lower().strip()
        
        # Validate length
        if len(guess) != 5:
            self.show_popup("Invalid Guess", "Please enter a 5-letter word.")
            return
        
        # Validate if word exists in dictionary
        if guess not in WORD_LIST:
            self.show_popup("Invalid Word", "This word is not in the dictionary.")
            return
        
        # Check guess
        feedback = self.check_guess(self.secret_word, guess)
        
        # Update grid - cores como na versão PC
        color_map = {
            'grey': (0.83, 0.83, 0.83, 1),    # lightgrey
            'yellow': (1, 1, 0, 1),            # yellow
            'green': (0.56, 0.93, 0.56, 1)    # lightgreen
        }
        
        text_color_map = {
            'grey': (0, 0, 0, 1),    # Texto PRETO para cinzento (como amarelo e verde)
            'yellow': (0, 0, 0, 1),  # Texto preto para amarelo
            'green': (0, 0, 0, 1)    # Texto preto para verde
        }
        
        for i in range(5):
            lbl = self.letter_labels[self.guess_count][i]
            lbl.text = guess[i].upper()
            lbl.color = text_color_map[feedback[i]]  # Cor do texto
            
            # Limpar canvas e redesenhar
            lbl.canvas.before.clear()
            with lbl.canvas.before:
                Color(*color_map[feedback[i]])
                lbl.rect = Rectangle(pos=lbl.pos, size=lbl.size)
                # Sem borda para letras preenchidas
                Color(0, 0, 0, 1)
                lbl.border = Line(rectangle=(lbl.x, lbl.y, lbl.width, lbl.height), width=2)
        
        # Update keyboard - cores como na versão PC com borda preta
        keyboard_color_map = {
            'grey': (0.83, 0.83, 0.83, 1),    # lightgrey
            'yellow': (1, 1, 0, 1),            # yellow
            'green': (0.56, 0.93, 0.56, 1)    # lightgreen
        }
        
        keyboard_text_color_map = {
            'grey': (0, 0, 0, 1),    # Texto PRETO para cinzento (como amarelo e verde)
            'yellow': (0, 0, 0, 1),  # Texto preto para amarelo
            'green': (0, 0, 0, 1)    # Texto preto para verde
        }
        
        state_precedence = {'default': 0, 'grey': 1, 'yellow': 2, 'green': 3}
        
        for i in range(len(guess)):
            letter = guess[i].upper()
            current_feedback_state = feedback[i]
            
            if letter in ENGLISH_ALPHABET:
                current_key_state = self.keyboard_letter_states.get(letter, 'default')
                
                new_precedence = state_precedence.get(current_feedback_state, 0)
                current_precedence = state_precedence.get(current_key_state, 0)
                
                if new_precedence > current_precedence:
                    self.keyboard_letter_states[letter] = current_feedback_state
                    btn = self.keyboard_buttons[letter]
                    btn.background_color = keyboard_color_map[current_feedback_state]
                    btn.color = keyboard_text_color_map[current_feedback_state]
                    
                    # Manter a borda preta
                    btn.canvas.before.clear()
                    with btn.canvas.before:
                        Color(0, 0, 0, 1)
                        btn.border_line = Line(rectangle=(btn.x, btn.y, btn.width, btn.height), width=1.5)
        
        # Check win condition
        if guess == self.secret_word:
            self.games_played += 1
            self.games_won += 1
            self.show_stats_popup(True)
            self.reset_game(None)
            return
        
        # Check loss condition
        self.guess_count += 1
        if self.guess_count >= 6:
            self.games_played += 1
            self.show_stats_popup(False)
            self.reset_game(None)
            return
        
        # Clear input
        self.guess_input.text = ''
    
    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def show_stats_popup(self, won):
        games_lost = self.games_played - self.games_won
        win_percentage = (self.games_won / self.games_played) * 100 if self.games_played > 0 else 0
        
        if won:
            message = f"You guessed the word: {self.secret_word.upper()}\n\n"
        else:
            message = f"The word was: {self.secret_word.upper()}\n\n"
        
        message += f"--- Statistics ---\n"
        message += f"Games played: {self.games_played}\n"
        message += f"Wins: {self.games_won}\n"
        message += f"Losses: {games_lost}\n"
        message += f"Win percentage: {win_percentage:.1f}%"
        
        popup = Popup(
            title="Congratulations!" if won else "Game Over!",
            content=Label(text=message),
            size_hint=(0.9, 0.5)
        )
        popup.open()
    
    def reset_game(self, instance):
        self.secret_word = self.generate_word()
        self.guess_count = 0
        self.guess_input.text = ''
        
        # Reset grid - voltar aos espaços vazios com borda
        for i in range(6):
            for j in range(5):
                lbl = self.letter_labels[i][j]
                lbl.text = ''
                lbl.color = (0, 0, 0, 1)  # Texto preto
                
                # Limpar e redesenhar com borda
                lbl.canvas.before.clear()
                with lbl.canvas.before:
                    Color(1, 1, 1, 1)  # Fundo branco
                    lbl.rect = Rectangle(pos=lbl.pos, size=lbl.size)
                    Color(0, 0, 0, 1)  # Borda preta
                    lbl.border = Line(rectangle=(lbl.x, lbl.y, lbl.width, lbl.height), width=2)
        
        # Reset keyboard - manter borda preta
        for letter in ENGLISH_ALPHABET:
            if letter in self.keyboard_buttons:
                btn = self.keyboard_buttons[letter]
                btn.background_color = (1, 1, 1, 1)  # Branco
                btn.color = (0, 0, 0, 1)              # Texto preto
                
                # Restaurar borda preta
                btn.canvas.before.clear()
                with btn.canvas.before:
                    Color(0, 0, 0, 1)
                    btn.border_line = Line(rectangle=(btn.x, btn.y, btn.width, btn.height), width=1.5)
                    
            if letter in self.keyboard_letter_states:
                self.keyboard_letter_states[letter] = 'default'

if __name__ == '__main__':
    WordMastermindApp().run()
S
