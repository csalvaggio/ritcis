# RITCIS Database of Handwritten Letters

The [MNIST database of handwritten digits](http://yann.lecun.com/exdb/mnist/) has long been a standard data set for training and testing machine learning architectures aimed at the classification problem.

The **RITCIS database of handwritten letters** (uppercase) has been developed to serve this same purpose.  This database has been created using samples prepared by students, staff, and faculty at the [Rochester Institute of Technology](https://www.rit.edu)'s [Chester F. Carlson Center for Imaging Science](https://www.rit.edu/science/chester-f-carlson-center-imaging-science) as part of the course titled *Image Processing and Computer Vision* (IMGS.361) [Fall Semester of AY2023-2024].

A sample handwritten letters form used to collect the samples for the RITCIS database is shown below:

<p align="center" width="100%">
    <img width="50%" src="images/sample.png">
</p>

To date, 109 forms have been prepared and used to create the current instantiation of the database.  This instantiation is split into 39,521 training images and 7,905 test images.

The format of the training/test images and labels files, located in the `datasets` directory above, are identical to those used for the MNIST database files.  Data readers designed for reading MNIST database files should work identically on the RITCIS database files.

The compressed database files located in `datasets` are named as 

    test-images-028-ubyte.gz
    test-labels-028-ubyte.gz
    train-images-028-ubyte.gz
    train-labels-028-ubyte.gz

where the `028` represents the square dimension of the images (28x28 pixels in this example).  Be sure to decompress these database files prior to use on your system.



flowchart LR
  A[Capture] --> B(Document) --> C{{Review and<br/>Approve}} --> D(Publish) --> E((( )))




## Data Preparation

The handwritten letters (paper/physical) forms were all scanned utilizing a Xerox AltaLink B8170.  The following modifications were made to the default scan settings:

* Output Color: Color
* Resolution: 600 dpi
* Quality/File Size: Lowest Compression / Largest File Size

(documentation is still in progress)

## Requirements

(documentation in progress)

## Acknowledgements

If you find this database useful and utilize it in your research, please attribute this repository in your publications as follows

Plain Text

    Salvaggio, Carl (2023). RITCIS Database of Handwritten Letters. GitHub. URL: https://github.com/csalvaggio/ritcis.

BibTeX

    @misc{salvaggio_ritcis_2023,
        title = {RITCIS Database of Handwritten Letters},
        author = {Carl Salvaggio},
        year = 2023,
        publisher = {Rochester Institute of Technology},
        howpublished = {https://github.com/csalvaggio/ritcis}
    }

<span style="font-size:small;color:red;">Copyright (C) 2023, Rochester Institute of Technology</span>