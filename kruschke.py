import pymc as pm
import numpy as np
import arviz as az
import matplotlib.pyplot as plt

# I found this as an official example:
# https://docs.pymc.io/en/stable/pymc-examples/examples/case_studies/BEST.html .

np.random.seed(1)

size = 100

data1 = np.random.normal(loc=1, scale=0.2, size=100)
data2 = np.random.normal(loc=1.1, scale=0.4, size=100)

all = np.hstack([data1, data2])

with pm.Model() as model:
    # “The mean the prior on mu is arbitrarily set to the mean of the
    # pooled data; this setting is done merely to keep the prior scaled
    # appropriately relative to the arbitrary scale of the data.”
    mu1 = pm.Normal("mu_1", mu=np.mean(all), sigma=1000 * np.std(all))
    mu2 = pm.Normal("mu_2", mu=np.mean(all), sigma=1000 * np.std(all))

    sigma1 = pm.Uniform("sigma_1", np.std(all) / 1000, 1000 * np.std(all))
    sigma2 = pm.Uniform("sigma_2", np.std(all) / 1000, 1000 * np.std(all))

    # Balances nearly normal distributions (nu > 30) with heavy tailed
    # distributions (nu < 30).
    nu = pm.Exponential("nu", 1 / 29) + 1

    t1 = pm.StudentT("t_1", mu=mu1, sigma=sigma1, nu=nu, observed=data1)
    t2 = pm.StudentT("t_2", mu=mu2, sigma=sigma2, nu=nu, observed=data2)

    diff_mu = pm.Deterministic("mu_1 - mu_2", mu1 - mu2)
    cred_eff_size = pm.Deterministic("cred eff size", diff_mu / np.sqrt(
        (sigma1**2 + sigma2**2) / 2))

    fname = "model.dat"
    try:
        sample = az.from_netcdf(fname)
    except:
        sample = pm.sample(10000, cores=2, return_inferencedata=True)
        # sample = az.to_netcdf(fname)
    # Posterior predictive check.
    ppc = pm.sample_posterior_predictive(sample, var_names=["t_1", "t_2"], return_inferencedata=True)


rope = {"mu_1 - mu_2": [{"rope": (-0.1, 0.1)}]}
ref_val = {"mu_1 - mu_2": [{"ref_val": -0.1}]}
az.plot_posterior(sample, rope=rope, ref_val=ref_val, show=True)

az.plot_ppc(ppc, num_pp_samples=10, show=True)
