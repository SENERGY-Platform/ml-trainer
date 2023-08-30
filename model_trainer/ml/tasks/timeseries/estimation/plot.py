import matplotlib
import matplotlib.pyplot as plt 
matplotlib.use('Agg')

def generate_plot(test_ts, pred_ts):
    # Plot predicted and expected timeseries
    test_ts.plot(label="expected")
    pred_ts.plot(label="prediction")
    plot = plt.gcf()
    # TODO close figure because of memory -> but then plot will be empty at save
    return plot