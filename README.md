# video_url_scanner - scan video URLs, generate report with image captures
Scan video url from file and create report, including url availability, thumbnail

Broadcast video, OTT(Video over the top),  Internet video, video surveillance(IPCamera), video AI(Object detection) rely on video signals, properly set up.

Q: If you need to deal with many video sources, what is the first step?</br>
A: Verify video information. 

Here is a short list:

* Server address, port, path
* Username, password
* Video format - width, height, framerate
* Video image

In video business, 99% problems can be identified if above information are collected.

This is what video_url_scanner is designed for.


# Design information
* video_url_scanner is a small tool. It takes video urls in text file and generate report with image capture.
* It supports video url in http://, https://, rtsp://, rtmp://. udp://, srt:// and more will be supported soon.
* Only one file - video_url_scanner.py - the main program. 


# Installation

First, install python3 (>3.8), pip and OpenCV</br>
Check requirements.txt if any package is missing.

Second, save files to a local folder. 
* video_url_scanner.py - main program
* sample.txt - use to demo program functions


# Usage

python should be included in PATH environment. (python3 may be default in Linux)

Assume user has opened a console window (windows or linux).

## Inspect video url in file.
This confirms if user should run actual scan on the file.

```Bash
python video_url_scanner.py -i sample.txt
```

Console should output like below:

 Scanning ...
Line:    1 [url] --- rtsp://admin:xxxxxxx@192.168.50.100:554/cam/realmonitor?channel=1&subtype=0</br>
Line:    2 [txt] --- #EXTM3U</br>
Line:    3 [txt] --- #EXTINF:-1 ,CH-1</br>
Line:    4 [url] ... https://gcalic.v.mylidn.com/gc/ynh_1/index.m3u8</br>
Line:    5 [txt] --- #EXTINF:-1 ,CH-2</br>
Line:    6 [url] ... https://gccncc.v.wsdns.com/gc/yyt_1/index.m3u8</br>
Line:    7 [txt] --- #EXTINF:-1 ,CH-3</br>
Line:    8 [url] ... https://gccncc.v.wsdns.com/gc/wygjt2_1/index.m3u8</br>
Line:    9 [txt] --- #EXTINF:-1 ,CH-4</br>
Line:   10 [url] ... https://gcalic.v.myaidn.com/gc/hswlf_1/index.m3u8</br>
Line:   11 [url] ... https://gctxyc.livepy.mcloud.com/gc/tsha3_1/index.m3u8</br>
Line:   12 [url] ... https://gctxyc.livepy.mcloud.com/gc/wysdh_1/index.m3u8</br>
(Above outputs are modified)

[txt] means the line has no url to check.</br>
[url] means the line has url to check.



## Perform scan
If output in last step is satisifed, user can perform scan.


```Bash
python video_url_scanner.py -i sample.txt -a True
```

The '-a True' option instructs program to perform scan.


Line:    3 [txt] --- #EXTINF:-1 , CH-1</br>
Line:    4 [url] ooo https://gcalic.v.mycdn.com/gc/yxhcnh_1/index.m3u8</br>
                       * Results: {"IP": "16.19.12.98", "Tc": 27, "Width": 1920, "Height": 1080, "fps": 25.0}</br>
                       
Line:    5 [txt] --- #EXTINF:-1 , CH-2</br>
Line:    6 [url] xxx https://gccncc.v.wdns.com/gc/yxyt_1/index.m3u8</br>
                       * Results: Failed to open url</br>
                       
Line:    7 [txt] --- #EXTINF:-1 , CH-3</br>
Line:    8 [url] xxx https://gccncc.v.wscs.com/gc/wygjt2_1/index.m3u8</br>
                       * Results: Failed to open url</br>
                       
Line:    9 [txt] --- #EXTINF:-1 ,CH-4</br>
Line:   10 [url] ooo https://gcalic.v.myicdn.com/gc/hswf_1/index.m3u8</br>
                       * Results: {"IP": "16.19.12.98", "Tc": 12, "Width": 1920, "Height": 1080, "fps": 25.0}  </br>
(Above outputs are modified)

After scan is done, output files are shown, like below:

Report file: sample-0105000342-rpt.html</br>
Packing into zip file ...sample-0105000342.zip</br>
Zip file: sample-0105000342.zip</br>

These files are in a new folder under current one.


### How to read results
--- means the line is considered as text.<br/>
ooo means the url contains valid video; the next line is video info.</br>
xxx means the url has problem to access; the next line is error message.</br>
"IP" - server IP; If server in url is domain name, server IP is from DNS or hosts in local.</br>
"Tc" - connection time, in million second. This is duration of TCP socket connection.</br>
"Width", "Height", "fps" - are basic infomation of video source.

ooo or xxx gives your idea if an url is valid. If xxx, result may be 'Failed to open url' or 'Can not connect to socket'.</br>
'Failed to open url' means server is online, but access is failed.</br>
'Can not connect to socket' means server is not accessible in socket level - no DNS, wrong IP, wrong port etc.</br>

"IP" is how server name is resolved by DNS from view of this machine.</br>
"Tc" gives your idea of how fast can connect to the server from this machine.</br>
"Width", "Height", "fps" allow you to verify if video signal settings accord to record.</br>


## Next step
User can enter the fold and open html file for report.

If the machine performs scan is a server,
download zip file to local machine; extract zip file and open the html file inside.

In web browser, report can be printed as "Save to PDF".

### How to use report
* Send to owner of video signals. Ask him/her to fix problems. - for IP cameras
* Pick good video sources. - for free Internet video
* Check settings of video sources. - if you are a video owner
* Send to big boss and blame some one :)

TIP: If want to know how stable video signals are, you can run scan multiple times.</br>
By comparing with reports in differnt machines(professionaly, should call probe) and different time,
more insights may be discovered.


## Screenshots


CLI
![](https://github.com/alexlzb/video_url_scanner/blob/main/img/cli.png)

Report in html format (default)
![](https://github.com/alexlzb/video_url_scanner/blob/main/img/web.png)

Save to PDF
![](https://github.com/alexlzb/video_url_scanner/blob/main/img/topdf.png)

</br>
</br>
