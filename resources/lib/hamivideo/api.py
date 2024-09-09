import requests
import htmlement
import time
import sys
from xml.etree import ElementTree
import json
import re
import os
from pathlib import Path
import random
import base64
import six
try:
	from selenium import webdriver
	from selenium.webdriver.chrome.options import Options as ChromeOptions
	from selenium.webdriver.firefox.options import Options as FirefoxOptions
	from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
	from selenium.webdriver.common.keys import Keys
	from selenium.webdriver.support.wait import WebDriverWait
	from selenium.webdriver.support import expected_conditions as EC
	from selenium.webdriver.common.by import By
except:
	include_selenium = False
	pass
try:
	import jsbeautifier
except:
	include_jsbeautifier = False
	pass

try:
	from multiprocessing.dummy import Pool as ThreadPool
	threadpool_imported = True
except:
	threadpool_imported = False
try:
	import multiprocessing
	workers = multiprocessing.cpu_count()
except:
	workers = 4
#from xbmcswift2 import Plugin, xbmc, xbmcaddon, xbmcgui, xbmcplugin

#https://stackoverflow.com/questions/57167357/why-does-socket-interfere-with-selenium

class Hamivideo(object):

	def __init__(self, **settings):
		settings.setdefault('chromedriver_path', "E:\\Software\\scripts\\python\\kodi_dev\\plugin.video.example\\chromedriver.exe")
		settings.setdefault('chromebinary_location', "D:\\PortableApps\\PortableApps\\GoogleChromePortable\\App\\Chrome-bin\\chrome.exe")
		settings.setdefault('geckodriver_path', "E:\\Software\\scripts\\python\\kodi_dev\\plugin.video.example\\geckodriver.exe")
		settings.setdefault('firefoxbinary_location', "D:\\PortableApps\\PortableApps\\FirefoxPortable\\App\\Firefox64\\firefox.exe")
		settings.setdefault('docker_remote_selenium_addr', "127.0.0.1:4444")
		settings.setdefault('browser_type', "remotech")
		settings.setdefault('chromeublockpath', "E:\\Software\\scripts\\python\\kodi_dev\\plugin.video.hamivideo\\ublock_extension_1_24_2_0.crx")
		settings.setdefault('firefoxblockpath', "E:\\Software\\scripts\\python\\kodi_dev\\plugin.video.hamivideo\\uBlock0_1.24.5rc1.firefox.signed.xpi")
		settings.setdefault('seleniumlogpath', "/home/pi/seleniumlogpath.txt")
		settings.setdefault('ptsplusloginidpw', (None,None))
		settings.setdefault('ptsplusloginchecksum', None)
		settings.setdefault('ptsplusloginxapikey', None)
		settings.setdefault('ptspluslogin_cookieinf', {
			'filename':Path(os.path.realpath(__file__)).parent / 'ptspluslogininf.txt',
			'cookieinf':None
			})
		settings.setdefault('hamiloginidpw', (None,None))
		settings.setdefault('youtube_api_key', None)
		settings.setdefault('hamilogin_cookieinf', {
			'filename':Path(os.path.realpath(__file__)).parent / 'hamilogininf.txt',
			'cookieinf':None
			})
		settings['ptsplusloginidpw'] = (settings['ptsplusloginidpw'][0],settings['ptsplusloginidpw'][1])
		settings['hamivideo_host_url'] = 'https://hamivideo.hinet.net/'
		self.settings = settings
		self.linetoday_url = 'https://today.line.me/'
		self.def_webdrive_binary_path(settings)
		self.useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0' # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
		self.request_user_agent = 'User-Agent: '+self.useragent #Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36
		self.mobile_request_useragent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
		self.linetv_host_url = 'https://www.linetv.tw'
		self.workers = workers
		self.hamiloginidpw = (settings['hamiloginidpw'][0],settings['hamiloginidpw'][1])
		self.ptsplus_loginres = None

	def try_multi_run(self,sp_multi_run_func,spargs):
		try:
			pool = ThreadPool(workers)
			datas = pool.map(sp_multi_run_func, spargs)
			pool.close()
			pool.join()
		except:
			datas = [sp_multi_run_func(sparg) for sparg in spargs]
		#if threadpool_imported:
		#else:
		#	datas = [sp_multi_run_func(sparg) for sparg in spargs]
		return datas

	def def_webdrive_binary_path(self, binary_and_driver_path):
		self.binary_and_driver_path = binary_and_driver_path
		if self.binary_and_driver_path['browser_type'].find('remote')!=-1:
			for key in ['chromedriver_path', 'chromebinary_location', 'geckodriver_path', 'firefoxbinary_location']:
				self.binary_and_driver_path.pop(key, None)

		
	def merge_two_dicts(self, x, y):
		z = x.copy()   # start with x's keys and values
		z.update(y)	# modifies z with y's keys and values & returns None
		return z

	def requesturl_get_ret(self, url, params=None, **kwargs):
		r = requests.get(url, params=params, **kwargs)
		return r.text

	def requesturl_get_jsonret(self, url, params=None, **kwargs):
		r = requests.get(url, params=params, **kwargs)
		return self.parse_json_response(r.text)

	def requesturl_post_ret(self, url, data=None, json=None, **kwargs):
		r = requests.post(url, data=data, json=json, **kwargs)
		return r.text

	def requesturl_post_jsonret(self, url, data=None, json=None, **kwargs):
		r = requests.post(url, data=data, json=json, **kwargs)
		return self.parse_json_response(r.text)

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
				if isinstance(content[key], six.text_type) or isinstance(content[key], six.string_types): #if (type(content[key]) is str or str(type(content[key])).find('unicode')!=-1):
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

	def return_hamidramamovies(self):
		html_doc = self.requesturl_get_ret(self.settings['hamivideo_host_url']+'%E5%BD%B1%E5%8A%87%E9%A4%A8%E2%81%BA/%E6%9C%80%E6%96%B0.do')
		root = htmlement.fromstring(html_doc)
		# parser = html5lib.HTMLParser(tree=html5lib.getTreeBuilder("dom"))
		# root = parser.parse(html_doc)
		main_menu_list = []
		items = root.findall(".//div[@class='swiper-wrapper']/li")
		items = [item for item in items if item.get('class').find("swiper-slide")!=-1]
		for item in items:
			main_menu_list.append({
				'name': item.find(".//a").text,
				'link': item.find(".//a").get('href'),
				'program': '',
				'icon': '',
				'programtime': '',
				'channelid': ''
			})
		items = root.findall(".//section/div[@class='title_in']")
		for item in items:
			linkitem = item.find(".//div[@class='bt_more_19']/a")
			if linkitem is not None:
				main_menu_list.append({
					'name': item.find(".//h2").text,
					'link': linkitem.get('onclick'),
					'program': '',
					'icon': '',
					'programtime': '',
					'channelid': ''
				})
		return main_menu_list

	def return_searchinghamidramamovies(self, keyword='', **kwargs):
		postdata = 'keyword={}&dataSource=%E6%89%80%E6%9C%89%E5%BD%B1%E7%89%87&sorting=3&recstart=0&recend=31'.format(keyword)
		req_headers = {
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'Host': 'hamivideo.hinet.net'
		}
		r = requests.post('https://hamivideo.hinet.net/search/content.do', data=postdata, json=json, headers=req_headers, **kwargs)
		results = self.parse_json_response(r.text)
		results = results['result']
		results = [{
			'name': None,
			'programtime': None,
			'program': "{} ({})".format(c['productName'], c['seriesValue']),
			'icon':c['imageId'],
			'thumbnail':c['imageId'],
			'contentId':c['contentId'],
			'contentPk':c['contentPk'],
			'link':c['link'],
			'info':c['description'],
			'series':c['series'],
		} for c in results]
		return results

	def return_get_hamidramamovies_infopage_streaming_url(self, link='', contentPk=None, loginidpw=None, is_singleepisode=True, **kwargs):
		if contentPk is not None:
			ret = self.ret_hami_streaming_url_by_req(channel_id=contentPk, loginidpw=loginidpw, ret_session=False)
			return ret
		
		# self.prepare_logininf(src='hami')
		channelapiurl = 'https://hamivideo.hinet.net/'+link
		# 間諜家家酒
		html_doc = self.requesturl_get_ret(channelapiurl)
		# print(f"link is {link}\n")
		# product/239732.do?cs=2
		responsejson = []
		matched_lines = htmlement.fromstring(html_doc)
		matched_streamingdata = matched_lines.findall(".//div[@class='list_program']/ul[@class='program_class_in']//li")
		matched_descriptions = matched_lines.findall(".//div[@class='descript']//p")
		matched_posters = matched_lines.findall(".//div[@class='pic posterImage']//img")
		for itemkey,item in enumerate(matched_streamingdata):
			title = "".join(list(item.itertext()))
			episode = item.find(".//p").text
			description = matched_descriptions[itemkey].get("data")
			item = {
				"episode": episode,
				"program": title,
				"name": title,
				"description": description,
				"icon": matched_posters[itemkey].get("data-src"),
				"thumbnail": matched_posters[itemkey].get("data-src"),
				"rating": item.get("data-rating"),
				"contentPk": item.get("data-id"),
				"link": item.get("data-id"),
			}
			responsejson.append(item)
		# sendUrl('/play/239732/OTT_VOD_0000339039.do','OTT_VOD_0000336292','0','');
		# loginidpw = self.hamiloginidpw if loginidpw==None else loginidpw
		# reqheaders_std = {
		# 	'Origin': 'https://hamivideo.hinet.net',
		# 	'user-agent': self.useragent,# 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
		# 	'Sec-Fetch-Site': 'same-origin',
		# 	'Accept': '*/*; q=0.01',
		# 	'Accept-Encoding': 'gzip, deflate, br',
		# 	'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
		# 	'Host': 'hamivideo.hinet.net',
		# 	'DNT': '1',
		# }
		# reqheaders_hamilogin = self.merge_two_dicts(reqheaders_std, {
		# 	'Referer': "https://hamivideo.hinet.net/hamivideo/index.do",
		# 	'Sec-Fetch-Dest': 'empty',
		# 	'Sec-Fetch-Mode': 'cors',
		# 	'X-Requested-With': 'XMLHttpRequest',
		# })
		# session = requests.Session()
		# session.headers.update(reqheaders_hamilogin)
		# response = session.get(channelapiurl, cookies=self.settings['hamilogin_cookieinf']['cookieinf'])
		# responsejson = self.parse_json_response(response.text)
		return responsejson

	def return_hamichannels(self):
		html_doc = self.requesturl_get_ret(self.settings['hamivideo_host_url']+'%E9%9B%BB%E8%A6%96%E9%A4%A8/%E5%85%A8%E9%83%A8.do')
		root = htmlement.fromstring(html_doc)
		main_menu_list = []
		for item in root.findall(".//div[@class='tvListBlock']/div[@class='list_item']"):
			title = item.find(".//h3/a").text
			#link = self.settings['hamivideo_host_url']+item.find(".//h3/a").get("href")
			#link = link.replace("//","/")
			link = item.find(".//h3/a").get("href")
			# link = self.settings['hamivideo_host_url']+re.findall(r"sendUrl\(\'(.+\.do)\',", link)[0]
			channelid = os.path.basename(link).replace('.do','')
			channel_icon = item.find(".//img").get("src")
			programtime = item.find(".//div[@class='time']")
			try:
				programtime = programtime.text
			except Exception as e:
				programtime = ""
			# program = item.find(".//div[@class='com']/p/a") #elemtree.tostring(item.find(".//div[@class='com']"))
			try:
				program = list(item.itertext())[2]
			except Exception as e:
				program = str(e)
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
		watchlinetodaytvelem = six.moves.filter(lambda x: re.search("(&#38651;&#35222;)", ElementTree.tostring(x)), topmenus ) #
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
			'User-Agent': self.useragent,
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
		searchboxcx = re.findall(r"cx\s=\s\'(.+)\'\;", searchbox)[0]
		searchbox = 'https://cse.google.com/cse.js?cx='+searchboxcx
		searchboxresponse = session.get(searchbox)
		cse_token = re.findall(r"cse_token\":\s\"(.+)\",", searchboxresponse.text)[0]
		cselibVersion = re.findall(r"cselibVersion\":\s\"(.+)\",", searchboxresponse.text)[0]
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
			'cse_tok':six.moves.urllib.parse.unquote(cse_token),
			'exp':'csqr,cc',
			'callback':'google.search.cse.api3966',
			'q':six.moves.urllib.parse.unquote(drama_name),
		}
		response = requests.get(dramaq_search_url, cookies=setcookies, params=dramaq_search_url_data)
		dramaq_search_results = re.findall(r"google\.search\.cse.+\(({[\w\d\s\W\D\S]+})\);", response.text)
		dramaq_search_results = self.parse_json_response(dramaq_search_results)[0]["results"]
		dramaq_search_results = six.moves.filter(lambda x: re.search(r"\d+\.html", x['url'])==None, dramaq_search_results)
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
			'User-Agent': self.useragent,
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
		dramaq_streamingurl = re.findall(r"var\sm3u8url\s=\s\'(.+)\'(\r|\n|\s)", dramaq_streamingurl)[0][0]
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
			'User-Agent': self.useragent,
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
				allpagesnum = re.search(r"共有(\d+)頁", allpagesnum)
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
		results = six.moves.reduce(lambda x,y: x+y, results)
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

	def gset_login_inf_fromtxt(self, src='hami', mode='r', data=None):
		with open(self.settings[src+'login_cookieinf']['filename'], mode, newline='') as jsonfile:
			if mode=='w':
				json.dump(data, jsonfile) #settings['hamilogin_cookieinf']['cookieinf']
				# print("write logging info to {} complete".format(self.settings['hamilogin_cookieinf']['filename']))
				return True
			else:
				data = json.load(jsonfile)
				# print(f"load logging info complete")
				return data

	def prepare_logininf(self, src='hami'):
		try:
			tplogindata = self.gset_login_inf_fromtxt(src=src, mode='r')
			# tplogindata = json.loads(tplogindata)
			self.settings[src+'login_cookieinf']['cookieinf'] = tplogindata
		except json.JSONDecodeError as e:
			self.settings[src+'login_cookieinf']['cookieinf'] = {}

	def ret_hami_streaming_url_by_req(self, channel_id, loginidpw=None, ret_session=False, currentRecursionDepth=0, allowedRecursionDepth=1):
		self.prepare_logininf(src='hami')
		channelapiurl = 'https://hamivideo.hinet.net/api/play.do?id='+channel_id
		loginidpw = self.hamiloginidpw if loginidpw==None else loginidpw
		reqheaders_std = {
			'Origin': 'https://hamivideo.hinet.net',
			'user-agent': self.useragent,# 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
			'Sec-Fetch-Site': 'same-origin',
			'Accept': '*/*; q=0.01',
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
		response = session.get(channelapiurl, cookies=self.settings['hamilogin_cookieinf']['cookieinf'])
		responsejson = self.parse_json_response(response.text)

		if 'url' not in responsejson: # when previous saved cookie not work in retrieving data
			response = session.get('https://hamivideo.hinet.net/index.do')
			indexdo_html = response.text
			docloginFormothers = re.compile(r"do\?others=([A-Za-z\d]+)").search(indexdo_html).group(1)
			setcookies = session.cookies.get_dict()
			#setcookies_str = "; ".join([k+"="+v for k,v in setcookies.items()])
			response = session.post('https://hamivideo.hinet.net/hamivideo/getDeviceLoginInfo.do', cookies=setcookies)
			deviceinfo = response.text
			#https://hamivideo.hinet.net/hamivideo/app/login.do?deviceId=1d0155e5c5004366f36db9a5141272b9&deviceType=1&deviceOS=android_9&deviceVender=htc&deviceIp=192.168.1.120&deviceName=HTC_U-3u HTTP/1.1
			response = session.post('https://hamivideo.hinet.net/loginTo.do', params={'loginMethod': 'wifi','others':docloginFormothers}, cookies=setcookies)
			def kick_hami_alreadylogin(response=response,session=session):
				# print("previous duplicated hamivideo login exists")
				kickloginpagehtml = response.text
				kickloginpagehtml_root = htmlement.fromstring(kickloginpagehtml)
				if kickloginpagehtml_root.text is None:
					actionurl = re.compile('<form.+action="(.+)">').search(kickloginpagehtml).group(1)
					canbekicked_devices = re.compile(r'<input.+name="(.+)"\svalue="(.+)".*>').findall(kickloginpagehtml)
					kickloginform_inputs = {v[0]:v[1] for v in canbekicked_devices}
					import html
					kickloginform_inputs['device'] = html.unescape(kickloginform_inputs['device'])
				else:
					kickloginform = kickloginpagehtml_root.find(".//form[@id='formPage']")
					actionurl = kickloginform.get('action')
					kickloginform_inputs = {elem.get('name'):elem.get('value') for elem in kickloginform.findall(".//input")}
				kicklogindevices = self.parse_json_response(kickloginform_inputs['device'])
				earliest_login = sorted([d['loginTime'] for d in kicklogindevices])[0]
				earliest_login_device = six.moves.filter(lambda x: x['loginTime']==earliest_login, kicklogindevices)
				earliest_login_device = list(earliest_login_device)[0]
				kicklogindata = self.merge_two_dicts(kickloginform_inputs, {
					'loginMethod': 'kick',
					'authLoginId':'',
					'otpw': earliest_login_device["logoutToken"],
					'autoLogin':'',
					'others':docloginFormothers,
					'authParam':'',
					'hn_captcha':'',
					'orig_loginMethod': earliest_login_device["deviceTypeId"],
					'orig_otpw':'',
				})
				kicklogindata.pop('device')
				response = session.post('https://hamivideo.hinet.net/hamivideo/loginTo.do', data=kicklogindata, cookies=setcookies)
				retcookies = session.cookies.get_dict()
				# print(f'actionurl is {actionurl} and if equals is {actionurl=="https://hamivideo.hinet.net/hamivideo/loginTo.do"}')
				return retcookies

			if (re.search("kick.do",response.text)!=None):
				setcookies = kick_hami_alreadylogin(response,session)
			else:
				setcookies = session.cookies.get_dict()
				#login with hn instead (previous hn method)
				if False:
					response = session.post('https://hamivideo.hinet.net/loginTo.do', params={'loginMethod': 'hn','others':docloginFormothers}, cookies=setcookies)
					loginformdata = six.moves.urllib.parse.parse_qs(response.url)
					loginformdata = {k:v[0] for k,v in loginformdata.items()}
					loginformdata['version'] = loginformdata.pop('https://member.cht.com.tw/HiReg/checkcookieservlet?version',1.0)
					loginformdata['uid'] = loginidpw[0]
					loginformdata['pw'] = loginidpw[1]
					reqheaders_chthnlogin = self.merge_two_dicts(reqheaders_hamilogin, {
						'Host': "member.cht.com.tw",
						'Origin': 'https://member.cht.com.tw',
						'Referer': response.url,
					})
					session.headers.update(reqheaders_chthnlogin)
					chthn_loginUrl = 'https://member.cht.com.tw/HiReg/multiauthentication'
					setcookies = session.cookies.get_dict()
					response = session.post(chthn_loginUrl, params=loginformdata, cookies=setcookies)
					setcookies = self.merge_two_dicts(session.cookies.get_dict(), response.cookies.get_dict())
					session.headers.update(reqheaders_hamilogin)
					#pass #print("no duplicated hamivideo login")
					if (re.search("kick.do",response.text)!=None):
						#print('duplicated hamivideo login, kicking')
						setcookies = kick_hami_alreadylogin(response,session)

			self.gset_login_inf_fromtxt(src='hami', mode='w', data=setcookies)
			# retroplay: https://hamivideo.hinet.net/api/play.do?id=OTT_TS_0000001744_2023100202300020231002043000&freeProduct=0&llsetting=false&_=1696218765840

			response = session.get(channelapiurl, cookies=setcookies)
			responsejson = self.parse_json_response(response.text)

		if ret_session==True:
			return {'session':session, 'cookie': setcookies, 'responsejson': responsejson}
		elif 'url' in responsejson:
			# raise ValueError(f'responsejson is {responsejson}')
			return responsejson['url']
		elif currentRecursionDepth<=allowedRecursionDepth:
			# raise ValueError(f'in recursion')
			return self.ret_hami_streaming_url_by_req(channel_id, loginidpw=loginidpw, ret_session=ret_session, currentRecursionDepth=currentRecursionDepth+1, allowedRecursionDepth=allowedRecursionDepth)
		else:
			errorMessage = 'error in ret_hami_streaming_url_by_req for channel_id={}, ret_session={}, responsejson={}, currentRecursionDepth={}, allowedRecursionDepth={}'.format(
				channel_id,ret_session,json.dumps(responsejson),currentRecursionDepth,allowedRecursionDepth
			)
			# raise BaseException(errorMessage)
			return errorMessage

	def ret_maplestage_streamingurl_by_req(self, singleepisodeurl):
		maple_homepage = 'https://8maple.ru/'
		reqheaders_std = {
			'User-Agent': self.useragent,
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
		video_refer_argums = re.findall(r"push\(\'(.+)\'\)", maplestage_singledrama_scripts)
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
		maplestagestreamingurl = re.findall(r"\(([\w\d\,]{15,})\)", maplestagestreamingurl)[0]
		maplestagestreamingurl = maplestagestreamingurl.split(",")
		maplestagestreamingurl = map(int, maplestagestreamingurl)
		maplestagestreamingurl = ''.join(map(unichr, maplestagestreamingurl))
		maplestagestreamingurl = re.findall(r"file\:\'\/\/[\w\d\-\.\/\%\?\=\&\:]+",maplestagestreamingurl)[0]
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

	def ptspluslogin(self, ptsplusloginidpw=None):
		# prepare_logininf gset_login_inf_fromtxt
		if ptsplusloginidpw is not None:
			loginid = ptsplusloginidpw[0]
			loginpw = ptsplusloginidpw[1]
		else:
			loginid = self.settings['ptsplusloginidpw'][0]
			loginpw = self.settings['ptsplusloginidpw'][1]
		if self.ptsplus_loginres==None:
			from requests.auth import HTTPBasicAuth
			loginurl = 'https://www.ptsplus.tv/api/v1/login' #https://www.ptsplus.tv/api/login'
			loginpayload = {
					# "username":loginid,
					# "loginType":1,
					# "authorization":"MTE2MjBjYjgtOTczYy00ZDY5LTg0YmItYmE0ZjcxZDAyNDYwOkZoVlhVdTl4Zmp4NmR3TlVNd0Fw"
					"account":loginid,
					"password":loginpw,
					"checksum": self.settings['ptsplusloginchecksum']
				}
			login_req_header = {
				'accept': 'application/json, text/plain, */*',
				# 'accept-encoding': 'gzip, deflate, br',
				# 'accept-language': 'zh-TW,zh;q=0.9',
				# 'asiaplay-device-model': 'Windows/NT 10.0/Chrome/94.0.4606.71',
				# 'asiaplay-device-type': 'WEB_PC',
				# 'asiaplay-device-version': '1.0.0.218',
				'content-type': 'application/json',
				# 'dnt': '1',
				'origin': 'https://www.ptsplus.tv',
				# 'referer': 'https://www.ptsplus.tv/zh/login',
				# 'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
				# 'sec-ch-ua-mobile': '?0',
				# 'sec-ch-ua-platform': "Windows",
				# 'sec-fetch-dest': 'empty',
				# 'sec-fetch-mode': 'cors',
				# 'sec-fetch-site': 'same-origin',
				'user-agent': self.useragent,
				'x-api-key': self.settings['ptsplusloginxapikey'],	
				}
			# print(f'loginpayload is {loginpayload} login_req_header is {login_req_header}')
			# reqauthidpw = ('11620cb8-973c-4d69-84bb-ba4f71d02460','FhVXUu9xfjx6dwNUMwAp')
			# loginres = self.requesturl_post_ret(loginurl, json=loginpayload, headers=login_req_header, auth=HTTPBasicAuth(reqauthidpw[0], reqauthidpw[1]))
			# print(f"loginurl {loginurl}, loginpayload {loginpayload}, login_req_header {login_req_header}")
			loginres = self.requesturl_post_ret(loginurl, json=loginpayload, headers=login_req_header)
			# print(f"loginres {loginres}")
			loginres = self.parse_json_response(loginres)
			# print(f'loginres is {loginres}')
			auth_after_login = {
				'Authorization':'Bearer '+loginres['accessToken']
			}
			self.gset_login_inf_fromtxt(src='ptsplus',mode='w',data=auth_after_login)
			reqheader_after_login = self.merge_two_dicts(login_req_header,auth_after_login)
			self.ptsplus_loginres = loginres
			self.ptsplus_reqheader_after_login = reqheader_after_login
			return {'loginres': loginres,'reqheader_after_login': reqheader_after_login}
		else:
			pass

	def ret_ptsplus_graphql(self, mode='maincatg', queryStr='KIDS_AND_FAMILY'):
		graphql_settings = {
			'maincatg' : {
				"親子家庭": "KIDS_AND_FAMILY",
				"戲劇影集": "DRAMA",
				"時事與紀錄片": "DOCUMENTARY",
				"生活與藝術": "LIFESTYLE_AND_ART",
				"直播": "Livestreams",
			},
			# 'ptsplus_graphql_guide' : """
			# 	{
			# 		"operationName":"Guides",
			# 		"variables":{"type":"KIDS_AND_FAMILY"},
			# 		"query": "query Guides($type: GuideTypeEnum!) { guides(type: $type) { id marketingLabel { id name introduction cover videos { id type episode { id name cover available __typename } program { ...ProgramSummary __typename } __typename } __typename } __typename }}fragment ProgramSummary on Program { id original useDRM episodeCount latestCover name introduction rating seasonCount type awards categories tags isFavorite __typename}"
			# 	}
			# """,
			'ptsplus_graphql_guide' : """
				{"operationName":"Guides","variables":{"type":"KIDS_AND_FAMILY"},"query": "query Guides($type: GuideTypeEnum!) { guides(type: $type) { id marketingLabel { id name introduction cover videos { id type episode { id name cover available __typename } program { ...ProgramSummary __typename } __typename } __typename } __typename }}fragment ProgramSummary on Program { id original useDRM episodeCount latestCover name introduction rating seasonCount type awards categories tags isFavorite __typename}"}
			""",
			'ptsplus_graphql_videomarketinglabel' : """
				{
					"operationName":"VideoMarketingLabel",
					"variables":{"videoMarketingLabelId":"2f3eeba3-a4ee-4359-9f89-73fa7c204ace"},
					"query": "query VideoMarketingLabel($videoMarketingLabelId: ID!) { videoMarketingLabel(id: $videoMarketingLabelId) { id cover introduction name subMarketingLabel { id name __typename } videos { id type program { ...ProgramSummary __typename } __typename } __typename }}fragment ProgramSummary on Program { id original useDRM episodeCount latestCover name introduction rating seasonCount type awards categories seasons { id bannerLOGO releaseMonth releaseYear canPurchase __typename } tags isFavorite __typename}"
				}
			""",
			'ptsplus_graphql_programdetail' : """
				{
					"operationName": "ProgramDetail",
					"variables": {
						"programId": "94861b17-fe6a-4bc2-b3e9-a563b455c690"
					},
					"query": "query ProgramDetail($programId: ID!) {  program(id: $programId) {    id    original    useDRM    seasonCount    episodeCount    latestCover    seasons {      id      name      bannerLOGO      bannerCover      cover      releaseYear      releaseMonth      showEpisodeNumber      episodes {        id        number        name        introduction        cover        available      video { id isDRM urlPrefixSignature stream subtitles { id name code __typename } }      __typename}      trailers {        id        index        name        introduction        cover        __typename      }      crews {        id        role        name        __typename      }      firstEpisodeIsFree      saleAt      introduction      price      watchedDays      canPurchase      __typename    }    rating    type    introduction    awards    name    categories    isFavorite    tags    inValidRegion    __typename  }}"
				}
			""",
			'ptsplus_graphql_episode' : """
				{
					"operationName":"EpisodeData",
					"variables":{"id":"cbcef1b9-de07-490e-b888-332bda733de6"},
					"query": "query EpisodeData($id: ID!) { episode(id: $id) { id name cover available introduction video { id isDRM urlPrefixSignature subtitles { id name code __typename } stream __typename } season { id name program { id name useDRM __typename } __typename } __typename }}"
				}
			""",
			'ptsplus_graphql_livestream' : """
				[
					{
						"operationName": "Livestreams",
						"variables": {
							"limit": 30,
							"offset": 0,
							"sort": "LISTING_FROM_DESC",
							"pinned": true
						},
						"query": "query Livestreams($limit: Int, $offset: Int, $searchTerm: String, $sort: LivestreamSortEnum!, $pinned: Boolean) {\n  livestreams(\n    limit: $limit\n    offset: $offset\n    searchTerm: $searchTerm\n    sort: $sort\n    pinned: $pinned\n  ) {\n    id\n    pageInfo {\n      ...PageInfo\n      __typename\n    }\n    records {\n      ...LivestreamFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment PageInfo on PageInfo {\n  id\n  totalRecords\n  hasNext\n  totalPages\n  __typename\n}\n\nfragment LivestreamFragment on Livestream {\n  id\n  index\n  cover\n  name\n  source\n  __typename\n}"
					},
					{
						"operationName": "LivestreamMarketingLabels",
						"variables": {
							"offset": 0,
							"limit": 30
						},
						"query": "query LivestreamMarketingLabels($limit: Int, $offset: Int, $searchTerm: String) {\n  livestreamMarketingLabels(\n    limit: $limit\n    offset: $offset\n    searchTerm: $searchTerm\n  ) {\n    id\n    pageInfo {\n      ...PageInfo\n      __typename\n    }\n    records {\n      id\n      name\n      livestreams {\n        ...LivestreamFragment\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment PageInfo on PageInfo {\n  id\n  totalRecords\n  hasNext\n  totalPages\n  __typename\n}\n\nfragment LivestreamFragment on Livestream {\n  id\n  index\n  cover\n  name\n  source\n  __typename\n}"
					}
				]
			"""
		}
		replace_patterns = {
			'ptsplus_graphql_guide' : "KIDS_AND_FAMILY",
			'ptsplus_graphql_videomarketinglabel' : "2f3eeba3-a4ee-4359-9f89-73fa7c204ace",
			'ptsplus_graphql_programdetail' : "94861b17-fe6a-4bc2-b3e9-a563b455c690",
			'ptsplus_graphql_episode' : "cbcef1b9-de07-490e-b888-332bda733de6",
			'ptsplus_graphql_livestream' : ""
		}
		if mode in ['maincatg','ptsplus_graphql_livestream']:
			return graphql_settings[mode]
		else:
			return graphql_settings[mode].replace(replace_patterns[mode],queryStr)

	def ret_ptsplus_menu_catgs(self,mode='maincatg', queryStr='KIDS_AND_FAMILY', loginidpw=None):
		ptsplus_req_apiurl = 'https://www.ptsplus.tv/graphql'
		# self.settings[src+'login_cookieinf']['cookieinf']

		# self.ptspluslogin(ptsplusloginidpw=loginidpw)
		# ptscatgsurl = 'https://prod-api.ptsplus.tv/program/channel?offset=0&limit=0'
		# catgs = self.requesturl_get_ret(ptscatgsurl,headers=self.ptsplus_reqheader_after_login)
		# catgs = self.parse_json_response(catgs)['data']
		# catgsurl = self.requesturl_get_ret('https://www.ptsplus.tv/zh',headers=self.ptsplus_reqheader_after_login)
		# catgsurl = re.search(r'<script src="([a-zA-Z\/\_\d-]+?app-.+?\.js){1}".+?</script>',catgsurl).group(1)
		# catgsurl = 'https://www.ptsplus.tv'+catgsurl
		# catgs = self.requesturl_get_ret(catgsurl,headers=self.ptsplus_reqheader_after_login)
		if mode=='maincatg':
			catgs = [{'genreName':catg, 'genreId':element} for catg,element in self.ret_ptsplus_graphql(mode=mode).items()]
			return catgs
		if mode=='ptsplus_graphql_livestream':
			return None
		reqStr = self.ret_ptsplus_graphql(mode=mode, queryStr=queryStr).strip()
		reqheaders_std = {
			'Origin': 'https://www.ptsplus.tv',
			'user-agent': self.useragent,
			'Sec-Fetch-Site': 'same-origin',
			'Accept': '*/*; q=0.01',
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
			'Host': 'www.ptsplus.tv',
			'DNT': '1',
		}
		reqheaders_ptspluslogin = self.merge_two_dicts(reqheaders_std, {
			'Referer': "https://www.ptsplus.tv/",
			'Sec-Fetch-Dest': 'empty',
			'Sec-Fetch-Mode': 'cors',
			'x-language': 'zh-TW',
			'content-type': 'application/json',
			'authority': 'www.ptsplus.tv',
			# 'X-Requested-With': 'XMLHttpRequest',
		})
		self.prepare_logininf(src='ptsplus')
		reqheaders_ptspluslogin = self.merge_two_dicts(reqheaders_ptspluslogin, self.settings['ptspluslogin_cookieinf']['cookieinf'])
		session = requests.Session()
		retryfetch = True
		retry_n = 0
		while retryfetch and retry_n<2:
			if 'Authorization' not in reqheaders_ptspluslogin or retry_n>0:
				self.ptspluslogin()
				self.prepare_logininf(src='ptsplus')
				reqheaders_ptspluslogin = self.merge_two_dicts(reqheaders_ptspluslogin, self.settings['ptspluslogin_cookieinf']['cookieinf'])
			session.headers.update(reqheaders_ptspluslogin)
			response = session.post(ptsplus_req_apiurl, json=json.loads(reqStr))
			responsejson = self.parse_json_response(response.text)
			if "error" not in responsejson:
				retryfetch = False
			retry_n += 1
		# ptsplus_graphql_guide ptsplus_graphql_videomarketinglabel ptsplus_graphql_programdetail ptsplus_graphql_episode ptsplus_graphql_livestream
		if mode=='ptsplus_graphql_guide':
			responsedata = responsejson["data"]["guides"]
			return responsedata
		if mode=='ptsplus_graphql_videomarketinglabel':
			responsedata = responsejson["data"]["videoMarketingLabel"]["videos"]
			for program_i,program in enumerate(responsedata):
				tpwholeseasons = []
				for season_i,season in enumerate(program['program']['seasons']):
					tpwholeseasons.append(str(season['releaseYear']))
				tpwholeseasons = ",".join(tpwholeseasons)
				responsedata[program_i]['program']['wholeseasons'] = "({tpwholeseasons})".format(tpwholeseasons=tpwholeseasons) if tpwholeseasons!="" else ""
			return responsedata
		if mode=='ptsplus_graphql_programdetail':
			responsedata = responsejson["data"]["program"]["seasons"]
			episodes = []
			for season in responsedata:
				newseason_data = {'season_'+key:season[key] for key in ['id','name','cover','releaseYear','bannerLOGO','bannerCover']}
				for episode in season['episodes']:
					video_prefix_dict = {'video_'+video_prefix_dict_k:video_prefix_dict_v for video_prefix_dict_k,video_prefix_dict_v in episode['video'].items()}
					new_epi_data = self.merge_two_dicts(newseason_data, episode)
					new_epi_data = self.merge_two_dicts(new_epi_data, video_prefix_dict)
					episodes.append(new_epi_data)
			return episodes
		if mode=='ptsplus_graphql_episode':
			responsedata = responsejson["data"]["episode"]
			setcookies = session.cookies.get_dict()
			responsedata['cookie'] = setcookies
			return responsedata

	def ret_ptsplus_programs_under_a_mainsubcatg(self,loginidpw=None): #,genre=1,subgenre=1,limit=20,loginidpw=None
		graphql_req = self.ret_ptsplus_graphql(mode='maincatg').items()
		catg_requestss = {element[0]:element[1] for catg,element in self.settings['ptspluscatgs'].items()}
		self.ptspluslogin(ptsplusloginidpw=loginidpw)
		# dramalisturl_under_a_catg = 'https://prod-api.ptsplus.tv/program/genre/{}-{}?limit={}&offset=0'.format(genre,subgenre,limit)
		# tp = self.requesturl_get_jsonret(dramalisturl_under_a_catg,headers=self.ptsplus_reqheader_after_login)
		# tp = tp['data']
		# 'https://www.ptsplus.tv/graphql'
		return tp
	
	def ret_ptsplus_programs_under_a_subcatg_multi_run_wrapper(self, args):
		return self.ret_ptsplus_programs_under_a_subcatg(*args)

	def ret_ptsplus_programs_under_a_catg(self,genre=1,subgenrelimit=50):
		spargs = [(int(genre), c) for c in range(subgenrelimit)]
		datas = self.try_multi_run(self.ret_ptsplus_programs_under_a_subcatg_multi_run_wrapper, spargs)
		programslist = six.moves.reduce(lambda x,y: x+y if len(y)>0 else x, datas, [])
		programslist = self.ptsplus_convert_poster_img_json_format(programslist)
		return programslist

	def ret_ptsplus_episodes_under_a_program(self,pts_TVprogram_seasonid,loginidpw=None):
		self.ptspluslogin(ptsplusloginidpw=loginidpw)
		pts_TVprogram_seasonlisturl_prefix = 'https://prod-api.ptsplus.tv/program/season/{}/videos?offset=0&limit=0'
		pts_TVprogram_seasonlisturl = pts_TVprogram_seasonlisturl_prefix.format(pts_TVprogram_seasonid)
		episodeslist = self.requesturl_get_jsonret(pts_TVprogram_seasonlisturl,headers=self.ptsplus_reqheader_after_login)
		episodeslist = episodeslist['data']['Episode']
		episodeslist = self.ptsplus_convert_poster_img_json_format(episodeslist)
		for ep_i,ep in enumerate(episodeslist):
			# Youtube video in PTS
			if 'youtubeEmbed' in ep and ep['youtubeEmbed']!='':
				episodeslist[ep_i]['m3u8url'] = self.ret_ptsplus_youtube_video_url(youtube_video_id=ep['youtubeEmbed'])
				# print("url is {}".format(episodeslist[ep_i]['m3u8url']))
			else:
				episodeslist[ep_i]['m3u8url'] = self.ret_ptsplus_video_streaming_url(ep['videoId'])
		return episodeslist

	def ret_ptsplus_youtube_video_url(self, youtube_video_id):
		ytApikey_ptsplus = self.settings['youtube_api_key']
		if ytApikey_ptsplus is not None and ytApikey_ptsplus!="":
			youtubeApiUrl = "https://www.youtube.com/youtubei/v1/player?key={ytApikey_ptsplus}&prettyPrint=false".format(ytApikey_ptsplus=ytApikey_ptsplus)
			req_json_data = {
				"videoId": youtube_video_id,
				"context": {
					"client": {
						"clientName": "WEB_EMBEDDED_PLAYER",
						"clientVersion": "1.20230627.01.00",
						"originalUrl": "https://www.youtube.com/embed/{youtube_video_id}?origin=https%3A%2F%2Fwww.ptsplus.tv&widgetid=2".format(youtube_video_id=youtube_video_id),
					}
				}
			}
			# print(f"req_json_data is {req_json_data}")
			youtubeApiRetData = self.requesturl_post_jsonret(youtubeApiUrl, json=req_json_data, headers={'Host':"www.googleapis.com"}) #self.ptsplus_reqheader_after_login
			# print(f"youtubeApiRetData is {youtubeApiRetData}")
			youtubeApiRetStreamingData = youtubeApiRetData['streamingData']
			if 'hlsManifestUrl' in youtubeApiRetStreamingData:
				return youtubeApiRetStreamingData['hlsManifestUrl']
			elif 'dashManifestUrl' in youtubeApiRetStreamingData:
				return youtubeApiRetStreamingData['dashManifestUrl']
			elif 'adaptiveFormats' in youtubeApiRetStreamingData:
				return youtubeApiRetStreamingData['adaptiveFormats'][0]['url']
			elif 'formats' in youtubeApiRetStreamingData:
				return youtubeApiRetStreamingData['formats'][-1]['url']
			else:
				print("\n\n youtubeApiRetStreamingData is {youtubeApiRetStreamingData} \n\n".format(youtubeApiRetStreamingData=youtubeApiRetStreamingData))
				return "error in ret_ptsplus_youtube_video_url at {youtube_video_id}".format(youtube_video_id=youtube_video_id)
		else:
			return "plugin://plugin.video.youtube/play/?video_id="+youtube_video_id


	def ptsplus_convert_poster_img_json_format(self,programslist):
		for program_i,program in enumerate(programslist):
			programslist[program_i]['artWorkImagesList'] = []
			programslist[program_i]['artWorkImagesDict'] = {}
			for artWork in program['artWorksList']:
				key_artWork = artWork['type']
				programslist[program_i]['artWorkImagesDict'][key_artWork] = six.moves.urllib.parse.quote_plus(artWork['fileURL'], safe=':/')
				programslist[program_i]['artWorkImagesList'].append(six.moves.urllib.parse.quote_plus(artWork['fileURL'], safe=':/'))
		return programslist

	def ret_ptsplus_video_streaming_url(self,videoId,loginidpw=None):
		self.ptspluslogin(ptsplusloginidpw=loginidpw)
		pts_TVprogram_video_url_prefix = 'https://prod-api.ptsplus.tv/me/play/signedURL/detail/1080/playlist.m3u8?access_token={}&videoId={}'
		pts_TVprogram_video_url = pts_TVprogram_video_url_prefix.format(self.ptsplus_loginres['accessToken'],videoId)
		return pts_TVprogram_video_url

	def ret_linetv_main_menu_catgs(self, catgurl=None):
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
			root = self.requesturl_get_ret(self.linetv_host_url)
			root = htmlement.fromstring(root)
			target_catgsnavs = root.findall(".//nav//a")
			target_catgsnavs = [{'link': e.get('href'), 'text': e.text} for e in target_catgsnavs]
			target_catgsnavs = [e for e in target_catgsnavs if re.search("channel_id", e['link'])]
			target_catgsnavs = [{e['text']: re.findall("channel_id=(.+)", e['link'])[0] } for e in target_catgsnavs]
		elif False:
			root = self.requesturl_get_ret('https://static.linetv.tw/api/drama/category.json')
			target_catgsnavs = json.loads(root)['data']
			target_catgsnavs = [{e['ga']: str(e['id'])} for e in target_catgsnavs] #e['id']
			target_catgsnavs = six.moves.reduce(self.merge_two_dicts,target_catgsnavs)
			return target_catgsnavs
		else:
			catgurl = self.linetv_host_url if catgurl==None else catgurl
			data = self.requesturl_get_ret(catgurl)
			root = htmlement.fromstring(data)
			target_catgsnavs = []
			for item in root.findall(".//div//nav//a"):
				if re.search('/channel/',item.get('href'))!=None and item.text!=None:
					target_catgsnavs.append({
						item.text: "{}{}".format(self.linetv_host_url,item.get("href"))
						})
			target_catgsnavs = six.moves.reduce(self.merge_two_dicts,target_catgsnavs)
			return target_catgsnavs

	def ret_linetv_dramas_of_a_catg(self, catgurl=1):
		researchres = re.search(r'channel/(\d+)/genre/(\d+)',catgurl)
		#linetv_catg = self.ret_linetv_main_menu_catgs()
		#dataurl_for_drama_in_a_category = 'https://www.linetv.tw/drama?area={}'
		#linetv_json_drama_data_url = catgurl.replace('https://www.linetv.tw/channel/','https://api.linetv.tw/search/v1/contents/channel/')
		#dataurl_for_drama_in_a_category = 'https://api.linetv.tw/content/v2/channels-pc-web/{}?appId=062097f1b1f34e11e7f82aag22000aee&chocomemberAppId=86a6b258-ac30-4816-bc14-a31e514226d7&version=9.61.1&countryCode=TW&languageId=zh'
		#dataurl_for_drama_in_a_category = 'https://api.linetv.tw/search/v1/contents/channel/{}/sort/VIEW_COUNT_LAST_7_DAYS/order/DESC/genre/?appId=062097f1b1f34e11e7f82aag22000aee&chocomemberAppId=86a6b258-ac30-4816-bc14-a31e514226d7&version=9.73.1&countryCode=TW&languageId=zh'
		#linetv_catg_api_req_header_refer = {str(v):dataurl_for_drama_in_a_category.format(v) for k,v in linetv_catg.items()}
		dataurl_for_drama_in_a_category = "https://api.linetv.tw/search/v1/contents/channel/{}/sort/VIEW_COUNT_LAST_7_DAYS/order/DESC/genre/{}?appId=062097f1b1f34e11e7f82aag22000aee&chocomemberAppId=86a6b258-ac30-4816-bc14-a31e514226d7&version=9.73.1&countryCode=TW&languageId=zh"
		dataurl_for_drama_in_a_category = dataurl_for_drama_in_a_category.format(researchres.group(1),researchres.group(2))
		#strcatg = str(catg)
		data = self.requesturl_get_ret(dataurl_for_drama_in_a_category)
		data = json.loads(data)
		if False:
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
		elif False:
			dramalist = six.moves.reduce(lambda x,y: x+[y], data['data']['home'], [])
			dramalist = six.moves.reduce(lambda x,y: x+y['data'], dramalist, [])
			dramalist = six.moves.filter(lambda x: ('type' in x) and (x['type']=='drama'), dramalist)
			#dramalist = six.moves.filter(lambda x: x['type']=='drama', dramalist)
			dramalist = list(dramalist)
			for dramalist_i, drama in enumerate(dramalist):
				for dramadatakey in ['description','info']:
					if dramadatakey not in drama:
						drama[dramadatakey] = ''
			return dramalist
		else:
			data = data['data']
			for dramalist_i, drama in enumerate(data):
				data[dramalist_i] = {
					'id': drama['contentId'],
					'name': drama['name'],
					'type': drama['type'],
					'info': drama['introduction'],
					'description': drama['introduction'],
					'posterUrl': drama['landscapePosterUrl'],
					'verticalPosterUrl': drama['portraitPosterUrl'],
				}
			return data

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

	def ret_linetv_drama(self, dramaid, method="old"):
		linetv_api_req_header = {
			'user-agent': self.useragent,
			'referer': "https://www.linetv.tw/drama/{dramaid}/".format(dramaid=dramaid),
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
		if method=="old":
			responsejsondramas = self.ret_linetv_dramas_metadata()
			for d in responsejsondramas:
				if (d['drama_id'])==int(dramaid):
					print("d is {d} in ret_linetv_drama".format(d=d))
					return d
		elif method=="invalid1":
			req_url = "https://itad.linetv.tw/api/v2/iba/web/v2?appId=062097f1b1f34e11e7f82aag22000aee&chocomemberAppId=86a6b258-ac30-4816-bc14-a31e514226d7&version=10.37.0&countryCode=TW&languageId=zh&dramaId="
			req_url += str(dramaid)
			req_headers = {
				'user-agent': self.useragent,
				'referer': 'https://www.linetv.tw/',
				'origin': 'https://www.linetv.tw',
				"method": "GET",
				"authority": "itad.linetv.tw",
				"scheme": "https",
				# "path": "/api/drama",
				"sec-fetch-dest": "empty",
				"dnt": "1",
				"accept": "*/*",
				"sec-fetch-site": "same-origin",
				"sec-fetch-mode": "cors",
				"accept-encoding": "gzip, deflate, br",
				"accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
			}
			responsejson = self.requesturl_get_ret(req_url, headers=req_headers)
			responsejson = self.parse_json_response(responsejson)
			print("responsejson is {responsejson}".format(responsejson=responsejson))
		else:
			responsejson = self.requesturl_get_ret("https://www.linetv.tw/api/dramaInfo/{dramaid}".format(dramaid=dramaid), headers=linetv_api_req_header)
			responsejson = self.parse_json_response(responsejson)
			responsejson = responsejson['info']
			return responsejson

	def ret_linetv_drama_description_multi_run_wrapper(self, args):
		return self.ret_linetv_drama_description(*args)

	def ret_linetv_drama_description(self, drama_id, episode=1):
		drama_page_url = 'https://www.linetv.tw/drama/'+str(drama_id)+'/eps/'+str(episode)
		drama_page_html = self.requesturl_get_ret(drama_page_url)
		root = htmlement.fromstring(drama_page_html)
		drama_descriptions = ["".join(d.itertext()) for d in root.find(".//section")]
		# print(f"drama_descriptions is {drama_descriptions}")
		# drama_descriptions = [t for t in drama_descriptions if re.search("h3",t) is not None]
		drama_descriptions = "\n".join(drama_descriptions)
		if False:
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
		return drama_descriptions

	def ret_linetv_drama_episode_seo_descriptions(self, drama_id):
		referer = "https://www.linetv.tw/drama/{drama_id}".format(drama_id=drama_id)
		linetv_api_req_header = {
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
		descriptions_data = self.requesturl_get_ret('https://static.linetv.tw/seo/drama/seo_sd_{drama_id}.json'.format(drama_id=drama_id), headers=linetv_api_req_header)
		descriptions_data = self.parse_json_response(descriptions_data)
		return descriptions_data

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

	def get_linetv_singleepidata(self, drama_id='', episode='', reqheaders=''):
		if episode=='':
			episode = 1
		# epi_data = 'https://www.linetv.tw/api/part/'+str(drama_id)+'/eps/'+str(episode)+'/part?chocomemberId=null'
		epi_data = 'https://www.linetv.tw/api/part/{drama_id}/eps/{episode}/part?appId={appid}&device=desktop_web&instanceId={instanceid}&sessionId={sessionid}&chocomemberId=&productType=VOD&os=&version=10.30.0'. \
			format(episode=episode,
		  		drama_id=drama_id,
				appid='062097f1b1f34e11e7f82aag22000aee',
				instanceid='f7f7df1c-4b51-4dc0-9fa4-cc04a6acf8f3',
				sessionid='f849b082-f058-4e30-8bf8-a4ed0dbfc32a')
		epi_data = self.requesturl_get_ret(epi_data, headers=reqheaders)
		epi_data = self.parse_json_response(epi_data)
		if 'epsInfo' not in epi_data:
			return False #only VIP may watch
		else:
			subtitleurl = epi_data['epsInfo']['source'][0]['links'][0]['subtitle']
			for_decrypt_post_data = {"keyType":epi_data['epsInfo']['source'][0]['links'][0]['keyType'],
						"keyId":epi_data['epsInfo']['source'][0]['links'][0]['keyId'],
						"dramaId":drama_id,
						"eps":epi_data['dramaInfo']['eps']}
			decryptdata = self.requesturl_post_ret('https://www.linetv.tw/api/part/dinosaurKeeper', data=for_decrypt_post_data, headers=reqheaders)
			decryptdata = self.parse_json_response(decryptdata)
			return epi_data, decryptdata, subtitleurl

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
		epi_data = self.get_linetv_singleepidata(drama_id, episode, reqheaders)
		if epi_data is not False:
			epi_data, decryptdata, subtitleurl = epi_data
			multibitrateplaylist = epi_data['epsInfo']['source'][0]['links'][0]['link']
			basepath = six.moves.urllib.parse.urlparse(multibitrateplaylist)
			basepath = basepath.scheme+'://'+basepath.netloc+os.path.dirname(basepath.path)
			singlebitrateplaylist = self.requesturl_get_ret(multibitrateplaylist).split("\n")
			singlebitrateplaylist = six.moves.filter(lambda x: x.find('480p')!=-1, singlebitrateplaylist)
			singlebitrateplaylist = six.moves.filter(lambda x: x.find('m3u8')!=-1, singlebitrateplaylist)
			singlebitrateplaylist = basepath+'/'+next(singlebitrateplaylist)
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
				'subtitle_url': subtitleurl
				}
			)
			return epi_data
		else:
			return False

	def ret_linetv_streaming_url(self, url):
		sdplaylist = self.ret_linetv_episode_data(url=url)
		sdplaylist = sdplaylist['playlisturl']+"|Origin=https://www.linetv.tw|Referer=https://www.linetv.tw/drama/"+sdplaylist['drama_id']+"/eps/1|user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0|authentication="+sdplaylist['token']
		return sdplaylist

	def ret_viutv(self, chid):
		#https://ewcdn10.nowe.com/session/p8-5-8518f8ab588-79c6022a266edc9/Content/DASH_VOS3/Live/channel(VOS_CH099)/manifest.mpd?token=4114b6b097b0ab0a8d2f4978b9b39300_1605648738
		sdplaylist = self.ret_linetv_episode_data(url=url)
		sdplaylist = sdplaylist['playlisturl']+"|Origin=https://www.linetv.tw|Referer=https://www.linetv.tw/drama/"+sdplaylist['drama_id']+"/eps/1|user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0|authentication="+sdplaylist['token']
		return sdplaylist

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

	def getNetworkResources(self, driver, ret="name"):
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
			self.driver = webdriver.Chrome(executable_path=self.binary_and_driver_path['chromedriver_path'], options=chromeoptions, desired_capabilities=merged_chrome_desired_capabilities, service_log_path=self.settings['seleniumlogpath'])
		elif self.binary_and_driver_path['browser_type']=='firefox':
			self.driver = webdriver.Firefox(executable_path=self.binary_and_driver_path['geckodriver_path'], firefox_binary=self.binary_and_driver_path['firefoxbinary_location'], firefox_profile=self.firefoxprofile, firefox_options=firefoxoptions, desired_capabilities=self.caps_ff, log_path=self.settings['seleniumlogpath'])
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
			networklogs = self.getNetworkResources(driver)
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
			searchres = six.moves.filter(lambda x: 'request' in list(six.viewkeys(x)), searchres)
			searchres = six.moves.filter(lambda x: 'url' in list(six.viewkeys(x['request'])), searchres)
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

	def get_hami_better_q_streamingsrc(self, streamingurl, newq='1920x1080'):
		pattern = re.compile('{newq}.+\n(.+)'.format(newq=newq))
		headers = {
			'User-Agent':self.useragent,
			'referer':'https://hamivideo.hinet.net',
			'origin':'https://hamivideo.hinet.net',
		}
		m3u8_content = self.requesturl_get_ret(streamingurl, headers=headers)
		parsed_url = six.moves.urllib.parse.urlparse(streamingurl)._asdict()
		newpathbase = parsed_url.pop('path')
		newpathbase = '/'.join(newpathbase.split('/')[:-1])
		newstreamingurl = '{scheme}://{netloc}{newpathbase}/{newpath}'.format(
			**parsed_url,
			newpathbase=newpathbase,
			newpath=pattern.search(m3u8_content).group(1)
			)
		return newstreamingurl

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
	parser.add_argument("--ptsloginid", help="ptsloginid")
	parser.add_argument("--ptsloginpw", help="ptsloginpw")
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
			# streamingurl = hamic.get_hami_better_q_streamingsrc(streamingurl)
			subtitleurl = None
		elif type=='linetv':
			epi_data = hamic.ret_linetv_episode_data(url=cchurl)
			streamingurl = epi_data['multibitrateplaylist']
			subtitleurl = epi_data['epsInfo']['source'][0]['links'][0]['subtitle']
		elif type=='linetoday':
			streamingurl = hamic.get_streamingurl_of_ch(cchurl, type=type, logtype='networklogs')
			subtitleurl = None
		elif type=='ptsplus_ch':
			loginpw = (args.ptsloginid, args.ptsloginpw)
			streamingurl = hamic.ret_ptsplus_episodes_under_a_program(pts_TVprogram_seasonid=churl,loginidpw=loginpw)
			streamingurl = json.dumps(streamingurl)
		elif type=='ptsplus_video':
			loginpw = (args.ptsloginid, args.ptsloginpw)
			streamingurl = hamic.ret_ptsplus_video_streaming_url(cchurl,loginidpw=loginpw)
		if re.search('(timed out|timeout|unknown error|connection refused|error in ret_hami_streaming_url_by_req)', streamingurl)!=None:
			pass
		else:
			print(streamingurl)