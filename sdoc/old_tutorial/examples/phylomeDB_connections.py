from ete3 import PhylomeDBConnector
# This connects to the main phylomeDB server (default parameters)
p = PhylomeDBConnector()
# This connects to a local version of phylomeDB, and you can set the
# user and password arguments
p = PhylomeDBConnector(host="localhost", user="public", passwd="public", port=3306)
