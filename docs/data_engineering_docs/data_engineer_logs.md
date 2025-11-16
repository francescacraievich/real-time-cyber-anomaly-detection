

- we have benign_traffic.json for normal traffic logs, that gest processed by a function in the init_normal_traffic.py and outputs in the folder data the file benign_traffic_fixed.json
  - traffic dividen in malign and benign

- porblem is that the files are over the LFS github file size (2GB)
  - solution: i am going to develop a system to get this jsons in another way

- formatting of the date field is necessary
  - should be all the same!