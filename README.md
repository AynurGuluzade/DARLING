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
@InProceedings{10.1007/978-3-030-77211-6_48,
    author="Guluzade, Aynur
    and Kacupaj, Endri
    and Maleshkova, Maria",
    editor="Tucker, Allan
    and Henriques Abreu, Pedro
    and Cardoso, Jaime
    and Pereira Rodrigues, Pedro
    and Ria{\~{n}}o, David",
    title="Demographic Aware Probabilistic Medical Knowledge Graph Embeddings of Electronic Medical Records",
    booktitle="Artificial Intelligence in Medicine",
    year="2021",
    publisher="Springer International Publishing",
    address="Cham",
    pages="408--417",
    abstract="Medical knowledge graphs (KGs) constructed from Electronic Medical Records (EMR) contain abundant information about patients and medical entities. The utilization of KG embedding models on these data has proven to be efficient for different medical tasks. However, existing models do not properly incorporate patient demographics and most of them ignore the probabilistic features of the medical KG. In this paper, we propose DARLING (Demographic Aware pRobabiListic medIcal kNowledge embeddinG), a demographic-aware medical KG embedding framework that explicitly incorporates demographics in the medical entities space by associating patient demographics with a corresponding hyperplane. Our framework leverages the probabilistic features within the medical entities for learning their representations through demographic guidance. We evaluate DARLING through link prediction for treatments and medicines, on a medical KG constructed from EMR data, and illustrate its superior performance compared to existing KG embedding models.",
    isbn="978-3-030-77211-6"
}
```
