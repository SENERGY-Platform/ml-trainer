from torch import nn
import torch

class Encoder(nn.Module):
    def __init__(self, number_encoder_layers, number_heads, embedding_dimension):
        super(Encoder, self).__init__()
        encoder_layer = nn.TransformerEncoderLayer(d_model=embedding_dimension, nhead=number_heads, batch_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=number_encoder_layers)

    def forward(self, input):
        return self.encoder(input)

class Decoder(nn.Module):
    def __init__(self, embedding_dimension, token_length):
        super(Decoder, self).__init__()
        self.prediction_layer = nn.Sequential(
                nn.Linear(embedding_dimension, 1048),
                nn.ReLU(),
                nn.Linear(1048, 1048),
                nn.ReLU(),
                nn.Linear(1048, token_length),
        )

    def forward(self, input):
        return self.prediction_layer(input)

class Embedding(nn.Module):
    def __init__(self, token_length, embedding_dimension, sequence_length):
        super(Embedding, self).__init__()
        self.projection_layer = nn.Linear(token_length, embedding_dimension)
        self.positional_embedding_layer = nn.Embedding(sequence_length, embedding_dimension)
        self.embedding_dimension = embedding_dimension
        self.sequence_length = sequence_length
        self.norm = nn.LayerNorm(embedding_dimension)

    def forward(self, input):
        projected_input = self.projection_layer(input)
        positions = torch.arange(self.sequence_length)
        position_embeddings = self.positional_embedding_layer(positions)
        embeddings = projected_input + position_embeddings
        normed_embeddings = self.norm(embeddings)
        return normed_embeddings

class TransformerTimeSeriesEncoder(nn.Module):
    def __init__(self, number_encoder_layers, number_heads, embedding_dimension, sequence_length, token_length):
        super(TransformerTimeSeriesEncoder, self).__init__()
        self.encoder = Encoder(number_encoder_layers, number_heads, embedding_dimension)
        self.decoder = Decoder(embedding_dimension, token_length)
        self.embedding = Embedding(token_length, embedding_dimension, sequence_length)

    def forward(self, input):
        embedding = self.embedding(input)
        encoding = self.encoder(embedding)
        decoding = self.decoder(encoding)
        return decoding