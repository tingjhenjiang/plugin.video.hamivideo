import requests
import htmlement
import sys
import xml.etree.ElementTree as elemtree
import json
import re
import time
import os
import random
import base64
import jsbeautifier
import six
if False:
	from selenium import webdriver
	from selenium.webdriver.chrome.options import Options as ChromeOptions
	from selenium.webdriver.firefox.options import Options as FirefoxOptions
	from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
	from selenium.webdriver.common.keys import Keys
	from selenium.webdriver.support.wait import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC
	from selenium.webdriver.common.by import By
import six.moves.urllib as urllib
try:
	from multiprocessing.dummy import Pool as ThreadPool
	threadpool_imported = True
except:
	threadpool_imported = False
#from xbmcswift2 import Plugin, xbmc, xbmcaddon, xbmcgui, xbmcplugin

#https://stackoverflow.com/questions/57167357/why-does-socket-interfere-with-selenium

class Hamivideo(object):

	def __init__(self, binary_and_driver_path={
		'chromedriver_path': "E:\\Software\\scripts\\python\\kodi_dev\\plugin.video.example\\chromedriver.exe",
		'chromebinary_location': "D:\\PortableApps\\PortableApps\\GoogleChromePortable\\App\\Chrome-bin\\chrome.exe",
		'geckodriver_path': "E:\\Software\\scripts\\python\\kodi_dev\\plugin.video.example\\geckodriver.exe",
		'firefoxbinary_location': "D:\\PortableApps\\PortableApps\\FirefoxPortable\\App\\Firefox64\\firefox.exe",
		'docker_remote_selenium_addr': "127.0.0.1:4444",
		'browser_type': "remotech",
		'chromeublockpath': "E:\\Software\\scripts\\python\\kodi_dev\\plugin.video.hamivideo\\ublock_extension_1_24_2_0.crx",
		'firefoxblockpath': "E:\\Software\\scripts\\python\\kodi_dev\\plugin.video.hamivideo\\uBlock0_1.24.5rc1.firefox.signed.xpi",
		'seleniumlogpath': "/home/pi/seleniumlogpath.txt"
	}):
		self.hamivideo_host_url = 'https://hamivideo.hinet.net/'
		self.linetoday_url = 'https://today.line.me/'
		self.def_webdrive_binary_path(binary_and_driver_path)
		self.seleniumlogpath = binary_and_driver_path['seleniumlogpath']
		self.useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
		self.request_user_agent = 'User-Agent: '+self.useragent #Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36
		self.mobile_request_useragent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
		try:
			import multiprocessing
			self.workers = multiprocessing.cpu_count()
		except:
			self.workers = 4

	def def_webdrive_binary_path(self, binary_and_driver_path):
		self.binary_and_driver_path = binary_and_driver_path
		if self.binary_and_driver_path['browser_type'].find('remote')!=-1:
			for key in ['chromedriver_path', 'chromebinary_location', 'geckodriver_path', 'firefoxbinary_location']:
				self.binary_and_driver_path.pop(key, None)

		
	def merge_two_dicts(self, x, y):
		z = x.copy()   # start with x's keys and values
		z.update(y)	# modifies z with y's keys and values & returns None
		return z

	def requesturl_get_ret(self, url, payload={}, headers={}):
		r = requests.get(url, params=payload, headers=headers)
		return r.text

	def requesturl_post_ret(self, url, data={}, headers={}):
		r = requests.post(url, data=data, headers=headers)
		return r.text

	def ret_domelement_with_text(self, pattern, elements, iter=True):
		ret_elements = list()
		for element in elements:
			try:
				elemtext = "".join(element.itertext()) if iter==True else element.text()
				if re.search(pattern, elemtext)!=None:
					ret_elements.append(element)
			except Exception as e:
				continue				
		return ret_elements
	
	def return_hamichannels(self):
		html_doc = self.requesturl_get_ret(self.hamivideo_host_url+'%E9%9B%BB%E8%A6%96%E9%A4%A8/%E5%85%A8%E9%83%A8.do')
		root = htmlement.fromstring(html_doc)
		main_menu_list = []
		for item in root.findall(".//div[@class='tvListBlock']/div[@class='list_item']"):
			title = item.find(".//h3/a").text
			#link = self.hamivideo_host_url+item.find(".//h3/a").get("href")
			#link = link.replace("//","/")
			link = item.find(".//h3/a").get("onclick")
			link = self.hamivideo_host_url+re.findall("sendUrl\(\'(.+\.do)\',", link)[0]
			channelid = os.path.basename(link).replace('.do','')
			channel_icon = item.find(".//img").get("src")
			programtime = item.find(".//div[@class='time']")
			try:
				programtime = programtime.text
			except Exception as e:
				programtime = ""
			program = elemtree.tostring(item.find(".//div[@class='com']"))
			try:
				program = program.split("<p>")[1].split("</p>")[0]
				program = htmlement.fromstring(program).find(".//a").text
			except Exception as e:
				#print(e)
				program = ""
			main_menu_list.append({
				'name': title,
				'link': link,
				'program': program,
				'icon': channel_icon,
				'programtime': programtime,
				'channelid': channelid
			})
		return main_menu_list

	def return_linetodaychs(self):
		topmenus = htmlement.fromstring(self.requesturl_get_ret(self.linetoday_url)).findall(".//ul[@class='gnb']/li")
		watchlinetodaytvelem = six.moves.filter(lambda x: re.search("(&#38651;&#35222;)", elemtree.tostring(x)), topmenus ) #
		watchlinetodaytvelem = list(watchlinetodaytvelem)[0]
		watchlinetodaytvelink = self.linetoday_url+watchlinetodaytvelem.find(".//a").get("href")
		root = htmlement.fromstring(self.requesturl_get_ret(watchlinetodaytvelink))
		main_menu_list = []
		for item in (root.findall(".//div[@id='left_area']//li")):
			linkitem = item.find(".//a")
			link = linkitem.get("href")
			title = " ".join(list(linkitem.itertext()))
			channel_icon = item.find(".//figure").get("data-background")
			main_menu_list.append({
				'name': title,
				'link': link, 
				'program': "",
				'icon': channel_icon,
				'programtime': ""
			})
		return main_menu_list

	def ret_dramaq_episodes(self, drama_name):
		dramaq_homepage = 'https://www.qdrama.tv'
		reqheaders_std = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
			'Connection': 'keep-alive',
			'DNT': '1',
		}
		reqheaders_dramaq = self.merge_two_dicts(reqheaders_std, {
			'Upgrade-Insecure-Requests': '1'
		})
		session = requests.Session()
		session.headers.update(reqheaders_dramaq)
		response = session.get(dramaq_homepage)
		response.encoding = 'UTF-8'
		setcookies = session.cookies.get_dict()
		session.headers.update(self.merge_two_dicts(reqheaders_dramaq, {
			'Referer': dramaq_homepage,
		}))
		dramaq_homepage_root = htmlement.fromstring(response.text)
		searchbox = dramaq_homepage_root.find(".//div[@class='search_box']//script").text
		searchboxcx = re.findall("cx\s=\s\'(.+)\'\;", searchbox)[0]
		searchbox = 'https://cse.google.com/cse.js?cx='+searchboxcx
		searchboxresponse = session.get(searchbox)
		cse_token = re.findall("cse_token\":\s\"(.+)\",", searchboxresponse.text)[0]
		cselibVersion = re.findall("cselibVersion\":\s\"(.+)\",", searchboxresponse.text)[0]
		dramaq_search_url = 'https://cse.google.com/cse/element/v1'
		dramaq_search_url_data = {
			'rsz':'filtered_cse',
			'num':'10',
			'hl':'zh-TW',
			'source':'gcsc',
			'gss':'.tw',
			'cselibv':cselibVersion,
			'cx':searchboxcx,
			'safe':'off',
			'cse_tok':urllib.parse.unquote(cse_token),
			'exp':'csqr,cc',
			'callback':'google.search.cse.api3966',
			'q':urllib.parse.unquote(drama_name),
		}
		response = requests.get(dramaq_search_url, cookies=setcookies, params=dramaq_search_url_data)
		dramaq_search_results = re.findall("google\.search\.cse.+\(({[\w\d\s\W\D\S]+})\);", response.text)
		dramaq_search_results = self.parse_json_response(dramaq_search_results)[0]["results"]
		dramaq_search_results = six.moves.filter(lambda x: re.search("\d+\.html", x['url'])==None, dramaq_search_results)
		dramaq_drama_link = next(dramaq_search_results)['url']
		response = session.get(dramaq_drama_link)
		response.encoding = 'UTF-8'
		dramaq_singledrama_root = htmlement.fromstring(response.text)
		episodelinks = dramaq_singledrama_root.findall(".//div[@class='items sizing']//li/a")
		try:
			#drama_description = dramaq_singledrama_root.find(".//div[@class='episode sizing']/pre").text+"".join(dramaq_singledrama_root.find(".//div[@class='intro sizing']").itertext())
			drama_description = "".join(dramaq_singledrama_root.find(".//div[@class='intro sizing']").itertext())
		except:
			drama_description = None
		main_menu_list = []
		for item in episodelinks:
			main_menu_list.append({
				'name': item.text,
				'link': dramaq_homepage+item.get('href'), 
				'program': drama_name,
				'icon': "",
				'programtime': "",
				'info': {
					'plot': drama_description
				}
			})
		main_menu_list.reverse()
		return main_menu_list

	def ret_dramaq_streaming_url_by_req(self, need_episode_url):
		dramaq_homepage = 'https://www.qdrama.tv'
		reqheaders_std = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
			'Connection': 'keep-alive',
			'DNT': '1',
		}
		reqheaders_dramaq = self.merge_two_dicts(reqheaders_std, {
			'Upgrade-Insecure-Requests': '1'
		})
		session = requests.Session()
		session.headers.update(reqheaders_dramaq)
		response = session.get(dramaq_homepage)
		setcookies = session.cookies.get_dict()
		session.headers.update(self.merge_two_dicts(reqheaders_dramaq, {
			'Referer': dramaq_homepage,
		}))
		response = session.get(need_episode_url, cookies=setcookies)
		response.encoding = 'UTF-8'
		dramaq_singleepisode_root = htmlement.fromstring(response.text)
		singleepisode_player_jsinfo = dramaq_singleepisode_root.findall(".//head/script")
		singleepisode_player_jsinfo = [jsi.get('src') for jsi in singleepisode_player_jsinfo if jsi.text==None]
		#singleepisode_player_jsinfo = filter(lambda x: re.search("rules", x)!=None, singleepisode_player_jsinfo)[0]
		singleepisode_video_sources = dramaq_singleepisode_root.findall(".//div[@class='sources']//a")
		singleepisode_video_sources = [singleepisode_video_source.get('data-data') for singleepisode_video_source in singleepisode_video_sources]
		singleepisode_video_sources = ["".join(reversed(singleepisode_video_source)) for singleepisode_video_source in singleepisode_video_sources]
		singleepisode_video_sources = [base64.b64decode(singleepisode_video_source) for singleepisode_video_source in singleepisode_video_sources]
		singleepisode_video_sources = [self.parse_json_response(singleepisode_video_source) for singleepisode_video_source in singleepisode_video_sources]
		singleepisode_video_sources = [{'id': x['ids'][0], 'source': x['source']} for x in singleepisode_video_sources if x['source'] in ['JYun','HYun','YYun','OYun','M3U8']]
		singleepisode_video_sources = [dramaq_homepage+'/m3u8/?ref='+x['id'] for x in singleepisode_video_sources]
		need_episode_url_inframe = random.choice(singleepisode_video_sources)
		response = session.get(need_episode_url_inframe)
		response.encoding = 'UTF-8'
		dramaq_singleepisode_player_root = htmlement.fromstring(response.text)
		dramaq_streamingurl = dramaq_singleepisode_player_root.findall(".//script")
		dramaq_streamingurl = [x.text for x in dramaq_streamingurl if x.text!=None and re.search('var m3u8url',x.text)!=None][0].strip()
		dramaq_streamingurl = re.findall("var\sm3u8url\s=\s\'(.+)\'(\r|\n|\s)", dramaq_streamingurl)[0][0]
		return dramaq_streamingurl

	def return_litv(self, url):
		'''
		Request URL: https://www.litv.tv/vod/ajax/getMainUrlNoAuth
		Request Method: POST
		Status Code: 200 OK
		Remote Address: 13.226.71.114:443
		Referrer Policy: no-referrer-when-downgrade
		Connection: keep-alive
		Content-Encoding: gzip
		Content-Type: application/json;charset=UTF-8
		Date: Wed, 15 Apr 2020 07:45:24 GMT
		Server: Apache-Coyote/1.1
		Transfer-Encoding: chunked
		Via: 1.1 f92eab68beb1e6605042ec06f0941a64.cloudfront.net (CloudFront)
		X-Amz-Cf-Id: YD5bikK6FCsZrT6VBBdzp97--B65HUriGar7foZ75OiIedJbKYbmAg==
		X-Amz-Cf-Pop: MNL50-C1
		X-Cache: Miss from cloudfront
		Accept: application/json, text/javascript, */*; q=0.01
		Accept-Encoding: gzip, deflate, br
		Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6
		browser_type: 
		Connection: keep-alive
		Content-Length: 79
		Content-Type: application/json
		Cookie: SESSION=d5552842-9d22-4cb4-bea0-cdacd52ad6d0
		DNT: 1
		Host: www.litv.tv
		Origin: https://www.litv.tv
		Referer: https://www.litv.tv/vod/drama/content.do?content_id=VOD00038218
		Sec-Fetch-Dest: empty
		Sec-Fetch-Mode: cors
		Sec-Fetch-Site: same-origin
		User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36
		X-Ajax-call: true
		X-Requested-With: XMLHttpRequest
		{assetId: "vod10577-000001M001_800K", watchDevices: ["PC", "PHONE", "PAD", "TV"]}
		assetId: "vod10577-000001M001_800K"
		watchDevices: ["PC", "PHONE", "PAD", "TV"]
		'''
		#real playlist
		#https://p-hebe.svc.litv.tv/hi/vod/lNotNzgNIMc/litv-drama-vod10577-000001M001-video_eng=400000-audio_eng=125435.m3u8
		pass

	def get_poku_dramas(self, opt):
		url = opt[0]
		mode = opt[1]
		homepage = "https://poku.tv"
		reqheaders_std = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
				'Connection': 'keep-alive',
				'DNT': '1',
				'sec-fetch-dest': 'document',
				'sec-fetch-mode': 'navigate',
				'sec-fetch-site': 'none',
				'sec-fetch-user': '?1',
				'upgrade-insecure-requests': '1',
				'cache-control': 'max-age=0'
			}
		session = requests.Session()
		session.headers.update(reqheaders_std)
		response = session.get(homepage)
		response.encoding = 'UTF-8'
		setcookies = session.cookies.get_dict()
		reqheaders_channel = self.merge_two_dicts(reqheaders_std, {
				#'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
				#'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
				'Referer': homepage,
				#'accept-encoding': 'gzip, deflate, br',
			})
		session.headers.update(reqheaders_channel)
		response = session.get(url, cookies=setcookies)
		setcookies = session.cookies.get_dict()
		root = htmlement.fromstring(response.text)
		all_dramas = list()
		if mode=='search':
			dramaselems = root.findall(".//li[@class='searchlist_item']")
			for dramaselem in dramaselems:
				all_dramas.append({
					'title': ":".join(dramaselem.find(".//h4[@class='vodlist_title']/a").itertext()),
					'link': homepage+dramaselem.find(".//h4[@class='vodlist_title']/a").get('href'),
					'thumbnail': dramaselem.find(".//div[@class='searchlist_img']/a").get('data-src'),
					'description': "".join(dramaselem.find(".//p[@class='vodlist_sub hidden_xs']").itertext()),
				})
			return all_dramas
		if mode=='drama':
			dramaselems = root.findall(".//ul") #vodlist vodlist_wi list_v12 clearfix
			dramaselems = six.moves.filter(lambda x: x.get('class')!=None, dramaselems)
			dramaselems = six.moves.filter(lambda x: re.search('vodlist', x.get('class') )!=None, dramaselems)
			dramaselems = six.moves.filter(lambda x: re.search('clearfix', x.get('class') )!=None, dramaselems)
			dramaselems = six.moves.filter(lambda x: re.search('vodlist_wi', x.get('class') )!=None, dramaselems) #vodlist vodlist_wi list_v12 clearfix
			for dramaselem in dramaselems:
				dramaselemlis = dramaselem.findall(".//li")
				for dramaselemli in dramaselemlis:
					all_dramas.append({
						'title': dramaselemli.find(".//a").get('title'),
						'thumbnail': dramaselemli.find(".//a").get('data-src'),
						'link': homepage+dramaselemli.find(".//a").get('href'),
						'description': dramaselemli.find(".//p[@class='vodlist_sub']").text,
					})
			return all_dramas
		elif mode=='listepisodes':
			thumbnail = root.find(".//div[@class='content_thumb fl']/a").get('data-src')
			dramatitle = root.find(".//div[@class='content_thumb fl']/a").get('title')
			metadata = root.find(".//div[@class='content_detail content_min fl']").itertext()
			metadata = [a.strip() for a in metadata]
			metadata = "".join(metadata)
			description = root.find(".//div[@class='content_desc full_text clearfix']").itertext()
			description = "".join(description)
			episodeelems = root.findall(".//ul[@class='content_playlist clearfix']/li/a")
			for episodeelem in episodeelems:
				single_res = {
					'dramaname': dramatitle,
					'title': episodeelem.text,
					'thumbnail': thumbnail,
					'metadata': metadata,
					'description': description,
					'link': homepage+episodeelem.get('href'),
				}
				single_res = {k:six.ensure_str(s) for k,s in single_res.items()}
				all_dramas.append(single_res)
			return all_dramas
		elif mode=='allnum':
			try:
				lastpagelink = root.findall(".//li[@class='hidden_mb']/a")[1].get('href')
				allpagesnum = root.find(".//div[@class='page_tips hidden_mb']").itertext()
				allpagesnum = [a.strip() for a in allpagesnum]
				allpagesnum = six.ensure_str("".join(allpagesnum))
				allpagesnum = re.search("共有(\d+)頁", allpagesnum)
				allpagesnum = allpagesnum.group(1)
				linktemplate = homepage+lastpagelink.replace("-"+allpagesnum, "-TARGETNUM");
				allpagesnum = int(allpagesnum)
				allpageslink = [linktemplate.replace('TARGETNUM', str(i)) for i in range(1, allpagesnum+1)]
				#allpagesnum = re.search("(\d+)", link)
				#allpagesnum = int(allpagesnum.group())
			except:
				allpagesnum = None
				linktemplate = None
				allpageslink = None
			return {'allpagesnum': allpagesnum, 'linktemplate': linktemplate, 'allpageslink': allpageslink}
		elif mode=='findstreamingurl':
			jsoncontent = root.find(".//div[@class='left_row fl']//script").text
			jsoncontent = jsoncontent.replace("var player_data=","")
			jsoncontent = self.parse_json_response(jsoncontent)
			videourl = jsoncontent['url']
			video_req_header = self.merge_two_dicts(reqheaders_channel, {
				'Connection': 'keep-alive',
				'Origin': homepage,
				'Referer': url,
				'Sec-Fetch-Dest': 'empty',
				'Sec-Fetch-Mode': 'cors',
				'Sec-Fetch-Site': 'cross-site',
				#Host: www.nmgxwhz.com:65
			})
			video_req_header_str = "&".join([k+"="+v for k,v in video_req_header.items()])
			content = {
				'videourl': videourl,
				'req_header_str': video_req_header_str,
				'req_header': video_req_header,
				'jsoncontent': jsoncontent,
			}
			return(content)

	def ret_maplestage_parent_catgs(self):
		maplestage_homepage = 'https://8maple.ru/'
		maplestage_homepage_doc_html = self.requesturl_get_ret(maplestage_homepage)
		maplestage_homepage_root = htmlement.fromstring(maplestage_homepage_doc_html)
		maplestage_parent_catgs = maplestage_homepage_root.findall(".//div[@id='main-nav']//a")
		maplestage_parent_catgs = [{
			'name': m.text,
			'link': m.get('href'), 
			'program': m.text,
			'icon': '',
			'programtime': ''
		} for m in maplestage_parent_catgs]
		return maplestage_parent_catgs

	def ret_maplestage_dramas_of_a_parent(self, drama_catg):
		#drama_catg = 'https://8maple.ru/%E9%9F%93%E5%8A%87%E7%B7%9A%E4%B8%8A%E7%9C%8B_/'
		drama_allyrs_from_a_catg_doc_html = self.requesturl_get_ret(drama_catg)
		root = htmlement.fromstring(drama_allyrs_from_a_catg_doc_html)
		yrs_of_a_catg_drama = root.findall(".//div[@id='content']//a")
		sample_yrlinks = {x.text:self.correction_for_url_without_http_prefix(x.get('href')) for x in yrs_of_a_catg_drama}
		iterargs = [[yrtitle,link] for yrtitle,link in sample_yrlinks.items()]
		if threadpool_imported:
			pool = ThreadPool(self.workers)
			results = pool.map(self.ret_maplestage_dramas_of_a_yr, iterargs)
			pool.close()
			pool.join()
		else:
			results = [self.ret_maplestage_dramas_of_a_yr(iterarg) for iterarg in iterargs]
		results = reduce(lambda x,y: x+y, results)
		#q = Queue.Queue()
		#for yrtitle, sample_link_of_a_year_init in sample_yrlinks.items():
		#	dramas_of_a_yr = self.ret_maplestage_dramas_of_a_yr(sample_link_of_a_year_init, yrtitle)
		#	all_dramas_of_a_catg.extend(dramas_of_a_yr)
		#	t = threading.Thread(target=self.ret_maplestage_dramas_of_a_yr, args = (sample_link_of_a_year_init, yrtitle))
		#	t.daemon = True
		#	t.start()
		#s = q.get()
		#	#break
		return results

	def ret_maplestage_dramas_of_a_yr(self, combn_sample_link_of_a_year_init_yrtitle):
		yrtitle = combn_sample_link_of_a_year_init_yrtitle[0]
		sample_link_of_a_year_init = combn_sample_link_of_a_year_init_yrtitle[1]
		i=1
		dramas_of_a_yr = list()
		while True: #here start to fetch all dramas in a yr
			#print("handling yrtitle "+yrtitle+" page number "+str(i))
			sample_link_of_a_year = sample_link_of_a_year_init+'page/'+str(i)+'/'
			dramas_of_a_yr_init_doc_html = self.requesturl_get_ret(sample_link_of_a_year)
			root_dramas_of_a_yr_init = htmlement.fromstring(dramas_of_a_yr_init_doc_html)
			more_dramas_search_results = root_dramas_of_a_yr_init.findall(".//div[@class='loop-content switchable-view grid-mini']/div[@class='nag cf']/div")
			if len(more_dramas_search_results)>0:
				for more_dramas_search_result in more_dramas_search_results:
					to_be_appended_drama_data = {
							'name': "("+yrtitle+")"+more_dramas_search_result.find(".//a").get('title'),
							'link': more_dramas_search_result.find(".//a").get('href'), 
							'program': yrtitle,
							'icon': more_dramas_search_result.find(".//img").get('src'),
							'programtime': ''
						}
					dramas_of_a_yr.append(to_be_appended_drama_data)
				i+=1
			else:
				break
			#break --comment to full, non comment to decrease time fetching video links
		return dramas_of_a_yr

	def ret_episode_links_of_a_maplestage_drama(self, dramalink):
		episode_links_of_a_drama_doc_html = self.requesturl_get_ret(dramalink)
		episode_links_of_a_drama_root = htmlement.fromstring(episode_links_of_a_drama_doc_html)
		drama_title = episode_links_of_a_drama_root.find(".//h1[@class='entry-title']").text
		drama_icon = episode_links_of_a_drama_root.find(".//table//img").get('src')
		drama_description = episode_links_of_a_drama_root.find(".//td[@colspan='3']").itertext()
		drama_description = "".join(list(drama_description))
		episode_links_of_a_drama = episode_links_of_a_drama_root.findall(".//div[@class='entry-content rich-content']//table//a")
		episode_links_of_a_drama = [{'icon': self.correction_for_url_without_http_prefix(drama_icon),
			'link': self.correction_for_url_without_http_prefix(e.get('href')),
			'name': e.text,
			'program': drama_title.strip(),
			'programtime': '',
			'info': {
				'plot': drama_description+e.text
			}} for e in episode_links_of_a_drama]
		return episode_links_of_a_drama

	def ret_friday_tv_by_req(self, channellink):
		#https://video.friday.tw/tv/18
		pass

	def ret_hami_epg(self, channel_id):
		pass

	def ret_hami_streaming_url_by_req(self, channel_id, ret_session=False):
		reqheaders_std = {
			'Origin': 'https://hamivideo.hinet.net',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
			'Sec-Fetch-Site': 'same-origin',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
			'Host': 'hamivideo.hinet.net',
			'DNT': '1',
		}
		reqheaders_hamilogin = self.merge_two_dicts(reqheaders_std, {
			'Referer': "https://hamivideo.hinet.net/hamivideo/index.do",
			'Sec-Fetch-Dest': 'empty',
			'Sec-Fetch-Mode': 'cors',
			'X-Requested-With': 'XMLHttpRequest',
		})
		session = requests.Session()
		session.headers.update(reqheaders_hamilogin)
		response = session.get('https://hamivideo.hinet.net/index.do')
		setcookies = session.cookies.get_dict()
		setcookies_str = "; ".join([k+"="+v for k,v in setcookies.items()])
		response = session.post('https://hamivideo.hinet.net/hamivideo/getDeviceLoginInfo.do', cookies=setcookies)
		deviceinfo = response.text
		#https://hamivideo.hinet.net/hamivideo/app/login.do?deviceId=1d0155e5c5004366f36db9a5141272b9&deviceType=1&deviceOS=android_9&deviceVender=htc&deviceIp=192.168.1.120&deviceName=HTC_U-3u HTTP/1.1
		response = session.post('https://hamivideo.hinet.net/loginTo.do', params={'loginMethod': 'wifi'}, cookies=setcookies)
		if (re.search("kick.do",response.text)!=None):
			#print("previous duplicated hamivideo login exists")
			kickloginpagehtml = response.text
			kickloginpagehtml_root = htmlement.fromstring(kickloginpagehtml)
			kickloginform = kickloginpagehtml_root.find(".//form[@id='formPage']")
			actionurl = kickloginform.get('action')
			kickloginform_inputs = {elem.get('name'):elem.get('value') for elem in kickloginform.findall(".//input")}
			kicklogindevices = self.parse_json_response(kickloginform_inputs['device'])
			earliest_login = sorted([d['loginTime'] for d in kicklogindevices])[0]
			earliest_login_device = six.moves.filter(lambda x: x['loginTime']==earliest_login, kicklogindevices)
			earliest_login_device = list(earliest_login_device)[0]
			kicklogindata = self.merge_two_dicts(kickloginform_inputs, {'loginMethod': 'kick', 'authLoginId':'', 'otpw': earliest_login_device["logoutToken"], 'autoLogin':'', 'orig_otpw':''})
			kicklogindata.pop('device')
			response = session.post('https://hamivideo.hinet.net/hamivideo/loginTo.do', data=kicklogindata, cookies=setcookies)
			setcookies = session.cookies.get_dict()
		else:
			pass #print("no duplicated hamivideo login")
		channelapiurl = 'https://hamivideo.hinet.net/api/play.do?id='+channel_id
		response = session.get(channelapiurl, cookies=setcookies)
		responsejson = self.parse_json_response(response.text)
		if ret_session==True:
			return {'session':session, 'cookie': setcookies}
		else:
			return responsejson['url']

	def ret_maplestage_streamingurl_by_req(self, singleepisodeurl):
		maple_homepage = 'https://8maple.ru/'
		reqheaders_std = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
			'Connection': 'keep-alive',
			'DNT': '1',
			#'Origin': 'https://8maple.ru',
			#'Sec-Fetch-Site': 'same-origin',
			#'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			#'Accept-Encoding': 'gzip, deflate, br',
			#'cache-control': 'max-age=0',
		}
		reqheaders_maplestage = self.merge_two_dicts(reqheaders_std, {
			'Upgrade-Insecure-Requests': '1'
			#'Referer': "https://8maple.ru/",
			#'Host': '8maple.ru',
			#'Sec-Fetch-Dest': 'document',
			#'Sec-Fetch-Mode': 'navigate',
			#'sec-fetch-site': 'none',
			#'sec-fetch-user': '?1',
			#'X-Requested-With': 'XMLHttpRequest',
		})
		session = requests.Session()
		session.headers.update(reqheaders_maplestage)
		response = session.get(maple_homepage)
		response.encoding = 'UTF-8'
		setcookies = session.cookies.get_dict()
		session.headers.update(self.merge_two_dicts(reqheaders_maplestage, {
			'Referer': maple_homepage,
		}))
		response = session.get(singleepisodeurl, cookies=setcookies)
		setcookies = session.cookies.get_dict()
		maplestage_singledrama_root = htmlement.fromstring(response.text)
		maplestage_singledrama_scripts = maplestage_singledrama_root.findall(".//script")
		maplestage_singledrama_scripts = [x.text.strip() for x in maplestage_singledrama_scripts if x.text!=None and re.search("(soyou|yandisk|m3u8)", x.text)!=None]
		maplestage_singledrama_scripts = [x for x in maplestage_singledrama_scripts if re.search("push", x)!=None]
		maplestage_singledrama_scripts = maplestage_singledrama_scripts[0]
		video_refer_argums = re.findall("push\(\'(.+)\'\)", maplestage_singledrama_scripts)
		video_refer_argums = set(video_refer_argums)
		video_refer_argums = six.moves.filter(lambda x: len(x)>10, video_refer_argums)
		video_refer_argums = map(lambda x: 'https://video.8maple.ru/yandisk/?url='+x if re.search('http',x)==None else x, video_refer_argums)
		video_refer_argums = six.moves.filter(lambda x: re.search('mobile.php',x)==None, video_refer_argums)
		video_refer_argums = sorted(video_refer_argums)
		session.headers.update(self.merge_two_dicts(reqheaders_maplestage, {
			'Referer': singleepisodeurl,
			'sec-fetch-dest': 'iframe',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-site': 'same-site',
			'upgrade-insecure-requests': '1',
		}))
		video_refer_argum = video_refer_argums[0]
		response = session.get(video_refer_argum, cookies=setcookies)
		maplestagestreamingurl_root = htmlement.fromstring(response.text)
		maplestagestreamingurl = maplestagestreamingurl_root.findall(".//script")
		maplestagestreamingurl = [x.text.strip() for x in maplestagestreamingurl if x.text!=None and re.search("(eval)", x.text)!=None]
		maplestagestreamingurl = maplestagestreamingurl[0]
		maplestagestreamingurl = jsbeautifier.beautify(maplestagestreamingurl)
		maplestagestreamingurl = re.findall("\(([\w\d\,]{15,})\)", maplestagestreamingurl)[0]
		maplestagestreamingurl = maplestagestreamingurl.split(",")
		maplestagestreamingurl = map(int, maplestagestreamingurl)
		maplestagestreamingurl = ''.join(map(unichr, maplestagestreamingurl))
		maplestagestreamingurl = re.findall("file\:\'\/\/[\w\d\-\.\/\%\?\=\&\:]+",maplestagestreamingurl)[0]
		maplestagestreamingurl = maplestagestreamingurl.replace("file:'", 'https:')
		session.headers.update(self.merge_two_dicts(reqheaders_maplestage, {
			'Referer': video_refer_argum,
			'Accept-Encoding': 'identity;q=1, *;q=0',
			'Sec-Fetch-Dest': 'video',
			'upgrade-insecure-requests': '1',
		}))
		craftedurlparameters = [k+"="+v for k,v in session.headers.items()]
		craftedurlparameters = "&".join(craftedurlparameters)
		return (maplestagestreamingurl+"|"+craftedurlparameters)

	def ret_linetv_main_menu_catgs(self):
		if False:
			return {
				'臺劇': 'tw',
				'韓劇': 'kr',
				'中劇': 'cn',
				'BL': 'bl',
				'綜藝娛樂': 'entr',
				'動畫': 'anime',
				'電影': 'movie',
				'韓國電影': 'kr_film',
				'兒少': 'kid',
				'泰劇': 'tha',
				'新加坡劇': 'sin',
				'其他': 'others',
			}
		elif False:
			root = self.requesturl_get_ret('https://www.linetv.tw')
			root = htmlement.fromstring(root)
			target_catgsnavs = root.findall(".//nav//a")
			target_catgsnavs = [{'link': e.get('href'), 'text': e.text} for e in target_catgsnavs]
			target_catgsnavs = [e for e in target_catgsnavs if re.search("channel_id", e['link'])]
			target_catgsnavs = [{e['text']: re.findall("channel_id=(.+)", e['link'])[0] } for e in target_catgsnavs]
		else:
			root = self.requesturl_get_ret('https://static.linetv.tw/api/drama/category.json')
			target_catgsnavs = json.loads(root)['data']
			target_catgsnavs = [{e['ga']: str(e['code'])} for e in target_catgsnavs] #e['id']
			target_catgsnavs = six.moves.reduce(self.merge_two_dicts,target_catgsnavs)
			return target_catgsnavs

	def ret_linetv_dramas_metadata(self, catg=''):
		linetv_catg = self.ret_linetv_main_menu_catgs()
		linetv_catg_api_req_header_refer = {v:'https://www.linetv.tw/drama?area='+v for k,v in linetv_catg.items()}
		referer = linetv_catg_api_req_header_refer[catg] if catg!='' else 'https://www.linetv.tw/drama'
		linetv_catg_api_req_header = {
			'user-agent': self.useragent,
			'referer': referer,
			"method": "GET",
			"authority": "www.linetv.tw",
			"scheme": "https",
			"path": "/api/drama",
			"sec-fetch-dest": "empty",
			"dnt": "1",
			"accept": "*/*",
			"sec-fetch-site": "same-origin",
			"sec-fetch-mode": "cors",
			"accept-encoding": "gzip, deflate, br",
			"accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
		}
		responsejson = self.requesturl_get_ret('https://www.linetv.tw/api/drama', headers=linetv_catg_api_req_header)
		responsejson = self.parse_json_response(responsejson)
		responsejsondramas = responsejson['summary']
		return responsejsondramas

	def ret_linetv_drama(self, dramaid):
		responsejsondramas = self.ret_linetv_dramas_metadata()
		for d in responsejsondramas:
			if (d['drama_id'])==int(dramaid):
				return d

	def ret_linetv_dramas_of_a_catg(self, catg):
		linetv_catg = self.ret_linetv_main_menu_catgs()
		linetv_catg_api_req_header_refer = {v:'https://www.linetv.tw/drama?area='+v for k,v in linetv_catg.items()}
		catg_html = self.requesturl_get_ret(linetv_catg_api_req_header_refer[catg])
		root = htmlement.fromstring(catg_html)
		targetdramadata = root.findall(".//script")
		targetdramadata = self.ret_domelement_with_text('optimist', targetdramadata)[0]
		targetdramadata = targetdramadata.text.replace('window.__INITIAL_STATE__ = ', '')
		targetdramadata = self.parse_json_response(json.loads(targetdramadata))
		targetdramadata = targetdramadata['entities']['dramas']
		#targetdramadata = targetdramadata.values()
		targetdramadata = list(six.viewvalues(targetdramadata))
		targetdramadata_catgid = targetdramadata[0]['area_id']
		targetdramadata_ids = [d['drama_id'] for d in targetdramadata]
		responsejsondramas = self.ret_linetv_dramas_metadata(catg)
		for drama in responsejsondramas:
			try:
				if str(drama['area_id'])==str(targetdramadata_catgid) and not(drama['drama_id'] in targetdramadata_ids):
					targetdramadata.append(drama)
			except:
				continue
		return targetdramadata

	def ret_linetv_drama_description_multi_run_wrapper(self, args):
		return self.ret_linetv_drama_description(*args)

	def ret_linetv_drama_description(self, drama_id, episode=1):
		drama_page_url = 'https://www.linetv.tw/drama/'+str(drama_id)+'/eps/'+str(episode)
		drama_page_html = self.requesturl_get_ret(drama_page_url)
		root = htmlement.fromstring(drama_page_html)
		try:
			drama_description1 = list(root.find(".//div[@class='flex-auto overflow-hidden flex items-center font-500 text-16 text-767676']").itertext())
		except:
			drama_description1 = []
		try:
			drama_description2 = list(root.find(".//div[@class='flex items-start mt-6']").itertext())
		except:
			drama_description2 = []
		drama_description = "".join(drama_description1+drama_description2)
		drama_description = drama_description.replace("expand_more", "")
		return {'drama_id': drama_id, 'drama_description': drama_description, 'drama_episode': episode}

	def ret_linetv_dramas_with_description_of_a_catg(self, catg):
		dramas = self.ret_linetv_dramas_of_a_catg(catg)
		drama_ids = [d['drama_id'] for d in dramas]
		if threadpool_imported:
			pool = ThreadPool(self.workers)
			descriptions = pool.map(self.ret_linetv_drama_description, drama_ids)
			pool.close()
			pool.join()
		else:
			descriptions = [self.ret_linetv_drama_description(drama_id) for drama_id in drama_ids]
		descriptions = {d['drama_id']:d['drama_description'] for d in descriptions}
		i=0
		for drama in dramas:
			drama_id = drama['drama_id']
			drama['description'] = descriptions[drama_id]
			drama['info'] = {
				'plot': descriptions[drama_id]
			}
			drama['name'] = drama['name']
			dramas[i] = drama
			i += 1
		return dramas

	def ret_linetv_episode_data_multi_run_wrapper(self, args):
		return self.ret_linetv_episode_data(*args)

	def ret_linetv_episode_data(self, drama_id='', episode='', url=''):
		if drama_id=='' and url!='':
			drama_id = 'https://www.linetv.tw/drama/10971/eps/1'.split('/eps/')
			episode = drama_id[1]
			drama_id = drama_id[0].split('https://www.linetv.tw/drama/')[1]
		reqheaders = {
			'Origin': 'https://www.linetv.tw',
			'user-agent': self.useragent,
			'Referer': "https://www.linetv.tw/drama/"+str(drama_id)+"/eps/"+str(episode),
		}
		#staticdramareq_prereq = 'https://static.linetv.tw/api/playback/'+str(drama_id)+'/'+str(episode)+'/'+str(drama_id)+'-eps-'+str(episode)
		#staticdramareq_prereqret = self.requesturl_get_ret(staticdramareq_prereq, headers=reqheaders)
		epi_data = 'https://www.linetv.tw/api/part/'+str(drama_id)+'/eps/'+str(episode)+'/part?chocomemberId=null'
		epi_data = self.requesturl_get_ret(epi_data, headers=reqheaders)
		epi_data = self.parse_json_response(epi_data)
		if 'epsInfo' not in list(six.viewkeys(epi_data)):
			return False #only VIP may watch
		for_decrypt_post_data = {"keyType":epi_data['epsInfo']['source'][0]['links'][0]['keyType'],
					"keyId":epi_data['epsInfo']['source'][0]['links'][0]['keyId'],
					"dramaId":drama_id,
					"eps":epi_data['dramaInfo']['eps']}
		decryptdata = self.requesturl_post_ret('https://www.linetv.tw/api/part/dinosaurKeeper', data=for_decrypt_post_data, headers=reqheaders)
		decryptdata = self.parse_json_response(decryptdata)
		multibitrateplaylist = epi_data['epsInfo']['source'][0]['links'][0]['link']
		basepath = urllib.parse.urlparse(multibitrateplaylist)
		basepath = basepath.scheme+'://'+basepath.netloc+os.path.dirname(basepath.path)
		singlebitrateplaylist = self.requesturl_get_ret(multibitrateplaylist).split("\n")
		singlebitrateplaylist = six.moves.filter(lambda x: x.find('480p')!=-1, singlebitrateplaylist)
		singlebitrateplaylist = six.moves.filter(lambda x: x.find('m3u8')!=-1, singlebitrateplaylist)
		singlebitrateplaylist = basepath+'/'+next(singlebitrateplaylist)
		#drama_data = self.ret_linetv_drama(drama_id)
		#epi_data = self.merge_two_dicts(drama_data,epi_data)
		epi_data = self.merge_two_dicts(epi_data,decryptdata)
		reqheaders = self.merge_two_dicts(reqheaders, {
				'authentication': epi_data['token'],
				'Sec-Fetch-Dest': 'empty',
				'sec-fetch-site': 'cross-site',
				'sec-fetch-mode': 'cors',
				'accept-language': 'zh-TW,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
				'accept-encoding': 'gzip, deflate, br',
				'accept': '*/*',
			}
		)
		reqheaders_strs = "&".join([k+"="+v for k,v in reqheaders.items()])
		#, 'staticdramareq_prereqret': staticdramareq_prereqret
		epi_data = self.merge_two_dicts(epi_data,{
			'singlebitrateplaylist': singlebitrateplaylist,
			'multibitrateplaylist': multibitrateplaylist,
			'episode': episode,
			'drama_id': drama_id,
			'reqheaders': reqheaders,
			'reqheaders_strs': reqheaders_strs,
			}
		)
		return epi_data

	def ret_linetv_streaming_url(self, url):
		sdplaylist = self.ret_linetv_episode_data(url=url)
		sdplaylist = sdplaylist['playlisturl']+"|Origin=https://www.linetv.tw|Referer=https://www.linetv.tw/drama/"+sdplaylist['drama_id']+"/eps/1|user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0|authentication="+sdplaylist['token']
		return sdplaylist

	def parse_json_response(self, content):
		if isinstance(content, six.text_type) or isinstance(content, six.string_types):
			try:
				content = json.loads(content)
			except:
				content = content
		if isinstance(content, list):
			content = [self.parse_json_response(c) for c in content]
		if isinstance(content, dict):
			for key,v in content.items():
				if isinstance(content[key], six.text_type)  or isinstance(content[key], six.string_types): #if (type(content[key]) is str or str(type(content[key])).find('unicode')!=-1):
					try:
						content[key] = self.parse_json_response(content[key])
					except:
						content[key] = content[key]
				if isinstance(content[key], dict):
					content[key] = self.parse_json_response(content[key])
		return content

	def correction_for_url_without_http_prefix(self, url, prfx='http://'):
		matchresult = re.match(r'(ftp|http)://.*', url)
		if matchresult==None:
			url = prfx+re.sub(r'^//(.*)', r'\g<1>', url, count=0, flags=0)
		return url

	def unique(self, list1):
		unique_list = []
		for x in list1:
			if x not in unique_list:
				unique_list.append(x)
		return unique_list

	def generate_selenium_options(self):
		chromeoptions = ChromeOptions()
		firefoxoptions = FirefoxOptions()
		chromeoptions.add_argument("--incognito")
		#chromeoptions.add_argument('--headless')
		chromeoptions.add_argument('--disable-images')
		chromeoptions.add_argument('--no-sandbox')
		chromeoptions.add_argument('--disable-dev-shm-usage')
		#chromeoptions.add_argument('--user-agent="xxxxxxxx"')
		chromeoptions.add_experimental_option("prefs", {
			"profile.managed_default_content_settings.images": 2,
			"profile.default_content_setting_values.notifications":2,
			"profile.managed_default_content_settings.stylesheets":2,
			"profile.managed_default_content_settings.popups":2,
			"profile.managed_default_content_settings.geolocation":2,
		})
		chromeoptions.add_argument('--ignore-certificate-errors')
		chromeoptions.add_experimental_option("excludeSwitches", ['enable-automation']);
		#chromeoptions.add_extension(self.binary_and_driver_path['chromeublockpath'])
		caps_ch = DesiredCapabilities.CHROME
		caps_ch = self.merge_two_dicts(caps_ch,
				{'browserName': 'chrome', 'loggingPrefs': {'performance': 'ALL'}, 'goog:loggingPrefs': {'performance': 'ALL'}}
			)
		caps_ff = DesiredCapabilities.FIREFOX
		firefoxprofile = webdriver.FirefoxProfile()
		firefoxoptions.set_preference("dom.disable_beforeunload", True)
		firefoxoptions.set_preference("dom.push.enabled", False)
		firefoxoptions.set_preference('devtools.console.stdout.content', True)
		firefoxoptions.add_argument("--private")
		firefoxoptions.add_argument('--headless')
		self.chromeoptions = chromeoptions
		self.caps_ch = caps_ch
		self.firefoxoptions = firefoxoptions
		self.caps_ff = caps_ff
		self.firefoxprofile = firefoxprofile

	def GetNetworkResources(self, driver, ret="name"):
		Resources = driver.execute_script("return window.performance.getEntries();")
		names = [resource['name'] for resource in Resources]
		if (ret=="name"):
			return names
		else:
			return Resources

	def setdriver(self, chromeoptions="", firefoxoptions=""):
		self.generate_selenium_options()
		if chromeoptions=="":
			chromeoptions = self.chromeoptions
		if firefoxoptions=="":
			firefoxoptions = self.firefoxoptions
		merged_chrome_desired_capabilities = self.merge_two_dicts(self.caps_ch, chromeoptions.to_capabilities())
		merged_firefox_desired_capabilities = self.merge_two_dicts(self.caps_ff, firefoxoptions.to_capabilities())
		if re.search('remote', self.binary_and_driver_path['browser_type'])!=None:
			if self.binary_and_driver_path['browser_type']=="remoteff":
				merged_desired_capabilities = merged_firefox_desired_capabilities
			else:
				merged_desired_capabilities = merged_chrome_desired_capabilities
			self.driver = webdriver.Remote(command_executor='http://'+self.binary_and_driver_path['docker_remote_selenium_addr']+'/wd/hub', desired_capabilities=merged_desired_capabilities)
		elif self.binary_and_driver_path['browser_type']=='chrome':
			self.chromeoptions.binary_location = self.binary_and_driver_path['chromebinary_location']
			self.driver = webdriver.Chrome(executable_path=self.binary_and_driver_path['chromedriver_path'], options=chromeoptions, desired_capabilities=merged_chrome_desired_capabilities, service_log_path=self.seleniumlogpath)
		elif self.binary_and_driver_path['browser_type']=='firefox':
			self.driver = webdriver.Firefox(executable_path=self.binary_and_driver_path['geckodriver_path'], firefox_binary=self.binary_and_driver_path['firefoxbinary_location'], firefox_profile=self.firefoxprofile, firefox_options=firefoxoptions, desired_capabilities=self.caps_ff, log_path=self.seleniumlogpath)
		if False and (self.binary_and_driver_path['browser_type']=='chrome' and os.path.exists(self.binary_and_driver_path['chromeublockpath'])):
			self.driver.get('chrome://extensions')
			time.sleep(1)
			go_to_extension_js_code = '''
				var extensionName = 'uBlock Origin';
				var extensionsManager = document.querySelector('extensions-manager');
				var extensionsItemList = extensionsManager.shadowRoot.querySelector(
				'extensions-item-list');
				var extensions = extensionsItemList.shadowRoot.querySelectorAll(
				'extensions-item');
				for (var i = 0; i < extensions.length; i += 1) {
					var extensionItem = extensions[i].shadowRoot;
					if (extensionItem.textContent.indexOf(extensionName) > -1) {
						extensionItem.querySelector('#detailsButton').click();
					}
				}
			'''
			enable_incognito_mode_js_code = '''
				var extensionsManager = document.querySelector('extensions-manager');
				var extensionsDetailView = extensionsManager.shadowRoot.querySelector(
				'extensions-detail-view');
				var allowIncognitoRow = extensionsDetailView.shadowRoot.querySelector(
				'#allow-incognito');
				allowIncognitoRow.shadowRoot.querySelector('#crToggle').click();
			'''
			self.driver.execute_script(go_to_extension_js_code)
			time.sleep(1)
			self.driver.execute_script(enable_incognito_mode_js_code)
			pass
		if (self.binary_and_driver_path['browser_type']=='firefox' and os.path.exists(self.binary_and_driver_path['firefoxublockpath'])):
			pass

	def driver_get_completesrc(self, churl='https://www.google.com.tw/', chromeoptions="", firefoxoptions=""):
		self.setdriver(chromeoptions=chromeoptions, firefoxoptions=firefoxoptions)
		driver = self.driver
		try:
			driver.get(churl)
			htmlsrc = str(driver.page_source)[1]
		except Exception as e:
			htmlsrc = str(e)
		finally:
			driver.close()
		return htmlsrc

	def driver_get_log_steps_hami(self, driver):
		minorlogs = ""
		#driver.implicitly_wait(60)
		presence_checkxpath = ["//div[@class='top_login']",
			"//div[@class='card loginType']/div[@class='btSet']/a",
			"//div[@id='login_section1']/div[@class='btSet bt_other']/a",
			"//div[@id='login_section2']/div[@class='btSet']/a",
			"//div[@id='loginKick']",
			"//button[@class='vjs-big-play-button']",
			"//button[@class='vjs-big-play-button']",
			"//button[contains(@class,'vjs-icon-cog')]",
			"//span[@class='vjs-menu-item-text' and contains(text(), '1080')]"
		]
		presence_action = ["memberBlock();",
			"loginCheck();",
			"loginOthers();",
			"loginBy('wifi');",
			"doKickLogin();",
			"elementclick",
			"elementclick",
			"elementclick",
			"elementclick"
		]
		i = 0
		while i<len(presence_checkxpath):
			#print(presence_checkxpath[i])
			try:
				alert = driver.switch_to_alert()
				alert.accept()
			except Exception as e:
				minorlogs += str(e)
			try:
				locator = (By.XPATH, presence_checkxpath[i])
				WebDriverWait(driver, 3, 0.5).until(EC.presence_of_element_located(locator))
				if presence_action[i]!='elementclick':
					driver.execute_script(presence_action[i])
				else:
					elem = driver.find_element_by_xpath(presence_checkxpath[i])
					elem.click()
				#driver.implicitly_wait(1)
				time.sleep(0.75)
			except Exception as e:
				minorlogs += str(e)
			try:
				alert = driver.switch_to.alert()
				alert.dismiss()
			except Exception as e:
				minorlogs += str(e)
			i += 1
		return minorlogs

	def clear_other_browser_processed(self):
		try:
			os.system('pgrep "chrom|firefox" | xargs kill')
		except:
			pass
		#try:
		#	os.system('taskkill /f /im firefox.exe')
		#except:
		#	pass
		try:
			os.system('taskkill /f /im chrome.exe')
		except:
			pass

	def driver_get_log_steps_linetoday(self, driver):
		minorlogs = "" #"//figure[@class='fig-cont']", 
		presence_checkxpaths = ["//div[@class='__ui_resolution']/button", "//div[@class='__ui_resolution']//li"]
		time.sleep(2)
		for presence_checkxpath in presence_checkxpaths:
			try:
				locator = (By.XPATH, presence_checkxpath)
				WebDriverWait(driver, 30, 0.1).until(EC.presence_of_element_located(locator))
				driver.find_elements_by_xpath(presence_checkxpath)[-1].click()
			except Exception as e:
				minorlogs += str(e)
		return minorlogs

	def driver_get_log_steps_maplestage(self, driver):
		minorlogs = ""
		videoiframeelementxpath = "//div[@name='video']//iframe"
		invideoframeplayxpath = "//body"
		waiting_ad_xpath = "//div[@class='baiduyytf']"
		try:
			locator = (By.XPATH, videoiframeelementxpath)
			WebDriverWait(driver, 30, 1).until(EC.frame_to_be_available_and_switch_to_it(locator))
			videoiframeelement = driver.find_element_by_xpath(videoiframeelementxpath)
		except Exception as e:
			minorlogs += str(e)
		try:
			locator = (By.XPATH, waiting_ad_xpath)
			WebDriverWait(driver, 30, 1).until(EC.invisibility_of_element_located(locator))
			invideoframeplayelement = driver.find_element_by_xpath(invideoframeplayxpath)
			invideoframeplayelement.click()
		except Exception as e:
			minorlogs += str(e)
		driver.switch_to.default_content()
		return minorlogs

	def driver_get_log_steps_linetv(self, driver):
		minorlogs = ""
		playlinetvxpaths = ["//button[@class='vjs-big-play-button']",
			"//button[@class='vjs-menu-button vjs-menu-button-popup vjs-button']",
			"//li[@data-label='480p']"]
		try:
			for playlinetvxpath in playlinetvxpaths:
				locator = (By.XPATH, playlinetvxpath)
				WebDriverWait(driver, 5, 0.2).until(EC.element_to_be_clickable(locator))
				linetvplayeelement = driver.find_element_by_xpath(playlinetvxpath)
				linetvplayeelement.click()
		except Exception as e:
			minorlogs += str(e)
		#time.sleep(3)
		return minorlogs

	def driver_get_log(self, churl='https://hamivideo.hinet.net/channel/OTT_LIVE_0000001869.do', type='hami', actions=True, chromeoptions="", firefoxoptions="", driver=""):
		if driver=="":
			self.setdriver(chromeoptions=chromeoptions, firefoxoptions=firefoxoptions)
			driver = self.driver
		driver.set_page_load_timeout(60)
		minorlogs = ""
		if actions==True:
			driver.get(churl)
			if type=='linetoday':
				minorlogs = minorlogs+self.driver_get_log_steps_linetoday(driver)
			elif type=='maplestage':
				minorlogs = minorlogs+self.driver_get_log_steps_maplestage(driver)
			elif type=='linetv':
				minorlogs = minorlogs+self.driver_get_log_steps_linetv(driver)
			else:
				minorlogs = minorlogs+self.driver_get_log_steps_hami(driver)
		try:
			performancelogs = driver.execute('getLog', {'type': 'performance'})['value']
		except Exception as e:
			performancelogs = str(e)
		try:
			networklogs = self.GetNetworkResources(driver)
		except Exception as e:
			networklogs = str(e)
		return {'networklogs': networklogs, 'performancelogs': performancelogs, 'minorlogs': minorlogs}

	def find_streamingurl_from_listofurls(self, logs, newest=True):
		needlog = None
		if newest==True:
			logs.reverse()
		for log in logs:
			if re.search('(m3u8|mp4)', log)!=None:
				needlog = log
				break
		return needlog

	def get_streaming_request_of_ch(self, logs, kwds = ['mp4','m3u8','User-Agent','Referer']):
		have_stream = False #Crafted HTTP Request Header
		excepterror = ""
		searchres = []
		mediakwds_str = "("+"|".join(kwds[0:2])+")"
		maplestage_exclude_patterns = "(.gif|.js|video.8maple.ru|ad.8maple.ru|_SD.m3u8|360p)"
		try:
			performancelogs = logs
			performancelogs = self.parse_json_response(performancelogs)
			for performancelog in performancelogs:
				for k, v in performancelog.items():
					try:
						jsondumpedv = json.dumps(v['message']['params'])
						kwds_res = [re.search(kwd,jsondumpedv)!=None for kwd in kwds]
						if kwds_res.count(True)>=3:
							searchres.append(v['message']['params']) #{k:v}
					except Exception as e:
						excepterror = excepterror+str(e)
						continue
			searchres = self.unique(searchres)
			searchres = six.moves.filter(lambda x: 'request' in x.keys(), searchres)
			searchres = six.moves.filter(lambda x: 'url' in x['request'].keys(), searchres)
			searchres = six.moves.filter(lambda x: re.search(maplestage_exclude_patterns, x['request']['url'])==None, searchres)
			searchres = six.moves.filter(lambda x: re.search(mediakwds_str, x['request']['url'])!=None, searchres)
			searchres = list(searchres)
			while True: #because got many requests, pick one randomly
				break_try_random_element = False
				try:
					searchres_onerandomelement = random.choice(searchres)
					crafted_url = searchres_onerandomelement['request']['url']+'|User-Agent='+searchres_onerandomelement['request']['headers']['User-Agent']+'&Referer='+searchres_onerandomelement['request']['headers']['Referer']
					break_try_random_element = True
				except Exception as e:
					break_try_random_element = False
				if break_try_random_element:
					break
			needlog = crafted_url
			if needlog!=None:
				have_stream = True
		except Exception as e:
			excepterror = excepterror+str(e)
		if have_stream == False:
			needlog = ("get streamingurl of ch error: "+excepterror)
		return needlog

	def get_streamingurl_of_ch(self, churl='https://hamivideo.hinet.net/channel/OTT_LIVE_0000001869.do', type='hami', chromeoptions="", firefoxoptions="", logtype='networklogs', kwds = ['mp4','m3u8','User-Agent','Referer']):
		#streamingurl = (json.loads(profilelog['message'])['message']['params']['request']['url'])
		have_stream = False
		excepterror = ""
		try:
			self.setdriver(chromeoptions=chromeoptions, firefoxoptions=firefoxoptions)
			driver = self.driver
			logs = self.driver_get_log(churl, type=type, chromeoptions=chromeoptions, firefoxoptions=firefoxoptions, driver=driver)
			try:
				driver.close()
			except Exception as e:
				excepterror += str(e)
			needlog = self.get_streaming_request_of_ch(logs[logtype], kwds=kwds) if logtype=='performancelogs' else self.find_streamingurl_from_listofurls(logs[logtype])
			if type=='linetv':
				needlog = needlog+'&:authority=keydeliver.linetv.tw&:method: OPTIONS:scheme: https'
			if needlog!=None:
				have_stream = True
		except Exception as e:
			excepterror = str(e)
		if have_stream == False:
			needlog = ("get streamingurl of ch error: "+excepterror)
		return needlog

	def get_better_q_streamingsrc(self, streamingurl, newq='4'):
		p = re.compile('index{1}_?\d?.m3u8')
		streamingurl = p.sub('index_'+newq+'.m3u8', streamingurl)
		return streamingurl

