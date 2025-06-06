# Hierarchical Latent Variable Models for Neural Data Analysis

## Authors:
- **Vaibhav Bommisetty** (vbommisetty@ucsd.edu) 
- **Mentor: Mikio Aoi** (maoi@ucsd.edu)  

---

## Summary:
How does the brain make decisions? This project dives into the neural mechanisms behind decision-making by analyzing brain activity in mice performing a visual decision-making task. Using advanced statistical models, we identify patterns in neural activity that correspond to specific behaviors, such as responding to visual stimuli or making choices. Our goal is to uncover how different brain regions work together to transform sensory information into actions, providing insights into the brain's decision-making process.

---

## Introduction:
Decision-making is a fundamental part of life, from choosing what to eat to making complex decisions at work. But how does the brain make these decisions? To answer this, we study the **superior colliculus (SC)**, a mid-brain region involved in processing sensory information and guiding actions. Specifically, we focus on two subregions of the SC—**SCdg** and **SCiw**—which play key roles in integrating sensory inputs and generating motor outputs. By analyzing neural activity in these regions, we aim to uncover how the brain encodes decision-making processes.

<img src="images/superior%20colliculus.png"
     alt="[The Superior Colliculus is highlighted in green. Although this image is of a human brain, the superior colliculus is present in all vertebrates, including mice.]"
     style="max-width: 100%; height: auto; display: block; margin-left: auto; margin-right: auto; border: 1px solid #ddd; padding: 5px; border-radius: 4px; margin-top: 15px; margin-bottom: 15px;">

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

1. **Sensitive Cluster Identification:** We identified neurons that respond strongly to specific events, such as the appearance of a visual stimulus or the start of a movement. This was done using permutation testing, a method that compares observed neural responses to random shuffles of the data to determine significance.
2. **Latent Variable Modeling:** We used Probabilistic Canonical Correlation Analysis (PCCA) to uncover hidden patterns in the neural data. PCCA is a statistical method that identifies shared variability between different sets of data, allowing us to model how neural activity relates to behavior.


---

## Results and Conclusion:

### Plots:

<!-- START OF CARUSEL -->

<div class="carousel-container">
    <div class="carousel-slide fade">
        <img src="results/PID_3675290c-8134-4598-b924-83edb7940269_Cluster_328_all.png" alt="Cluster 328 All Trials">
        <div class="carousel-caption">
            Neural activity of Cluster 328 across all trials.
            </div>
    </div>

    <div class="carousel-slide fade">
        <img src="results/PID_3675290c-8134-4598-b924-83edb7940269_Cluster_328_correct-incorrect.png" alt="Cluster 328 Correct vs Incorrect">
        <div class="carousel-caption">
            Cluster 328 activity: comparing correct vs. incorrect trials.
            </div>
    </div>

    <div class="carousel-slide fade">
        <img src="results/PID_3675290c-8134-4598-b924-83edb7940269_Cluster_328_left-right.png" alt="Cluster 328 Left vs Right Stimulus">
        <div class="carousel-caption">
            Cluster 328 activity: comparing responses to left vs. right stimuli.
            </div>
    </div>

    <a class="prev" onclick="plusSlides(-1)">&#10094;</a>
    <a class="next" onclick="plusSlides(1)">&#10095;</a>

    <div class="dots-container" style="text-align:center">
        <span class="dot" onclick="currentSlideDisplay(1)"></span>
        <span class="dot" onclick="currentSlideDisplay(2)"></span>
        <span class="dot" onclick="currentSlideDisplay(3)"></span>
    </div>
</div>

<style>
.carousel-container {
    position: relative;
    max-width: 700px; 
    margin: 20px auto; 
    border: 1px solid #ddd;
    border-radius: 5px;
    overflow: hidden;
    background-color: #f9f9f9; 
}

.carousel-slide {
    display: none;
    padding: 10px;
    text-align: center;
}

.carousel-slide img {
    max-width: 100%; 
    height: auto;  
    max-height: 450px; 
    border-radius: 4px;
    margin-bottom: 10px;
}

.carousel-caption {
    font-size: 1em;
    color: #333; 
    padding: 5px 0;
    line-height: 1.4;
}

.fade {
    animation-name: fadeEffect;
    animation-duration: 0.8s;
}

@keyframes fadeEffect {
    from {opacity: .4}
    to {opacity: 1}
}

.prev, .next {
    cursor: pointer;
    position: absolute;
    top: 50%;
    width: auto;
    padding: 16px;
    margin-top: -25px;
    color: white;
    font-weight: bold;
    font-size: 20px;
    transition: 0.3s ease;
    border-radius: 0 3px 3px 0;
    user-select: none;
    background-color: rgba(0,0,0,0.4);
}

.next {
    right: 0;
    border-radius: 3px 0 0 3px;
}

.prev:hover, .next:hover {
    background-color: rgba(0,0,0,0.7);
}

.dots-container {
    text-align: center;
    padding: 10px 0;
    background-color: #f1f1f1;
}

.dot {
    cursor: pointer;
    height: 13px;
    width: 13px;
    margin: 0 3px;
    background-color: #bbb;
    border-radius: 50%;
    display: inline-block;
    transition: background-color 0.3s ease;
}

.active, .dot:hover {
    background-color: #717171;
}
</style>

<script>
let slideIndex = 1;

