# zkbrowser
A tiny python script to browsing and deleting nodes in zookeeper in your favorite web browser.

## Required modules
* kazoo
* tornado

## Installing
```
sudo pip install tornado kazoo
```

## Running
```
python zkbrowser.py --listenport 80 --hosts localhost:2181,localhost:2182
```

Now point your browser to 
http://localhost
