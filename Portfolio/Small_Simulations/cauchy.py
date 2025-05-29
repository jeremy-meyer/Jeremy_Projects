

# Cauchy violates the CLT because it has infinite variance, but what about the LLN?

# Question: Does the sample mean of a cauchy estimate converge to the true mean as N gets larger?
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

nsim = 100_000
Ns = [1, 5, 10, 50, 100, 500, 1000, 5000 ,10000]

def calc_sample_mean(N):
  draws = np.random.standard_cauchy(N)
  return np.mean(draws)

def bin_values(x, max_val=25):
  if abs(x) <= max_val:
    return round(x *2, 0)/2.0
  else:
    return (max_val + 0.1) * (-1 if x < 0 else 1)


sampling_dists = {n: [bin_values(calc_sample_mean(n)) for s in range(nsim)] for n in Ns}
sampling_df = pd.melt(pd.DataFrame(sampling_dists), value_vars=Ns, var_name='N', value_name='xbar')
sampling_df_binned = (
  sampling_df
  .groupby(['N', 'xbar'])
  .size()
  .reset_index(name='counts')
)

sampling_df_binned['total'] = sampling_df_binned.groupby('N')['counts'].transform('sum')
sampling_df_binned['%'] = sampling_df_binned['counts'] / sampling_df_binned['total']
sampling_df_binned['N'] = sampling_df_binned['N'].apply(lambda x: "N=" + str(x))
               
sns.lineplot(sampling_df_binned, x='xbar', y='%', hue='N').set_title("Cauchy Sampling Distribution (100k samples)")
plt.show()

# Normal
def calc_sample_mean(N):
  draws = np.random.standard_normal(N)
  return np.mean(draws)

def bin_values(x, max_val=5):
  if abs(x) <= max_val:
    return round(x *2, 1)
  else:
    return (max_val + 0.1) * (-1 if x < 0 else 1)


sampling_dists2 = {n: [bin_values(calc_sample_mean(n)) for s in range(nsim)] for n in Ns}
sampling_df = pd.melt(pd.DataFrame(sampling_dists2), value_vars=Ns, var_name='N', value_name='xbar')
sampling_df_binned = (
  sampling_df
  .groupby(['N', 'xbar'])
  .size()
  .reset_index(name='counts')
)

sampling_df_binned['total'] = sampling_df_binned.groupby('N')['counts'].transform('sum')
sampling_df_binned['%'] = sampling_df_binned['counts'] / sampling_df_binned['total']
sampling_df_binned2 = sampling_df_binned[sampling_df_binned["N"]<=100]
sampling_df_binned2['N'] = sampling_df_binned2['N'].apply(lambda x: "N=" + str(x))

               
sns.lineplot(sampling_df_binned2, x='xbar', y='%', hue='N').set_title("Normal Sampling Distribution (100k samples)")
plt.show()