function showSlides(n) {
    let i;
    let slides = document.querySelectorAll(".carousel-container .carousel-slide");
    let dots = document.querySelectorAll(".carousel-container .dot");

    if (n > slides.length) {slideIndex = 1}
    if (n < 1) {slideIndex = slides.length}

    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    for (i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "");
    }

    slides[slideIndex-1].style.display = "block";
    if (dots.length > 0 && dots[slideIndex-1]) {
        dots[slideIndex-1].className += " active";
    }
}

function plusSlides(n) {
    showSlides(slideIndex += n);
}

function currentSlideDisplay(n) {
    showSlides(slideIndex = n);
}

document.addEventListener('DOMContentLoaded', function() {
    showSlides(slideIndex);
});

</script>




<!-- END OF CARUSEL -->

<div class="carousel-container" id="carousel2"> <div class="carousel-slide fade">
        <img src="results/PCCA RMSE from Hierarchical Latent Variable Models.png" alt="PCCA RMSE">
        <div class="carousel-caption">
            PCCA Reconstruction Error (RMSE) Analysis.
            </div>
    </div>

    <div class="carousel-slide fade">
        <img src="results/Stim - Cluster 270.png" alt="Stimulus Cluster 270">
        <div class="carousel-caption">
            Stimulus-aligned activity for Cluster 270.
            </div>
    </div>

    <a class="prev" onclick="plusSlidesCarousel2(-1)">&#10094;</a>
    <a class="next" onclick="plusSlidesCarousel2(1)">&#10095;</a>

    <div class="dots-container" style="text-align:center">
        <span class="dot" onclick="currentSlideDisplayCarousel2(1)"></span>
        <span class="dot" onclick="currentSlideDisplayCarousel2(2)"></span>
    </div>
</div>

<style>
/* Styles for carousel2 (can be shared if identical, or namespaced like this) */
#carousel2.carousel-container {
    position: relative;
    max-width: 700px;
    margin: 20px auto;
    border: 1px solid #ddd;
    border-radius: 5px;
    overflow: hidden;
    background-color: #f9f9f9;
}

#carousel2 .carousel-slide {
    display: none;
    padding: 10px;
    text-align: center;
}

#carousel2 .carousel-slide img {
    max-width: 100%;
    height: auto;
    max-height: 450px;
    border-radius: 4px;
    margin-bottom: 10px;
}

#carousel2 .carousel-caption {
    font-size: 1em;
    color: #333;
    padding: 5px 0;
    line-height: 1.4;
}

#carousel2 .fade { /* Re-using fadeEffect if defined globally, or define for #carousel2 */
    animation-name: fadeEffect; /* Assumes fadeEffect is defined from previous carousel, or copy it here */
    animation-duration: 0.8s;
}

/* Ensure fadeEffect is defined if not already global */
/* @keyframes fadeEffect { from {opacity: .4} to {opacity: 1} } */


#carousel2 .prev, #carousel2 .next {
    cursor: pointer;
    position: absolute;
    top: 50%;
    width: auto;
    padding: 16px;
    margin-top: -25px;
    color: white;
    font-weight: bold;
    font-size: 20px;
    transition: 0.3s ease;
    border-radius: 0 3px 3px 0;
    user-select: none;
    background-color: rgba(0,0,0,0.4);
}

#carousel2 .next {
    right: 0;
    border-radius: 3px 0 0 3px;
}

#carousel2 .prev:hover, #carousel2 .next:hover {
    background-color: rgba(0,0,0,0.7);
}

#carousel2 .dots-container {
    text-align: center;
    padding: 10px 0;
    background-color: #f1f1f1;
}

#carousel2 .dot {
    cursor: pointer;
    height: 13px;
    width: 13px;
    margin: 0 3px;
    background-color: #bbb;
    border-radius: 50%;
    display: inline-block;
    transition: background-color 0.3s ease;
}

#carousel2 .active, #carousel2 .dot:hover { /* Note: '.active' might need to be '#carousel2 .active' if dots are specific */
    background-color: #717171;
}
</style>

<script>
// --- Script for Carousel 2 ---
// To avoid conflicts if you have multiple carousels on one page,
// it's best to make the variables and functions specific to this carousel.

let slideIndexCarousel2 = 1;

function showSlidesCarousel2(n) {
    let i;
    // Select elements specifically within this carousel (e.g., using an ID)
    let carouselContainer = document.getElementById("carousel2");
    if (!carouselContainer) return; // Exit if carousel container not found

    let slides = carouselContainer.querySelectorAll(".carousel-slide");
    let dots = carouselContainer.querySelectorAll(".dot");

    if (n > slides.length) {slideIndexCarousel2 = 1}
    if (n < 1) {slideIndexCarousel2 = slides.length}

    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    for (i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "");
    }

    slides[slideIndexCarousel2-1].style.display = "block";
    if (dots.length > 0 && dots[slideIndexCarousel2-1]) {
        dots[slideIndexCarousel2-1].className += " active";
    }
}

function plusSlidesCarousel2(n) {
    showSlidesCarousel2(slideIndexCarousel2 += n);
}

function currentSlideDisplayCarousel2(n) {
    showSlidesCarousel2(slideIndexCarousel2 = n);
}

// Initialize Carousel 2
document.addEventListener('DOMContentLoaded', function() {
    // Check if the carousel element exists before trying to initialize
    if (document.getElementById("carousel2")) {
        showSlidesCarousel2(slideIndexCarousel2);
    }
});

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
