Talce an arbitrary DNA sequence from NCBI 5 restriction enzgmes (enzgmez name, regognized sequence)
application should take into account multiple enzgmes accounts 

EcoRl | 5'GAATTC 5'---G DELTE_DOWN_SYMBOL AATTC---3'
      | 3'CTTAAG 3'---CTTAA DELTA_UP_SYMBOL G---5'

BamHl | 5'GGATCC 5'---G DELTE_DOWN_SYMBOL GATCC---3'
      | 3'CCTAGG 3'---CCTAG DELTE_UP_SYMBOL G---5'

      THE OUTPUT SHOULD TAKE INTO CONSIDERATION COMBINATIONS OF DIFFERENT RESTRICTION ENZGMES

      
A sim of the electrophibsesus gel biased on the nr of restrictions enz used (either a bacterial genome or a viral genome to use cleavage site)

Hindlll | 5'GAAGCTT 5'---A DELTE_DOWN_SYMBOL AGCTT---3'
      | 3'TTCGAA 3'---TTCGA DELTA_UP_SYMBOL A---5'

Tagl  | 5'TCGA 5'---T DELTE_DOWN_SYMBOL CGA---3'
      | 3'AGCT 3'---AGC DELTE_UP_SYMBOL T---5'


Haelll  | 5'GGCC 5'---GG DELTE_DOWN_SYMBOL CC---3'
        | 3'CCGG 3'---CC DELTE_UP_SYMBOL GG---5'



Input: recognized sequence (oricare ar fi symbol or whatever the input) restriction enz a DNA to be digested
Output: 1) No. of cleavages (oricare ar fi symbol or whatever the input) restrict enz 
        2) cleavefes positions & lenght
        3) up arrow


Second task:
use a random generated DNA sequence (make sure it's rand rand like use time or all) in which you insert inverted repeats in order to simulate different transposes this way you know what is sorted out
the minimum distance between the inverted repeats composing the transposes should be of 10 positions 

the inverted repeats...

taken in the consideration the following cases:
1) overlapping transposes, nested transposes and the normal pattern in which normal transposes are positioned one after the other

Output: position of each transposes in each seq.
        lenght