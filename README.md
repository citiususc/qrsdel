# qrsdel
This project provides the implementation of a noise robust multi-lead QRS
delineation algorithm on ECG signals. It is recommended to be familiar with the
[WFDB software package](http://www.physionet.org/physiotools/wfdb.shtml) in
order to fully exploit this package.

## Installation

This project is implemented in pure python, so no installation is required.
However, there are strong dependencies with the following python packages:

1. [blist](https://pypi.python.org/pypi/blist)
2. [scipy](https://pypi.python.org/pypi/scipy)
3. [numpy](https://pypi.python.org/pypi/numpy)

Moreover, if you want to use **qrsdel** as a standalone application, it is
necessary to have access to a proper installation of the WFDB software
package.

Once all these dependencies are satisfied, is enough to download the project
sources and execute or import the proper python scripts, as explained in the
next section.

## Getting Started

### qrsdel as a standalone application:

**qrsdel** can be used directly from the command line in order to perform the
delineation of a set of previously detected QRS complexes in a signal file in the
[WFDB format](http://www.physionet.org/physiotools/wag/wag.htm). To do this,
simply enter following command from the root *qrsdel* directory:

```
python -m qrsdel.qrsdel [-h] -r RECORD -a REF -o OUTPUT
  -r RECORD   Input record.
  -a REF      Annotator name containing reference QRS annotations.
  -o OUTPUT   Annotator name where the delineation results are stored.
```

This action loads the `RECORD` record and the QRS annotations from the
annotations file with `REF` extension, and generates a new annotations file
with `OUTPUT` extension with the delineation of every QRS complex.

### qrsdel as a library:

It can also be possible to use **qrsdel** as a library to be included in wider
projects. In that case, there are no dependencies with the WFDB software package,
but the responsibility to provide the signal and the proper parameters remains
in the user. The entry point of the library is the `delineate_qrs()` function
in the *qrsdel/delineation.py* module, and a usage example is shown in the
*qrsdel/qrsdel.py* main module.

Using **qrsdel** as a library allows you to deeply control how the algorithm
works, besides obtaining additional information as per-lead delineation
information or qualitative characterizations of the recognized waveforms.

## Algorithm Evaluation

The project also includes some utilities to evaluate the robustness of the
algorithm. The *generate_nsqtdb.py* script allows to generate a new database from
the [Physionet QT database](http://www.physionet.org/physiobank/database/qtdb/)
by adding different amounts of electrode motion noise to each record, by
following these steps:

1. Download the full QT database to a new directory, and also copy the *em_250*
record that can be found in the *records* directory.
2. Modify the *generate_nsqtdb.py* script to set `DB_DIR` variable to the path
to the directory where the database has been downloaded.
3. Run `python generate_nsqtdb.py` in order to generate the new records.

Once the database has been generated and **qrsdel** has been executed with each
record, the *error_measurements.py* module can be used to generate a markdown
report with the mean error and standard deviation of the QRS delineation in each
record. Following we show an example of one of such reports, obtained from the
original records of the QT database.

### Distances table
| Record | Se | QRS Onset (ms) | QRS Peak (ms)| QRS Offset (ms)|
|--------|----|----------------|--------------|----------------|
|**sel100** |1.00|6.00 ± 15.24|-10.80 ± 2.10|-2.13 ± 6.67|
|**sel102** |0.99|44.86 ± 24.70|-41.43 ± 24.01|-48.33 ± 59.78|
|**sel103** |1.00|20.40 ± 7.96|-2.93 ± 3.71|-1.07 ± 9.23|
|**sel104** |1.00|24.36 ± 17.83|-29.19 ± 22.59|-7.27 ± 21.55|
|**sel114** |1.00|9.84 ± 15.50|-1.44 ± 1.92|-7.20 ± 14.49|
|**sel116** |1.00|9.04 ± 13.24|-11.68 ± 1.93|-0.48 ± 15.77|
|**sel117** |1.00|11.60 ± 9.54|-10.00 ± 3.39|0.80 ± 11.79|
|**sel123** |1.00|15.87 ± 16.18|-6.67 ± 2.39|8.40 ± 13.52|
|**sel14046** |1.00|6.84 ± 7.55|-10.06 ± 3.19|0.52 ± 5.63|
|**sel14157** |1.00|16.67 ± 15.73|-17.73 ± 4.58|-2.27 ± 7.98|
|**sel14172** |1.00|17.04 ± 13.45|-19.68 ± 13.76|-0.48 ± 6.82|
|**sel15814** |1.00|17.07 ± 13.10|-4.13 ± 7.41|-22.53 ± 34.06|
|**sel16265** |1.00|10.00 ± 11.21|-7.60 ± 2.39|9.73 ± 10.21|
|**sel16272** |1.00|-4.00 ± 11.78|-4.27 ± 2.52|3.87 ± 8.42|
|**sel16273** |1.00|-4.27 ± 18.12|-12.80 ± 6.65|3.07 ± 8.18|
|**sel16420** |1.00|12.93 ± 6.59|-1.73 ± 4.09|0.80 ± 7.11|
|**sel16483** |1.00|15.33 ± 9.86|-9.87 ± 2.47|7.73 ± 8.26|
|**sel16539** |1.00|8.40 ± 7.11|-6.27 ± 5.90|3.33 ± 5.37|
|**sel16773** |1.00|20.80 ± 10.45|-10.27 ± 3.04|7.07 ± 7.84|
|**sel16786** |1.00|-9.07 ± 16.65|-17.60 ± 2.44|-0.53 ± 9.45|
|**sel16795** |1.00|8.00 ± 8.82|-19.73 ± 3.57|1.20 ± 8.83|
|**sel17152** |1.00|17.73 ± 7.64|3.47 ± 3.22|-3.33 ± 12.99|
|**sel17453** |1.00|10.00 ± 8.63|-16.27 ± 3.26|6.27 ± 8.98|
|**sel213** |1.00|22.25 ± 14.55|-16.28 ± 11.98|8.73 ± 8.18|
|**sel221** |1.00|0.40 ± 16.76|-7.73 ± 4.49|5.33 ± 15.64|
|**sel223** |1.00|10.32 ± 17.62|-0.65 ± 1.79|27.87 ± 15.26|
|**sel230** |1.00|12.32 ± 12.05|-12.16 ± 3.83|8.88 ± 7.26|
|**sel231** |1.00|-11.44 ± 16.14|-13.04 ± 5.65|5.52 ± 17.71|
|**sel232** |1.00|10.53 ± 9.09|2.13 ± 2.00|-54.67 ± 39.70|
|**sel233** |1.00|10.40 ± 11.01|-5.73 ± 3.68|2.00 ± 8.69|
|**sel30** |1.00|-0.93 ± 19.51|-9.20 ± 1.83|-14.40 ± 8.62|
|**sel301** |1.00|11.33 ± 8.20|-4.40 ± 2.15|8.27 ± 7.08|
|**sel302** |1.00|17.73 ± 5.23|-6.13 ± 2.47|-1.07 ± 7.79|
|**sel306** |1.00|2.56 ± 14.55|-11.78 ± 3.99|3.11 ± 7.61|
|**sel307** |1.00|14.67 ± 6.23|-6.00 ± 2.00|6.27 ± 6.51|
|**sel308** |1.00|13.52 ± 15.39|-48.24 ± 8.67|3.12 ± 10.25|
|**sel31** |1.00|16.40 ± 21.00|-12.00 ± 2.31|-9.60 ± 6.08|
|**sel310** |1.00|19.87 ± 5.11|-9.60 ± 1.96|0.67 ± 7.24|
|**sel32** |1.00|8.53 ± 13.77|-11.60 ± 4.54|-3.60 ± 10.03|
|**sel33** |1.00|24.67 ± 3.11|-10.80 ± 3.60|-16.53 ± 14.23|
|**sel34** |1.00|19.73 ± 4.95|-10.00 ± 2.00|-40.40 ± 6.88|
|**sel35** |1.00|12.90 ± 13.51|-10.71 ± 2.36|-7.48 ± 7.09|
|**sel36** |1.00|15.74 ± 10.56|-9.42 ± 2.39|-61.29 ± 38.51|
|**sel37** |1.00|18.08 ± 16.86|-7.68 ± 8.68|-7.12 ± 12.83|
|**sel38** |1.00|32.27 ± 11.77|24.00 ± 6.20|-16.27 ± 9.74|
|**sel39** |1.00|4.93 ± 6.42|-17.20 ± 4.75|-25.73 ± 28.16|
|**sel40** |1.00|20.80 ± 11.61|-12.13 ± 2.19|-6.13 ± 8.56|
|**sel41** |1.00|17.47 ± 6.81|-7.60 ± 1.58|-2.53 ± 9.77|
|**sel42** |1.00|43.47 ± 5.91|-12.40 ± 10.75|-6.40 ± 5.23|
|**sel43** |1.00|57.20 ± 13.15|-3.73 ± 5.56|-0.27 ± 5.26|
|**sel44** |1.00|33.47 ± 29.64|-10.13 ± 2.00|-28.67 ± 23.03|
|**sel45** |1.00|22.67 ± 5.78|-11.60 ± 1.89|-6.27 ± 8.93|
|**sel46** |1.00|5.07 ± 17.34|-18.53 ± 8.67|-2.80 ± 5.38|
|**sel47** |1.00|24.67 ± 16.75|-12.00 ± 3.10|-13.87 ± 16.58|
|**sel48** |1.00|17.73 ± 12.51|-13.33 ± 1.89|-22.13 ± 15.86|
|**sel49** |1.00|15.47 ± 5.03|-5.73 ± 1.98|-11.60 ± 10.65|
|**sel50** |1.00|15.62 ± 16.62|-8.88 ± 3.57|-4.25 ± 14.03|
|**sel51** |1.00|10.93 ± 5.05|-1.20 ± 1.83|-20.00 ± 7.45|
|**sel52** |1.00|-1.87 ± 21.48|-8.00 ± 2.53|-8.67 ± 12.61|
|**sel803** |1.00|12.00 ± 7.93|-3.73 ± 2.29|8.67 ± 13.15|
|**sel808** |1.00|3.87 ± 8.67|-27.73 ± 3.99|1.20 ± 7.88|
|**sel811** |1.00|13.47 ± 14.22|-4.80 ± 2.40|6.67 ± 18.48|
|**sel820** |1.00|-0.27 ± 13.14|-10.00 ± 2.25|10.40 ± 9.44|
|**sel821** |1.00|6.13 ± 7.28|-8.93 ± 3.38|4.93 ± 4.09|
|**sel840** |1.00|9.26 ± 4.56|-12.06 ± 5.72|8.00 ± 6.34|
|**sel847** |1.00|4.36 ± 13.41|-8.97 ± 3.94|2.91 ± 6.70|
|**sel853** |1.00|-0.67 ± 16.82|-17.47 ± 2.63|7.20 ± 5.69|
|**sel871** |1.00|32.69 ± 9.27|-29.60 ± 9.06|3.60 ± 5.82|
|**sel872** |1.00|15.20 ± 7.19|-4.53 ± 2.25|10.93 ± 6.10|
|**sel873** |1.00|12.97 ± 5.83|-7.27 ± 5.95|4.36 ± 6.56|
|**sel883** |1.00|10.13 ± 14.92|-6.40 ± 3.20|6.27 ± 15.75|
|**sel891** |1.00|5.75 ± 15.13|-19.32 ± 2.51|-3.61 ± 18.79|
|**sele0104** |1.00|16.40 ± 4.77|-11.73 ± 2.29|9.73 ± 7.84|
|**sele0106** |1.00|20.53 ± 4.47|-5.07 ± 9.85|11.73 ± 4.73|
|**sele0107** |1.00|17.06 ± 11.24|-6.59 ± 3.20|2.47 ± 5.74|
|**sele0110** |1.00|8.93 ± 4.70|-13.47 ± 7.12|3.20 ± 4.78|
|**sele0111** |1.00|7.60 ± 7.11|-10.53 ± 3.50|7.20 ± 17.26|
|**sele0112** |1.00|16.40 ± 10.62|-10.24 ± 3.68|19.36 ± 8.37|
|**sele0114** |1.00|13.87 ± 10.11|-6.53 ± 2.42|10.13 ± 9.45|
|**sele0116** |1.00|2.13 ± 16.77|-6.00 ± 3.39|-18.13 ± 25.77|
|**sele0121** |1.00|7.07 ± 5.03|-3.87 ± 1.63|14.93 ± 8.06|
|**sele0122** |1.00|11.33 ± 4.51|-9.73 ± 1.98|16.27 ± 7.72|
|**sele0124** |1.00|7.04 ± 8.96|-5.76 ± 4.74|3.28 ± 11.99|
|**sele0126** |1.00|11.73 ± 7.65|-1.60 ± 4.80|8.80 ± 10.65|
|**sele0129** |1.00|-10.27 ± 19.67|-22.80 ± 3.12|14.27 ± 7.84|
|**sele0133** |1.00|4.00 ± 20.16|-24.67 ± 3.11|13.33 ± 7.96|
|**sele0136** |1.00|18.93 ± 5.46|-6.00 ± 2.68|9.47 ± 7.04|
|**sele0166** |1.00|-29.78 ± 13.15|-11.67 ± 7.20|-0.44 ± 16.43|
|**sele0170** |1.00|9.87 ± 5.91|-3.87 ± 0.72|6.93 ± 3.26|
|**sele0203** |1.00|11.33 ± 7.87|-5.33 ± 2.15|2.67 ± 8.78|
|**sele0210** |1.00|17.73 ± 7.64|-6.00 ± 2.00|2.93 ± 12.00|
|**sele0211** |1.00|9.60 ± 18.11|-5.07 ± 2.05|8.53 ± 8.87|
|**sele0303** |1.00|14.27 ± 4.70|-2.13 ± 2.68|12.40 ± 8.54|
|**sele0405** |1.00|-2.13 ± 10.26|-12.80 ± 2.17|2.67 ± 10.03|
|**sele0406** |1.00|5.29 ± 13.95|-5.68 ± 3.01|4.26 ± 3.79|
|**sele0409** |1.00|12.00 ± 6.28|-3.73 ± 1.44|0.40 ± 5.69|
|**sele0411** |1.00|7.20 ± 6.23|-6.53 ± 2.19|3.60 ± 12.58|
|**sele0509** |1.00|6.27 ± 4.58|-6.13 ± 2.00|-34.13 ± 5.34|
|**sele0603** |1.00|6.53 ± 13.72|-10.80 ± 2.95|1.20 ± 15.18|
|**sele0604** |1.00|8.53 ± 6.09|-15.33 ± 7.24|7.87 ± 10.46|
|**sele0606** |1.00|16.93 ± 6.59|-6.13 ± 2.00|-26.80 ± 4.64|
|**sele0607** |1.00|22.40 ± 14.03|-23.07 ± 1.69|4.80 ± 6.88|
|**sele0609** |1.00|21.87 ± 11.40|1.60 ± 1.96|11.07 ± 12.12|
|**sele0612** |1.00|13.47 ± 14.51|-6.00 ± 2.25|-0.93 ± 11.99|
|**sele0704** |1.00|11.60 ± 9.08|-20.27 ± 4.84|-84.53 ± 12.76|
|**Total:** |1.00|13.09 ± 17.48|-11.47 ± 12.01|-2.41 ± 22.34|


