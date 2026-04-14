# ReFAIR: Toward a Context-Aware Recommender for Fairness Requirements Engineering

<div style="text-align:center"><img src="images/approach.png" width="200%"/></div>

ReFair is a novel Solution designed to assist Data Scientists and Software Engineers in building fair Machine Learning (ML) solutions. Its primary objective is to recommend potential sensitive features that could affect the fair behavior of an ML-intensive system during development.

<div style="text-align:center"><img src="images/story_analysis.png" /></div>
The main idea behind ReFair is to analyze a User Story by identifying the application domain and the potential ML tasks required. Based on this information, ReFair suggests possible sensitive features for each task detected that are typically impactful in the identified domain.

As you can see, our approach is composed of two different machine learning modules:

<ul>
    <li><b>Single Label Classifier:</b> This module takes a User Story as input and has the main objective of detecting the <b>Application Domain</b> of the story.</li>
    <li><b>Multi Label Classifier:</b> This module takes a User Story as input and has the main objective of detecting the <b>Possible Learning Tasks</b> related to it.</li>
</ul>

Finally, once our approach detects the tasks and domain, it consults a specific mapping that we have built based on literature [1]. The mapping suggests possible <b>Sensitive Features</b> that the tool should pay attention to.


To develop an initial prototype of our approach, we created a Synthetic Dataset consisting of Machine Learning-specific User Stories. We then trained a supervised <b>XGB CLASSIFIER</b> for domain detection and a supervised <b>Linear SVC Label Powerset</b> multi-label classifier for task detection using this dataset. Finally, we developed an integrated console script that takes a User Story as input and displays the sensitive features for each task-domain pair.


For further specific information, we kindly invite you to read our research paper, which can be found at the following link: "LINK to PAPER TBD".

## Repository Structure
Our Repository is structured into four subdirectories:

<ol>
<li><b>Starting Assets:</b> This contains the resources we used to develop our approach [1, 2], which we discussed in our paper;</li>
    The main contents of this subfolders are:
    <ol>
        <li><a href="./1. Starting Assets/Fabris Ontology Reenginering/fairness_databriefs_alpha_v01.ttl">The original datasets ontology</a> provided by Fabris et al.; </li>
        <li>The <a href = "/1. Starting Assets/ML Keyword Dictionary/AI vocabulary.xlsx">The ML techniques dictionary</a> used to generate the user stories provided by Duran-Silva et al.;</li>
    </ol>
<li><b>Synthetic User Stories:</b> This contains the synthetic dataset we used to train our classifiers, as well as the basic dictionaries we used to create it. The main contents of this subfolders are:
    <ol>
        <li><a href="./2. Synthetic User Stories/Synthetic User Stories.xlsx">The user stories dataset</a>; </li>
        <li>The <a href = "./2. Synthetic User Stories/Dictionaries">Domains and ML Tasks dictionary</a> we used to create the user stories;</li>
        <li>The  <a href = "./2. Synthetic User Stories/Dataset validation/Dataset_Validation.ipynb"> dataset validation script </a> and the
            <a href = "./2. Synthetic User Stories/Dataset validation/">validation resources</a> we used to validate it.</li>
    </ol>
</li>
<li><b>Source Code:</b> This contains the source code related to the selection of the classification models and the integrated <b>ReFair bash script</b>;
    The main contents of this subfolders are:
    <ol>
        <li> The <a href="./3. Source Code/1. Domain Detection/domain_classification.ipynb">domain classification</a> analysis script and <a href = "./3. Source Code/1. Domain Detection/">resources</a> used to train the ML Model for the domain classification models.; </li>
        <li> The <a href="./3. Source Code/2. Tasks Detection/MLTask_classification.ipynb">machine learning classification</a> analysis script and <a href = "./3. Source Code/2. Tasks Detection/">resources</a> used to train the ML Model for the machine learning tasks classification models.; </li>
        <li>The <a href = "./3. Source Code/3. Features Extraction/Features_Extraction_Starting_Prototype.ipynb">feature extraction script</a> and the <a href = "./3. Source Code/3. Features Extraction/datasets/">knowdlege mapping</a> regarding the relations between the application domains, the ML tasks and the sensitive features;</li>
        <li>The integrate <a href = "./3. Source Code/ReFair/REFAIR.py"> ReFair </a> executable script.</li>
    </ol>
</li>
<li><b>Experimental Results:</b> This contains experimental reports regarding models selection and approach validation.</li>
    The main contents of this subfolders are:
    <ol>
        <li>The <a href="./4. Experimental Results/1. Domain Detection/">results</a> of the domains classification analysis;</li>
        <li>The <a href="./4. Experimental Results/2. Tasks Detection/">results</a> of the tasks classification analysis;</li>
        <li>The <a href="./4. Experimental Results/4. Pipeline Evaluation/">data, scripts, and results</a> related to the overall ReFair pipeline evaluation, in terms of input User Stories, and sensitive features suggested by ReFair</li>
        <li>The <a href="./4. Experimental Results/3. Models Validation/">data, scripts, and results</a> regarding the additional experiment we performed with the practitioners.</li>
    </ol>
</ol>

Please considered that in the appendix subfolders, are reported specific readme files to help the reader in contents visualization and understanding. In particular, to replicate the study, run the analysis, and obtained the same results, please make sure to include in the same directories of the main scripts the required resourses in terms of: python dependencies, datasets, and CSVs. To ensure a good level of simplicity, all analysis scripts have been coded via python notebooks, the execution of which simply requires having installed a compatible tool such as Visual Studio Code and a version of Python no lower than 3.9. Alternatively, it is possible to import the scripts and resources into Google Colab.

## Technincal Report
In the main folder of the study appendix we released a <b>detailed technical report</b> that discuss the detailed steps and results related to the main steps of our study complementing the contents of the main paper.

## Installation & Configuration

<b>To Check</b>
In order to run the ReFair bash  prototype, all you need is Python.


Firstly clone the project and open a console in the ReFair folder, under Source Code (you can also copy the subdirectory ReFair in a different location if necessary).

The first thing to do is install Python version 3.9 (You can download it [here](https://www.python.org/downloads/)).

Immediatly after, it is necessary setting up the virtual environment in the same folder (https://docs.python.org/3/library/venv.html).


```bash
    python -m venv .
```

Sequentially, it is necessary to install all dependencies, by using the following command:

```bash
    pip install -r requirements.txt 
```

To properly run the bash script you need to add an external large model for Multi Labelling tokenizzation under the subfolder models ([link](https://www.kaggle.com/datasets/danielwillgeorge/glove6b100dtxt)):
 ```bash
    glove.6B.100d.txt
```   

Finally, you can exeute <b>ReFair pipeline</b> as follow:
<div style="text-align:center"><img src="images/refair-execution.png" /></div>

## References

<ol>
    <li>Fabris, A., Messina, S., Silvello, G., & Susto, G. A. (2022). Algorithmic fairness datasets: the story so far. Data Mining and Knowledge Discovery, 36(6), 2074-2152.</li>
    <li> N. Duran-Silva, E. Fuster, F. A. Massucci, C. Parra-Rojas, Arnau Quinquill`a, F. Roda, B. Rondelli, N. Bovenzi, and C. Toietta, “A controlled vocabulary for research and innovation in the field of artificial intelligence (ai),” 2021.</li>
    
    
</ol>
