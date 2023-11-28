import onnxruntime
from transformers import AutoTokenizer
import numpy as np
from pyvi.ViTokenizer import tokenize
from modules.VNMarkNormalization import VNMarkNormalization
import time

class SentenceEmbedding(object):
    def __init__(self, path_to_tokenizer, path_to_model):

        self.tokenizer, self.model = self.load_model(path_to_tokenizer, path_to_model)
        self.accent_norm = VNMarkNormalization()

    @staticmethod
    def load_model(path_to_tokenizer, path_to_model):
        tokenizer = AutoTokenizer.from_pretrained(path_to_tokenizer)
        model = onnxruntime.InferenceSession(path_to_model, providers=['AzureExecutionProvider', 'CPUExecutionProvider'])

        return tokenizer, model

    def embed(self, text):
        text = self.accent_norm.normalizeSentence(text.lower(), useViDetect=True, isCorrect=False)
        text = tokenize(text)
        print(text)
        tokens = self.tokenizer.encode_plus(text)
        print(tokens)
        tokens = {name: np.atleast_2d(value).astype(np.int64) for name, value in tokens.items()}
        return self.model.run(None, tokens)[0][0]


if __name__ == "__main__":
   
    model = SentenceEmbedding("..\\tokenizer", "..\\embeddings.onnx")
    # model = SentenceEmbedding("./tokenizer", 'https://huggingface.co/tanaha2002/embedding/blob/main/embeddings.onnx')
    # begin = time.time()
    b = model.embed("Bạn là gà hay thóc?")
    print(f"a: {b}")
    # a= model.embed("PostgreSQL に接続したのち、下記のコマンドを実行し拡張機能を追加してください。 下記では、UUID と pgvector の拡張機能を有効にしています。PostgreSQL のインスタンスを生成した後、ローカルの環境からアクセスができるようになっているか、下記のコマンドを実行して確認してください。")
    # c = model.embed("Nhân viên kinh doanh của cơ hội 'quản lý chi phí' là ai?")
    # d = model.embed("Có bao nhiêu nhân viên kinh doanh? Đó là những ai?")
    # e = model.embed("Phương tiện nào không thuộc bất kỳ cơ hội nào?")
    # special = model.embed('''Bạn là gà hay thóc?''')
    # end = time.time()
    
    # #caculate cosine similarity between special and a,b,c,d
    # print((special.dot(a) / (np.linalg.norm(special) * np.linalg.norm(a))))
    # print((special.dot(b) / (np.linalg.norm(special) * np.linalg.norm(b))))
    # print((special.dot(c) / (np.linalg.norm(special) * np.linalg.norm(c))))
    # print((special.dot(d) / (np.linalg.norm(special) * np.linalg.norm(d))))
    # print((special.dot(e) / (np.linalg.norm(special) * np.linalg.norm(e))))
    
    # print(len(a))