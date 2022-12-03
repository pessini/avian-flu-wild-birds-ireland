import pandas as pd

bird_flu = pd.read_pickle("./data/bird-flu.pkl")
watch_ireland = pd.read_pickle("./data/BirdWatchIreland.pkl")

bird_flu.to_pickle("./data/bird-flu4.pkl", protocol=4)
watch_ireland.to_pickle("./data/BirdWatchIreland4.pkl", protocol=4)
