CS579-final-project
===================

How to run:


A. go to ./src directory
B. save your twitter key/access_token in file "twitter.cfg"


Data collection:

    A. Stream API:
        A. run "./stream_dataCollection.sh"
        B. data will be saved in ./stream_data/
        C. Output infomation will be saved in ./dcout.txt
        
    B. Rest API:
        A. run "./stream_dataCollection.sh"
        B. data will be saved in ./rest_data/
        C. Output infomation will be saved in ./rdcout.txt

Program:

    A. make sure that "./stream_data/" and "./rest_data/" exist
    B. open tap.ipynb "ipython notebook --matplotlib inline tap.ipynb"
    C. Search for "Begin here" cell
    D. Run every cell begin with that cell. The functions of each cells are described in the first few lines of the cell
    E. When meet "End here", stop running
