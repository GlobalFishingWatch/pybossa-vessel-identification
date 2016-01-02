#Installing Pybossa

The following outlines how to install PyBossa on Google Cloud virtual machine.

This is how I set up PyBossa. I followed the instructions from [on installing PyBossa by hand](http://docs.pybossa.com/en/latest/install.html), and made two small modifications:
* We didn't clone the master -- instead we got the most recent release. Which was v1.3.0
* I needed to install one more python library that was not included in requirements. I note it below (pip install Flask-Misaka). It would probably be good to know why I had to do this, as I should not have had to given the instructions.

