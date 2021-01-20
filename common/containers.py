class Row:
    def __init__(self, element):
        self.element = element
        self.id = self.get_id()
        self.dictionary = {'id': self.id}
        self.sent_to_db = False

    def get_id(self):
        return self.element.find_element_by_css_selector('[id]').get_attribute('id')

    def get_data(self):
        assert False, 'no data to be found here, has to be overriden'

    def set_dictionary(self):
        self.dictionary['data'] = self.get_data()


class TextRow(Row):
    def __init__(self, element):
        Row.__init__(self, element)
        self.data = self.get_data()
        self.set_dictionary()

    def get_data(self):
        elements = self.element.find_elements_by_css_selector('.wall_post_text')
        if elements:
            return [el.text for el in elements]
        else:
            return []


class ImgRow(Row):
    def __init__(self, element):
        Row.__init__(self, element)
        self.data = self.get_data()
        self.set_dictionary()

    def get_data(self):
        elements = self.element.find_elements_by_css_selector('.page_post_thumb_wrap')
        if elements:
            return list(el.get_attribute('style').split('"')[-2]
                        for el in elements)
        else:
            return []


class HrefRow(Row):
    def __init__(self, element):
        Row.__init__(self, element)
        self.data = self.get_data()
        self.set_dictionary()

    def get_data(self):
        return list(
            el.get_attribute('href') for el in (self.element.find_elements_by_css_selector('.wall_post_text a[href]')
                                                + self.element.find_elements_by_css_selector('media_desc a[href]')))


class File:
    def __init__(self, filename, mutex):
        self.filename = filename
        self.mutex = mutex
