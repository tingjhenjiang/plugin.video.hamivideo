import re, socket, json, sys, six
from xbmcswift2 import Plugin, xbmc, xbmcaddon, xbmcgui, xbmcplugin
from resources.lib.hamivideo.api import Hamivideo
import base64, time, os
try:
	from multiprocessing.dummy import Pool as ThreadPool
	threadpool_imported = True
except:
	threadpool_imported = False
try:
	import YDStreamExtractor
	yDStreamExtractor_imported = True
except:
	yDStreamExtractor_imported = False
#import web_pdb

socket.setdefaulttimeout(180)
fakemediaurl_suffix = 'index.m3u8'
try:
	import multiprocessing
	workers = multiprocessing.cpu_count()
except:
	workers = 4
#project https://www.9900.com.tw/B003.htm
#project https://www.gdaily.org/22554/2020-watch-video
plugin = Plugin()
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
addonid = xbmcaddon.Addon().getAddonInfo('id')
plugin_storagepath = plugin.storage_path
settings = {
	'chromedriver_path': plugin.get_setting('chromedriver_path',  six.text_type),
	'chromebinary_location': plugin.get_setting('chromebinary_location',  six.text_type),
	'geckodriver_path': plugin.get_setting('geckodriver_path',  six.text_type),
	'firefoxbinary_location': plugin.get_setting('firefoxbinary_location',  six.text_type),
	'docker_remote_selenium_addr': plugin.get_setting('docker_remote_selenium_addr',  six.text_type),
	'browser_type': plugin.get_setting('browser_type',  six.text_type),
	'chromeublockpath': plugin.get_setting('chromeublockpath',  six.text_type),
	'firefoxublockpath': plugin.get_setting('firefoxublockpath',  six.text_type),
	'seleniumlogpath': plugin.get_setting('seleniumlogpath',  six.text_type),
	'ptsplusloginidpw': (plugin.get_setting('ptsplusid', six.text_type),plugin.get_setting('ptspluspw', six.text_type)),
	'ptsplusloginchecksum': plugin.get_setting('ptsplusloginchecksum', six.text_type),
	'ptsplusloginxapikey': plugin.get_setting('ptsplusloginxapikey', six.text_type),
	'hamiloginidpw': (plugin.get_setting('hamiid', six.text_type),plugin.get_setting('hamipw', six.text_type)),
	'youtube_api_key': plugin.get_setting('youtube_api_key', six.text_type)	
}

@plugin.route('/')
def index():
	hamichlst = [{
		'label': 'Hamivideo channels',
		'path': plugin.url_for('list_hamichannels', menutype='parent', subcatg='default'),
		'is_playable': False
	}]
	linetodaylst = [{
		'label': 'Line Today channels',
		'path': plugin.url_for('list_linetodaychannels'),
		'is_playable': False
	}]
	maplestagelst = [{
		'label': 'MapleStage channels',
		'path': plugin.url_for('list_maplestagechs', churl="default", menutype='parent'),
		'is_playable': False
	}]
	linetvlst = [{
		'label': 'Linetv channels',
		'path': plugin.url_for('list_linetvchannels', churl="default", menutype='parent', total_eps='default'),
		'is_playable': False
	}]
	ptspluslst = [{
		'label': 'PTS plus channels',
		'path': plugin.url_for('list_ptspluschannels', churl="default", menutype='parent', total_eps='default'),
		'is_playable': False
	}]
	viutvlst = [{
		'label': 'Viutv channels',
		'path': plugin.url_for('list_viutvchannels', churl="default", menutype='parent'),
		'is_playable': False
	}]
	pokulst = [{
		'label': 'Poku channels',
		'path': plugin.url_for('list_pokuchannels', churl="default", menutype='parent'),
		'is_playable': False
	}]
	dramaqlst = [{
		'label': 'Dramaq channels',
		'path': plugin.url_for('list_dramaq', drama_name="None"),
		'is_playable': False
	}]
	directplaylst = [{
		'label': 'Play Streaming URL Directly',
		'path': plugin.url_for('playchannel', churl=fakemediaurl_suffix, menutype='direct'),
		'is_playable': True,
	}]
	backgroundinfolist = [{
		'label': 'Background info',
		'path': plugin.url_for('backgroundinfo'),
		'is_playable': False
	},{
		'label': 'Next view mode',
		'path': plugin.url_for('nextviewmode'),
		'is_playable': False
	},]
	#linetodaylst+maplestagelst+viutvlst+pokulst+dramaqlst+
	return plugin.finish(hamichlst+linetvlst+ptspluslst+directplaylst) #view_mode=50

