# zkbrowser
A tiny python script to browsing and deleting nodes in zookeeper in your favorite web browser.

## Required modules
* kazoo
* tornado
* argparse

## Installing
```
sudo pip install tornado kazoo argparse
```

## Running
```
python zkbrowser.py --listenport 80 --hosts localhost:2181,localhost:2182
```

Now point your browser to 
http://localhost
