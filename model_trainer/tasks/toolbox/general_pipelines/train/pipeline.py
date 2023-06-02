import torch.optim as optim
from torch import nn 
from general_pipelines.train.logging_utils import AverageMeter, ProgressMeter
import torch 
import similaritymeasures
from general_pipelines.train.stopping import EarlyStopping
import matplotlib.pyplot as plt 
from os.path import join as pjoin 

class TrainPipeline():
    def __init__(self, model, train_dataloader, number_epochs, lr, val_dataloader, loss_function, optimizer, out_dir, early_stopping_patience, early_stopping_delta):
        self.early_stopping_patience = early_stopping_patience
        self.early_stopping_delta = early_stopping_delta
        self.out_dir = out_dir
        self.model = model

        if optimizer == 'SGD':
            self.optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9)
        else:
            self.optimizer = optim.Adam(model.parameters(), lr=lr)
            
        self.train_dataloader = train_dataloader
        self.val_dataloader = val_dataloader
        self.number_epochs = number_epochs
        self.number_batches = len(self.train_dataloader)
        self.loss_function = loss_function

        # Logging
        self.setup_logging()

    def setup_logging(self):
        self.train_batch_losses_meter = AverageMeter('Loss', ':.4e', 'batch loss')
        self.train_batch_progress = ProgressMeter(
                                    self.number_batches,
                                    [self.train_batch_losses_meter],
                                    "Train")

        self.val_batch_losses_meter = AverageMeter('Loss', ':.4e', 'val loss')
        self.val_batch_progress = ProgressMeter(
                                    len(self.val_dataloader),
                                    [self.val_batch_losses_meter],
                                    "Val")

        self.train_epoch_losses_meter = AverageMeter('Train Loss', ':.4e', 'epoch loss')
        self.val_epoch_losses_meter = AverageMeter('Val Loss', ':.4e', 'epoch loss')
        self.epoch_progress = ProgressMeter(
                                self.number_batches,
                                [self.train_epoch_losses_meter, self.val_epoch_losses_meter])
        
    def train_batch(self, data):
        # zero the parameter gradients
        self.optimizer.zero_grad()

        # forward + backward + optimize
        outputs = self.model(data)
        loss = self.calc_loss(data, outputs)
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def train_epoch(self, epoch):
        for i, data in enumerate(self.train_dataloader, 0):
            batch_loss = self.train_batch(data)
            self.train_batch_losses_meter.update(batch_loss)
            self.train_batch_progress.log_batch(epoch, i)

        avg_epoch_loss = self.train_batch_losses_meter.avg

        # Reset batch meter so that for each epoch the average is only calculated on the epoch batches
        self.train_batch_losses_meter.reset()
        
        self.train_epoch_losses_meter.update(avg_epoch_loss)   

    def calc_loss(self, input, recons):
        #input = input.flatten(1)
        #recons = recons.flatten(1)

        if self.loss_function == 'L1':
            loss_fn = nn.L1Loss(reduction='mean') # mean over data point losses -> mean over sequence legnth -> mean over samples
            loss = loss_fn(input, recons)
        elif self.loss_function == 'MSE':
            loss_fn = nn.MSELoss(reduction='mean')
            loss = loss_fn(input, recons)

        #loss = torch.mean(loss)
        return loss

    def run_validation(self, epoch):
        self.model.eval()
        with torch.no_grad():
            for i, data in enumerate(self.val_dataloader, 0):
                outputs = self.model(data)
                loss = self.calc_loss(data, outputs)
                self.val_batch_losses_meter.update(loss)
                self.val_batch_progress.log_batch(epoch, i)
        
        val_epoch_loss = self.val_batch_losses_meter.avg
        self.val_epoch_losses_meter.update(val_epoch_loss)


    def plot(self):
        plt.clf()
        plt.plot(self.train_epoch_losses_meter.all, label="Train")
        plt.plot(self.val_epoch_losses_meter.all, label="Validation")
        plt.xticks([i for i in range(len(self.val_epoch_losses_meter.all_avg))])
        plt.title("Epoch Loss")
        plt.legend()
        plt.savefig(pjoin(self.out_dir, 'loss', 'epoch_loss.png'))

        plt.clf()
        plt.plot(self.train_batch_losses_meter.all_avg)
        plt.title("Train Batch Loss")
        plt.savefig(pjoin(self.out_dir, 'loss', 'train_batch_loss.png'))

        plt.clf()
        plt.plot(self.val_batch_losses_meter.all_avg)
        plt.title("Val Batch Loss")
        plt.savefig(pjoin(self.out_dir, 'loss', 'val_batch_loss.png'))

    def train(self): 
        self.model.train()
        early_stopping = EarlyStopping(self.early_stopping_patience, self.early_stopping_delta)
        n_epochs = 0 

        for epoch in range(self.number_epochs): 
            self.train_epoch(epoch) 

            # Check Valiation loss
            self.run_validation(epoch)

            self.epoch_progress.log_epoch(epoch)
            self.plot()

            n_epochs += 1 
            early_stopping(self.val_epoch_losses_meter.val)
            if early_stopping.early_stop:
                print('Early Stop')
                break
        
        return self.model, n_epochs
    
 