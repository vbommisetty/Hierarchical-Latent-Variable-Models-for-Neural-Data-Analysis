# Hierarchical Latent Variable Models for Neural Data Analysis

## Authors:
- **Vaibhav Bommisetty** (vbommisetty@ucsd.edu)  
- **Beomseuk Seo** (bseo@ucsd.edu)  
- **Mentor: Mikio Aoi** (maoi@ucsd.edu)  

---

## Summary:
How does the brain make decisions? This project dives into the neural mechanisms behind decision-making by analyzing brain activity in mice performing a visual decision-making task. Using advanced statistical models, we identify patterns in neural activity that correspond to specific behaviors, such as responding to visual stimuli or making choices. Our goal is to uncover how different brain regions work together to transform sensory information into actions, providing insights into the brain's decision-making process.

---

## Introduction:
Decision-making is a fundamental part of life, from choosing what to eat to making complex decisions at work. But how does the brain make these decisions? To answer this, we study the **superior colliculus (SC)**, a brain region involved in processing sensory information and guiding actions. Specifically, we focus on two subregions of the SC—**SCdg** and **SCiw**—which play key roles in integrating sensory inputs and generating motor outputs. By analyzing neural activity in these regions, we aim to uncover how the brain encodes decision-making processes.

<style>
  .brain-map {
    max-width: 600px;
    display: block;
    margin: auto;
  }
  .region {
    fill-opacity: 0.6;
    cursor: pointer;
    transition: fill-opacity 0.2s ease-in-out;
  }
  .region:hover {
    fill-opacity: 1;
  }
  .tooltip {
    position: absolute;
    background: white;
    padding: 5px;
    border: 1px solid black;
    display: none;
    font-size: 14px;
  }
</style>

<div id="tooltip" class="tooltip"></div>

<svg class="brain-map" viewBox="0 0 600 400">
  <!-- Background brain shape -->
  <path d="M100,150 C200,50 400,50 500,150 C550,250 400,350 300,350 C200,350 50,250 100,150"
    fill="#ccc" stroke="black" stroke-width="2"></path>

  <!-- Superior Colliculus Deep Gray Layer (SCdg) -->
  <path class="region" d="M250,200 C280,180 320,180 350,200 C340,220 260,220 250,200"
    fill="blue" data-name="Superior Colliculus Deep Gray Layer (SCdg)"></path>

  <!-- Superior Colliculus Intermediate White Layer (SCiw) -->
  <path class="region" d="M250,220 C280,200 320,200 350,220 C340,240 260,240 250,220"
    fill="yellow" data-name="Superior Colliculus Intermediate White Layer (SCiw)"></path>
</svg>

<script>
  const tooltip = document.getElementById("tooltip");

  document.querySelectorAll(".region").forEach(region => {
    region.addEventListener("mouseenter", (e) => {
      tooltip.innerText = e.target.dataset.name;
      tooltip.style.display = "block";
    });

    region.addEventListener("mousemove", (e) => {
      tooltip.style.left = e.pageX + 10 + "px";
      tooltip.style.top = e.pageY + 10 + "px";
    });

    region.addEventListener("mouseleave", () => {
      tooltip.style.display = "none";
    });
  });
</script>

---

## Background:

### Decision-Making Task:
Mice were trained to perform a visual decision-making task. They were shown visual patterns (striped gratings) on either the left or right side of a screen and had to turn a steering wheel in the corresponding direction to receive a reward. Correct choices were rewarded with a drop of sugar water, while incorrect choices resulted in a timeout. This task allowed us to study how neural activity changes during sensory processing, decision-making, and feedback.

### Data:
We used data from the **International Brain Laboratory (IBL)**, one of the largest collections of neural recordings in neuroscience. The dataset includes recordings from 139 mice, with activity from over 600,000 neural units captured using advanced **Neuropixels probes**. These probes allow us to measure the activity of hundreds of neurons simultaneously, providing a detailed view of how different brain regions work together.

### Interactive Data Exploration:
The frame below allows you to explore the different probes and even view a video of the trials. The probe that is currently selected is the probe that gathered data for the SCdg brain region.

