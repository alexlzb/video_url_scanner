# -*- coding: UTF-8 -*-
"""
@author:Alex
@file:video_url_scanner.py
@time:2023/12/20
"""
import os
import re
import cv2
import sys
import time
import json
import socket
import zipfile
import argparse
from datetime import datetime
from urllib.parse import urlparse


os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = "timeout;20000"

def is_valid_ip_address(ip):
    pattern = r'^((25[0-5]|2[0-4]\d|1\d{2}|[1-9]\d|\d)\.){3}(25[0-5]|2[0-4]\d|1\d{2}|[1-9]\d|\d)$'
    return re.match(pattern, ip) is not None


def url_check(url, prefix):
    try:
        # Support http,https,rtmp,rtsp
        result = urlparse(url)
        h = result.hostname
        p = 80
        if(result.port is not None):
            p = result.port

        ip = h
        if(is_valid_ip_address(h) == False):
            try:
                ip = socket.gethostbyname(h)
            except Exception as e:
                pass

        # Test raw video source - for IP and PORT only
        
        t0 = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        state = sock.connect_ex((h, p))
        t = int((time.time() - t0)*1000) #ms
        sock.shutdown(socket.SHUT_RDWR) 
        sock.close() 

        if(state==0):

            # TODO ffprobe method


            # cv2 method
            testsrc = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
            if(testsrc.isOpened()):
                time.sleep(3)
                vid_width = int(testsrc.get(3))
                vid_height = int(testsrc.get(4))
                vid_fps = round(testsrc.get(5),1)

                cc = 0
                img_list = []
                while cc < 10:
                    isSuccess,frame = testsrc.read()
                    if(isSuccess and cc in [3,6,9]):  # Capture at 3/6/9s
                        fn = prefix + f'-{(int(time.time()))}.jpg'
                        cv2.imwrite(fn, frame)
                        img_list.append(fn)
                    time.sleep(0.5) 
                    cc += 1

                testsrc.release()
                res = { 'IP': ip,
                        'Tc': t,  
                        'Width': vid_width, 
                        'Height': vid_height, 
                        'fps': vid_fps,
                        'images': img_list,
                        'code': 0,
                        'msg': ''
                        }
                return(res)
            else:
                return({ 'code': 102, 'msg': 'Failed to open url' })

        else:
            return({ 'code': 101, 'msg': 'Can not connect to socket' })

    except Exception as e:
        return({ 'code': 100, 'msg': str(e) })


