# Demographic Aware Probabilistic Medical Knowledge Graph Embeddings of Electronic Medical Records

## Requirements and Setup
Python version >= 3.7

PyTorch version >= 1.2.0

``` bash
# clone the repository
git clone https://github.com/AynurGuluzade/DARLING.git
cd DARLING
pip install -r requirements.txt
```

## Download MIMIC-III dataset
We construct a Medical Knowledge Graph using MIMIC-III dataset, which contains clinical information of patients. For accessing the data, researchers should complete an online training course and then apply for permission to download the complete MIMIC-III dataset. You can find more information [here](https://mimic.physionet.org/).

After dowloading you will need to the move files under the [data](data) directory.

## Construct Probabilistic Medical Knowledge Graph with Demographics
For constructing the knowledge graph please run:
``` bash
# construct medical kg
python scripts/prob_medical_kg_with_demographics.py
```

## Train Framework
For training you will need to adjust the paths in [args](args.py) file. At the same file you can also modify and experiment with different model settings.
``` bash
# train Framework
python train.py
```

## Test Framework
``` bash
# test Framework
python test.py
```

## License
The repository is under [MIT License](LICENCE).

## Cite
```bash
@inproceedings{
    guluzade2021darling,
    title={Demographic Aware Probabilistic Medical Knowledge Graph Embeddings of Electronic Medical Records},
    author={Aynur Guluzade and Endri Kacupaj and Maria Maleshkova},
    booktitle={Artificial Intelligence in Medicine (AIME 2021)},
    year={2021}
}
```
