from consumption import ConsumptionPreProcessor
import pandas as pd 

df = pd.DataFrame({
    "time": ["01 Jan 1970 00:00:00 GMT", "02 Jan 1970 00:00:00 GMT", "02 Jan 1970 00:10:00 GMT"],
    "value": [1, 2, 3]
})
print(ConsumptionPreProcessor(df, "H").run())