@plugin.route('/listhamichannels/<menutype>/<subcatg>')
def list_hamichannels(menutype="parent", subcatg="default"):
	hamic = Hamivideo(**settings)
	if menutype=="tv":
		channels = hamic.return_hamichannels()
		channels = [{
			'label': '%s %s %s' % (c['name'], c['programtime'], c['program']),
			'label2': '%s' % (c['program']),
			'path': plugin.url_for('playchannel', menutype='hami', churl=c['link']), #.replace('.do', '.m3u8')
			'icon': c['icon'],
			'thumbnail': c['icon'],
			'is_playable': True,
		} for c in channels]
	elif menutype=='dramavideos':
		channels = hamic.return_hamidramamovies()
		channels = [{
			'label': '%s %s %s' % (c['name'], c['programtime'], c['program']),
			'label2': '%s' % (c['program']),
			'path': plugin.url_for('list_hamichannels', menutype=menutype, subcatg=subcatg),
			'icon': c['icon'],
			'thumbnail': c['icon'],
			'is_playable': False,
		} for c in channels]
	else:
		channels = [
			{'display':'電視運動館','name':'tv','icon':'https://static-hamivideo.cdn.hinet.net/resources/images/ic_logo_tv.svg'},
			{'display':'影劇館','name':'dramavideos','icon':'https://static-hamivideo.cdn.hinet.net/resources/images/ic_logo_video.svg'}
		]
		channels = [{
			'label': c['display'],
			'path': plugin.url_for('list_hamichannels', menutype=c['name'], subcatg='default'),
			'icon': c['icon'],
			'thumbnail': c['icon'],
			'is_playable': False,
		} for c in channels]
	return plugin.finish(channels)

@plugin.route('/listlinetodaychannels/')
def list_linetodaychannels():
	hamic = Hamivideo(**settings)
	channels = hamic.return_linetodaychs()
	channels = [{
		'label': c['name'],
		'path': plugin.url_for('playchannel', churl=c['link'].replace('.do', '.m3u8')+fakemediaurl_suffix, menutype='linetoday'),
		'icon': c['icon'],
		'thumbnail': c['icon'],
		'is_playable': True,
	} for c in channels]
	length_of_ch = str(len(channels))
	return plugin.finish(channels)

@plugin.route('/listlinetvchannels/<menutype>/<churl>')
def list_linetvchannels(churl="", menutype="parent"):
	hamic = Hamivideo(**settings)
	if menutype=="parent":
		channels = hamic.ret_linetv_main_menu_catgs(hamic.linetv_host_url)
		channels = [{
			'label': k,
			'path': plugin.url_for('list_linetvchannels', churl=v, menutype='listsubcatgs'),
			'icon': '',
			'thumbnail': '',
			'is_playable': False,
		} for k,v in channels.items()]
		channels.append({
			'label': '搜尋影片',
			'path': plugin.url_for('list_linetvchannels', churl='first', menutype='search'),
			'icon': '',
			'thumbnail': '',
			'is_playable': False,
		})
	if menutype=="search":
		if churl=='first':
			keyword = plugin.keyboard(six.ensure_str(''), heading="輸入搜尋關鍵字").strip()
			channels = hamic.ret_linetv_search_res_dict(keyword=keyword)
			channels = [{
				'label': c['name'] if 'name' in c else None,
				'label2': c['introduction'] if 'introduction' in c else None,
				'path': plugin.url_for('list_linetvchannels', churl=c['drama_id'], menutype='listeps'),
				'icon': c['poster_url'] if 'poster_url' in c else None,
				'thumbnail': c['vertical_poster'] if 'poster_url' in c else None,
				'info': None, #c['info'],
				'is_playable': False,
			} for c in channels]
	if menutype=="listsubcatgs":
		channels = hamic.ret_linetv_main_menu_catgs(churl)
		channels = [{
			'label': k,
			'path': plugin.url_for('list_linetvchannels', churl=v, menutype='listdramas'),
			'icon': '',
			'thumbnail': '',
			'is_playable': False,
		} for k,v in channels.items()]
	if menutype=="listdramas":
		#channels = hamic.ret_linetv_dramas_with_description_of_a_catg(churl)
		channels = hamic.ret_linetv_dramas_of_a_catg(churl)
		channels = [{
			'label': c['name'],
			'label2': c['description'],
			'path': plugin.url_for('list_linetvchannels', churl=c['id'], menutype='listeps'),
			'icon': c['posterUrl'],
			'thumbnail': c['verticalPosterUrl'],
			'info': c['info'],
			'is_playable': False,
		} for c in channels]
	if menutype=='listeps':
		drama_id = int(churl)
		drama = hamic.ret_linetv_drama(drama_id, method='needparse')
		episode_args = [(drama_id, c) for c in range(1, drama['total_eps']+1)]
		try:
			descriptions = hamic.ret_linetv_drama_episode_seo_descriptions(drama_id)
			descriptions = {int(d['eps']):d['description'] for d in descriptions['info'] }
		except:
			# descriptions = hamic.try_multi_run(hamic.ret_linetv_drama_description_multi_run_wrapper, episode_args)
			description = hamic.ret_linetv_drama_description(drama_id)
			descriptions = {c:description for c in range(drama['total_eps']+1)}
		episodedatas = [d for d in hamic.try_multi_run(hamic.ret_linetv_episode_data_multi_run_wrapper, episode_args) if d is not False]
		episodedatas = [None] + episodedatas
		channels = list()
		for c in range(1, int(drama['total_eps'])+1):
			try:
				reqheaders_strs = episodedatas[c]['reqheaders_strs']
				channel = {
					'label': episodedatas[c]['epsInfo']['eps_title'],
					'label2': '',
					'path': episodedatas[c]['multibitrateplaylist'],
					'icon': drama['vertical_poster_url'] if 'vertical_poster_url' in drama else None,
					'thumbnail': drama['vertical_poster_url'] if 'vertical_poster_url' in drama else None,
					'info': {'plot': descriptions[c]},
					'properties': {
						'inputstream': 'inputstream.adaptive',
						'inputstream.adaptive.license_type': 'com.widevine.alpha', #,  'com.microsoft.playready'
						'inputstream.adaptive.manifest_type': 'hls',
						'inputstream.adaptive.license_key': 'time='+str(round(time.time(),3)).replace('.','').ljust(13, '0')+'|'+reqheaders_strs+'||R', #str(int(time.time() ) )
						# 'inputstream.adaptive.stream_headers': reqheaders_strs,
					},
					'is_playable': True,
					#'setsubtitles': episodedatas[c]['subtitle_url']
				}
			except:
				channel = {
					'label': "第 {c} 集未上架".format(c=c),
					'label2': '',
					'path': None,
					'icon': None,
					'thumbnail': None,
					'info': None,
					'properties': None,
					'is_playable': False,
				}
			channels.append(channel)
	return plugin.finish(channels)

