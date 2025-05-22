# IIBProj_Text2CompModel

<!-- dealing with multiple Java versions:

[text](https://batsov.com/articles/2021/12/10/working-with-multiple-versions-of-java-on-ubuntu/) -->

This is the code repository for my IIB project under Dr Alice Cicirello on "From Text to Computational Models for Dynamical Systems". Due to the nature of the project, the documentation and organisation of the code was not explicitly maintained to a high standard as the main deliverable was just the results and report for the project.

This README will serve as a brief outline of the repository and its structure so that if someone intends to continue working on the project that they can have a headstart on figuring how all these files fit together

I will eventually leave a link to the final project report here so that people can have additional context to the repository

## Prerequisites

This repository requires the OPENIE tool from [text](https://github.com/dair-iitd/OpenIE-standalone). The script "run_OPENIE.sh" could be edited to run the openIE model if you set the path to the executable necessary.

## Structure

This section will details the different important folders and what they contain

### Assets
contains a bunch of generated diagrams and text files used as inputs for the software

### artificer
An implementation of a paper that the project was based on [text](https://www.sciencedirect.com/science/article/pii/S0950705122011649), we then copied this implementation into the dynamo folder to further extend on the paper's ideas into the project we finally made.

### dynamo
The final implementation of the project, the modules in this folder should have names that are self-explanatory. To run the code, you can edit up the "dyn_main.py" file in the root folder and it should run the entire project.




