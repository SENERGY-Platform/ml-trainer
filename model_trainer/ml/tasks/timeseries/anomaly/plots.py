import matplotlib.pyplot as plt 
import torch 

def plot_losses(losses):
    fig, ax = plt.subplots(figsize = (6,4))
    ax.hist(losses, alpha = 0.65)
    ax.set_yticks([])

    quants = torch.quantile(losses, torch.tensor([0.9, 0.95, 0.99], dtype=torch.float32))
    quants = torch.round(quants, decimals=3)
    quants90 = quants[0]
    quants95 = quants[1]
    quants99 = quants[2]
        
    # [quantile, opacity, length]
    quants = [[quants90, 0.8, 0.46], [quants95, 0.6, 0.56], [quants99, 0.6, 0.66]]
    # Plot the lines with a loop
    for i in quants:
        ax.axvline(i[0], alpha = i[1], ymax = i[2], linestyle = ":")

    ax.text(quants90-.25, 0.47, f"90th: {quants90}", size = 10, alpha =.8)
    ax.text(quants95-.25, 0.57, f"95th: {quants95}", size = 10, alpha =.8)
    ax.set_title('Distribution of losses from train samples')
    return fig

def plot_reconstructions(reconstructions, indices, test_data, title):
    fig = plt.figure()
    new_plot = fig.add_subplot(111)
    idx = indices[0]
    #idx = 0
    new_plot.plot(test_data[idx], color="green", label="Original")
    new_plot.plot(reconstructions[idx], color="red", label="Reconstruction")
    new_plot.set_title(title)
    new_plot.legend()
    return fig