@plugin.route('/listptspluschannels/<menutype>/<churl>')
def list_ptspluschannels(churl="", menutype="parent"):
	hamic = Hamivideo(**settings)
	if menutype=="parent":
		channels = hamic.ret_ptsplus_menu_catgs(mode='maincatg')
		channels = [{
			'label': v['genreName'],
			'path': plugin.url_for('list_ptspluschannels', churl=v['genreId'], menutype='listtopics'),
			'icon': '',
			'thumbnail': '',
			'is_playable': False,
		} for v in channels]
	if menutype=="listtopics":
		channels = hamic.ret_ptsplus_menu_catgs(mode='ptsplus_graphql_guide', queryStr=churl)
		plugin.log.info('genreId is: '+churl)
		channels = [{
			'label': v['marketingLabel']['name'],
			'label2': '',
			'path': plugin.url_for('list_ptspluschannels', churl=v['marketingLabel']['id'], menutype='listprograms'),
			'info': {},
			'thumbnail': v['marketingLabel']['cover'],
			'icon': v['marketingLabel']['cover'],
			'is_playable': False,
		} for v in channels]
	if menutype=="listprograms":
		channels = hamic.ret_ptsplus_menu_catgs(mode='ptsplus_graphql_videomarketinglabel', queryStr=churl)
		plugin.log.info('genreId is: '+churl)
		channels = [{
			'label': "{} {}".format(v['program']['name'], v['program']['wholeseasons']),
			'label2': '',
			'path': plugin.url_for('list_ptspluschannels', churl=v['program']['id'], menutype='listeps'),
			'info': {'plot': v['program']['introduction']},
			'thumbnail': v['program']['latestCover'],
			'icon': v['program']['latestCover'],
			'is_playable': False,
		} for v in channels]
	if menutype=="listeps":
		import six.moves.urllib.parse
		plugin.log.info('programId is: '+churl)
		retchannels = []
		channels = hamic.ret_ptsplus_menu_catgs(mode='ptsplus_graphql_programdetail', queryStr=churl)#hamic.ret_ptsplus_episodes_under_a_program(churl)
		for channel_i,v in enumerate(channels):
			host = six.moves.urllib.parse.urlparse(v['video_stream']).netloc
			subtitleurl = v['video_subtitles'] if len(v['video_subtitles'])>1 else None
			streamingurl = v['video_stream']
			streamingurl += 'hls.m3u8'
			reqheaders_strs = 'Authority=%s&Host=%s&Referer=https://www.ptsplus.tv&Origin=https://www.ptsplus.tv&User-Agent=%s' % (host,host,hamic.useragent)
			reqheaders_strs = reqheaders_strs.strip()
			retchannels.append( {
				'label': "{} 第 {:03d} 集 {}  ({})".format( v['season_name'], v['number'], v['name'], v['season_releaseYear']),
				'label2': '',
				'path': streamingurl,
				'info': {'plot': v['introduction'],'year':v['season_releaseYear']},
				'thumbnail': v['cover'],
				'icon': v['cover'],
				'properties': {
					'inputstream': 'inputstream.adaptive',
					'inputstream.adaptive.manifest_type': 'hls',
					'inputstream.adaptive.stream_headers': reqheaders_strs,
					'inputstream.adaptive.manifest_headers': reqheaders_strs,
					'inputstream.adaptive.manifest_params': v['video_urlPrefixSignature'],
					'inputstream.adaptive.stream_params': v['video_urlPrefixSignature'],
				},
			'is_playable': True,
			} )
		channels = sorted(retchannels, key=lambda k: k['label'])
	return plugin.finish(channels)

