# methacetin
[![GitHub version](https://badge.fury.io/gh/matthiaskoenig%2Fliverfunction.svg)](https://badge.fury.io/gh/matthiaskoenig%2Fliverfunction)
[![Build Status](https://travis-ci.org/matthiaskoenig/liverfunction.svg?branch=develop)](https://travis-ci.org/matthiaskoenig/liverfunction)

<b><a href="https://orcid.org/0000-0003-1725-179X" title="https://orcid.org/0000-0003-1725-179X"><img src="./docs/images/orcid.png" height="15"/></a> Matthias König</b>


## Funding
Matthias König is supported by the Federal Ministry of Education and Research (BMBF, Germany) 
within the research network Systems Medicine of the Liver (LiSyM, grant number 031L0054).

<a href="http://www.lisym.org/" alt="LiSyM" target="_blank"><img src="./docs/images/lisym.png" height="35"></a> &nbsp;&nbsp;
<a href="http://www.bmbf.de/" alt="BMBF" target="_blank"><img src="./docs/images/bmbf.png" height="35"></a> &nbsp;&nbsp;

## Installation
### Setup

```
git clone https://github.com/matthiaskoenig/liverfunction.git
cd liverfunction
mkvirtualenv liverfunction --python=python3.6
(liverfunction) pip install -e .
(liverfunction) pip install jupyterlab --upgrade
```
Install jupyter kernel
```
# install kernel for ipython
(liverfunction) python -m ipykernel install --user --name=liverfunction

# start jupyter lab
(liverfunction) jupyter lab
```

### Testing
```
tox -e py35
```

```
(limax) pytest
```


## Release notes

### 0.0.1
* initial package build

----
&copy; 2018-2019 Matthias König.
