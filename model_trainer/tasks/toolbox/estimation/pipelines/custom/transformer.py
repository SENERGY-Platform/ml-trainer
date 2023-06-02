from torch.utils.data import DataLoader
from general_pipelines.train.pipeline import TrainPipeline
from .dataset import WindowDataSetFromTS
from transformers import TimeSeriesTransformerConfig, TimeSeriesTransformerForPrediction
from accelerate import Accelerator
from torch.optim import AdamW

class TransformerForecastPipeline():
    def __init__(self, **kwargs) -> None:
        config = TimeSeriesTransformerConfig(
            prediction_length=prediction_length,
            # context length:
            context_length=prediction_length * 2,
            # lags coming from helper given the freq:
            lags_sequence=lags_sequence,
            # we'll add 2 time features ("month of year" and "age", see further):
            num_time_features=len(time_features) + 1,
            # we have a single static categorical feature, namely time series ID:
            num_static_categorical_features=1,
            # it has 366 possible values:
            cardinality=[len(train_dataset)],
            # the model will learn an embedding of size 2 for each of the 366 possible values:
            embedding_dimension=[2],
            
            # transformer params:
            encoder_layers=4,
            decoder_layers=4,
            d_model=32,
        )

        self.model = TimeSeriesTransformerForPrediction(config)

    def fit(self, ts):
        train_dataset = WindowDataSetFromTS(ts)
        train_dataloader = DataLoader(train_dataset, batch_size=self.config["BATCH_SIZE"], shuffle=True)
        
        accelerator = Accelerator()
        device = accelerator.device

        self.model.to(device)
        optimizer = AdamW(self.model.parameters(), lr=6e-4, betas=(0.9, 0.95), weight_decay=1e-1)

        self.model, optimizer, train_dataloader = accelerator.prepare(
            self.model,
            optimizer,
            train_dataloader,
        )

        self.model.train()
        for epoch in range(40):
            for idx, batch in enumerate(train_dataloader):
                optimizer.zero_grad()
                outputs = self.model(
                    static_categorical_features=batch["static_categorical_features"].to(device)
                    if config.num_static_categorical_features > 0
                    else None,
                    static_real_features=batch["static_real_features"].to(device)
                    if config.num_static_real_features > 0
                    else None,
                    past_time_features=batch["past_time_features"].to(device),
                    past_values=batch["past_values"].to(device),
                    future_time_features=batch["future_time_features"].to(device),
                    future_values=batch["future_values"].to(device),
                    past_observed_mask=batch["past_observed_mask"].to(device),
                    future_observed_mask=batch["future_observed_mask"].to(device),
                )
                loss = outputs.loss

                # Backpropagation
                accelerator.backward(loss)
                optimizer.step()

                if idx % 100 == 0:
                    print(loss.item())
        
    def predict(self, number_steps):
        self.model.eval()

        forecasts = []

        for batch in test_dataloader:
            outputs = self.model.generate(
                static_categorical_features=batch["static_categorical_features"].to(device)
                if config.num_static_categorical_features > 0
                else None,
                static_real_features=batch["static_real_features"].to(device)
                if config.num_static_real_features > 0
                else None,
                past_time_features=batch["past_time_features"].to(device),
                past_values=batch["past_values"].to(device),
                future_time_features=batch["future_time_features"].to(device),
                past_observed_mask=batch["past_observed_mask"].to(device),
            )
            forecasts.append(outputs.sequences.cpu().numpy())