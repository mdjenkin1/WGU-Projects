import pickle
import pprint
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append("../tools/")
from feature_format import featureFormat, targetFeatureSplit


stock_features = ['poi', 'restricted_stock_deferred', 'total_stock_value', 'exercised_stock_options', 'restricted_stock']

cleaned_data = pickle.load(open("../pickle_jar/final_project_dataset_cleaned.pkl"))
stock_data = featureFormat(cleaned_data, stock_features)
poi_np, stock_data_np_arrays = targetFeatureSplit(stock_data)
stock_data_df = pd.DataFrame(stock_data_np_arrays, columns = stock_features[1:])

###
### Stock Data

plt.style.use('ggplot')
#stock_matrix = pd.plotting.scatter_matrix(stock_data_df)
#stock_matrix.show()

stock_matrix = sns.pairplot(stock_data_df)
#plt.show()
plt.savefig("../pickle_jar/stock_pairplot.png")

pprint.pprint(stock_data_df.loc[stock_data_df['restricted_stock'] < 0])

for person in cleaned_data:
    if cleaned_data[person]['restricted_stock'] < 0:
        print("{} has positive restricted stock deferrals".format(person))
        pprint.pprint(cleaned_data[person])

##
## Newly identified bad data scrubbed
##

cleaned_data = pickle.load(open("../pickle_jar/dataset_final_clean.pkl"))
stock_data = featureFormat(cleaned_data, stock_features)
poi_np, stock_data_np_arrays = targetFeatureSplit(stock_data)
stock_data_df = pd.DataFrame(stock_data_np_arrays, columns = stock_features[1:])

stock_matrix = sns.pairplot(stock_data_df)
#plt.show()
plt.savefig("../pickle_jar/stock_pairplot_cleaned.png")
