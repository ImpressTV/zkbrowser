#!/usr/bin/env python

import tornado
import tornado.web
import tornado.httpserver
import tornado.ioloop
import kazoo
import kazoo.client
import argparse
import os

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

zk = kazoo.client.KazooClient(hosts=args.hosts)
zk.start()

print('Kazoo connected...')

class RequestHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        print(self.request.full_url())
        zkPath = self.request.path
        zkDelete = self.get_query_argument('delete', default='no')
        path = self.request.path.replace('//', '/')
        url = self.request.protocol + "://" + self.request.host + path

        if url.endswith('/'):
            url = url[:-1]

        if zkDelete == 'yes':
            zk.delete(zkPath, recursive=True)
            self.redirect(url + '/..')
        else:
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

app = tornado.web.Application([
    (r'/(favicon\.ico)', tornado.web.StaticFileHandler, {'path': os.getcwd()}),
    (r'/(.)*', RequestHandler)])
http_server = tornado.httpserver.HTTPServer(app)
http_server.listen(int(args.listenport))

#Starting the server
tornado.ioloop.IOLoop.instance().start()