#https://ewcdn14.nowe.com/session/p8-5-f9faefbc85c-318d3fad569f91c/Content/DASH_VOS3/Live/channel(VOS_CH099)/manifest.mpd?token=64115504543cf37b453522b15e9d1f54_1590492587
#https://ewcdn13.nowe.com/session/p8-3-37e14e40349-c4ae989921b1c8d/Content/DASH_VOS3/Live/channel(VOS_CH099)/manifest.mpd?token=45004cf6c70e3c78068506ad52ec14fc_1590493141
#https://ewcdn13.nowe.com/session/p8-3-37e14e40349-c4ae989921b1c8d/Content/DASH_VOS3/Live/channel(VOS_CH099)/manifest.mpd?token=45004cf6c70e3c78068506ad52ec14fc_1590493141
#https://ewcdn13.nowe.com/session/p8-3-37e14e40349-c4ae989921b1c8d/Content/DASH_VOS3/Live/channel(VOS_CH099)/manifest.mpd?token=45004cf6c70e3c78068506ad52ec14fc_1590493141
#listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
#listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
#listitem.setMimeType('application/dash+xml')
#listitem.setProperty('inputstream.adaptive.stream_headers', 'Referer=blah&User-Agent=Blah')
#listitem.setContentLookup(False)
@plugin.route('/listviutvchannels/<menutype>/<churl>')
def list_viutvchannels(churl="", menutype="parent"):
	hamic = Hamivideo(**settings)
	channels = [hamic.ret_viutv(chid) for chid in ["096","099"]]
	channels = [{
			'label': c['name'],
			'label2': c['description'],
			'path': plugin.url_for('playchannel', churl=c['mpdurl'], menutype='viutv'),
			'icon': c['icon'],
			'thumbnail': c['icon'],
			'info': c['info'],
			'properties': {
				'inputstreamaddon': 'inputstream.adaptive',
				'inputstream.adaptive.license_type': 'com.widevine.alpha', #,  'com.widevine.alpha'
				'inputstream.adaptive.manifest_type': 'mpd',
				'inputstream.adaptive.license_key': "|".join([
					"https://fwp.nowe.com/wrapperWV",
					json.dumps({
						'Host':'fwp.nowe.com',
						'Origin':'https://viu.tv',
						'Referer':'https://viu.tv/',
						'TE':'Trailers',
					}),
					json.dumps({
						"rawLicenseRequestBase64":"CAQ=",
						"drmToken":c['drmToken'],
					}),
					"B", #[Response]
					#'inputstream.adaptive.stream_headers': reqheaders_strs,
				])
			},
			'is_playable': True,
		} for c in channels]
	return plugin.finish(channels)

