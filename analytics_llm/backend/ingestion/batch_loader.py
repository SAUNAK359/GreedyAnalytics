import pandas as pd

class BatchSource(DataSource):
    def __init__(self, file):
        self.df = pd.read_csv(file)

    def schema(self):
        return dict(self.df.dtypes)

    def sample(self):
        return self.df.head(10)
