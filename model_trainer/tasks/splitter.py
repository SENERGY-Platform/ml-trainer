from darts.utils.model_selection import train_test_split

class Splitter():
    def single_split(self, ts):
        train_ts, test_ts = train_test_split(ts, test_size=0.25)
        return train_ts, test_ts