@plugin.route('/listmaplestagedramas/<menutype>/<churl>')
def list_maplestagechs(churl="", menutype="parent"):
	hamic = Hamivideo(**settings)
	if menutype=="parent":
		channels = hamic.ret_maplestage_parent_catgs()
		channels = [{
			'label': c['name'], #+xbmc.executebuiltin('Container.SetViewMode(%s)' % view_mode_id)
			'path': plugin.url_for('list_maplestagechs', churl=c['link'], menutype='underparent'),
			'icon': c['icon'],
			'thumbnail': c['icon'],
			'is_playable': False,
		} for c in channels]
	if menutype=="underparent":
		channels = hamic.ret_maplestage_dramas_of_a_parent(churl)
		channels = [{
			'label': c['name'],
			'path': plugin.url_for('list_maplestagechs', churl=c['link'], menutype='underdrama'),
			'icon': c['icon'],
			'thumbnail': c['icon'],
			'is_playable': False,
		} for c in channels]
	if menutype=="underdrama":
		channels = hamic.ret_episode_links_of_a_maplestage_drama(churl)
		drama_name = channels[0]['program']
		channels = [{
			'label': c['name'],
			'label2': c['info']['plot'],
			'path': plugin.url_for('playchannel', churl=c['link']+fakemediaurl_suffix, menutype='maplestage'),
			'icon': c['icon'],
			'thumbnail': c['icon'],
			'info': c['info'],
			'is_playable': True,
		} for c in channels]
		channels.append({
			'label': 'Switch to DramaQ sources for '+six.ensure_str(drama_name),
			'path': plugin.url_for('list_dramaq', drama_name=base64.b64encode(six.ensure_str(drama_name)) ),
			'is_playable': False,
		})
	length_of_ch = str(len(channels))
	return plugin.finish(channels, sort_methods = ['label', 'title'])

@plugin.route('/list_dramaq/<drama_name>')
def list_dramaq(drama_name="None"):
	hamic = Hamivideo(**settings)
	if drama_name=="None":
		drama_name = plugin.keyboard(six.ensure_str(''), heading="搜尋Dramaq/Qdrama")
	else:
		drama_name = base64.b64decode(drama_name)
	channels = hamic.ret_dramaq_episodes(drama_name)
	channels = [{
		'label': c['name'],
		'path': plugin.url_for('playchannel', churl=c['link']+fakemediaurl_suffix, menutype='dramaq'),
		'icon': c['icon'],
		'thumbnail': c['icon'],
		'info': c['info'],
		'is_playable': True,
	} for c in channels]
	return plugin.finish(channels, sort_methods = ['label'])

@plugin.route('/nextviewmode/')
def nextviewmode():
	#xbmc.executebuiltin('Container.NextViewMode()')
	#xbmcplugin.setContent(plugin.handle, 'movies')
	plugin.set_content('guide')


@plugin.route('/backgroundinfo')
def backgroundinfo():
	import platform, os
	hamic = Hamivideo(**settings)
	htmlsrc = "test"
	items = [
		{'label': plugin_storagepath},
		{'label': platform.machine()},
		{'label': settings['chromebinary_location']},
		{'label': settings['chromedriver_path']},
		{'label': htmlsrc}
	]
	return plugin.finish(items)

@plugin.route('/channeldetail/<churl>')
def show_channel_detail(churl):
	#hamic = Hamivideo()
	#xbmc.executebuiltin(streamingurl)
	#xbmcgui.Dialog().ok(addonname,streamingurl)
	plugin.log.info('now in addonname '+addonname+" and addon id is "+addonid)
	#plugin.log.info('parsed result: %s' % streamingurl)
	pluginplaybackurl = 'plugin://%s/play/%s' % (addonid, churl)
	#plugin.set_resolved_url(pluginplaybackurl)
	#plugin.log.info('Playing url: %s' % streamingurl)
	#return plugin.finish([{"label": 'test', 'path': 'test'}])
	#print(streamingurl)
	#pass
	#items = [{
	#	'label': 'play',
	#	'path': streamingurl,
	#	'is_playable': True
	#}]
	#return plugin.finish(items)

