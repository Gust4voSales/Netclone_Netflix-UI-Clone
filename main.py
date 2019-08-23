import os
from kivy.app import App
from kivy.config import Config
Config.set('graphics', 'resizable', 0)
Config.set('kivy', 'exit_on_escape', 0)
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.lang.builder import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen

Builder.load_string(open(os.path.join("config", "kvfile.kv"), encoding="utf-8").read(), rulesonly=True)


class Manager(ScreenManager):
    pass


class PopupWarning(Popup):
    pass


class LoginScreen(Screen):
    def login_verification(self):
        if self.ids.email.text == 'netflix@gmail.com' and self.ids.passw.text == '1234':
            self.clean_inputs()
            self.ids.dica.text = ''  # Remove o texto com o login da conta da LoginScreen
            App.get_running_app().root.current = 'netflixmenu'
        else:
            self.incorrect_login()
            self.clean_inputs()

    def clean_inputs(self):
        if self.ids.checkbox.active:
            self.ids.passw.text = ''
        else:
            self.ids.email.text = self.ids.passw.text = ''

    def incorrect_login(self):
        popup = PopupWarning()
        popup.open()

        self.ids.dica.text = 'email = netflix@gmail.com\nsenha = 1234'  # Mostra qual o login da conta

    def istab_pressed(self, text):
        # Verifica se o TextInput da senha ta sendo utilizado, se sim, retira o 'tab'
        if len(text) > 0 and text[-1] == '\t':
            self.ids.passw.text = text[:-1]


class NetflixHome(Screen):
    def on_pre_enter(self, *args):
        Window.bind(on_keyboard=self.isupdate)
        self.ids.scroll_home.scroll_y = 1
        self.add_content()

    def on_leave(self, *args):
        self.ids.content.clear_widgets()

    def isupdate(self, window, key, *args):
        if key == 286:  # Apertou f5
            self.on_pre_enter()
            if App.get_running_app().root.current == 'resultpage':
                App.get_running_app().root.current = 'netflixmenu'

    def add_content(self):
        # Retira todos os Widgets filhos caso a pagina seja atualizada não haverá Content Lists repetidos
        self.ids.content.clear_widgets()
        self.ids.content.add_widget(Banner())
        for folder in os.listdir('Content'):
            files = os.listdir(os.path.join('Content', folder))
            content = ContentList()
            content.create(folder, files)
            self.ids.content.add_widget(content)


class Banner(BoxLayout):
    pass


