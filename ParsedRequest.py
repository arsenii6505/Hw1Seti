from bs4 import BeautifulSoup

class ParsedRequest:
    def __init__(self):
        self.method = "GET"
        self.additional_path = ""
        self.params = {}
        self.cookies = {}
        self.data = {}
        self.files = {}
        self.headers = {}
        self.step = 0
        self.texts = []

    @staticmethod
    def parse(string):
        # print(string)
        answer = ParsedRequest()
        html = BeautifulSoup(string, "lxml")
        texts = [j.strip() for j in html.find_all(string=True) if j != "\n"]
        answer.texts = texts
        # for j in texts:
        #     print(j)
        i = 1
        # номер шага
        if len(texts) <= 1:
            debug_cheat()
        answer.step = int(texts[i][texts[i].find("#") + 1:texts[i].find("(")])
        i += 1
        # метод и путь
        if "POST" in texts[i] or ("Загр" in texts[i]):
            answer.method = "POST"
            i += 1
            answer.additional_path = texts[i]
            i += 1
        elif "GET" in texts[i]:
            answer.method = "GET"
            i += 1
            answer.additional_path = texts[i]
            i += 1
        elif "Пере" in texts[i]:
            answer.method = "GET"
            answer.additional_path = html.find('a').get("href")
            i += 3
        #остальное
        needed_dict = {}
        key_value = ""
        while i < len(texts):
            if "данные" in texts[i]:
                needed_dict = answer.data
                i += 2
            elif "параметры" in texts[i]:
                needed_dict = answer.params
                i += 2
            elif "UTF8" in texts[i]:
                needed_dict = answer.files
                i += 2
            elif "заголовки" in texts[i]:
                needed_dict = answer.headers
                i += 2
            elif "cookie" in texts[i]:
                needed_dict = answer.cookies
                i += 2
            else:
                if key_value == "":
                    key_value = texts[i]
                else:
                    needed_dict[key_value] = texts[i]
                    key_value = ""
            i += 1
        return answer

def debug_cheat():
    return True