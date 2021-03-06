#!/usr/bin/env python

# Copyright 2016 Parham Pourdavood

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import httplib, urllib, base64, ast, json

def caption(image_src, api_key):
	"""
	It takes an image URL and an API key to send a request to Microsoft Computer Vision API
	and returns a caption(string) for the image. 

	Parameters
	----------
	image_src:		str
	api_key:		str
	                Microsoft's api_key

	Returns
	-------
	captioned_data:	str
	"""
	headers = {
		# Request headers
		'Content-Type': 'application/json',
		'Ocp-Apim-Subscription-Key': api_key,
	}

	params = urllib.urlencode({
		# Request parameters
		'maxCandidates': '1',
	})

    #data is the data that takes the image source. It is converted to str using a json method
	data = json.dumps({"Url": image_src}, separators=(',',':'))


	try:
		conn = httplib.HTTPSConnection('api.projectoxford.ai')
		conn.request("POST", "/vision/v1.0/describe?%s" % params, data, headers)
		response = conn.getresponse()
		data = ast.literal_eval(response.read())
		#captioned_data is a JSON that we need to navigate in order to get to the caption text.
		captioned_data = data['description']['captions'][0]["text"]
		return(captioned_data)
		conn.close()
	except Exception as e:
		print("")


import json
import requests
import urlparse

def is_url(url):
	"""
	check to see if the address is a URL or a local path

	parameters
	----------
	url:		str

	returns
	-------
	   -		Bool
	"""
	return urlparse.urlparse(url).scheme != ""


def upload(image_address):
	"""
	It uses uploads.im api to stream the images that are local.

	parameters
	----------
	image_address:		str
                        the local address of the image(e.g, 'images/photo.jpg')

    returns
    -------
    (main_url, main_width):			tuple
                        			(the url of new uploaded image, the width of the image)
	"""

	# A post request to uploads.im API to get the url of the uploaded image
	if is_url(image_address) == False:
		url = "http://uploads.im/api"
		files = {'media': open(image_address, 'rb')}
		request = requests.post(url, files=files)
		data = json.loads(request.text)
		image_url = data[u'data'][u'img_url']
		image_width = data[u'data'][u'img_width']
		main_url = image_url.encode('ascii','ignore')
		main_width = int(image_width.encode('ascii','ignore'))
		print("Processing...")
		return(main_url, main_width)
	else:
		request = requests.get("http://uploads.im/api?upload=" + image_address)
		data = json.loads(request.text)
		if request.status_code == 200 and data[u'status_code'] == 200:
			image_url = data[u'data'][u'img_url']
			image_width = data[u'data'][u'img_width']
			main_url = image_url.encode('ascii','ignore')
			main_width = int(image_width.encode('ascii','ignore'))
			print("Processing...")
			return(main_url, main_width)






from bs4 import BeautifulSoup
import os
from PIL import Image
import html5lib

def apply(html_file, api_key):

	'''
	it takes an html file and creates a new html file in which all the alt attribute of img tags
	are filled out with their related caption. (made by caption function in caption module)

	parameters
	----------
	html_file:		HTML
	api_key:		str
	                Microsoft's api_key
	'''

	with open(html_file) as f:
		html_data = f.read()

	#Using a third party library called beautifulSoup for parse and manipulate HTML DOM
	parsed_html = BeautifulSoup(html_data, 'html5lib')

	#assign all the image tags to img_tages
	img_tags = parsed_html.find_all('img')

	#goes over each img tag and see if its alt attribute has a value. If it doesn't,
	#it will fill out the alt with the corresponding caption for the image.
	for each_image in img_tags:
		value = each_image.get("alt")
		if value == None or value == "":
			# uploaded data is tuple: (Captioned text, the width of the image)
			uploaded_data = upload(each_image["src"])
			if uploaded_data != None:
				# here we filter the images that are smaller than 200px width.
				if uploaded_data[1] > 200:
					uploaded_url = uploaded_data[0]
					each_image["alt"] = caption(uploaded_url, api_key)

	# set the output file to desktop
	output_file = open(os.path.expanduser("~/Desktop/altify.html"), 'a')
	output_file.write(parsed_html.prettify())


import argparse



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("html", help = "The path to you html file", type = str)
	parser.add_argument("key", help = "Your Microsoft Cognitive Services Key", type = str)
	args = parser.parse_args()
	apply(args.html, args.key)