@plugin.route('/list_pokuchannels/<churl>/<menutype>')
def list_pokuchannels(churl='default', menutype='parent'):
	hamic = Hamivideo(**settings)
	nextmode = {
		'parent': 'drama',
		'drama': 'listepisodes',
		'search': 'listepisodes',
		'listepisodes': 'poku',
	}
	nextpluginurl = {
		'parent': 'list_pokuchannels',
		'drama': 'list_pokuchannels',
		'search': 'list_pokuchannels',
		'listepisodes': 'playchannel',
	}
	if menutype=='parent':
		channels = {
			'電視劇': 'tvseries',
			'電視劇美劇': 'us',
			'電視劇韓劇': 'kr',
			'電視劇陸劇': 'cn',
			'電視劇台劇': 'tw',
			'電視劇日劇': 'jp',
			'電影': 'movies',
			'電影劇情電影': 'dramamovie',
			'電影動作': 'action',
			'電影喜劇': 'comedy',
			'電影科幻': 'scifi',
			'電影愛情': 'romance',
			'電影動漫': 'anime',
			'電影戰爭': 'war',
			'電影恐怖': 'horror',
			'電影動畫': 'cartoon',
			'電影紀錄片': 'documentary',
			'綜藝': 'tvshow',
			'動漫': 'anime',
		}
		channels = {k:"https://poku.tv/vodtype/"+v+".html" for k,v in channels.items()}
		additional_channels = {
			'綜藝中國1': 'https://poku.tv/vodshow/tvshow-%E5%A4%A7%E9%99%B8----------.html',
			'綜藝臺灣': 'https://poku.tv/vodshow/tvshow-%E8%87%BA%E7%81%A3----------.html',
			'綜藝香港': 'https://poku.tv/vodshow/tvshow-%E9%A6%99%E6%B8%AF----------.html',
			'綜藝韓國': 'https://poku.tv/vodshow/tvshow-%E9%9F%93%E5%9C%8B----------.html',
			'綜藝日本': 'https://poku.tv/vodshow/tvshow-%E6%97%A5%E6%9C%AC----------.html',
			'綜藝中國2': 'https://poku.tv/vodshow/tvshow-%E4%B8%AD%E5%9C%8B----------.html',
			'綜藝歐美': 'https://poku.tv/vodshow/tvshow-%E6%AD%90%E7%BE%8E----------.html',
			'動漫中國': 'https://poku.tv/vodshow/anime-%E5%A4%A7%E9%99%B8----------.html',
			'動漫臺灣': 'https://poku.tv/vodshow/anime-%E8%87%BA%E7%81%A3----------.html',
			'動漫香港': 'https://poku.tv/vodshow/anime-%E9%A6%99%E6%B8%AF----------.html',
			'動漫韓國': 'https://poku.tv/vodshow/anime-%E9%9F%93%E5%9C%8B----------.html',
			'動漫日本': 'https://poku.tv/vodshow/anime-%E6%97%A5%E6%9C%AC----------.html',
			'動漫美國': 'https://poku.tv/vodshow/anime-%E7%BE%8E%E5%9C%8B----------.html',
		}
		channels = hamic.merge_two_dicts(channels, additional_channels)
		channels = [{
			'label': six.ensure_str(k),
			'path': plugin.url_for(nextpluginurl[menutype], churl=v, menutype=nextmode[menutype]),
			'icon': '',
			'thumbnail': '',
			'info': '',
			'is_playable': False,
		} for k,v in channels.items()]
		channels.append({
			'label': six.ensure_str('搜尋poku.tv'),
			'path': plugin.url_for(nextpluginurl[menutype], churl='search', menutype='search'),
			'icon': '',
			'thumbnail': '',
			'info': '',
			'is_playable': False,
		})
	if menutype=='search':
		searchkwd = plugin.keyboard(six.ensure_str(''), heading="搜尋Poku.tv")
		searchurl = 'https://poku.tv/vodsearch/-------------.html?submit=&wd='+searchkwd
		results = hamic.get_poku_dramas([searchurl,'search'])
		channels = [{
			'label': v['title'],
			'path': plugin.url_for(nextpluginurl[menutype], churl=v['link'], menutype=nextmode[menutype]),
			'icon': v['thumbnail'],
			'thumbnail': v['thumbnail'],
			'info': {
				'plot': v['description'],
			},
			'is_playable': False,
		} for v in results]
	if menutype in ['drama','listepisodes']:
		if menutype=='drama':
			allpagesnum_info = hamic.get_poku_dramas([churl,'allnum'])
			if allpagesnum_info['allpageslink']!=None:
				iterargs = [[x, menutype] for x in allpagesnum_info['allpageslink']]
				if threadpool_imported:
					pool = ThreadPool(workers)
					results = pool.map(hamic.get_poku_dramas, iterargs)
					pool.close()
					pool.join()
				else:
					results = [hamic.get_poku_dramas(iterarg) for iterarg in iterargs]
				results = reduce(lambda x,y: x+y, results)
			else:
				results = hamic.get_poku_dramas([churl,menutype])
				results = hamic.unique(results)
			is_playable = False
		else:
			results = hamic.get_poku_dramas([churl,menutype])
			is_playable = True
		channels = [{
			'label': v['title'],
			'path': plugin.url_for(nextpluginurl[menutype], churl=(v['link']+fakemediaurl_suffix if menutype=='listepisodes' else v['link']), menutype=nextmode[menutype]),
			'icon': v['thumbnail'],
			'thumbnail': v['thumbnail'],
			'info': {
				'plot': (v['description']+v['metadata'] if menutype=='listepisodes' else v['description']),
			},
			'is_playable': is_playable,
		} for v in results]
	return plugin.finish(channels, sort_methods = ['label'])

