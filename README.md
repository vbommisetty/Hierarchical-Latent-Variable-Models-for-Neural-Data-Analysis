# Hierarchial Latent Variable Models for Neural Data Analysis

This repository provides a fully reproducible pipeline for performing **Probabilistic Canonical Correlation Analysis (PCCA)** on neural data. The implementation is based on **Gunderson’s PCCA model** with modifications for improved performance and usability.

## 📌 Features
- **Sensitive Cluster Analysis**: Identifies neural clusters with significant task-related activity.
- **Dimensionality Reduction**: Applies **PCA (Principal Component Analysis)** to preprocess neural data before PCCA.
- **Canonical Correlation Analysis (CCA) & PCCA**: Performs **CCA & PCCA** to analyze relationships between neural populations.
- **Automated Plot Generation**: Saves raster plots, PSTHs, RMSE graphs, and correlation matrices to the `results/` folder.

---

## 🔧 Installation, Setup, and Run

### **1. Clone the Repository**
```sh
git clone https://github.com/vbommisetty/Hierarchical-Latent-Variable-Models-for-Neural-Data-Analysis.git
cd Hierarchical-Latent-Variable-Models-for-Neural-Data-Analysis
```
### **2. Create a Virtual Environment** (Recommended, but not required.)
```sh
python -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate
```

### **3. Install Dependencies**
To install the dependencies (Python version 3.11 or higher required!):
Run the following command from the root directory of the project:
```
pip install -r requirements.txt
```
### **4. Running the Pipeline**
Run the pipeline with a single command:
```sh
python run.py
```

## 📚 References:

Gunderson, Gregory. 2018a. “Canonical Correlation Analysis in Detail.” https://gregorygundersen.com/blog/2018/07/17/cca/

Gunderson, Gregory. 2018b. “Probabilistic Canonical Correlation Analysis in Detail.” https://gregorygundersen.com/blog/2018/09/10/pcca/#klami2015group

Jun, James J., Nicholas A. Steinmetz, Joshua H. Siegle, et al. 2017. “Fully Integrated Silicon Probes for High-Density Recording of Neural Activity.” Nature 551 (7679): 232–236.

Nichols, Thomas E., and Andrew P. Holmes. 2002. “Nonparametric Permutation Tests for Functional Neuroimaging: A Primer with Examples.” Human Brain Mapping 15 (1): 1–25.

Bonferroni, Carlo Emilio. 1936. “Teoria Statistica Delle Classi e Calcolo Delle Probabilità.” Pubblicazioni del R. Istituto Superiore di Scienze Economiche e Commerciali di Firenze 8: 3–62.

Benjamini, Yoav, and Yosef Hochberg. 1995. “Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing.” Journal of the Royal Statistical Society: Series B (Methodological) 57 (1): 289–300.

Gold, Joshua I., and Michael N. Shadlen. 2007. “The Neural Basis of Decision Making.” Annual Review of Neuroscience 30: 535–574.

Krauzlis, Richard J., Lee P. Lovejoy, and Alexandre Zénon. 2013. “Superior Colliculus and Visual Spatial Attention.” Annual Review of Neuroscience 36: 165–182.



Sha Lei, Courtney Cheung, Shuyu Wang, and Yutian Shi 2024. "Hierarchial Latent Variable Models for Neural Data Analysis"
https://github.com/courtneyacheung/Hierarchical-Latent-Variable-Models-for-Neural-Data-Analysis/tree/main
