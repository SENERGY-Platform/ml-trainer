from torch import nn 
from general_pipelines.train.logging_utils import ProgressMeter
import torch 
import similaritymeasures
    
class InferencePipeline():
    def __init__(self, model, dataloader, loss_function):
        self.model = model
        self.dataloader = dataloader
        self.loss_function = loss_function

    def calc_loss(self, input, recons):
        if self.loss_function == 'curve':
            input = input.squeeze(0)
            input = input.reshape(input.size()[0]*input.size()[1], 1)
            recons = recons.squeeze(0)
            recons = recons.reshape(recons.size()[0]*recons.size()[1], 1)
            dtw, d = similaritymeasures.dtw(input, recons)
            return torch.tensor(dtw)
        elif self.loss_function == 'L1':
            loss = nn.L1Loss()
            return loss(input, recons).detach()
        elif self.loss_function == 'MSE':
            loss = nn.MSELoss()
            return loss(input, recons).detach()

    def run(self):
        self.model.eval()
        number_batches = len(self.dataloader)
        progress = ProgressMeter(
                    number_batches,
                    [])

        losses = []
        recons = []

        with torch.no_grad():
            for i, data in enumerate(self.dataloader, 0):
                recon = self.model(data)

                for sample_idx in range(data.size()[0]):
                    sample = data[sample_idx]
                    recon_sample = recon[sample_idx]
                    loss = self.calc_loss(sample, recon_sample)
                    losses.append(loss)
                    recons.append(recon)
                
                progress.log(f'Sample [{i}/{number_batches}]', "", "")

        return torch.tensor(losses), torch.vstack(recons)