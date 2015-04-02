#!/usr/bin/env python

import tornado
import tornado.web
import tornado.httpserver
import tornado.ioloop
import kazoo
import kazoo.client
import argparse
import base64
import os
import logging
import sys

parser = argparse.ArgumentParser(description='Zookeeper client browser')
parser.add_argument(
    '--listenport',
    help='HTTP listen port',
    required=False,
    metavar='PORT',
    default='8888')
parser.add_argument(
    '--hosts',
    help='ZooKeeper hosts with ports',
    required=False,
    metavar='HOSTS',
    default='localhost:2181')
args = parser.parse_args()

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

zk = kazoo.client.KazooClient(hosts=args.hosts)
zk.start()

logging.info('Kazoo connected')

class RequestHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        logging.info('GET request: {0}'.format(self.request.full_url()))

        zkPath = self.request.path
        zkDelete = self.get_query_argument('delete', default='no')
        zkSet = self.get_query_argument('set', default='no')
        zkSetValueB64 = self.get_query_argument('value', default='')
        path = self.request.path.replace('//', '/')
        url = self.request.protocol + "://" + self.request.host + path

        if url.endswith('/'):
            url = url[:-1]

        if zkDelete == 'yes':
            logging.debug('Deleting node: {0}'.format(zkPath))

            zk.delete(zkPath, recursive=True)
            self.redirect(url + '/..')
        elif zkSet == 'yes':
            zkSetValue = base64.b64decode(zkSetValueB64)
            logging.debug('Setting node content: {0} : {1}'.format(zkPath, zkSetValue))

            zk.set(zkPath, zkSetValue)
            self.redirect(url)
        else:
            logging.debug('Printing information of node {0}'.format(zkPath))

            zkChildren = sorted(zk.get_children(zkPath))
            raw_data = zk.get(zkPath)
            zkData = raw_data[0]
            zkInfo = raw_data[1]

            self.render('zkbrowser_template.html',
                zkPath=zkPath,
                zkData=zkData,
                zkInfo=zkInfo,
                zkChildren=zkChildren,
                url=url)

logging.info('Setting up web server')

app = tornado.web.Application([
    (r'/(favicon\.ico)', tornado.web.StaticFileHandler, {'path': os.getcwd()}),
    (r'/(.)*', RequestHandler)])
http_server = tornado.httpserver.HTTPServer(app)
http_server.listen(int(args.listenport))

logging.info('Starting web server')

tornado.ioloop.IOLoop.instance().start()