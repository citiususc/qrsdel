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
report with the mean error and standard deviation of the delineation in each
record.