def html_output(res, prefix):
    # res: []
    # - ['IsVideoUrl'] : bool
    # - ['link'] : str
    # - ['code'] : int
    # - ['msg'] : str
    # - ['result'] : str
    # - ['images'] : list[str,...]

    rpt_day = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_fn = prefix + '-rpt' + '.html'
    fo = open(output_fn, "w", encoding="utf-8")

    url_style =  '<style type="text/css">\n'
    url_style =  url_style + 'table { width: 1280px; border-collapse: collapse; border: 1px solid black } \n'
    url_style =  url_style + 'td { border: 1px solid black } \n'
    url_style =  url_style + 'p { width: 500px; word-break: break-all; } \n'
    url_style =  url_style + 'img { width: 200px; margin: 6px 10px 4px 10px } \n'
    url_style =  url_style + '</style>'
    html_text = f'<html>\n <head>\n <title>VIDEO URL SCAN REPORT {prefix}</title> \n'
    html_text = html_text + f'<meta charset="UTF-8">\n {url_style}</head>\n'
    html_text = html_text + f'<body></br></br><h2 align="center">Video URL Scan Report - {rpt_day}</h2>\n'
    html_text = html_text + f'</br><table>\n'
    html_text = html_text + '<tr><td> Line </td><td> Video Info</td><td> Scan Result </td></tr>'

    count = 0
    for r in res:
        count += 1
        
        code = r['code'] 
        msg = r['msg']
        url = r['link']
        if(r['IsVideoUrl']):
            thisRow = f'<tr><td>{count}</td><td><p> {url}</p>'
            if(code == 0):
                res = json.dumps(r['result'])
                images = r['images']
                thisRow = thisRow + f'{res}</td><td>'
                if(len(images)>0):
                    for imgFn in images:
                        thisRow = thisRow + f'<img src="{imgFn}" />'
                thisRow = thisRow + '</td>'
            else:
                thisRow = thisRow + f'</td><td><b style="color: #f00;"> {msg}</b></td>'
        else:
            thisRow = f'<tr><td>{count}</td><td><p> {url}</p></td><td> TEXT </td>'

        # Line saving
        html_text = html_text + thisRow + '</tr>\n'

    html_text = html_text + '</table><br />- End of Doc -</body>\n</html>\n'
    fo.write(html_text)
    fo.close()

    return(output_fn)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video url scanner')
    parser.add_argument("-i", "--input", type=str, required=True,
        help="file to scan")
    parser.add_argument("-a", "--action_flag", type=bool, default=False,
        help="no action by default")

    args = vars(parser.parse_args())
    input_fn = args["input"]
    action_flag = args["action_flag"]

    if(os.path.exists(input_fn)):
        full_fn = os.path.join(os.getcwd(), input_fn)
        fn_List = os.path.splitext(input_fn)
        
        prefix = fn_List[0] + '-' + datetime.now().strftime("%m%d%H%M%S")

        if(action_flag):
            os.makedirs(prefix)
            os.chdir(prefix)
            os.system('cp %s %s'%(full_fn, input_fn))

        fi = open(input_fn, 'r', encoding='utf-8')
        zipList = []
        results = []

        count = 1
        print(' Scanning ...')
        for line in fi.readlines():
            this_res = {}   # keys: IsVideoUrl, link, code, result, images
            # - ['IsVideoUrl'] : bool
            # - ['link'] : str
            # - ['result'] : str
            # - ['code'] : int
            # - ['images'] : list[str,...]

            print('L:%4d '%count, end='')
            count += 1
            
            # Line processing
            # line0 = line.replace('\n', '')
            line0 = line.strip()
            vid_url_flag = False
            offset = -1 # In case text before URL

            if(not line0):
                continue

            if(line0[0] == '#'):
                vid_url_flag = False
            else:
                offset = line0.find('http')
                if(offset > -1): # Include m3u8, flv
                    if( line0.find('m3u8') > 0 or line0.find('M3U8') > 0 or line0.find('flv') > 0 or line0.find('FLV') > 0):
                        vid_url_flag = True
                        line0 = line0[offset:]

                offset = line0.find('rtsp')
                if(offset > -1):
                    vid_url_flag = True
                    line0 = line0[offset:]

                offset = line0.find('rtmp')
                if(offset > -1):
                    vid_url_flag = True
                    line0 = line0[offset:]

            if(vid_url_flag):
                this_res['IsVideoUrl'] = True
                this_res['link'] = line0
                url = line0

                if(action_flag):
                    r = url_check(url, f"l{count-1}")
                    this_res['code'] = r.pop('code')
                    this_res['msg'] = r.pop('msg')

                    if(this_res['code'] == 0):
                        zipList = zipList + r['images']
                        this_res['images'] = r.pop('images')
                        this_res['result'] = r

                        print(f'[url] ooo {url}')
                        print(f'{" "*22} * Results: ' + json.dumps(r))
                    else:
                        print(f'[url] xxx {url}')
                        print(f'{" "*22} * Results: ' + this_res['msg'])

                else:
                    this_res = {
                        'code': 1,
                        'msg': 'Nil' 
                    }
                    print(f'[url] ... {url}')

            else:
                this_res['IsVideoUrl'] = False
                this_res['link'] = line0
                this_res['code'] = 100
                this_res['msg'] = 'TXT'
                print(f'[txt] --- {line0}')

            if(this_res):
                results.append(this_res)

        fi.close()

        # Formatted report
        if(action_flag and results):
            output_fn = html_output(results, prefix)
            print('\n\nReport file: ' + output_fn)
            zipList.append(output_fn)

            # Backup current config
            fn_List = os.path.splitext(input_fn)
            backup_file = prefix+fn_List[1]
            os.system('cp %s %s'%(input_fn, backup_file))

            # Write to zipfile
            if(zipList):
                output_fn = prefix + '.zip'
                print(f'Packing into zip file ...{output_fn}')
                with zipfile.ZipFile(output_fn, 'w') as zipObj:
                    for fn in zipList:
                        zipObj.write(fn)
                    zipObj.write(backup_file)
            print('Zip file: ' + output_fn)

            # End of main

    else:
        print('%s is not found.'%(input_fn))

    if(action_flag == False):
        print("\n *** Check input file only; Please use '-a True' to execute scan.\n\n ")
