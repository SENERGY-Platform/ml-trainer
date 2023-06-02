from torch.utils.data import Dataset

import torch 

class WindowDataSetFromTS(Dataset):
    def __init__(self, ts, context_length, prediction_length, stride=1):
        super().init()
        self.ts = ts
        self.context_length = context_length
        self.prediction_length = prediction_length
        self.sequences = []
        self.stride = stride

    def generate_sequences(self):
        input_start_index = 0
        input_end_index = self.context_length
        output_end_index = input_end_index + self.prediction_length

        while output_end_index < len(self.ts):
            input_tensor = torch.tensor(self.ts.pd_series[input_start_index:input_end_index])

            output_start_index = input_end_index
            output_end_index = output_start_index + self.prediction_length
            expected_output_tensor = torch.tensor(self.ts.pd_series[output_start_index:output_end_index])

            input_start_index += self.stride 

            self.sequences.append((input_tensor, expected_output_tensor))

    def __getitem__(self, idx):
        return self.sequences[idx]

    def __len__(self):
        return len(self.sequences)

# TODO random sequence by generating random input_start_index without stride
        
