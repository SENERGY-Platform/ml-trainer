import torch 
from enum import Enum
import wandb 

class AverageMeter(object):
    """Computes and stores the average and current value"""
    def __init__(self, name, fmt=':f', key=""):
        self.name = name
        self.fmt = fmt
        self.reset()
        self.key = key
        self.all = []
        self.all_avg = []

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val):
        self.val = val
        self.sum += val        
        self.count += 1
        self.avg = self.sum / self.count
        self.all.append(val)
        self.all_avg.append(self.avg)

    def __str__(self):
        fmtstr = '{name} {val' + self.fmt + '} ({avg' + self.fmt + '})'
        return fmtstr.format(**self.__dict__)


class ProgressMeter(object):
    def __init__(self, number_batches, meters, prefix=""):
        self.meters = meters
        self.number_batches = number_batches
        self.prefix = prefix

    def log(self, prefix, index_name, index):
        # Print to stdout
        entries = [self.prefix, prefix]
        entries += [str(meter) for meter in self.meters]
        print('\t'.join(entries))

        # Log to wandb
        for meter in self.meters:
            #wandb.log({meter.key: meter.val, index_name: index})
            #wandb.log({f"average {meter.key}": meter.avg, index_name: index})
            pass 

    def log_epoch(self, epoch_idx):
        prefix = f"Epoch: [{epoch_idx}]"
        self.log(prefix, "epoch", epoch_idx)
    
    def log_batch(self, epoch_idx, batch_idx):
        batch_prefix = f"Epoch: [{epoch_idx}] - Batch [{batch_idx}/{self.number_batches}]"
        global_batch_idx = epoch_idx * self.number_batches + batch_idx
        self.log(batch_prefix, "batch", global_batch_idx)

        