import json
import os

class I18n:
    def __init__(self, module_name):
        self.module_name = module_name

    def __check_available_i18n(self):
        module_path = os.path.join(os.getcwd(), os.path.join('server/i18n', self.module_name))
        if os.path.isdir(module_path):
            self.module_path = module_path
            return [lang_file.replace('.json', '') for lang_file in os.listdir(module_path)]
        else:
            return module_path

    def load_translation(self, language):
        if language in self.__check_available_i18n():
            with open(os.path.join(self.module_path, f'{language}.json')) as translation_file:
                return json.load(translation_file)
