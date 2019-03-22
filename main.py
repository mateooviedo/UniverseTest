# import kivy
import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.popup import Popup

# Import utils libraries
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager, Screen

# layouts
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

# Variables globals
answer_user = []

'''
  Definimos las screen
'''
class IntroScreen(Screen):
  def __init__(self, mainwid):
    super(IntroScreen, self).__init__()
    self.mainwid = mainwid

  
  def play(self):
    self.mainwid.go_menu()


  def exit(self):
    App().stop()


class GameEasyScreen(Screen):
  def __init__(self, mainwid):
    super(GameEasyScreen, self).__init__()
    self.mainwid = mainwid
    self.multi_answer, self.questions, self.buttons_select = [], [], []
    self.only_answer = ''
    self.if_next_question = False
    self.number_question = 0
    self.question_actual = ''

  def setup_game(self):
    # get questions easy
    questions_easy = JsonStore('Utils/Db/database_questions.json').get('Quest_Easy')
    self.questions = questions_easy
    self.multi_answer = []
    self.only_answer = ''
    self.in_game(self.questions)


  def in_game(self, questions):
    self.clear_widgets()
    if self.number_question == 0 or self.if_next_question:
      question = questions[self.number_question]
      box_layout = BoxLayout(orientation = 'vertical')
      # Validate if the question have multi answer
      label_text = ''
      self.question_actual = str(question.get('question'))
      if len(question.get('answers_correct')) > 1:
        label_text = str(question.get('question')) + ' (Mutiple seleccion)'
      else:
        label_text = str(question.get('question')) + ' (Unica respuesta)'
      # Create label widget for question
      label_question = Label(text = label_text)
      box_layout.add_widget(label_question)

      # layout grid to questions
      grid_layout_questions = GridLayout(cols = 1)

      # Create buttons for answers
      # Validate if is answer multiple
      if len(question.get('answers_correct')) > 1:
        for answer in question.get('answers_correct'):
          toggle_button_answer = ToggleButton(text = answer, group = 'questions')
          # bind toggle button
          toggle_button_answer.bind(on_press = self.select_multi_answer)
          grid_layout_questions.add_widget(toggle_button_answer)
        
        # Create buttons form incorrect answers
        for answer_incorrect in question.get('answers_incorrects'):
          toggle_button_answer = ToggleButton(text = answer_incorrect, group = 'questions')
          # bind toggle button
          toggle_button_answer.bind(on_press = self.select_multi_answer)
          grid_layout_questions.add_widget(toggle_button_answer)
      else:
        button_answer = Button(text = str(question.get('answers_correct')[0]))
        # bind button answer
        button_answer.bind(on_press = self.select_answer)
        grid_layout_questions.add_widget(button_answer)
        # Create buttons form incorrect answers
        for answer_incorrect in question.get('answers_incorrects'):
          button = Button(text = answer_incorrect)
          button.bind(on_press = self.select_answer)
          grid_layout_questions.add_widget(button)

      # add grid_questions_layout to box_layout
      box_layout.add_widget(grid_layout_questions)
    
      # validate if is the last question
      text_button = 'Finalizar'
      if (self.number_question + 1) < len(self.questions):
        text_button = 'Siguiente pregunta'

      # Create button to next_question
      btn_next_or_finish_question = Button(text = text_button)
      box_layout.add_widget(btn_next_or_finish_question)
      # bind next_question
      btn_next_or_finish_question.bind(on_press = self.next_question_or_finish)

      self.add_widget(box_layout)

  
  def select_multi_answer(self, instance):
    if instance.color == [1, 1, 1, 1]:
      instance.color = [0, 1, 1, 1]
      self.multi_answer.append(instance.text)
    else:
      instance.color = [1, 1, 1, 1]
      self.multi_answer.remove(instance.text)

  
  def select_answer(self, instance):
    if instance is not self.buttons_select:
      self.buttons_select.append(instance)

    for button in self.buttons_select:
      button.color = [1, 1, 1, 1]

    instance.color = [0, 1, 1, 1]
    self.only_answer = instance.text


  def next_question_or_finish(self, instance):
    # Validate if the user answer some question
    if len(self.multi_answer) == 0 and self.only_answer == '':
      # create popup
      box_content_popup = BoxLayout(orientation = 'vertical')
      button_close_popup = Button(text='Cerrar')
      label_popup = Label(text = 'Por favor seleccione una pregunta')
      box_content_popup.add_widget(label_popup)
      box_content_popup.add_widget(button_close_popup)
      popup = Popup(title = 'Información', content=box_content_popup, auto_dismiss=False)
      button_close_popup.bind(on_press=popup.dismiss)
      popup.open()
    else:
      # save answer user
      global answer_user
      answer = {}
      answer['question'] = self.question_actual
      if len(self.multi_answer) > 0:
        answer['answers_correct'] = self.multi_answer
      else:
        answer['answers_correct'] = []
        answer['answers_correct'].append(self.only_answer)

      answer_user.append(answer)
      self.if_next_question = True
      self.number_question += 1
      if self.number_question < len(self.questions):
        self.setup_game()
      else:
        self.mainwid.go_finish_game_screen()
      

class FinishGameScreen(Screen):
  def __init__(self, mainwid):
    super(FinishGameScreen, self).__init__()

  
  def setup(self):
    global answer_user
    print(answer_user)


class MenuScreen(Screen):
  def __init__(self, mainwid):
    super(MenuScreen, self).__init__()
    self.mainwid = mainwid

  
  def play_easy(self):
    global answer_user
    answer_user = []
    self.mainwid.go_game_easy()

  
  def play_medium(self):
    print('Medio')


  def play_expert(self):
    print('Experto')

  
  def exit(self):
    App().stop()


class MainWid(ScreenManager):
  def __init__(self, **kwargs):
    super(MainWid, self).__init__()
    # Definimos todas las screens
    self.IntroScreen = IntroScreen(self)
    self.MenuScreen = MenuScreen(self)
    self.GameEasyScreen = GameEasyScreen(self)
    self.FinishGameScreen = FinishGameScreen(self)

    # Creamos screen
    wid = Screen(name = 'UniverseTest')
    # Añadimos las screen a la screen principal
    wid.add_widget(self.IntroScreen)
    # Añadimos la screen principal al ScreenManager
    self.add_widget(wid)

    # Creamos screen
    wid = Screen(name = 'UniverseTest Menu')
    # Añadimos las screen a la screen principal
    wid.add_widget(self.MenuScreen)
    # Añadimos la screen principal al ScreenManager
    self.add_widget(wid)

    # Creamos screen
    wid = Screen(name = 'UniverseTest Game')
    # Añadimos las screen a la screen principal
    wid.add_widget(self.GameEasyScreen)
    # Añadimos la screen principal al ScreenManager
    self.add_widget(wid)

    # Creamos screen
    wid = Screen(name = 'UniverseTest Finish Game')
    # Añadimos las screen a la screen principal
    wid.add_widget(self.FinishGameScreen)
    # Añadimos la screen principal al ScreenManager
    self.add_widget(wid)

  def go_intro(self):
    self.current = 'UniverseTest'

  
  def go_menu(self):
    self.current = 'UniverseTest Menu'


  def go_game_easy(self):
    self.current = 'UniverseTest Game'
    self.GameEasyScreen.setup_game()


  def go_finish_game_screen(self):
    self.current = 'UniverseTest Finish Game'
    self.FinishGameScreen.setup()


class MainApp(App):
  title = 'UniverseTest'
  def build(self):
    return MainWid()


if __name__ == '__main__':
  MainApp().run()