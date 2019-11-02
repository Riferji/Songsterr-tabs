# Introduction

In *https://www.songsterr.com/* we can find a lot of tablatures for guitar songs. In this proyect, we define an scrapper than takes an songsterr's url as input and takes screenshots from the page, save all of it in the disk, an finally bind all together in a single pdf using Miktext.

# Libraries
  
+ selenium  
+ pandas  
+ time  
+ tqdm  
+ os    
+ io  
+ glob  
+ subprocess  

# How to start it

You need to configure the path to Chrome.exe and Firefox.exe at the start of the Songsterr class.

Secondly, you need to have *chromedriver* and *geckodriver* in your executable path (Provided in the folder). Those programs are necessary for run the Chrome and Firefox drivers.

Finally, you need Miktext to compile the pdf in your shell (It will use the sentence *pdflatex "{tex_path}" -quiet -output-directory="{output_path}" -aux-directory="{aux_path}"*