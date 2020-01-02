from .load import loadPrepareData
from .evaluate import device, evaluate
from .model import EncoderRNN, LuongAttnDecoderRNN
import torch


class AttentionChatbot:
    def __init__(self, model_path, corpus_path, pairs_path, voc_path):
        torch.set_grad_enabled(False)

        hidden_size = 512
        n_layers = 1
        # self.voc, self.pairs = loadPrepareData(corpus_path)
        self.voc = torch.load(voc_path, map_location=device)
        self.pairs = torch.load(pairs_path, map_location=device)
        embedding = torch.nn.Embedding(self.voc.n_words, hidden_size)
        encoder = EncoderRNN(self.voc.n_words, hidden_size, embedding, n_layers)
        attn_model = 'dot'
        decoder = LuongAttnDecoderRNN(attn_model, embedding, hidden_size, self.voc.n_words, n_layers)

        checkpoint = torch.load(model_path, map_location=device)
        encoder.load_state_dict(checkpoint['en'])
        decoder.load_state_dict(checkpoint['de'])

        # train mode set to false, effect only on dropout, batchNorm
        encoder.eval()
        decoder.eval()
        encoder.train(False)
        decoder.train(False)

        self.encoder = encoder.to(device)
        self.decoder = decoder.to(device)

    def __call__(self, sentence):
        try:
            output_words, _ = evaluate(self.encoder, self.decoder, self.voc, sentence, 1)
            return [' '.join(output_words).replace('<EOS>', '')]
        except KeyError:
            return None
