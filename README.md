structureREST
==============
structureREST is a library of wrapper functions and a RESTful server for calculating basic structure descriptors of bulk crystalline materials. It also has support for some methods which compare but do not describe structures, like the pymatgen StructureMatcher.

Features
--------
* Descriptors:
  * Matminer CrystalNNFingerprint
  * STRUCTURE TIDY spacegroup/wyckoff
  * SOAP
* Comparitors:
  * Matminer CrystalNNFingerprint
  * pymatgen StructureMatcher
  * SOAP
    * Average Distance Kernel w/ similarity cutoff
* Continuous Distance Metrics:
  * Matminer CrystalNNFingerprint
  * SOAP
    * Average Distance Kernel

Installation
------------
Dependencies:
  * pymatgen
  * ase
  * matminer
  * QUIP with GAP
  * quippy
  * glosim2
    * tqdm
    * psutil
  * flask
  * flask_restful
  * numpy
  * scipy
  
1. Clone the repository

    ``git clone https://github.com/zooks97/structureREST ~/structureREST``

2. Install python dependencies

  ``pip install numpy scipy pymatgen ase matminer flask flask_restful``

3. Install QUIP / GAP / quippy
    
    a. One option is to use the precompiled Docker image [libatoms/quip](https://hub.docker.com/r/libatomsquip/quip/). This image is a bit bloated (3 compilations of QUIP, LAMMPS included, etc.).
    
    ``docker pull libatomsquip/quip``
    
    b. A more lightweight option is to compile the Dockerfile in `docker/`
    
      From `docker/`:
      
        . build.sh
        . run.sh
    
    c. If you're feeling adventurous, you could try to locally compile QUIP, GAP, and quippy following the instructions in the [libAtoms/QUIP repository](https://github.com/libAtoms/QUIP).

4. Install [glosim2](https://github.com/cosmo-epfl/glosim2)

  In the same environment where QUIP / GAP / quippy are installed (docker image or locally), do the following to get glosim2:
    
    git clone https://github.com/cosmo-epfl/glosim2
    pip install tqdm psutil

To use structureREST libraries, use `sys.path.insert(0, 'path/to/structureREST/lib)` followed by `import [filename]` to import all functions / classes / etc. from `structureREST/lib/[filename].py`.

To run the RESTful server, point your favorite webserver to `script/rest/structurerest.py`. Documentation for the RESTful interface can be found in `docs/`. If you wish to use SOAP through the restful interface, the current method is to install a small RESTful server `script/rest/soaprest.py` wherever quippy is available. Make sure to also download `glosim2` and modify `script/rest/soaprest.py` so that glosim is added to the path.
