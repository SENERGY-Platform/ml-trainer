from general_pipelines.train.pipeline import TrainPipeline
from general_pipelines.inference.pipeline import InferencePipeline
from torch.utils.data import DataLoader
import torch 

class AnomalyPipeline():
    def __init__(self, config):
        self.config = config

    def fit(self, train_dataset, val_dataset):
        train_dataloader = DataLoader(train_dataset, batch_size=self.config["BATCH_SIZE"], shuffle=True)
        val_dataloader = DataLoader(val_dataset, batch_size=self.config["BATCH_SIZE"], shuffle=True)
        pipeline = TrainPipeline(self.model, train_dataloader, self.config["NUM_EPOCHS"], self.config["LR"], val_dataloader, self.config['LOSS'], self.config['OP'], self.config['OUT_DIR'], self.config['EARLY_STOPPING_PATIENCE'], self.config['EARLY_STOPPING_DELTA'])
        trained_model, n_epochs = pipeline.train()
        self.model = trained_model

        # Calculate final train sample losses for threshold 
        pipeline = InferencePipeline(self.model, train_dataloader, self.config['LOSS'])
        all_losses, _ = pipeline.run()
        self.train_losses = all_losses
       
        return n_epochs, self.train_losses

    def calc_threshold(self, losses, quantil):
        quantiles = torch.tensor([quantil], dtype=torch.float32)
        quants = torch.quantile(losses, quantiles)
        threshold = quants[0]
        return threshold

    def get_anomalies(self, strategy='quantil', quantil='95'):
        if strategy == 'quantil':
            threshold = self.calc_threshold(self.train_losses, quantil)
            anomaly_indices = torch.where(self.test_losses > threshold)[0]
            anomalit_recons = self.test_recons[anomaly_indices]
            normal_indices = torch.where(self.test_losses < threshold)[0]
            normal_recons = self.test_recons[normal_indices]        
            
            return anomalit_recons, anomaly_indices, normal_recons, normal_indices

    def predict(self, dataset, quantil):
        dataloader = DataLoader(dataset, batch_size=64)
        pipeline = InferencePipeline(self.model, dataloader, self.config['LOSS'])
        self.test_losses, self.test_recons = pipeline.run()

        anomalit_recons, anomaly_indices, normal_recons, normal_indices = self.get_anomalies("quantil", quantil)
        return anomalit_recons, anomaly_indices, normal_recons, normal_indices, self.test_losses