@plugin.route('/play/<menutype>/<churl>')
def playchannel(churl, menutype="hami"):
	hamic = Hamivideo(**settings)
	#hamic.clear_other_browser_processed()
	if menutype in ['linetoday','maplestage','linetv','dramaq','poku']:
		cchurl = churl.replace(fakemediaurl_suffix,'')
	elif menutype=='direct':
		if churl in ['','index.m3u8'] or churl is None:
			cchurl = plugin.keyboard(six.ensure_str(''), heading="輸入串流網址").strip()
		else:
			cchurl = churl
	else:
		cchurl = churl.replace('.m3u8','.do')
	plugin.log.info('starting parsing '+cchurl+' by '+menutype)
	if menutype=='maplestage':
		streamingurl = hamic.ret_maplestage_streamingurl_by_req(cchurl)
		#streamingurl = hamic.get_streamingurl_of_ch(cchurl, menutype=menutype, logtype='performancelogs')
		subtitleurl = None
		#decoding discussion: https://www.52pojie.cn/thread-944303-1-1.html
		#https://tools.ietf.org/html/rfc8216#section-4.3.2.4
		#https://github.com/peak3d/inputstream.adaptive/wiki/Integration
		#python someone demonstrate key decryption https://www.52pojie.cn/thread-986218-1-1.html
		#https://www.52pojie.cn/thread-1123891-1-1.html
	if menutype=='dramaq':
		streamingurl = hamic.ret_dramaq_streaming_url_by_req(cchurl)
		subtitleurl = None
	elif menutype=='hami':
		channelid = os.path.basename(cchurl).replace('.do','')
		print(f"channelid is {channelid}")
		streamingurl = hamic.ret_hami_streaming_url_by_req(channelid)
		print(f"streamingurl is {streamingurl}")
		# streamingurl = hamic.get_hami_better_q_streamingsrc(streamingurl)
		streamingurl = streamingurl+"|Referer=https://hamivideo.hinet.net&Origin=https://hamivideo.hinet.net&User-Agent={useragent}".format(useragent=hamic.useragent)
		subtitleurl = None
	#elif menutype=='linetv':
	#	epi_data = hamic.ret_linetv_episode_data(url=cchurl)
	#	streamingurl = epi_data['multibitrateplaylist']
	#	subtitleurl = epi_data['epsInfo']['source'][0]['links'][0]['subtitle']
	elif menutype=='viutv':
		streamingurl = cchurl #hamic.ret_viutv(churl)['mpdurl']
		subtitleurl = None
	elif menutype=='poku':
		streamingurl = hamic.get_poku_dramas([cchurl, 'findstreamingurl'])
		streamingurl = streamingurl['videourl']+'|'+streamingurl['req_header_str']
		subtitleurl = None
	elif menutype=='direct':
		patternContainsYoutube = re.search('(youtube\.com|youtu\.be/)',cchurl)
		if patternContainsYoutube!=None:
			youtube_video_id = re.match(".+((youtube\.com/.+v=|youtu\.be/|youtube\.com/live/)([^\s&\?]+))",cchurl).group(3)
			cchurl = "plugin://plugin.video.youtube/play/?video_id="+youtube_video_id
			plugin.log.info('procceed youtube url with '+cchurl)
		elif re.search('\.(m3u8|mp4|mov|rtsp|flv|mpd)',cchurl)!=None:
			cchurl = cchurl
		else:
			try:
				vid = YDStreamExtractor.getVideoInfo(cchurl,quality=2)
				cchurl = vid.streamURL()
			except Exception as errorYoutubeDL:
				plugin.log.info('yDStreamExtractor_imported is'+str(yDStreamExtractor_imported))
				plugin.log.info(str(errorYoutubeDL)+' error')
				cchurl = cchurl
		streamingurl = cchurl
		subtitleurl = None
	elif menutype=='linetoday':
		streamingurl = hamic.get_streamingurl_of_ch(cchurl, menutype=menutype, logtype='networklogs')
		subtitleurl = None
	if re.search('(timed out|timeout|unknown error|connection refused)', streamingurl)!=None:
		#hamic.clear_other_browser_processed()
		pass
	plugin.log.info('result of parsing is: '+streamingurl)
	plugin.set_resolved_url(streamingurl, subtitles=subtitleurl)

