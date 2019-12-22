import json
import random


def load_template(source):
    with open(source, 'r', encoding='utf-8') as f:
        return json.load(f)


class Generator:
    """ 基于模板的文本生成 """

    def __init__(self, temp_file, repeat_factor=2):
        self.repeat_factor = repeat_factor

        data = load_template(temp_file)
        self.famous = data["famous"]  # a 代表前面垫话，b代表后面垫话
        self.before = data["before"]  # 在名人名言前面弄点废话
        self.after = data['after']  # 在名人名言后面弄点废话
        self.bosh = data['bosh']  # 代表文章主要废话来源

        self.next_bosh = self.shuffle(self.bosh)
        self.next_famous = self.shuffle(self.famous)

    def shuffle(self, temp):
        candidates = list(temp) * self.repeat_factor
        while True:
            random.shuffle(candidates)
            for i in candidates:
                yield i

    def get_famous(self):
        xx = next(self.next_famous)
        xx = xx.replace("a", random.choice(self.before))
        xx = xx.replace("b", random.choice(self.after))
        return xx

    def check_end(self, text):
        while not text.endswith("。"):
            text += next(self.next_bosh)
        return text

    def __call__(self, title, max_length):
        res = []
        text_length = 0
        text = str()
        while text_length < max_length:
            n = random.randint(0, 100)
            if n < 5:
                text = self.check_end(text)
                text_length += len(text)
                res.append(text)
                text = str()
            elif n < 20:
                text += self.get_famous()
            else:
                text += next(self.next_bosh)
        if len(text) > 0:
            text = self.check_end(text)
            res.append(text)
        return [text.replace("x", title) for text in res]
