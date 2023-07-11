import matplotlib.pyplot as plt 

def log_plot(test_ts, pred_ts, mlflow):
    # Plot predicted and expected timeseries

    test_ts.plot(label="expected")
    pred_ts.plot(label="prediction")
    mlflow.log_figure(plt.gcf(), 'plots/predictions.png')