# Suggested view codes for each type from different skins (initial list thanks to xbmcswift2 library)
ALL_VIEW_CODES = {
	'list': {
		'skin.confluence': 50,  # List
		'skin.aeon.nox': 50,  # List
		'skin.droid': 50,  # List
		'skin.quartz': 50,  # List
		'skin.re-touched': 50,  # List
		'skin.estuary': 50,
		# 50 = List, 51 = Poster, 52 = Lists,53 = Shift, 54 = InfoWall  55 = Wide list, 500 = Wall,501= List, 502 = Fanart
	},
	'thumbnail': {
		'skin.confluence': 501,  # Thumbnail
		'skin.aeon.nox': 500,  # Wall
		'skin.droid': 51,  # Big icons
		'skin.quartz': 51,  # Big icons
		'skin.re-touched': 500,  # Thumbnail
		'skin.estuary': 500,
		# 50 = List, 51 = Poster, 52 = Lists, 53 = Shift, 54 = InfoWall  55 = Wide list, 500 = Wall,501= List, 502 = Fanart
	},
	'movies': {
		'skin.confluence': 500,  # Thumbnail 515, # Media Info 3
		'skin.aeon.nox': 500,  # Wall
		'skin.droid': 51,  # Big icons
		'skin.quartz': 52,  # Media info
		'skin.re-touched': 500,  # Thumbnail
		'skin.estuary': 52,
		# 50 = List, 51 = Poster,52 = Lists,53 = Shift, 54 = InfoWall  55 = Wide list, 500 = Wall,501= List, 502 = Fanart
	},
	'tvshows': {
		'skin.confluence': 500,  # Thumbnail 515, # Media Info 3
		'skin.aeon.nox': 500,  # Wall
		'skin.droid': 51,  # Big icons
		'skin.quartz': 52,  # Media info
		'skin.re-touched': 500,  # Thumbnail
		'skin.estuary': 54,
		# 50 = List, 51 = Poster,52 = Lists, 53 = Shift, 54 = InfoWall  55 = Wide list, 500 = Wall,501= List, 502 = Fanart
	},
	'seasons': {
		'skin.confluence': 50,  # List
		'skin.aeon.nox': 50,  # List
		'skin.droid': 50,  # List
		'skin.quartz': 52,  # Media info
		'skin.re-touched': 50,  # List
		'skin.estuary': 53,
		# 50 = List, 51 = Poster,52 = Lists, 53 = Shift, 54 = InfoWall  55 = Wide list, 500 = Wall,501= List, 502 = Fanart
	},
	'episodes': {
		'skin.confluence': 500,  # Media Info
		'skin.aeon.nox': 518,  # Infopanel
		'skin.droid': 50,  # List
		'skin.quartz': 52,  # Media info
		'skin.re-touched': 550,  # Wide
		'skin.estuary': 55.
		# 50 = List, 51 = Poster,52 = Lists,53 = Shift,54 = InfoWall  55 = Wide list, 500 = Wall,501= List, 502 = Fanart
	},
	'sets': {
		'skin.confluence': 500,  # List
		'skin.aeon.nox': 50,  # List
		'skin.droid': 50,  # List
		'skin.quartz': 50,  # List
		'skin.re-touched': 50,  # List
		'skin.estuary': 55,
		# 50 = List, 51 = Poster,52 = Lists,53 = Shift,54 = InfoWall  55 = Wide list, 500 = Wall,501= List, 502 = Fanart
	},
}


def set_view(view_mode, view_code=0):
	if get_setting('auto-view') == 'true':

		# Set the content for extended library views if needed
		xbmcplugin.setContent(int(sys.argv[1]), view_mode)
		if view_mode == MOVIES:
			xbmcplugin.setContent(int(sys.argv[1]), "movies")
		elif view_mode == TV_SHOWS:
			xbmcplugin.setContent(int(sys.argv[1]), "tvshows")
		elif view_mode == SEASONS:
			xbmcplugin.setContent(int(sys.argv[1]), "seasons")
		elif view_mode == EPISODES:
			xbmcplugin.setContent(int(sys.argv[1]), "episodes")
		elif view_mode == THUMBNAIL:
			xbmcplugin.setContent(int(sys.argv[1]), "thumbnail")
		elif view_mode == LIST:
			xbmcplugin.setContent(int(sys.argv[1]), "list")
		elif view_mode == SETS:
			xbmcplugin.setContent(int(sys.argv[1]), "sets")

		skin_name = xbmc.getSkinDir()  # Reads skin name
		try:
			if view_code == 0:
				view_codes = ALL_VIEW_CODES.get(view_mode)
				# kodi.log(view_codes)
				view_code = view_codes.get(skin_name)
				# kodi.log(view_code)
				xbmc.executebuiltin("Container.SetViewMode(" + str(view_code) + ")")
			# kodi.log("Setting First view code "+str(view_code)+" for view mode "+str(view_mode)+" and skin "+skin_name)
			else:
				xbmc.executebuiltin("Container.SetViewMode(" + str(view_code) + ")")
			# kodi.log("Setting Second view code for view mode "+str(view_mode)+" and skin "+skin_name)
		except:
			# kodi.log("Unable to find view code "+str(view_code)+" for view mode "+str(view_mode)+" and skin "+skin_name)
			pass
		# else:
		# 	xbmc.executebuiltin("Container.SetViewMode(sets)")

if __name__ == '__main__':
	plugin.run()