class SearchBox(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Cria um bind do botão de pesquisa com a função que abre o SearchBox
        Clock.schedule_once(lambda *_: self.ids.searchbtn.bind(on_press=self.open_animation_search_box), 1)
        # Cria o TextInput da SearchBox
        self.search_input = TextInput(multiline=False, hint_text='Títulos', background_color=[0, 0, 0, .1],
                                      on_text_validate=self.search, foreground_color=[1, 1, 1, 1])

    def search(self, *args):
        if self.search_input.text != '':
            if App.get_running_app().root.current != 'resultpage':
                App.get_running_app().root.current = 'resultpage'

            App.get_running_app().root.get_screen('resultpage').pre_search(self.search_input.text.lower().strip())

        self.search_input.text = ''  # Remove o texto da pesquisa

    def open_animation_search_box(self, *args):
        self.btn = self.ids.searchbtn

        self.search_input.size_hint = [.02, .4]
        self.search_input.pos_hint = {'center_y': .5, 'center_x': .57}
        # Chama função que seta o foco do TextInput pra True depois que a animação é feita
        Clock.schedule_once(self.searchinput_focus, .3)

        #  Cria a animação de abertura do botão e do TextInput
        anim_btn = Animation(size_hint=[.15, .45], duration=.01) + Animation(size_hint=[.08, .35], duration=.01) + \
            Animation(pos_hint={'center_x': .1}, duration=.05)
        anim_txt = Animation(size_hint=[.8, .4], d=.15, t='in_sine')

        anim_btn.start(self.btn)  # Inicia a animação do botão
        self.add_widget(self.search_input)  # Adiciona o TextInput
        anim_txt.start(self.search_input)  # Inicia a animação do TextInput

        # Retira o bind do botão com a animação de abertura e cria um bind com a pesquisa
        self.btn.unbind(on_press=self.open_animation_search_box)
        self.btn.bind(on_press=self.search)

        # Cria evento no Clock que a cada frame verifica o foco do TextInput da SearchBox pra saber se ela deve fechar
        Clock.schedule_once(lambda *_: Clock.schedule_interval(self.isdefocused, 0), .4)

    def close_animation_search_box(self, *args):
        #  Cria a animação de fechamento do botão e do TextInput
        anim_btn = Animation(size_hint=[.15, .45], duration=.01) + Animation(size_hint=[.08, .35], duration=.01) + \
            Animation(pos_hint={'center_x': .9}, duration=.1)

        self.remove_widget(self.search_input)  # Remove o TextInput
        anim_btn.start(self.btn)  # Inicia a animação

        # Retira o bind com a pesquisa do botão e cria um bind com a animação de abertura novamente
        self.btn.unbind(on_press=self.search)
        self.btn.bind(on_press=self.open_animation_search_box)

    def searchinput_focus(self, *args):
        self.search_input.focus = True

    def isdefocused(self, *args):
        if not self.search_input.focus:
            # Caso o TextInput perca o foco significa que clicaram fora do seu campo então ele deve fechar
            self.close_animation_search_box()
            Clock.unschedule(self.isdefocused)  # Remove evento que fica verificando o foco do TextInput


class ContentList(BoxLayout):
    def create(self, foldername, images):
        self.padding = 0, 0, 0, 50
        self.ids.label.text = foldername
        self.ids.grid.cols = len(images)
        if len(images) > 0:
            for image in images:
                image_path = os.path.join('Content', foldername, image)
                image_content = ImageContent(image_path)
                self.ids.grid.add_widget(image_content)


class ImageContent(Button):
    def __init__(self, image_path, **kwargs):
        super().__init__(**kwargs)
        self.image_path = image_path
        self.size_hint = None, None
        self.size = 240, 151

        self.background_normal = self.background_down = self.image_path

    def on_press(self):
        print(self.image_path)


class ResultPage(Screen):
    def pre_search(self, text):
        if len(text) > 0:
            # Pega todos os filmes e séries disponíveis sem repetir
            all_images = []
            for folder, subfolders, files in os.walk('Content'):
                 for file in files:
                    if file[:-4] not in all_images:
                        all_images.append(file[:-4])

            self.search_files(text, all_images)

    def search_files(self, text, all_images):
        # Verifica se a pesquisa acha algo
        results = []
        for individual_word in text.split(' '):
            for image in all_images:
                if individual_word in image.lower():
                    results.append(image + '.jpg')

        folders = os.listdir('Content')
        paths = []
        for result in results:
            for folder in folders:
                folder_path = os.path.join('Content', folder)
                images = os.listdir(folder_path)
                if result in images:
                    img_index = images.index(result)
                    paths.append(os.path.join(folder_path, images[img_index]))
                    break

        self.add_content(text, paths)

    def add_content(self, text, paths=None):
        self.ids.stack.clear_widgets()
        self.ids.scroll_result.scroll_y = 1
        if len(paths) > 0:
            self.ids.searchtext.text = '    Resultado da pesquisa para ' + text.title()
            for path in paths:
                self.ids.stack.add_widget(ImageContent(path))
        else:
            self.ids.searchtext.text = '  Não foi encontrado resultado para ' + text.title()


class NetClone(App):
    app_icon = os.path.join('config', 'icone.ico')
    netflix_logo = os.path.join('config', 'netflix.png')
    background_login = os.path.join('config', 'background.jpg')
    dropmenu_icon = os.path.join('config', 'icone_sair.jpg')
    search_btn = os.path.join('config', 'search_btn.png')
    roundborder = os.path.join('config', 'roundborder.png')
    banner = os.path.join('config', 'banner.jpg')
    netflix_font = os.path.join('config', 'net_font.ttf')

    def build(self):
        self.icon = self.app_icon
        return Manager()


NetClone().run()