<div style="width: 100%; height: 700px; border: 1px solid #ddd; border-radius: 5px; overflow: hidden; margin: 20px 0;">
    <iframe 
        src="https://viz.internationalbrainlab.org/app?dset=bwm&pid=069c2674-80b0-44b4-a3d9-28337512967f&tid=0&cid=-1&qc=0&spikesorting=ss_original" 
        style="width: 100%; height: 100%; border: none;"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope" 
        allowfullscreen>
    </iframe>
</div>

*Courtesy of the International Brain Lab (IBL). [https://viz.internationalbrainlab.org/](https://viz.internationalbrainlab.org/)*

---

## Methods:
To analyze the data, we used a combination of statistical and machine learning techniques:

1. **Sensitive Cluster Identification:** We identified neurons that respond strongly to specific events, such as the appearance of a visual stimulus or the start of a movement. This was done using **permutation testing**, a method that compares observed neural responses to random shuffles of the data to determine significance.

2. **Latent Variable Modeling:** We used **Probabilistic Canonical Correlation Analysis (PCCA)** to uncover hidden patterns in the neural data. PCCA is a statistical method that identifies shared variability between different sets of data, allowing us to model how neural activity relates to behavior.
---

## Results and Conclusion:

### Plots:
<style>
  .gallery img {
    height: 150px;
    margin: 5px;
    cursor: pointer;
    transition: transform 0.2s;
  }
  .gallery img:hover {
    transform: scale(1.1);
  }
  .modal {
    display: none;
    position: fixed;
    z-index: 999;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.8);
  }
  .modal img {
    display: block;
    max-width: 80%;
    max-height: 80%;
    margin: auto;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }
  .modal-close {
    position: absolute;
    top: 15px;
    right: 25px;
    font-size: 30px;
    color: white;
    cursor: pointer;
  }
</style>

<div class="gallery">
  <img src="results/PID_3675290c-8134-4598-b924-83edb7940269_Cluster_328_all.png" onclick="openModal(this.src)">
  <img src="results/PID_3675290c-8134-4598-b924-83edb7940269_Cluster_328_correct-incorrect.png" onclick="openModal(this.src)">
  <img src="results/PID_3675290c-8134-4598-b924-83edb7940269_Cluster_328_left-right.png" onclick="openModal(this.src)">
  <img src="results/Stim - Cluster 270.png" onclick="openModal(this.src)">
  <img src="results/PCCA Reconstruction Error.png" onclick="openModal(this.src)">
</div>

<div id="modal" class="modal" onclick="closeModal()">
  <span class="modal-close">&times;</span>
  <img id="modal-image">
</div>

<script>
  function openModal(src) {
    document.getElementById("modal").style.display = "block";
    document.getElementById("modal-image").src = src;
  }
  function closeModal() {
    document.getElementById("modal").style.display = "none";
  }
</script>
### Conclusion:
Our analysis revealed distinct patterns of neural activity in the SCdg and SCiw regions during decision-making. For example, certain neurons responded more strongly to visual stimuli on the left versus the right, while others were more active during correct versus incorrect choices. Using PCCA, we were able to identify shared patterns of activity that correspond to specific behaviors, such as turning the wheel or receiving feedback.

However, our results also highlighted some limitations. While PCCA is effective at capturing linear relationships, it struggles with more complex, nonlinear dynamics. This is where methods like GPFA could be more powerful, as they can model smooth, time-varying patterns in neural activity.

---

## Future Work:
To build on this research, we plan to:
1. Explore **Gaussian Process Factor Analysis (GPFA)** to better capture nonlinear relationships and temporal dynamics in neural data.
2. Investigate other brain regions involved in decision-making to understand how different areas work together.
3. Develop more efficient computational methods to handle the large-scale data generated by modern neuroscience experiments.

By combining advanced statistical models with high-resolution neural recordings, we hope to uncover new insights into how the brain makes decisions and ultimately contribute to a deeper understanding of brain function.

---