'''
https://video.8maple.ru/yandisk/?w=600&h=445&url=63619D61B26ADAAFD3899B667E77DFD78380B788936996A594CF67D4A85FD1CE95ABCAA694ABCCC9C79F626A5DABA8A67771B87FC6606369629668877866869A68579E768A7A9A8A9B71586A645BAB9B5B72AA5BA67357756A89729B5868A5926560D2A49964CCD3C695AB609D69DB9B_yandisk
DNT: 1
Sec-Fetch-Dest: empty
referer: https://8maple.ru/338188/
sec-fetch-dest: iframe
sec-fetch-mode: navigate
sec-fetch-site: same-site
upgrade-insecure-requests: 1
'''


if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("--type", help="video host")
	parser.add_argument("--churl", help="video url")
	args = parser.parse_args()
	type = args.type
	churl = args.churl
	if (churl!=None):
		settings = dict()
		hamic = Hamivideo()
		if False: #for debugging
			#res = hamic.ret_linetv_dramas_of_a_catg("kid")
			#res = hamic.ret_linetv_dramas_metadata()
			res = hamic.ret_linetv_drama(churl)
			episode_args = [(int(churl), c) for c in range(1, res['current_eps']+1)]
			#res = hamic.ret_linetv_dramas_of_a_catg("kid")[0]
			#res = hamic.ret_linetv_main_menu_catgs()
			#res = type(res)
			pool = ThreadPool(4)
			episodedatas = pool.map(hamic.ret_linetv_episode_data_multi_run_wrapper, episode_args)
			print(episodedatas)
			sys.exit()
			descriptions = pool.map(hamic.ret_linetv_drama_description_multi_run_wrapper, episode_args)
			episodedatas = {int(d['episode']):d for d in episodedatas}
			descriptions = {int(d['drama_episode']):d['drama_description'] for d in descriptions}
			print(episodedatas)
			sys.exit()
		fakemediaurl_suffix = 'index.m3u8'
		#if type in ['linetoday','maplestage','linetv','dramaq']:
		#	cchurl = churl.replace(fakemediaurl_suffix,'')
		#else:
		#	cchurl = churl.replace('.m3u8','.do')
		cchurl = churl
		if type=='maplestage':
			streamingurl = hamic.ret_maplestage_streamingurl_by_req(cchurl)
			subtitleurl = None
		if type=='dramaq':
			streamingurl = hamic.ret_dramaq_streaming_url_by_req(cchurl)
			subtitleurl = None
		elif type=='hami':
			channelid = os.path.basename(cchurl).replace('.do','')
			streamingurl = hamic.ret_hami_streaming_url_by_req(channelid)
			streamingurl = hamic.get_better_q_streamingsrc(streamingurl)
			subtitleurl = None
		elif type=='linetv':
			epi_data = hamic.ret_linetv_episode_data(url=cchurl)
			streamingurl = epi_data['multibitrateplaylist']
			subtitleurl = epi_data['epsInfo']['source'][0]['links'][0]['subtitle']
		elif type=='linetoday':
			streamingurl = hamic.get_streamingurl_of_ch(cchurl, type=type, logtype='networklogs')
			subtitleurl = None
		if re.search('(timed out|timeout|unknown error|connection refused)', streamingurl)!=None:
			pass
		else:
			print(streamingurl)